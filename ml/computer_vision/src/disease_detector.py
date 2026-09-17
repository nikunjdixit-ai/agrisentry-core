"""
AgriSentry - Canonical Plant Disease Detection Module
Provides production-ready, CPU-only leaf disease inference.

Key features:
1. Singleton model loading (loaded once into memory).
2. Strictly CPU-only inference (device='cpu').
3. Robust input handling (Path, string, PIL Image, bytes, UploadFile).
4. Safe error handling (corrupt images, non-images, empty inputs).
5. Explainable severity heuristic based on normalized lesion coverage.
6. Strictly JSON-serializable output schema for FastAPI, agents, and frontend.
7. Zero treatment advice in CV layer (reserved for RAG/agents).
"""

import io
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO

# Project paths
CV_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = CV_DIR / "models" / "agrisentry_disease_model.pt"
BACKUP_MODEL_PATH = CV_DIR.parents[1] / "runs" / "plantvillage_yolov8n" / "weights" / "best.pt"

# Versioning
MODEL_NAME = "agrisentry_disease_model"
MODEL_VERSION = "1.0.0"

# Inference defaults
DEFAULT_IMG_SIZE = 256
DEFAULT_CONF_THRESHOLD = 0.25
DEFAULT_IOU_THRESHOLD = 0.45


def parse_crop_and_display_name(raw_class_name: str) -> Tuple[str, str]:
    """
    Safely extract the crop name and a human-friendly disease display name
    from standard PlantVillage class strings (e.g. 'Pepper,_bell___Bacterial_spot').
    """
    if "___" in raw_class_name:
        crop_part, disease_part = raw_class_name.split("___", 1)
    else:
        crop_part, disease_part = "unknown", raw_class_name

    # Normalize crop name
    clean_crop = (
        crop_part.replace("Pepper,_bell", "bell pepper")
        .replace("_", " ")
        .strip()
        .lower()
    )

    # Normalize disease display name
    clean_disease = (
        disease_part.replace("_(Citrus_greening)", " (Citrus Greening)")
        .replace("_(Black_Measles)", " (Black Measles)")
        .replace("_(Isariopsis_Leaf_Spot)", " (Isariopsis Leaf Spot)")
        .replace("Two-spotted_spider_mite", "(Two-Spotted Spider Mite)")
        .replace("_", " ")
        .strip()
    )

    if clean_disease.lower() == "healthy":
        display_name = f"{clean_crop.title()} (Healthy)"
    else:
        display_name = f"{clean_crop.title()} {clean_disease.title()}".strip()

    return clean_crop, display_name


