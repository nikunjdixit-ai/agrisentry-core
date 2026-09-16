from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image
from ultralytics import YOLO

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

    global _model

    if _model is not None:
        return _model

    model_path: Optional[Path] = None

    for candidate in MODEL_CANDIDATES:

        if candidate.exists():
            model_path = candidate
            break

    if model_path is None:

        searched_paths = "\n".join(
            str(path)
            for path in MODEL_CANDIDATES
        )

        raise FileNotFoundError(
            "YOLO model file not found. "
            f"Searched paths:\n{searched_paths}"
        )

    print(
        f"Loading YOLO model from: {model_path}"
    )

    _model = YOLO(str(model_path))

    return _model


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
    image: Image.Image,
) -> Dict[str, Any]:

    model = get_model()

    raw_results = model.predict(
        source=image,
        imgsz=256,
        conf=0.25,
        verbose=False,
    )

    # Convert result iterator/list into a normal list.
    results: List[Any] = list(
        cast(Any, raw_results)
    )

    if not results:

        return {
            "disease": "Unknown",
            "confidence": 0.0,
            "detections": [],
            "severity": {
                "level": "unknown",
                "affected_area_percent": 0.0,
                "method": "No prediction result",
            },
        }

    result: Any = results[0]

    names: Any = getattr(
        result,
        "names",
        {},
    )

    detections: List[Dict[str, Any]] = []

    boxes: Any = getattr(
        result,
        "boxes",
        None,
    )

    if boxes is not None:

        class_values: Any = getattr(
            boxes,
            "cls",
            None,
        )

        confidence_values: Any = getattr(
            boxes,
            "conf",
            None,
        )

        coordinate_values: Any = getattr(
            boxes,
            "xyxy",
            None,
        )

        if (
            class_values is not None
            and confidence_values is not None
            and coordinate_values is not None
        ):

            number_of_boxes = len(
                class_values
            )

            for index in range(number_of_boxes):

                class_id = int(
                    class_values[index].item()
                )

                confidence = float(
                    confidence_values[index].item()
                )

                coordinates = (
                    coordinate_values[index]
                    .cpu()
                    .tolist()
                )

                if len(coordinates) != 4:
                    continue

                x1, y1, x2, y2 = coordinates

                if isinstance(names, dict):

                    class_name = names.get(
                        class_id,
                        f"class_{class_id}",
                    )

                else:

                    class_name = names[class_id]

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": str(
                            class_name
                        ),
                        "confidence": round(
                            confidence,
                            4,
                        ),
                        "bbox": [
                            round(float(x1), 2),
                            round(float(y1), 2),
                            round(float(x2), 2),
                            round(float(y2), 2),
                        ],
                    }
                )

    detections.sort(
        key=lambda item: item["confidence"],
        reverse=True,
    )

    if detections:

        top_detection = detections[0]

        disease = top_detection["class_name"]
        confidence = top_detection["confidence"]

    else:

        disease = "Unknown or no disease detected"
        confidence = 0.0

    severity = estimate_severity(
        detections=detections,
        image_width=image.width,
        image_height=image.height,
    )

    return {
        "disease": disease,
        "confidence": confidence,
        "detections": detections,
        "severity": severity,
        "image_size": {
            "width": image.width,
            "height": image.height,
        },
    }


# ----------------------------------
# Diagnosis Endpoint
# ----------------------------------

@router.post("")
async def diagnose_crop(
    image: UploadFile = File(...),
    crop: str = Form("unknown"),
    region: str = Form("unknown"),
    query: str = Form(""),
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

        pil_image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

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
            pil_image
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

    # ----------------------------------
    # Prepare Workflow State
    # ----------------------------------

    normalized_crop = crop.strip().lower()
    normalized_region = region.strip().lower()

    workflow_query = query.strip()

    if not workflow_query:

        workflow_query = (
            f"{normalized_crop} disease treatment "
            f"and management in {normalized_region}"
        )

    initial_state: Dict[str, Any] = {
        "user_query": workflow_query,

        "crop_details": {
            "crop": normalized_crop,
            "region": normalized_region,
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