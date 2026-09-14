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


if __name__ == "__main__":
    unittest.main()