def calculate_severity(
    detections: List[Dict[str, Any]],
    image_width: int,
    image_height: int,
    is_healthy: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    """
    Explainable severity estimation heuristic.
    Calculates the cumulative bounding box area ratio relative to image dimensions.
    Returns:
        severity_level: 'low', 'moderate', 'high', or 'unknown'
        details: Dictionary with coverage percent and calculation rationale.
    """
    if is_healthy:
        return "low", {
            "level": "low",
            "affected_area_percent": 0.0,
            "method": "Leaf classified as healthy by vision model",
        }

    if not detections or image_width <= 0 or image_height <= 0:
        return "unknown", {
            "level": "unknown",
            "affected_area_percent": 0.0,
            "method": "No disease bounding boxes available for severity calculation",
        }

    image_area = float(image_width * image_height)
    total_bbox_area = 0.0

    for det in detections:
        bbox = det.get("bbox", {})
        x1, y1, x2, y2 = bbox.get("x1", 0.0), bbox.get("y1", 0.0), bbox.get("x2", 0.0), bbox.get("y2", 0.0)
        box_w = max(0.0, float(x2) - float(x1))
        box_h = max(0.0, float(y2) - float(y1))
        total_bbox_area += box_w * box_h

    # Cap affected area percent at 100%
    affected_percent = min(100.0, round((total_bbox_area / image_area) * 100.0, 2))

    if affected_percent < 15.0:
        level = "low"
    elif affected_percent <= 40.0:
        level = "moderate"
    else:
        level = "high"

    return level, {
        "level": level,
        "affected_area_percent": affected_percent,
        "method": "Cumulative bounding-box leaf area ratio heuristic",
    }


class DiseaseDetector:
    """
    Singleton Disease Detector for AgriSentry.
    Ensures the YOLO weights are loaded into CPU memory exactly once.
    """
    _instance: Optional["DiseaseDetector"] = None

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        target_path: Optional[Path] = None

        if model_path is not None:
            p = Path(model_path)
            if p.exists():
                target_path = p

        if target_path is None:
            if DEFAULT_MODEL_PATH.exists():
                target_path = DEFAULT_MODEL_PATH
            elif BACKUP_MODEL_PATH.exists():
                target_path = BACKUP_MODEL_PATH
            else:
                raise FileNotFoundError(
                    f"AgriSentry disease model not found. "
                    f"Checked '{DEFAULT_MODEL_PATH}' and '{BACKUP_MODEL_PATH}'."
                )

        print(f"[AgriSentry CV] Loading disease detector model on CPU from: {target_path}")
        self.model_path = target_path
        self.model = YOLO(str(target_path))
        self.class_names = self.model.names
        self.num_classes = len(self.class_names)
        print(f"[AgriSentry CV] Model loaded successfully with {self.num_classes} classes.")

    @classmethod
    def get_instance(cls, model_path: Optional[Union[str, Path]] = None) -> "DiseaseDetector":
        if cls._instance is None:
            cls._instance = cls(model_path=model_path)
        return cls._instance

    @staticmethod
    def _load_image(image_input: Any) -> Tuple[Optional[Image.Image], Optional[str]]:
        """
        Safely convert various input types (path, bytes, file-like, PIL Image) into RGB PIL Image.
        """
        try:
            if isinstance(image_input, (str, Path)):
                path = Path(image_input)
                if not path.exists():
                    return None, f"Image file not found: {path}"
                img = Image.open(path).convert("RGB")
                return img, None

            elif isinstance(image_input, bytes):
                if len(image_input) == 0:
                    return None, "Received empty image byte stream."
                img = Image.open(io.BytesIO(image_input)).convert("RGB")
                return img, None

            elif hasattr(image_input, "read"):
                # File-like object (e.g. UploadFile.file or BytesIO)
                data = image_input.read()
                if hasattr(image_input, "seek"):
                    image_input.seek(0)
                if len(data) == 0:
                    return None, "File-like object contains 0 bytes."
                img = Image.open(io.BytesIO(data)).convert("RGB")
                return img, None

            elif isinstance(image_input, Image.Image):
                return image_input.convert("RGB"), None

            else:
                return None, f"Unsupported image input type: {type(image_input)}"

        except UnidentifiedImageError:
            return None, "Invalid or corrupted image format. Please upload a valid JPG or PNG image."
        except Exception as exc:
            return None, f"Failed to decode image: {str(exc)}"

    def detect(
        self,
        image_input: Any,
        conf_threshold: float = DEFAULT_CONF_THRESHOLD,
        iou_threshold: float = DEFAULT_IOU_THRESHOLD,
        img_size: int = DEFAULT_IMG_SIZE,
    ) -> Dict[str, Any]:
        """
        Perform disease detection on an image using CPU-only inference.
        Returns a structured, 100% JSON-serializable dictionary.
        """
        start_time = time.time()

        # 1. Validate & load image
        pil_image, error_msg = self._load_image(image_input)
        if pil_image is None or error_msg is not None:
            return {
                "status": "error",
                "model": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "crop": "unknown",
                "disease": None,
                "disease_display_name": None,
                "confidence": 0.0,
                "severity": "unknown",
                "severity_details": {
                    "level": "unknown",
                    "affected_area_percent": 0.0,
                    "method": "Validation failure",
                },
                "detections": [],
                "recommendation_context": {
                    "crop": "unknown",
                    "disease": None,
                    "confidence": 0.0,
                },
                "inference_time_ms": 0.0,
                "message": error_msg or "Failed to load image.",
            }

        img_width, img_height = pil_image.width, pil_image.height
        if img_width < 10 or img_height < 10:
            return {
                "status": "error",
                "model": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "crop": "unknown",
                "disease": None,
                "disease_display_name": None,
                "confidence": 0.0,
                "severity": "unknown",
                "severity_details": {
                    "level": "unknown",
                    "affected_area_percent": 0.0,
                    "method": "Image dimensions too small",
                },
                "detections": [],
                "recommendation_context": {
                    "crop": "unknown",
                    "disease": None,
                    "confidence": 0.0,
                },
                "inference_time_ms": 0.0,
                "message": f"Image dimensions too small ({img_width}x{img_height}).",
            }

        # 2. Run YOLO inference on CPU strictly
        try:
            results = self.model.predict(
                source=pil_image,
                imgsz=img_size,
                conf=conf_threshold,
                iou=iou_threshold,
                device="cpu",
                verbose=False,
            )
        except Exception as exc:
            return {
                "status": "error",
                "model": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "crop": "unknown",
                "disease": None,
                "disease_display_name": None,
                "confidence": 0.0,
                "severity": "unknown",
                "severity_details": {"level": "unknown", "affected_area_percent": 0.0, "method": "Inference error"},
                "detections": [],
                "recommendation_context": {"crop": "unknown", "disease": None, "confidence": 0.0},
                "inference_time_ms": round((time.time() - start_time) * 1000, 2),
                "message": f"YOLO CPU inference failed: {str(exc)}",
            }

        inference_time_ms = round((time.time() - start_time) * 1000, 2)

        # 3. Parse detections
        detections: List[Dict[str, Any]] = []
        if results and len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            cls_vals = boxes.cls.cpu().tolist() if boxes.cls is not None else []
            conf_vals = boxes.conf.cpu().tolist() if boxes.conf is not None else []
            xyxy_vals = boxes.xyxy.cpu().tolist() if boxes.xyxy is not None else []

            for i in range(len(cls_vals)):
                cid = int(cls_vals[i])
                conf = round(float(conf_vals[i]), 4)
                raw_cname = self.class_names.get(cid, f"class_{cid}")
                c_crop, c_display = parse_crop_and_display_name(raw_cname)

                coords = xyxy_vals[i]
                bbox_dict = {
                    "x1": round(float(coords[0]), 1),
                    "y1": round(float(coords[1]), 1),
                    "x2": round(float(coords[2]), 1),
                    "y2": round(float(coords[3]), 1),
                }

                detections.append({
                    "class_id": cid,
                    "class_name": str(raw_cname),
                    "display_name": str(c_display),
                    "crop": str(c_crop),
                    "confidence": conf,
                    "bbox": bbox_dict,
                })

        # Sort highest confidence first
        detections.sort(key=lambda d: d["confidence"], reverse=True)

        # 4. Determine final prediction and response status
        if not detections:
            return {
                "status": "no_detection",
                "model": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "crop": "unknown",
                "disease": None,
                "disease_display_name": None,
                "confidence": 0.0,
                "severity": "unknown",
                "severity_details": {
                    "level": "unknown",
                    "affected_area_percent": 0.0,
                    "method": "No disease bounding boxes met the confidence threshold",
                },
                "detections": [],
                "recommendation_context": {
                    "crop": "unknown",
                    "disease": None,
                    "confidence": 0.0,
                },
                "inference_time_ms": inference_time_ms,
                "message": "No reliable disease detection found. Please upload a clearer leaf image.",
            }

        top_detection = detections[0]
        primary_disease = top_detection["class_name"]
        primary_confidence = top_detection["confidence"]
        primary_crop = top_detection["crop"]
        primary_display = top_detection["display_name"]
        is_healthy = "healthy" in primary_disease.lower()

        # Calculate severity
        severity_level, severity_details = calculate_severity(
            detections=detections,
            image_width=img_width,
            image_height=img_height,
            is_healthy=is_healthy,
        )

        return {
            "status": "success",
            "model": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "crop": primary_crop,
            "disease": primary_disease,
            "disease_display_name": primary_display,
            "confidence": primary_confidence,
            "severity": severity_level,
            "severity_details": severity_details,
            "detections": detections,
            "recommendation_context": {
                "crop": primary_crop,
                "disease": primary_disease,
                "confidence": primary_confidence,
            },
            "inference_time_ms": inference_time_ms,
            "message": "Disease detected successfully." if not is_healthy else "Leaf detected healthy.",
        }


# Convenience factory functions for Member 2, Member 3 and Member 4
def get_disease_detector(model_path: Optional[Union[str, Path]] = None) -> DiseaseDetector:
    """Return the singleton DiseaseDetector instance."""
    return DiseaseDetector.get_instance(model_path=model_path)


def predict_disease(
    image_input: Any,
    conf_threshold: float = DEFAULT_CONF_THRESHOLD,
    model_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Direct function to run disease prediction on CPU.
    Callable by Member 3 (Voice) or Member 4 (Frontend scripts).
    """
    detector = get_disease_detector(model_path=model_path)
    return detector.detect(image_input=image_input, conf_threshold=conf_threshold)
