# AgriSentry — Computer Vision & Plant Disease Perception (Member 1)

## 1. Project Purpose
The AgriSentry Computer Vision module provides rapid, accurate, and multi-class crop disease detection from leaf imagery. It acts as the visual perception engine for the AgriSentry agricultural intelligence platform, feeding structured diagnostic data into the LangGraph multi-agent decision graph, vernacular voice pipelines, and farmer dashboard.

---

## 2. Canonical Model Information
- **Canonical Model Path:** `ml/computer_vision/models/agrisentry_disease_model.pt`
- **Metadata Path:** `ml/computer_vision/models/model_metadata.json`
- **Architecture:** Ultralytics YOLOv8n (Detection task)
- **Base Checkpoint Source:** `runs/plantvillage_yolov8n/weights/best.pt` (Epoch 13)
- **Number of Classes:** 38 crop disease classes
- **Input Image Resolution:** $256 \times 256$ pixels (RGB)
- **Runtime Target:** Strictly CPU-only inference (`device="cpu"`)

### Complete Class Names
The 38 classes span major agricultural crops:
1. `Apple___Apple_scab`
2. `Apple___Black_rot`
3. `Apple___Cedar_apple_rust`
4. `Apple___healthy`
5. `Blueberry___healthy`
6. `Cherry___Powdery_mildew`
7. `Cherry___healthy`
8. `Corn___Cercospora_leaf_spot Gray_leaf_spot`
9. `Corn___Common_rust`
10. `Corn___Northern_Leaf_Blight`
11. `Corn___healthy`
12. `Grape___Black_rot`
13. `Grape___Esca_(Black_Measles)`
14. `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)`
15. `Grape___healthy`
16. `Orange___Haunglongbing_(Citrus_greening)`
17. `Peach___Bacterial_spot`
18. `Peach___healthy`
19. `Pepper,_bell___Bacterial_spot`
20. `Pepper,_bell___healthy`
21. `Potato___Early_blight`
22. `Potato___Late_blight`
23. `Potato___healthy`
24. `Raspberry___healthy`
25. `Soybean___healthy`
26. `Squash___Powdery_mildew`
27. `Strawberry___Leaf_scorch`
28. `Strawberry___healthy`
29. `Tomato___Bacterial_spot`
30. `Tomato___Early_blight`
31. `Tomato___Late_blight`
32. `Tomato___Leaf_Mold`
33. `Tomato___Septoria_leaf_spot`
34. `Tomato___Spider_mites Two-spotted_spider_mite`
35. `Tomato___Target_Spot`
36. `Tomato___Tomato_Yellow_Leaf_Curl_Virus`
37. `Tomato___Tomato_mosaic_virus`
38. `Tomato___healthy`

---

## 3. How to Load and Run Inference on CPU

### Python Quickstart
```python
from ml.computer_vision.src.disease_detector import predict_disease

# Run CPU-only inference on an image path or PIL Image
result = predict_disease("ml/computer_vision/sample_batch/test_leaf.jpg")

print(f"Status: {result['status']}")
print(f"Crop: {result['crop']}")
print(f"Disease: {result['disease_display_name']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Severity: {result['severity']}")
```

### Singleton Detector Class
```python
from ml.computer_vision.src.disease_detector import get_disease_detector

detector = get_disease_detector()
result = detector.detect(image_input, conf_threshold=0.25)
```

---

## 4. Input & Output Contracts

### Supported Input Types
- File path as `str` or `pathlib.Path`
- `PIL.Image.Image` object
- Raw `bytes` buffer
- File-like objects (`BytesIO`, FastAPI `UploadFile.file`)

### Output Schema (Success)
```json
{
  "status": "success",
  "model": "agrisentry_disease_model",
  "model_version": "1.0.0",
  "crop": "tomato",
  "disease": "Tomato___Septoria_leaf_spot",
  "disease_display_name": "Tomato Septoria Leaf Spot",
  "confidence": 0.8425,
  "severity": "high",
  "severity_details": {
    "level": "high",
    "affected_area_percent": 99.96,
    "method": "Cumulative bounding-box leaf area ratio heuristic"
  },
  "detections": [
    {
      "class_id": 32,
      "class_name": "Tomato___Septoria_leaf_spot",
      "display_name": "Tomato Septoria Leaf Spot",
      "crop": "tomato",
      "confidence": 0.8425,
      "bbox": {
        "x1": 0.0,
        "y1": 0.3,
        "x2": 800.0,
        "y2": 824.0
      }
    }
  ],
  "recommendation_context": {
    "crop": "tomato",
    "disease": "Tomato___Septoria_leaf_spot",
    "confidence": 0.8425
  },
  "inference_time_ms": 59.5,
  "message": "Disease detected successfully."
}
```

### Output Schema (No Detection)
```json
{
  "status": "no_detection",
  "model": "agrisentry_disease_model",
  "model_version": "1.0.0",
  "crop": "unknown",
  "disease": null,
  "disease_display_name": null,
  "confidence": 0.0,
  "severity": "unknown",
  "severity_details": {
    "level": "unknown",
    "affected_area_percent": 0.0,
    "method": "No disease bounding boxes met the confidence threshold"
  },
  "detections": [],
  "recommendation_context": {
    "crop": "unknown",
    "disease": null,
    "confidence": 0.0
  },
  "inference_time_ms": 48.2,
  "message": "No reliable disease detection found. Please upload a clearer leaf image."
}
```

