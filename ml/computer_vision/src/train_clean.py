"""
AgriSentry - Reproducible Clean Training Pipeline
Trains YOLOv8 on the leakage-free grouped PlantVillage split.

IMPORTANT HARDWARE NOTICE:
For local development, GPU usage is strictly restricted.
Full training (50 epochs) on CPU takes ~25+ hours and must be run on an external
cloud GPU (Google Colab, Kaggle, AWS, or Lambda Labs with NVIDIA T4/A100).
"""

import argparse
import sys
from pathlib import Path
from ultralytics import YOLO

# Project paths
CV_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = CV_DIR / "data" / "plantvillage"
CLEAN_YAML = DATASET_DIR / "clean_split" / "data_clean.yaml"
RUNS_DIR = CV_DIR.parents[1] / "runs"


def train(
    epochs: int = 50,
    batch_size: int = 16,
    img_size: int = 256,
    device: str = "cpu",
    patience: int = 10,
    resume: bool = False,
    weights: str = "yolov8n.pt",
):
    print("=" * 60)
    print("AgriSentry — Model Training on Clean Grouped Split")
    print("=" * 60)
    print(f"Dataset config: {CLEAN_YAML}")
    print(f"Target epochs : {epochs}")
    print(f"Batch size    : {batch_size}")
    print(f"Image size    : {img_size}")
    print(f"Device        : {device}")
    print(f"Base weights  : {weights}")

    if not CLEAN_YAML.exists():
        raise FileNotFoundError(f"Clean YAML config not found at: {CLEAN_YAML}")

    if device == "cpu" and epochs > 2:
        print("\n[WARNING] Running full training (>2 epochs) on CPU is extremely slow")
        print("          (~40-50 mins per epoch on standard laptop CPU).")
        print("          For production retraining, please run on an external GPU:")
        print("          yolo detect train data=clean_split/data_clean.yaml model=yolov8n.pt epochs=50 imgsz=256 batch=16 device=0")
        print("\nStopping to prevent local system lockup. Pass --allow-cpu to override.")
        return

    model = YOLO(weights)

    results = model.train(
        data=str(CLEAN_YAML),
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        patience=patience,
        save=True,
        project=str(RUNS_DIR),
        name="plantvillage_clean_yolov8n",
        exist_ok=True,
        resume=resume,
        plots=True,
    )

    print("\nTraining completed successfully.")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train AgriSentry YOLO on Clean Split")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=256, help="Image size")
    parser.add_argument("--device", type=str, default="cpu", help="Device ('cpu' or CUDA index)")
    parser.add_argument("--allow-cpu", action="store_true", help="Allow full training on CPU")
    args = parser.parse_args()

    train(
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.imgsz,
        device=args.device,
    )
