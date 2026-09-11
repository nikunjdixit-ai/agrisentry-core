
from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from ultralytics import YOLO

from ml.computer_vision.src.config import (
    BEST_MODEL_PATH,
    IMAGE_SIZE,
    IOU_THRESHOLD,
    SAMPLE_IMAGE_1,
)
from ml.computer_vision.src.predict import (
    predict_single_image,
    predict_folder,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TEST_IMAGE = SAMPLE_IMAGE_1

TEST_OUTPUT_ROOT = (
    PROJECT_ROOT / "runs" / "reliability_tests"
)


# ==========================================
# Utility Functions
# ==========================================

def print_result(
    test_name: str,
    passed: bool,
    details: str = "",
) -> bool:
    """
    Print the result of an individual test.
    """

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {test_name}")

    if details:
        print(f"       {details}")

    return passed


def run_single_prediction(
    model: YOLO,
    image_path: str | Path,
    output_dir: str | Path,
    confidence: float = 0.25,
    device: int | str = "cpu",
) -> dict:
    """
    Compatibility wrapper around predict_single_image().

    Uses the actual parameter names supported by
    the current prediction pipeline.
    """

    return predict_single_image(
        model=model,
        image_path=image_path,
        output_dir=output_dir,
        image_size=IMAGE_SIZE,
        confidence=confidence,
        iou=IOU_THRESHOLD,
        device=device,
    )


# ==========================================
# Test 1: Valid Single Image
# ==========================================

def test_valid_single_image(model: YOLO) -> bool:
    """
    Verify that a valid image produces a structured prediction.
    """

    try:
        result = run_single_prediction(
            model=model,
            image_path=TEST_IMAGE,
            output_dir=(
                TEST_OUTPUT_ROOT
                / "valid_single_image"
            ),
            confidence=0.25,
            device="cpu",
        )

        valid_statuses = {
            "high_confidence",
            "medium_confidence",
            "low_confidence",
            "no_prediction",
        }

        passed = (
            isinstance(result, dict)
            and result.get("image") == str(
                TEST_IMAGE.resolve()
            )
            and result.get("status") in valid_statuses
            and "all_detections" in result
            and "unique_diseases" in result
        )

        return print_result(
            "Valid single-image prediction",
            passed,
            (
                f"Status: {result.get('status')}, "
                f"Disease: {result.get('disease')}"
            ),
        )

    except Exception as error:
        return print_result(
            "Valid single-image prediction",
            False,
            str(error),
        )


# ==========================================
# Test 2: Invalid Image Path
# ==========================================

def test_invalid_image_path(model: YOLO) -> bool:
    """
    Verify that a missing image raises FileNotFoundError.
    """

    invalid_path = (
        PROJECT_ROOT / "does_not_exist.jpg"
    )

    try:
        run_single_prediction(
            model=model,
            image_path=invalid_path,
            output_dir=(
                TEST_OUTPUT_ROOT
                / "invalid_path"
            ),
            confidence=0.25,
            device="cpu",
        )

        return print_result(
            "Invalid image path handling",
            False,
            (
                "Expected FileNotFoundError, "
                "but no error was raised."
            ),
        )

    except FileNotFoundError:
        return print_result(
            "Invalid image path handling",
            True,
            "FileNotFoundError was raised correctly.",
        )

    except Exception as error:
        return print_result(
            "Invalid image path handling",
            False,
            f"Unexpected error: {error}",
        )


# ==========================================
# Test 3: Unsupported File
# ==========================================

def test_unsupported_extension(model: YOLO) -> bool:
    """
    Verify that a non-image file is rejected.

    The current pipeline passes the file to
    Ultralytics, which raises an error for
    invalid image content.
    """

    with TemporaryDirectory() as temp_dir:
        invalid_file = (
            Path(temp_dir) / "sample.txt"
        )

        invalid_file.write_text(
            "This is not an image.",
            encoding="utf-8",
        )

        try:
            run_single_prediction(
                model=model,
                image_path=invalid_file,
                output_dir=(
                    TEST_OUTPUT_ROOT
                    / "unsupported_extension"
                ),
                confidence=0.25,
                device="cpu",
            )

            return print_result(
                "Unsupported extension handling",
                False,
                (
                    "Expected an error, "
                    "but no error was raised."
                ),
            )

        except (
            ValueError,
            FileNotFoundError,
            RuntimeError,
        ) as error:
            return print_result(
                "Unsupported extension handling",
                True,
                (
                    "Invalid image was rejected correctly: "
                    f"{error}"
                ),
            )

        except Exception as error:
            return print_result(
                "Unsupported extension handling",
                False,
                f"Unexpected error: {error}",
            )


# ==========================================
# Test 4: Empty Folder
# ==========================================

def test_empty_folder(model: YOLO) -> bool:
    """
    Verify that an empty folder raises FileNotFoundError.

    The current predict_folder() implementation
    intentionally raises an error when no supported
    images are found.
    """

    with TemporaryDirectory() as temp_dir:
        empty_folder = (
            Path(temp_dir) / "empty_folder"
        )

        empty_folder.mkdir()

        try:
            predict_folder(
                input_dir=empty_folder,
                model_path=BEST_MODEL_PATH,
                output_dir=(
                    TEST_OUTPUT_ROOT
                    / "empty_folder"
                ),
                image_size=IMAGE_SIZE,
                confidence=0.25,
                iou=IOU_THRESHOLD,
                device="cpu",
            )

            return print_result(
                "Empty folder handling",
                False,
                (
                    "Expected FileNotFoundError, "
                    "but no error was raised."
                ),
            )

        except FileNotFoundError as error:
            return print_result(
                "Empty folder handling",
                True,
                (
                    "Empty folder was rejected correctly: "
                    f"{error}"
                ),
            )

        except Exception as error:
            return print_result(
                "Empty folder handling",
                False,
                f"Unexpected error: {error}",
            )


# ==========================================
# Test 5: CPU Inference
# ==========================================

def test_cpu_inference(model: YOLO) -> bool:
    """
    Verify that prediction works on the CPU.
    """

    try:
        result = run_single_prediction(
            model=model,
            image_path=TEST_IMAGE,
            output_dir=(
                TEST_OUTPUT_ROOT
                / "cpu_inference"
            ),
            confidence=0.25,
            device="cpu",
        )

        passed = isinstance(result, dict)

        return print_result(
            "CPU inference",
            passed,
            "CPU prediction completed successfully.",
        )

    except Exception as error:
        return print_result(
            "CPU inference",
            False,
            str(error),
        )


# ==========================================
# Test 6: Confidence Thresholds
# ==========================================

def test_confidence_thresholds(model: YOLO) -> bool:
    """
    Verify prediction behavior at different
    confidence thresholds.
    """

    thresholds = [
        0.10,
        0.25,
        0.50,
        0.75,
    ]

    prediction_results = []

    valid_statuses = {
        "high_confidence",
        "medium_confidence",
        "low_confidence",
        "no_prediction",
    }

    try:
        for threshold in thresholds:
            result = run_single_prediction(
                model=model,
                image_path=TEST_IMAGE,
                output_dir=(
                    TEST_OUTPUT_ROOT
                    / (
                        "confidence_"
                        + str(threshold).replace(
                            ".",
                            "_",
                        )
                    )
                ),
                confidence=threshold,
                device="cpu",
            )

            prediction_results.append(
                {
                    "threshold": threshold,
                    "status": result.get("status"),
                    "detections": len(
                        result.get(
                            "all_detections",
                            [],
                        )
                    ),
                }
            )

        passed = all(
            item["status"] in valid_statuses
            for item in prediction_results
        )

        return print_result(
            "Different confidence thresholds",
            passed,
            json.dumps(
                prediction_results
            ),
        )

    except Exception as error:
        return print_result(
            "Different confidence thresholds",
            False,
            str(error),
        )


# ==========================================
# Test 7: Output Structure
# ==========================================

def test_output_structure(model: YOLO) -> bool:
    """
    Verify that the prediction response contains
    all required fields.
    """

    required_keys = {
        "image",
        "status",
        "message",
        "disease",
        "confidence",
        "confidence_percent",
        "all_detections",
        "unique_diseases",
        "output_directory",
    }

    try:
        result = run_single_prediction(
            model=model,
            image_path=TEST_IMAGE,
            output_dir=(
                TEST_OUTPUT_ROOT
                / "output_structure"
            ),
            confidence=0.25,
            device="cpu",
        )

        missing_keys = (
            required_keys - set(result.keys())
        )

        passed = (
            not missing_keys
            and isinstance(
                result["all_detections"],
                list,
            )
            and isinstance(
                result["unique_diseases"],
                list,
            )
            and isinstance(
                result["status"],
                str,
            )
        )

        if missing_keys:
            details = (
                f"Missing keys: "
                f"{sorted(missing_keys)}"
            )
        else:
            details = (
                "All required keys are present."
            )

        return print_result(
            "Prediction output structure",
            passed,
            details,
        )

    except Exception as error:
        return print_result(
            "Prediction output structure",
            False,
            str(error),
        )


# ==========================================
# Main Test Runner
# ==========================================

def main() -> int:
    """
    Run all reliability tests.
    """

    print("=" * 70)
    print(
        "AgriSentry Prediction Pipeline "
        "Reliability Tests"
    )
    print("=" * 70)

    if not BEST_MODEL_PATH.exists():
        print(
            "\nERROR: Model not found at:"
            f"\n{BEST_MODEL_PATH}"
        )
        return 1

    if not TEST_IMAGE.exists():
        print(
            "\nERROR: Test image not found at:"
            f"\n{TEST_IMAGE}"
        )
        return 1

    TEST_OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\nLoading model...")

    model = YOLO(
        str(BEST_MODEL_PATH)
    )

    tests = [
        test_valid_single_image,
        test_invalid_image_path,
        test_unsupported_extension,
        test_empty_folder,
        test_cpu_inference,
        test_confidence_thresholds,
        test_output_structure,
    ]

    passed_count = 0

    for test in tests:
        if test(model):
            passed_count += 1

    total_count = len(tests)
    failed_count = (
        total_count - passed_count
    )

    print("\n" + "=" * 70)
    print("Reliability Test Summary")
    print("=" * 70)

    print(
        f"Passed: "
        f"{passed_count}/{total_count}"
    )

    print(
        f"Failed: "
        f"{failed_count}/{total_count}"
    )

    print(
        f"Output directory: "
        f"{TEST_OUTPUT_ROOT}"
    )

    summary_path = (
        TEST_OUTPUT_ROOT
        / "test_summary.json"
    )

    summary = {
        "total_tests": total_count,
        "passed_tests": passed_count,
        "failed_tests": failed_count,
        "success_rate": round(
            passed_count
            / total_count
            * 100,
            2,
        ),
        "output_directory": str(
            TEST_OUTPUT_ROOT
        ),
    }

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Summary saved to: "
        f"{summary_path}"
    )

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())