---

## 5. Severity Estimation Heuristic
The severity level is an explainable heuristic derived strictly from vision model geometric outputs:
$$\text{Affected Area Ratio} = \frac{\sum_{i} (\text{width}_i \times \text{height}_i)}{\text{Image Width} \times \text{Image Height}} \times 100\%$$

- **`low`:** $< 15.0\%$ leaf area affected, or leaf classified as healthy.
- **`moderate`:** $15.0\% \le \text{area} \le 40.0\%$.
- **`high`:** $> 40.0\%$ leaf area affected.
- **`unknown`:** No detections or invalid image dimensions.

*Note: This is an approximate visual heuristic and does not claim definitive agronomic certainty. Treatment advice is strictly decoupled from the CV module and managed by the RAG/Agent layers.*

---

## 6. Integration Instructions

### Member 2 — FastAPI & LangGraph Integration
- **Router:** `api/routes/diagnosis.py`
- **Endpoints:**
  - `POST /diagnosis` and `POST /api/v1/diagnosis`: Accepts multipart form image upload (`image: UploadFile`), `crop: Form("unknown")`, `region: Form("unknown")`, `query: Form("")`.
  - Automatically runs `run_yolo_inference()`, infers crop if unspecified, injects detection into `AgriSentryState`, executes LangGraph agents, and enriches response with RAG advisories, vendor catalog, and mandi prices.

### Member 3 — Voice & Telephony Pipeline Integration
- Import the standalone helper:
  ```python
  from ml.computer_vision.src.disease_detector import predict_disease
  ```
- Pass either the image file path received via WhatsApp/Twilio or the raw bytes buffer. The returned JSON is directly serializable for audio prompt generation.

### Member 4 — Frontend Dashboard Integration
- All outputs are 100% JSON-serializable (no NumPy scalars, PyTorch tensors, or Path objects).
- Bounding boxes are formatted as `{ "x1": float, "y1": float, "x2": float, "y2": float }` in image pixel coordinates, ready for HTML5 Canvas or SVG overlays.

---

## 7. Dataset Splits & Leakage Audit

### Original Split Audit
- **Total Images:** 54,293 images across 38 classes.
- **Leakage Finding:** Hash-based audit revealed 11 duplicate image groups (22 image files) crossing split boundaries (14 images train $\leftrightarrow$ val, 8 images train $\leftrightarrow$ test).
- **Cause:** Random shuffling of raw un-deduplicated files.

### Clean Grouped Split (`clean_split/`)
- Generated via `ml/computer_vision/src/split_grouped_clean.py`.
- Groups duplicate image hashes together before partitioning to strictly eliminate cross-split contamination.
- **Train Split:** 43,433 images (43,417 unique groups) -> `clean_split/train.txt`
- **Val Split:** 5,429 images (5,427 unique groups) -> `clean_split/val.txt`
- **Test Split:** 5,431 images (5,428 unique groups) -> `clean_split/test.txt`
- **Cross-Split Hash Leakage:** **Strictly 0.00%**
- **Clean YAML Configuration:** `ml/computer_vision/data/plantvillage/clean_split/data_clean.yaml`

---

## 8. Training Configuration & External Cloud GPU Retraining
Because training on CPU takes ~25+ hours and local laptop GPU (RTX 3050) is restricted, full retraining must be performed on an external cloud GPU instance (Colab, Kaggle, Lambda Labs, RunPod).

### External GPU Retraining Command
```bash
# Clone repository and execute with cloud GPU
yolo detect train \
  data=ml/computer_vision/data/plantvillage/clean_split/data_clean.yaml \
  model=yolov8n.pt \
  epochs=50 \
  imgsz=256 \
  batch=16 \
  device=0 \
  patience=10 \
  project=runs \
  name=plantvillage_clean_yolov8n
```

### Reproducible Training Script
```bash
python ml/computer_vision/src/train_clean.py --epochs 50 --batch 16 --imgsz 256 --device 0
```

---

## 9. Known Limitations & Domain Gap Analysis
1. **Single-Leaf Laboratory Setting:** PlantVillage leaves are photographed against uniform grey/black backdrops with controlled illumination. Average bounding box area is $82.2\%$ of the image frame.
2. **PlantVillage-to-Field Domain Gap:** In real farm settings, photographs contain complex backgrounds, multiple overlapping leaves, shadows, and varying sunlight. As demonstrated in `plantdoc_diagnostic.py`, zero-shot in-field performance is reduced compared to laboratory metrics.
3. **Class Imbalance:** Source classes range from 122 images (Potato healthy) to 4,404 images (Citrus greening), reflecting natural agricultural dataset skew.

---

## 10. Running Tests
Run the comprehensive 17-point test suite on CPU:
```bash
python -m unittest tests/test_disease_detector.py
```
All tests run strictly on CPU (`device="cpu"`) in under 1 second.
