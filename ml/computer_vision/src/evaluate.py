from pathlib import Path
from ultralytics import YOLO

from config import (
    DATASET_YAML,
    BEST_MODEL_PATH,
    IMAGE_SIZE,
    DEVICE,
    PROJECT_ROOT,
)


def evaluate_model():
    print("=" * 60)
    print("AgriSentry - Plant Disease Model Evaluation")
    print("=" * 60)

    print(f"Model: {BEST_MODEL_PATH}")
    print(f"Dataset: {DATASET_YAML}")
    print(f"Image size: {IMAGE_SIZE}")
    print(f"Device: {DEVICE}")

    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model weights not found: {BEST_MODEL_PATH}"
        )

    if not DATASET_YAML.exists():
        raise FileNotFoundError(
            f"Dataset configuration not found: {DATASET_YAML}"
        )

    model = YOLO(str(BEST_MODEL_PATH))

    results = model.val(
        data=str(DATASET_YAML),
        split="test",
        imgsz=IMAGE_SIZE,
        device=DEVICE,
        project=str(PROJECT_ROOT / "runs"),
        name="test_evaluation",
        exist_ok=True,
        verbose=True,
    )

    print("\n" + "=" * 60)
    print("Evaluation completed successfully")
    print("=" * 60)

    if hasattr(results, "box"):
        print(f"Precision: {results.box.mp:.4f}")
        print(f"Recall: {results.box.mr:.4f}")
        print(f"mAP@50: {results.box.map50:.4f}")
        print(f"mAP@50-95: {results.box.map:.4f}")

    print(
        f"\nEvaluation results saved in: "
        f"{PROJECT_ROOT / 'runs' / 'test_evaluation'}"
    )


if __name__ == "__main__":
    evaluate_model()
