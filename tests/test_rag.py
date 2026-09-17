import unittest

from api.rag.agro_rag import AgroRAG


class TestAgroRAG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rag = AgroRAG()

    def test_retrieve_existing_document(self):
        docs = self.rag.retrieve_agri_context(
            query="whitefly attack",
            crop="cotton",
            region="Punjab"
        )

        self.assertGreater(len(docs), 0)
        self.assertEqual(docs[0].crop_type, "cotton")

    def test_fallback_document(self):
        docs = self.rag.retrieve_agri_context(
            query="unknown disease",
            crop="banana",
            region="Kerala"
        )

        self.assertGreater(len(docs), 0)
        self.assertEqual(docs[0].crop_type, "banana")

    def test_document_fields(self):
        docs = self.rag.retrieve_agri_context(
            query="whitefly",
            crop="cotton",
            region="Punjab"
        )

        doc = docs[0]

        self.assertTrue(hasattr(doc, "title"))
        self.assertTrue(hasattr(doc, "content"))
        self.assertTrue(hasattr(doc, "problem_category"))
        self.assertTrue(hasattr(doc, "compliance_safety_level"))
        self.assertTrue(hasattr(doc, "match_level"))
        self.assertTrue(hasattr(doc, "source_name"))
        self.assertTrue(hasattr(doc, "source_url"))
        self.assertTrue(hasattr(doc, "chemical_treatment"))

    def test_peach_bacterial_spot_punjab_exact_match(self):
        """Verify exact Tier 1 retrieval for Peach Bacterial Spot in Punjab with PAU source."""
        docs = self.rag.retrieve_agri_context(
            query="Peach bacterial spot Xanthomonas treatment",
            crop="peach",
            region="Punjab",
            disease="Peach___Bacterial_spot",
            language="en"
        )

        self.assertGreater(len(docs), 0)
        doc = docs[0]
        self.assertEqual(doc.crop_type, "peach")
        self.assertEqual(doc.match_level, "exact")
        self.assertFalse(doc.is_general_advisory)
        self.assertIn("PAU", doc.source_name)
        self.assertIn("pau.edu", doc.source_url)
        self.assertIn("Copper Oxychloride", doc.chemical_treatment)
        self.assertIn("Streptocycline", doc.chemical_treatment)
        self.assertIn("shot-hole", doc.content.lower())
        self.assertIn("canker", doc.content.lower())
        self.assertIn("drip", doc.moisture_irrigation_guidance.lower())

        # Verify exact PAU/CIBRC approved dosage verification (no fabricated dosage)
        self.assertIn("3.0 g/L", doc.chemical_treatment)
        self.assertIn("100 ppm", doc.chemical_treatment)
        self.assertIn("21", doc.phi_safety_limitations)

    def test_general_disease_level_tier2(self):
        """Verify Tier 2 general recommendation when crop is unlisted but disease category matches."""
        docs = self.rag.retrieve_agri_context(
            query="Bacterial spot management",
            crop="strawberry",
            region="Punjab",
            disease="bacterial_spot",
            language="en"
        )

        self.assertGreater(len(docs), 0)
        doc = docs[0]
        self.assertEqual(doc.match_level, "disease_level")
        self.assertTrue(doc.is_general_advisory)
        self.assertIn("General disease-level advisory", doc.content)
        self.assertIn("verify local label restrictions", doc.content.lower())
        self.assertIn("not specified in the verified source", doc.chemical_treatment.lower())

    def test_hindi_localization_preserves_advisory(self):
        """Verify Hindi language retrieval returns meaningful Hindi text."""
        docs = self.rag.retrieve_agri_context(
            query="",
            crop="peach",
            region="Punjab",
            disease="Peach___Bacterial_spot",
            language="hi"
        )

        self.assertGreater(len(docs), 0)
        doc = docs[0]
        self.assertEqual(doc.crop_type, "peach")
        self.assertEqual(doc.match_level, "exact")
        self.assertIn("आड़ू", doc.content)
        self.assertIn("जीवाणु", doc.content)
        self.assertIn("कॉपर ऑक्सीक्लोराइड", doc.content)

    def test_tomato_septoria_leaf_spot_exact_match(self):
        """Verify exact Tier 1 retrieval for Tomato Septoria Leaf Spot."""
        docs = self.rag.retrieve_agri_context(
            query="Tomato septoria leaf spot",
            crop="tomato",
            region="Punjab",
            disease="Tomato___Septoria_leaf_spot",
            language="en"
        )

        self.assertGreater(len(docs), 0)
        doc = docs[0]
        self.assertEqual(doc.crop_type, "tomato")
        self.assertEqual(doc.match_level, "exact")
        self.assertIn("IIVR", doc.source_name)
        self.assertIn("Mancozeb", doc.chemical_treatment)


if __name__ == "__main__":
    unittest.main()