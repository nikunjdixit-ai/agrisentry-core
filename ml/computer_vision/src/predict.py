import argparse
import json
from pathlib import Path
from typing import Any

from ultralytics import YOLO

try:
    from config import (
        BEST_MODEL_PATH,
        CONFIDENCE_THRESHOLD,
        DEVICE,
        IMAGE_SIZE,
        IOU_THRESHOLD,
        validate_paths,
    )
except ImportError:
    from .config import (
        BEST_MODEL_PATH,
        CONFIDENCE_THRESHOLD,
        DEVICE,
        IMAGE_SIZE,
        IOU_THRESHOLD,
        validate_paths,
    )


# ==========================================
# Prediction Configuration
# ==========================================

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}

HIGH_CONFIDENCE_THRESHOLD = 0.70
MEDIUM_CONFIDENCE_THRESHOLD = 0.40


# ==========================================
# Group Detections by Disease
# ==========================================

def group_detections_by_disease(
    predictions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Group detections by disease name.

    For every disease, store:
    - Class ID
    - Disease name
    - Highest confidence
    - Number of detections
    """

    grouped: dict[str, dict[str, Any]] = {}

    for prediction in predictions:
        class_name = prediction["class_name"]

        if class_name not in grouped:
            grouped[class_name] = {
                "class_id": prediction["class_id"],
                "class_name": class_name,
                "highest_confidence": prediction["confidence"],
                "highest_confidence_percent": (
                    prediction["confidence_percent"]
                ),
                "detections_count": 1,
            }

        else:
            grouped[class_name]["detections_count"] += 1

            if (
                prediction["confidence"]
                > grouped[class_name]["highest_confidence"]
            ):
                grouped[class_name][
                    "highest_confidence"
                ] = prediction["confidence"]

                grouped[class_name][
                    "highest_confidence_percent"
                ] = prediction["confidence_percent"]

    grouped_predictions = list(grouped.values())

    grouped_predictions.sort(
        key=lambda item: item["highest_confidence"],
        reverse=True,
    )

    return grouped_predictions


# ==========================================
# Single Image Prediction
# ==========================================

def predict_single_image(
    model: YOLO,
    image_path: str | Path,
    output_dir: str | Path,
    image_size: int = IMAGE_SIZE,
    confidence: float = CONFIDENCE_THRESHOLD,
    iou: float = IOU_THRESHOLD,
    device: int | str = DEVICE,
) -> dict[str, Any]:
    """
    Run prediction on one image and return
    a structured result.
    """

    image_path = Path(image_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    import gc
    import torch

    torch.set_num_threads(1)
    if hasattr(torch, "set_num_interop_threads"):
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass

    with torch.inference_mode():
        results = model.predict(
            source=str(image_path),
            imgsz=image_size,
            conf=confidence,
            iou=iou,
            device=device,
            save=True,
            project=str(output_dir.parent),
            name=output_dir.name,
            exist_ok=True,
            verbose=False,
        )

    result = results[0]
    predictions = []

    # --------------------------------------
    # Extract Raw Detections
    # --------------------------------------

    if result.boxes is not None and len(result.boxes) > 0:
        class_names = result.names

        for box in result.boxes:
            class_id = int(
                box.cls[0].item()
            )

            confidence_score = float(
                box.conf[0].item()
            )

            class_name = class_names[class_id]

            predictions.append(
                {
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": round(
                        confidence_score,
                        6,
                    ),
                    "confidence_percent": round(
                        confidence_score * 100,
                        2,
                    ),
                }
            )

    # Highest confidence first
    predictions.sort(
        key=lambda item: item["confidence"],
        reverse=True,
    )

    # --------------------------------------
    # Group Duplicate Diseases
    # --------------------------------------

    unique_diseases = group_detections_by_disease(
        predictions
    )

    # --------------------------------------
    # Determine Final Prediction
    # --------------------------------------

    if predictions:
        best_prediction = predictions[0]

        final_disease = best_prediction["class_name"]
        final_confidence = best_prediction["confidence"]

        if final_confidence >= HIGH_CONFIDENCE_THRESHOLD:
            status = "high_confidence"

            message = (
                "Prediction confidence is high."
            )

        elif final_confidence >= MEDIUM_CONFIDENCE_THRESHOLD:
            status = "medium_confidence"

            message = (
                "Prediction confidence is moderate. "
                "Consider uploading a clearer image "
                "for confirmation."
            )

        else:
            status = "low_confidence"

            message = (
                "Prediction confidence is low. "
                "Please upload a clearer image."
            )

    else:
        status = "no_prediction"
        final_disease = None
        final_confidence = None

        message = (
            "No disease detected. "
            "Please upload a clear image of "
            "the affected leaf."
        )

    # --------------------------------------
    # Structured Prediction Response
    # --------------------------------------

    gc.collect()

    return {
        "image": str(image_path),
        "status": status,
        "message": message,
        "disease": final_disease,
        "confidence": final_confidence,
        "confidence_percent": (
            round(
                final_confidence * 100,
                2,
            )
            if final_confidence is not None
            else None
        ),
        "all_detections": predictions,
        "unique_diseases": unique_diseases,
        "output_directory": str(output_dir),
    }


# ==========================================
# Public Single Image Function
# ==========================================

def predict_image(
    image_path: str | Path,
    model_path: str | Path = BEST_MODEL_PATH,
    output_dir: str | Path = "runs/predictions",
    image_size: int = IMAGE_SIZE,
    confidence: float = CONFIDENCE_THRESHOLD,
    iou: float = IOU_THRESHOLD,
    device: int | str = DEVICE,
) -> dict[str, Any]:
    """
    Load the trained model and predict
    one image.
    """

    image_path = Path(image_path).resolve()
    model_path = Path(model_path).resolve()

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    model = YOLO(str(model_path))

    prediction = predict_single_image(
        model=model,
        image_path=image_path,
        output_dir=output_dir,
        image_size=image_size,
        confidence=confidence,
        iou=iou,
        device=device,
    )

    print_prediction_result(prediction)

    return prediction


# ==========================================
# Batch / Folder Prediction
# ==========================================

def predict_folder(
    input_dir: str | Path,
    model_path: str | Path = BEST_MODEL_PATH,
    output_dir: str | Path = "runs/batch_predictions",
    image_size: int = IMAGE_SIZE,
    confidence: float = CONFIDENCE_THRESHOLD,
    iou: float = IOU_THRESHOLD,
    device: int | str = DEVICE,
) -> list[dict[str, Any]]:
    """
    Run prediction on all supported images
    inside a folder.
    """

    input_dir = Path(input_dir).resolve()
    model_path = Path(model_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory not found: {input_dir}"
        )

    if not input_dir.is_dir():
        raise NotADirectoryError(
            f"Not a directory: {input_dir}"
        )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    image_paths = sorted(
        path
        for path in input_dir.iterdir()
        if (
            path.is_file()
            and path.suffix.lower()
            in SUPPORTED_IMAGE_EXTENSIONS
        )
    )

    if not image_paths:
        raise FileNotFoundError(
            f"No supported images found in: {input_dir}"
        )

    model = YOLO(str(model_path))

    predictions = []

    for image_path in image_paths:
        prediction = predict_single_image(
            model=model,
            image_path=image_path,
            output_dir=output_dir,
            image_size=image_size,
            confidence=confidence,
            iou=iou,
            device=device,
        )

        predictions.append(prediction)

    # --------------------------------------
    # Save Batch Results as JSON
    # --------------------------------------

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_file = (
        output_dir / "predictions.json"
    )

    results_file.write_text(
        json.dumps(
            predictions,
            indent=4,
        ),
        encoding="utf-8",
    )

    print("\n===== Batch Prediction Summary =====")
    print(
        f"Input directory: "
        f"{input_dir}"
    )
    print(
        f"Images processed: "
        f"{len(predictions)}"
    )
    print(
        f"JSON results saved to: "
        f"{results_file}"
    )

    return predictions


# ==========================================
# Readable Console Output
# ==========================================

def print_prediction_result(
    prediction: dict[str, Any],
) -> None:
    """
    Print a readable prediction result.
    """

    print("\n===== AgriSentry Prediction =====")

    print(
        f"Image: "
        f"{prediction['image']}"
    )

    print(
        f"Status: "
        f"{prediction['status']}"
    )

    print(
        f"Message: "
        f"{prediction['message']}"
    )

    if prediction["disease"] is None:
        print(
            "Final result: "
            "No disease prediction detected."
        )

    else:
        print(
            f"Disease: "
            f"{prediction['disease']}"
        )

        print(
            f"Confidence: "
            f"{prediction['confidence_percent']:.2f}%"
        )

    print("\nAll detections:")

    if not prediction["all_detections"]:
        print("No detections found.")

    else:
        for index, item in enumerate(
            prediction["all_detections"],
            start=1,
        ):
            print(
                f"{index}. "
                f"{item['class_name']} | "
                f"{item['confidence_percent']:.2f}%"
            )

    print("\nUnique diseases:")

    if not prediction["unique_diseases"]:
        print("No unique diseases found.")

    else:
        for index, item in enumerate(
            prediction["unique_diseases"],
            start=1,
        ):
            print(
                f"{index}. "
                f"{item['class_name']} | "
                f"Highest confidence: "
                f"{item['highest_confidence_percent']:.2f}% | "
                f"Detections: "
                f"{item['detections_count']}"
            )

    print(
        "\nAnnotated output directory: "
        f"{prediction['output_directory']}"
    )


# ==========================================
# Command Line Interface
# ==========================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run AgriSentry plant disease "
            "prediction."
        )
    )

    input_group = (
        parser.add_mutually_exclusive_group(
            required=True
        )
    )

    input_group.add_argument(
        "--image",
        help=(
            "Path to a single input "
            "leaf image."
        ),
    )

    input_group.add_argument(
        "--folder",
        help=(
            "Path to a folder containing "
            "input images."
        ),
    )

    parser.add_argument(
        "--model",
        default=str(BEST_MODEL_PATH),
        help=(
            "Path to the trained YOLO model."
        ),
    )

    parser.add_argument(
        "--output",
        default="runs/predictions",
        help=(
            "Directory for prediction "
            "outputs."
        ),
    )

    parser.add_argument(
        "--imgsz",
        type=int,
        default=IMAGE_SIZE,
        help="Inference image size.",
    )

    parser.add_argument(
        "--conf",
        type=float,
        default=CONFIDENCE_THRESHOLD,
        help=(
            "Confidence threshold."
        ),
    )

    parser.add_argument(
        "--iou",
        type=float,
        default=IOU_THRESHOLD,
        help="IoU threshold.",
    )

    parser.add_argument(
        "--device",
        default=str(DEVICE),
        help=(
            "Inference device, such as "
            "0 or cpu."
        ),
    )

    args = parser.parse_args()

    validate_paths()

    device = (
        int(args.device)
        if args.device.isdigit()
        else args.device
    )

    if args.image:
        predict_image(
            image_path=args.image,
            model_path=args.model,
            output_dir=args.output,
            image_size=args.imgsz,
            confidence=args.conf,
            iou=args.iou,
            device=device,
        )

    elif args.folder:
        predict_folder(
            input_dir=args.folder,
            model_path=args.model,
            output_dir=args.output,
            image_size=args.imgsz,
            confidence=args.conf,
            iou=args.iou,
            device=device,
        )


if __name__ == "__main__":
    main()