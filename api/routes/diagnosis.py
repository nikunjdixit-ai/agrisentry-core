from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image

from api.agents.graph import app as agri_workflow


# ----------------------------------
# Router
# ----------------------------------

router = APIRouter(
    prefix="/diagnosis",
    tags=["Diagnosis"],
)


# ----------------------------------
# Project Configuration
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_CANDIDATES = [
    PROJECT_ROOT
    / "ml"
    / "computer_vision"
    / "models"
    / "agrisentry_disease_model.pt",

    PROJECT_ROOT
    / "runs"
    / "plantvillage_yolov8n"
    / "weights"
    / "best.pt",

    PROJECT_ROOT
    / "runs"
    / "plantvillage_yolov8n"
    / "best.pt",

    PROJECT_ROOT / "best.pt",
]

_model: Optional[Any] = None


# ----------------------------------
# Load YOLO Model
# ----------------------------------

def get_model() -> Any:
    """Return the shared singleton YOLO model via DiseaseDetector to prevent duplicate models in memory."""
    from ml.computer_vision.src.disease_detector import get_disease_detector
    return get_disease_detector().model


# ----------------------------------
# Severity Estimation
# ----------------------------------

def estimate_severity(
    detections: List[Dict[str, Any]],
    image_width: int,
    image_height: int,
) -> Dict[str, Any]:

    if not detections:

        return {
            "level": "unknown",
            "affected_area_percent": 0.0,
            "method": "No disease region detected",
        }

    image_area = image_width * image_height

    if image_area <= 0:

        return {
            "level": "unknown",
            "affected_area_percent": 0.0,
            "method": "Invalid image dimensions",
        }

    total_box_area = 0.0

    for detection in detections:

        bbox = detection.get("bbox", [])

        if len(bbox) != 4:
            continue

        x1, y1, x2, y2 = bbox

        box_width = max(
            0.0,
            float(x2) - float(x1),
        )

        box_height = max(
            0.0,
            float(y2) - float(y1),
        )

        total_box_area += (
            box_width * box_height
        )

    affected_area_percent = (
        total_box_area / image_area
    ) * 100

    if affected_area_percent < 10:

        severity_level = "mild"

    elif affected_area_percent < 30:

        severity_level = "moderate"

    else:

        severity_level = "severe"

    return {
        "level": severity_level,
        "affected_area_percent": round(
            min(affected_area_percent, 100.0),
            2,
        ),
        "method": (
            "Approximate bounding-box area heuristic"
        ),
    }


# ----------------------------------
# YOLO Inference
# ----------------------------------

def run_yolo_inference(
    image_input: Any,
) -> Dict[str, Any]:
    """
    Run plant disease inference using process-isolated DiseaseDetector on CPU.
    When inference finishes, the OS kernel immediately reclaims all model memory.
    """
    from ml.computer_vision.src.disease_detector import predict_disease_isolated
    return predict_disease_isolated(image_input)


# ----------------------------------
# Diagnosis Endpoint
# ----------------------------------

@router.post("")
async def diagnose_crop(
    image: UploadFile = File(...),
    crop: str = Form("unknown"),
    region: str = Form("unknown"),
    query: str = Form(""),
    language: str = Form("en"),
) -> Dict[str, Any]:

    # ----------------------------------
    # Validate Uploaded File
    # ----------------------------------

    content_type = image.content_type or ""

    if not content_type.startswith("image/"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image file.",
        )

    try:

        image_bytes = await image.read()

        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty.",
            )

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to read image: {error}",
        ) from error

    # ----------------------------------
    # Run YOLO Diagnosis
    # ----------------------------------

    try:
        model_result = run_yolo_inference(
            image_bytes
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"YOLO inference failed: {error}",
        ) from error
    finally:
        import gc
        del image_bytes
        gc.collect()

    # ----------------------------------
    # Prepare Workflow State
    # ----------------------------------

    normalized_crop = crop.strip().lower()
    normalized_region = region.strip().lower()
    normalized_language = language.strip().lower()

    if normalized_language == "hi":
        if model_result.get("status") == "no_detection":
            model_result["message"] = "कोई स्पष्ट रोग लक्षण नहीं मिला। कृपया पत्ती की स्पष्ट फोटो अपलोड करें।"
        elif "healthy" in str(model_result.get("disease", "")).lower():
            model_result["message"] = "पत्ती स्वस्थ पाई गई।"
        else:
            model_result["message"] = "रोग की पहचान सफलतापूर्वक की गई।"

    detected_crop = model_result.get("crop")
    if (normalized_crop in ("", "unknown") or not normalized_crop) and detected_crop and detected_crop != "unknown":
        normalized_crop = detected_crop

    workflow_query = query.strip()

    if not workflow_query:
        disease_name = model_result.get("disease_display_name") or model_result.get("disease") or "disease"
        if normalized_language == "hi":
            workflow_query = (
                f"{normalized_crop} {disease_name} उपचार और प्रबंधन ({normalized_region})"
            )
        else:
            workflow_query = (
                f"{normalized_crop} {disease_name} treatment "
                f"and management in {normalized_region}"
            )

    initial_state: Dict[str, Any] = {
        "user_query": workflow_query,

        "crop_details": {
            "crop": normalized_crop,
            "region": normalized_region,
            "language": normalized_language,
            "disease": model_result.get("disease"),
            "disease_display_name": model_result.get("disease_display_name"),
        },

        "diagnostic_result": model_result,

        "rag_context": [],

        "vendor_options": [],

        "mandi_prices": {},

        "current_step": "model_diagnosis_complete",

        "verification_flag": False,

        "retry_count": 0,

        "verification_notes": "",

        "evidence_score": 0.0,
    }

    # ----------------------------------
    # Run Agent Workflow
    # ----------------------------------

    try:

        workflow_result: Dict[str, Any] = cast(
            Dict[str, Any],
            agri_workflow.invoke(
                cast(Any, initial_state)
            ),
        )

    except Exception as error:

        return {
            "status": "partial_success",
            "message": (
                "YOLO diagnosis completed, but "
                "agricultural workflow failed."
            ),
            "diagnosis": model_result,
            "workflow_error": str(error),
        }

    # ----------------------------------
    # Final Response
    # ----------------------------------

    return {
        "status": "success",
        "language": normalized_language,

        "diagnosis": model_result,

        "workflow": {
            "diagnostic_result": workflow_result.get(
                "diagnostic_result"
            ),

            "rag_context": workflow_result.get(
                "rag_context",
                [],
            ),

            "vendor_options": workflow_result.get(
                "vendor_options",
                [],
            ),

            "mandi_prices": workflow_result.get(
                "mandi_prices",
                {},
            ),

            "current_step": workflow_result.get(
                "current_step"
            ),

            "verification_flag": workflow_result.get(
                "verification_flag",
                False,
            ),

            "verification_notes": workflow_result.get(
                "verification_notes",
                "",
            ),

            "evidence_score": workflow_result.get(
                "evidence_score",
                0.0,
            ),
        },
    }