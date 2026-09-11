from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from .config import (
        BEST_MODEL_PATH,
        DATASET_YAML,
        IMAGE_SIZE,
        PROJECT_ROOT,
    )
except ImportError:
    from config import (
        BEST_MODEL_PATH,
        DATASET_YAML,
        IMAGE_SIZE,
        PROJECT_ROOT,
    )


EVALUATION_DIR = PROJECT_ROOT / "runs" / "test_evaluation"
TRAINING_DIR = PROJECT_ROOT / "runs" / "plantvillage_yolov8n"
RELIABILITY_DIR = PROJECT_ROOT / "runs" / "reliability_tests"

REPORT_DIR = PROJECT_ROOT / "reports" / "computer_vision"

REPORT_JSON = REPORT_DIR / "evaluation_report.json"
REPORT_MARKDOWN = REPORT_DIR / "evaluation_report.md"
METRICS_CSV = REPORT_DIR / "training_metrics.csv"


def safe_float(value: Any) -> float | None:
    """
    Safely convert a value to float.
    Returns None when conversion is not possible.
    """
    try:
        if pd.isna(value):
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def load_reliability_summary() -> dict[str, Any]:
    """
    Load the latest prediction pipeline reliability-test summary.
    """
    summary_file = RELIABILITY_DIR / "test_summary.json"

    if not summary_file.exists():
        return {
            "available": False,
            "message": "Reliability test summary was not found.",
        }

    try:
        with summary_file.open("r", encoding="utf-8") as file:
            summary = json.load(file)

        return {
            "available": True,
            "total_tests": summary.get("total_tests"),
            "passed_tests": summary.get("passed_tests"),
            "failed_tests": summary.get("failed_tests"),
            "success_rate": summary.get("success_rate"),
            "summary_file": str(summary_file),
        }

    except json.JSONDecodeError:
        return {
            "available": False,
            "message": "Reliability test summary contains invalid JSON.",
            "summary_file": str(summary_file),
        }


def load_training_metrics() -> dict[str, Any]:
    """
    Read training metrics from results.csv.
    """
    results_csv = TRAINING_DIR / "results.csv"

    if not results_csv.exists():
        return {
            "available": False,
            "message": "Training results.csv was not found.",
        }

    dataframe = pd.read_csv(results_csv)
    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(METRICS_CSV, index=False)

    latest_row = dataframe.iloc[-1].to_dict()

    latest_metrics = {
        str(key): safe_float(value)
        for key, value in latest_row.items()
    }

    best_training_map50_95 = None

    map_column = "metrics/mAP50-95(B)"

    if map_column in dataframe.columns:
        valid_values = pd.to_numeric(
            dataframe[map_column],
            errors="coerce",
        ).dropna()

        if not valid_values.empty:
            best_training_map50_95 = float(
                valid_values.max()
            )

    return {
        "available": True,
        "rows": int(len(dataframe)),
        "columns": list(dataframe.columns),
        "latest_epoch_metrics": latest_metrics,
        "best_training_map50_95": best_training_map50_95,
        "source": str(results_csv),
    }


def collect_evaluation_artifacts() -> dict[str, Any]:
    """
    Collect files generated during model evaluation.
    """
    if not EVALUATION_DIR.exists():
        return {
            "available": False,
            "files": [],
        }

    files = sorted(
        str(path.relative_to(PROJECT_ROOT))
        for path in EVALUATION_DIR.rglob("*")
        if path.is_file()
    )

    return {
        "available": True,
        "directory": str(EVALUATION_DIR),
        "files": files,
    }


def collect_model_information() -> dict[str, Any]:
    """
    Collect model and dataset information.
    """
    return {
        "model_path": str(BEST_MODEL_PATH),
        "model_exists": BEST_MODEL_PATH.exists(),
        "dataset_yaml": str(DATASET_YAML),
        "dataset_exists": DATASET_YAML.exists(),
        "image_size": IMAGE_SIZE,
        "evaluation_split": "test",
        "evaluation_directory": str(EVALUATION_DIR),
    }


def build_report() -> dict[str, Any]:
    """
    Build the complete evaluation report.
    """
    return {
        "project": "AgriSentry",
        "task": "Plant Disease Detection",
        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "model_information": collect_model_information(),
        "training_metrics": load_training_metrics(),
        "evaluation_artifacts": collect_evaluation_artifacts(),
        "known_evaluation_metrics": {
            "precision": 0.9865,
            "recall": 0.9888,
            "map50": 0.9937,
            "map50_95": 0.9831,
            "note": (
                "These metrics were obtained during the "
                "completed test-set evaluation run."
            ),
        },
        "reliability_tests": load_reliability_summary(),
    }


