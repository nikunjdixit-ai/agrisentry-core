"""
AgriSentry - Comprehensive Computer Vision & Integration Test Suite
Verifies all 17 requirements for Member 1 deliverables.
Runs strictly on CPU without GPU initialization.
"""

import json
import os
import unittest
from pathlib import Path
from PIL import Image

# Enforce CPU-only environment
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from fastapi.testclient import TestClient
from ultralytics import YOLO

from api.main import app
from ml.computer_vision.src.disease_detector import (
    DiseaseDetector,
    get_disease_detector,
    predict_disease,
    calculate_severity,
    parse_crop_and_display_name,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_MODEL = PROJECT_ROOT / "ml" / "computer_vision" / "models" / "agrisentry_disease_model.pt"
METADATA_FILE = PROJECT_ROOT / "ml" / "computer_vision" / "models" / "model_metadata.json"
SAMPLE_LEAF = PROJECT_ROOT / "ml" / "computer_vision" / "sample_batch" / "test_leaf.jpg"


class TestAgriSentryDiseaseDetector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.detector = get_disease_detector()
        cls.client = TestClient(app)

    # 1. Model loading
    def test_01_model_loading(self):
        self.assertIsNotNone(self.detector.model)
        self.assertIsInstance(self.detector, DiseaseDetector)

    # 2. CPU-only model loading
    def test_02_cpu_only_model_loading(self):
        device = getattr(self.detector.model, "device", None)
        # Ultralytics model device should be cpu
        self.assertEqual(str(device).lower(), "cpu")

    # 3. Class metadata
    def test_03_class_metadata(self):
        self.assertIsInstance(self.detector.class_names, dict)
        self.assertIn(0, self.detector.class_names)
        self.assertEqual(self.detector.class_names[0], "Apple___Apple_scab")

    # 4. Number of classes
    def test_04_number_of_classes(self):
        self.assertEqual(self.detector.num_classes, 38)
        self.assertEqual(len(self.detector.class_names), 38)

    # 5. Valid image inference
    def test_05_valid_image_inference(self):
        self.assertTrue(SAMPLE_LEAF.exists(), f"Sample image missing at: {SAMPLE_LEAF}")
        result = self.detector.detect(SAMPLE_LEAF)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["crop"], "tomato")
        self.assertEqual(result["disease"], "Tomato___Septoria_leaf_spot")
        self.assertGreater(result["confidence"], 0.70)
        self.assertGreater(len(result["detections"]), 0)

    # 6. Invalid image handling
    def test_06_invalid_image_handling(self):
        result = self.detector.detect("non_existent_image_path.jpg")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"].lower())
        self.assertIsNone(result["disease"])

    # 7. Corrupted image handling
    def test_07_corrupted_image_handling(self):
        corrupted_bytes = b"This is not a valid JPEG or PNG file binary."
        result = self.detector.detect(corrupted_bytes)
        self.assertEqual(result["status"], "error")
        self.assertIn("corrupted", result["message"].lower())

    # 8. No-detection handling
    def test_08_no_detection_handling(self):
        # A completely blank white image should result in no detection
        blank_img = Image.new("RGB", (256, 256), color=(255, 255, 255))
        result = self.detector.detect(blank_img, conf_threshold=0.85)
        self.assertIn(result["status"], ["no_detection", "error"])
        if result["status"] == "no_detection":
            self.assertIsNone(result["disease"])
            self.assertEqual(result["confidence"], 0.0)
            self.assertEqual(len(result["detections"]), 0)

    # 9. Confidence threshold
    def test_09_confidence_threshold(self):
        # With threshold 0.999, sample leaf should yield no detection
        result = self.detector.detect(SAMPLE_LEAF, conf_threshold=0.999)
        self.assertEqual(result["status"], "no_detection")
        self.assertEqual(len(result["detections"]), 0)

    # 10. Bounding-box serialization
    def test_10_bounding_box_serialization(self):
        result = self.detector.detect(SAMPLE_LEAF)
        self.assertTrue(len(result["detections"]) > 0)
        bbox = result["detections"][0]["bbox"]
        for coord in ["x1", "y1", "x2", "y2"]:
            self.assertIn(coord, bbox)
            self.assertIsInstance(bbox[coord], (int, float))

    # 11. JSON serializability
    def test_11_json_serializability(self):
        result = self.detector.detect(SAMPLE_LEAF)
        serialized = json.dumps(result)
        self.assertIsInstance(serialized, str)
        deserialized = json.loads(serialized)
        self.assertEqual(deserialized["status"], "success")

    # 12. Severity output
    def test_12_severity_output(self):
        result = self.detector.detect(SAMPLE_LEAF)
        self.assertIn(result["severity"], ["low", "moderate", "high", "unknown"])
        self.assertIn("affected_area_percent", result["severity_details"])
        self.assertIsInstance(result["severity_details"]["affected_area_percent"], (int, float))

        # Test severity heuristic direct
        level, details = calculate_severity([], 100, 100)
        self.assertEqual(level, "unknown")
        level_h, details_h = calculate_severity([], 100, 100, is_healthy=True)
        self.assertEqual(level_h, "low")

    # 13. API image endpoint
    def test_13_api_image_endpoint(self):
        with open(SAMPLE_LEAF, "rb") as f:
            response = self.client.post(
                "/diagnosis",
                files={"image": ("test_leaf.jpg", f, "image/jpeg")},
                data={"crop": "tomato", "region": "Uttar Pradesh"}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["diagnosis"]["crop"], "tomato")
        self.assertEqual(data["diagnosis"]["disease"], "Tomato___Septoria_leaf_spot")
        self.assertIn("workflow", data)

    # 14. Existing JSON /diagnose endpoint compatibility
    def test_14_existing_json_diagnose_compatibility(self):
        response = self.client.post(
            "/diagnose",
            json={
                "crop": "cotton",
                "region": "Punjab",
                "query": "whitefly infestation advisory"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_step"], "market_complete")
        self.assertTrue(data["verification_flag"])

    # 15. LangGraph compatibility
    def test_15_langgraph_compatibility(self):
        from api.agents.graph import app as graph_app
        state = {
            "user_query": "Tomato leaf curl",
            "crop_details": {"crop": "tomato", "region": "Punjab"},
            "diagnostic_result": {"status": "success", "disease": "Tomato___Tomato_Yellow_Leaf_Curl_Virus"},
            "rag_context": [],
            "vendor_options": [],
            "mandi_prices": {},
            "current_step": "init",
            "verification_flag": False,
            "retry_count": 0,
            "verification_notes": "",
            "evidence_score": 0.0,
        }
        res = graph_app.invoke(state)
        self.assertEqual(res["current_step"], "market_complete")
        self.assertIn("weather", res["diagnostic_result"])

    # 16. Canonical model path
    def test_16_canonical_model_path(self):
        self.assertTrue(CANONICAL_MODEL.exists(), f"Canonical model missing at: {CANONICAL_MODEL}")
        self.assertGreater(CANONICAL_MODEL.stat().st_size, 10 * 1024 * 1024)

    # 17. Model metadata file
    def test_17_model_metadata_file(self):
        self.assertTrue(METADATA_FILE.exists(), f"Metadata file missing at: {METADATA_FILE}")
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["model_name"], "agrisentry_disease_model")
        self.assertEqual(meta["number_of_classes"], 38)
        self.assertIn("known_limitations", meta)
        self.assertIn("domain_gap_analysis", meta)


if __name__ == "__main__":
    unittest.main()
