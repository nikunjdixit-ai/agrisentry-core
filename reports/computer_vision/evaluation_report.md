# AgriSentry — Plant Disease Detection Evaluation Report

## 1. Project Information

| Property | Value |
|---|---|
| Project | AgriSentry |
| Task | Plant Disease Detection |
| Evaluation split | test |
| Image size | 256 |
| Model | `C:\Users\HP\agrisentry-core\runs\plantvillage_yolov8n\weights\best.pt` |
| Dataset configuration | `C:\Users\HP\agrisentry-core\ml\computer_vision\data\plantvillage\data.yaml` |
| Report generated | 2026-09-11T22:03:10 |

## 2. Final Test-Set Metrics

| Metric | Score |
|---|---:|
| Precision | 0.9865 |
| Recall | 0.9888 |
| mAP@50 | 0.9937 |
| mAP@50–95 | 0.9831 |

### Percentage Summary

- **Precision:** 98.65%
- **Recall:** 98.88%
- **mAP@50:** 99.37%
- **mAP@50–95:** 98.31%

## 3. Reliability Testing


| Test Result | Count |
|---|---:|
| Total tests | 7 |
| Passed tests | 7 |
| Failed tests | 0 |
| Success rate | 100.0% |

The prediction pipeline passed all implemented reliability tests.


## 4. Training Metrics

Training results available: **True**

Number of recorded training rows:
**15**

Best recorded training mAP@50–95:
**0.9827**

### Latest Recorded Training Metrics

- **epoch:** 15.0
- **time:** 4499.47
- **train/box_loss:** 0.33626
- **train/cls_loss:** 0.43839
- **train/dfl_loss:** 0.98644
- **metrics/precision(B):** 0.99059
- **metrics/recall(B):** 0.98545
- **metrics/mAP50(B):** 0.99313
- **metrics/mAP50-95(B):** 0.9826
- **val/box_loss:** 0.20715
- **val/cls_loss:** 0.20154
- **val/dfl_loss:** 0.78497
- **lr/pg0:** 0.021684
- **lr/pg1:** 0.007228
- **lr/pg2:** 0.021684
- **lr/pg3:** 0.007228
- **lr/pg4:** 0.021684
- **lr/pg5:** 0.007228
- **lr/pg6:** 0.021684
- **lr/pg7:** 0.007228

## 5. Evaluation Artifacts

The following files were generated during evaluation:

- `runs\test_evaluation\BoxF1_curve.png`
- `runs\test_evaluation\BoxPR_curve.png`
- `runs\test_evaluation\BoxP_curve.png`
- `runs\test_evaluation\BoxR_curve.png`
- `runs\test_evaluation\confusion_matrix.png`
- `runs\test_evaluation\confusion_matrix_normalized.png`
- `runs\test_evaluation\val_batch0_labels.jpg`
- `runs\test_evaluation\val_batch0_pred.jpg`
- `runs\test_evaluation\val_batch1_labels.jpg`
- `runs\test_evaluation\val_batch1_pred.jpg`
- `runs\test_evaluation\val_batch2_labels.jpg`
- `runs\test_evaluation\val_batch2_pred.jpg`

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