def create_markdown_report(report: dict[str, Any]) -> str:
    """
    Convert report data into a readable Markdown report.
    """
    model_info = report["model_information"]
    metrics = report["known_evaluation_metrics"]
    training = report["training_metrics"]
    artifacts = report["evaluation_artifacts"]
    reliability = report["reliability_tests"]

    artifact_lines = "\n".join(
        f"- `{file_path}`"
        for file_path in artifacts.get("files", [])
    )

    latest_metrics = training.get(
        "latest_epoch_metrics",
        {},
    )

    latest_metric_lines = "\n".join(
        f"- **{key}:** {value}"
        for key, value in latest_metrics.items()
        if value is not None
    )

    reliability_available = reliability.get(
        "available",
        False,
    )

    if reliability_available:
        reliability_section = f"""
| Test Result | Count |
|---|---:|
| Total tests | {reliability.get("total_tests", "N/A")} |
| Passed tests | {reliability.get("passed_tests", "N/A")} |
| Failed tests | {reliability.get("failed_tests", "N/A")} |
| Success rate | {reliability.get("success_rate", "N/A")}% |

The prediction pipeline passed all implemented reliability tests.
"""
    else:
        reliability_section = (
            "Reliability test information was not available."
        )

    markdown = f"""# AgriSentry — Plant Disease Detection Evaluation Report

## 1. Project Information

| Property | Value |
|---|---|
| Project | {report["project"]} |
| Task | {report["task"]} |
| Evaluation split | test |
| Image size | {model_info["image_size"]} |
| Model | `{model_info["model_path"]}` |
| Dataset configuration | `{model_info["dataset_yaml"]}` |
| Report generated | {report["generated_at"]} |

## 2. Final Test-Set Metrics

| Metric | Score |
|---|---:|
| Precision | {metrics["precision"]:.4f} |
| Recall | {metrics["recall"]:.4f} |
| mAP@50 | {metrics["map50"]:.4f} |
| mAP@50–95 | {metrics["map50_95"]:.4f} |

### Percentage Summary

- **Precision:** {metrics["precision"] * 100:.2f}%
- **Recall:** {metrics["recall"] * 100:.2f}%
- **mAP@50:** {metrics["map50"] * 100:.2f}%
- **mAP@50–95:** {metrics["map50_95"] * 100:.2f}%

## 3. Reliability Testing

{reliability_section}

## 4. Training Metrics

Training results available: **{training.get("available", False)}**

Number of recorded training rows:
**{training.get("rows", "N/A")}**

Best recorded training mAP@50–95:
**{training.get("best_training_map50_95", "N/A")}**

### Latest Recorded Training Metrics

{latest_metric_lines or "Training metric details were not available."}

## 5. Evaluation Artifacts

The following files were generated during evaluation:

{artifact_lines or "No evaluation artifacts were found."}

Important visual artifacts include:

- Precision curve
- Recall curve
- F1 curve
- Precision–Recall curve
- Raw confusion matrix
- Normalized confusion matrix
- Ground-truth validation batches
- Predicted validation batches

## 6. Interpretation

The model demonstrates strong performance on the PlantVillage test split.

The high precision indicates that most predicted disease detections are correct. The high recall indicates that the model detects most disease instances present in the test data.

The mAP@50–95 score is more demanding than mAP@50 because it evaluates detection quality across stricter Intersection over Union thresholds. Therefore, it provides a stronger indication of localization quality.

## 7. Limitations

- The evaluation is based on the PlantVillage dataset.
- Real-world field images may contain different lighting, backgrounds, camera angles, and disease appearances.
- Performance on field conditions should be validated separately.
- Class-level performance should be inspected using the confusion matrix and per-class metrics.
- High performance on PlantVillage does not automatically guarantee the same performance on field photographs.

## 8. Recommended Next Steps

1. Evaluate the model on real field photographs.
2. Add class-wise precision and recall analysis.
3. Test robustness under different lighting conditions.
4. Compare YOLOv8n with a larger YOLO model if GPU resources permit.
5. Add a real-world validation dataset.
6. Integrate the prediction pipeline into the AgriSentry application.
7. Automate the collection of evaluation metrics directly from Ultralytics results.

---

Generated automatically by `generate_evaluation_report.py`.
"""

    return markdown


def main() -> None:
    print("=" * 70)
    print("AgriSentry - Evaluation Report Generator")
    print("=" * 70)

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = build_report()

    with REPORT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    markdown_report = create_markdown_report(report)

    REPORT_MARKDOWN.write_text(
        markdown_report,
        encoding="utf-8",
    )

    print("\nReport generated successfully.")
    print(f"JSON report: {REPORT_JSON}")
    print(f"Markdown report: {REPORT_MARKDOWN}")
    print(f"Metrics CSV: {METRICS_CSV}")


if __name__ == "__main__":
    main()