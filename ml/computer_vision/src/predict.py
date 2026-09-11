import argparse
from pathlib import Path

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


def predict_image(
    image_path: str | Path,
    model_path: str | Path = BEST_MODEL_PATH,
    output_dir: str | Path = "runs/predictions",
    image_size: int = IMAGE_SIZE,
    confidence: float = CONFIDENCE_THRESHOLD,
    iou: float = IOU_THRESHOLD,
    device: int | str = DEVICE,
) -> None:
    """
    Run plant disease prediction on a single image.
    """

    image_path = Path(image_path).resolve()
    model_path = Path(model_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(model_path))

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

    print("\n===== AgriSentry Prediction =====")
    print(f"Image: {image_path}")
    print(f"Model: {model_path}")

    if result.boxes is None or len(result.boxes) == 0:
        print("\nFinal result: No disease prediction detected.")
        return

    class_names = result.names
    predictions = []

    for box in result.boxes:
        class_id = int(box.cls[0].item())
        confidence_score = float(box.conf[0].item())
        class_name = class_names[class_id]

        predictions.append(
            {
                "class_name": class_name,
                "confidence": confidence_score,
            }
        )

    predictions.sort(
        key=lambda item: item["confidence"],
        reverse=True,
    )

    print("\nAll detections:")

    for index, prediction in enumerate(predictions, start=1):
        print(
            f"{index}. "
            f"Class: {prediction['class_name']} | "
            f"Confidence: {prediction['confidence']:.4f}"
        )

    best_prediction = predictions[0]

    print("\n===== Final Prediction =====")
    print(f"Disease: {best_prediction['class_name']}")
    print(f"Confidence: {best_prediction['confidence']:.2%}")
    print(f"\nAnnotated output saved to: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run AgriSentry plant disease prediction."
    )

    parser.add_argument(
        "--image",
        required=True,
        help="Path to the input leaf image.",
    )

    parser.add_argument(
        "--model",
        default=str(BEST_MODEL_PATH),
        help="Path to the trained YOLO model.",
    )

    parser.add_argument(
        "--output",
        default="runs/predictions",
        help="Directory for prediction outputs.",
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
        help="Confidence threshold.",
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
        help="Inference device, such as 0 or cpu.",
    )

    args = parser.parse_args()

    validate_paths()

    device = int(args.device) if args.device.isdigit() else args.device

    predict_image(
        image_path=args.image,
        model_path=args.model,
        output_dir=args.output,
        image_size=args.imgsz,
        confidence=args.conf,
        iou=args.iou,
        device=device,
    )


if __name__ == "__main__":
    main()
