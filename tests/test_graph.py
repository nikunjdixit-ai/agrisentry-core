import unittest

from api.agents.graph import app


class TestGraph(unittest.TestCase):

    def test_complete_workflow(self):
        state = {
            "user_query": "Whitefly attack on cotton leaves",
            "crop_details": {
                "crop": "cotton",
                "region": "Punjab"
            },
            "diagnostic_result": {},
            "rag_context": [],
            "vendor_options": [],
            "mandi_prices": {},
            "current_step": "",
            "verification_flag": False,
            "retry_count": 0,
            "verification_notes": "",
            "evidence_score": 0.0
        }

        result = app.invoke(state)

        self.assertTrue(result["verification_flag"])
        self.assertGreater(result["evidence_score"], 0.8)
        self.assertEqual(result["current_step"], "market_complete")
        self.assertGreater(len(result["rag_context"]), 0)
        self.assertGreater(len(result["vendor_options"]), 0)
        self.assertIn("modal_price_per_quintal", result["mandi_prices"])


if __name__ == "__main__":
    unittest.main()