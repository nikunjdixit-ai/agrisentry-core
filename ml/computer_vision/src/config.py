from pathlib import Path


# Project root:
# C:/Users/HP/agrisentry-core
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Computer Vision directories
CV_ROOT = PROJECT_ROOT / "ml" / "computer_vision"
DATASET_ROOT = CV_ROOT / "data" / "plantvillage"
WEIGHTS_ROOT = CV_ROOT / "weights"

# Training runs are stored at project root
RUNS_ROOT = PROJECT_ROOT / "runs"

# Best trained model
BEST_MODEL_PATH = (
    RUNS_ROOT
    / "plantvillage_yolov8n"
    / "weights"
    / "best.pt"
)

LAST_MODEL_PATH = (
    RUNS_ROOT
    / "plantvillage_yolov8n"
    / "weights"
    / "last.pt"
)

# Canonical production model and metadata
CANONICAL_MODEL_PATH = (
    CV_ROOT
    / "models"
    / "agrisentry_disease_model.pt"
)

MODEL_METADATA_PATH = (
    CV_ROOT
    / "models"
    / "model_metadata.json"
)

# Dataset configuration
DATASET_YAML = DATASET_ROOT / "data.yaml"
CLEAN_DATASET_YAML = DATASET_ROOT / "clean_split" / "data_clean.yaml"

# Default inference settings - strictly CPU only
IMAGE_SIZE = 256
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
DEVICE = "cpu"

# Sample images
SAMPLE_IMAGE_1 = CV_ROOT / "test_leaf.jpg"
SAMPLE_IMAGE_2 = CV_ROOT / "test_leaf_2.jpg"
SAMPLE_IMAGE_3 = CV_ROOT / "test_leaf_3.jpg"


def validate_paths() -> None:
    """Validate important project paths."""
    required_paths = {
        "Dataset YAML": DATASET_YAML,
        "Best model": BEST_MODEL_PATH,
    }

    missing_paths = [
        f"{name}: {path}"
        for name, path in required_paths.items()
        if not path.exists()
    ]

    if missing_paths:
        message = "Missing required paths:\n" + "\n".join(missing_paths)
        raise FileNotFoundError(message)
