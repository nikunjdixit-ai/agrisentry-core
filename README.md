# 🌾 AgriSentry

AgriSentry is an AI-powered agricultural intelligence platform designed to support farmers through plant disease detection, crop monitoring, environmental analysis, and future predictive intelligence.

The project currently focuses on the **Computer Vision pipeline for plant disease detection** using YOLO-based object detection models. Other components such as API serving, forecasting, satellite analysis, and agentic intelligence are currently under development or maintained as project scaffolds.

---

## 📌 Project Status

| Component | Status |
|---|---|
| PlantVillage dataset preparation | Implemented |
| Dataset train/validation/test split | Implemented |
| YOLO-based plant disease detection | Implemented and evaluated |
| Duplicate-data analysis | Implemented |
| Clean test-set generation | Implemented |
| PlantDoc external diagnostic evaluation | Implemented |
| API layer | Scaffold |
| Forecasting module | Planned / Scaffold |
| Satellite and environmental intelligence | Planned |
| Agentic AI layer | Planned |
| Production deployment | Not implemented |

---

## 🎯 Objectives

AgriSentry aims to develop a modular agricultural intelligence system capable of:

- Detecting plant diseases from leaf images
- Identifying disease classes using deep learning
- Supporting image-based crop health analysis
- Evaluating model performance on internal and external datasets
- Preparing a foundation for weather-based and environmental forecasting
- Providing future API-based model serving
- Supporting future farmer-oriented recommendations and alerts

---

## 🧠 Current Core Module: Computer Vision

The current working module uses a YOLO-based deep learning pipeline trained on the PlantVillage dataset.

### Main capabilities

- Dataset organization and splitting
- YOLO-format dataset preparation
- Plant disease model training
- Model evaluation
- Image prediction
- Duplicate detection across dataset splits
- Clean test-set generation
- External evaluation using PlantDoc images
- Class-wise performance analysis

---

## 🏗️ Project Architecture

```text
AgriSentry
│
├── Computer Vision
│   ├── Dataset preparation
│   ├── Dataset validation
│   ├── YOLO model training
│   ├── Model evaluation
│   ├── Image prediction
│   └── External validation
│
├── API Layer
│   ├── FastAPI application
│   ├── Routes
│   ├── Schemas
│   └── Services
│
├── Forecasting
│   ├── Future weather analysis
│   ├── Environmental forecasting
│   └── Crop-risk prediction
│
└── Future Intelligence Layer
    ├── Satellite analysis
    ├── Agentic AI
    ├── Farmer recommendations
    └── Agricultural alerts
```

---

## 📂 Repository Structure

```text
agrisentry-core/
│
├── api/
│   ├── main.py
│   ├── routes/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
│
├── ml/
│   ├── common/
│   │   └── __init__.py
│   │
│   ├── computer_vision/
│   │   ├── README.md
│   │   ├── test_leaf.jpg
│   │   ├── test_leaf_2.jpg
│   │   ├── test_leaf_3.jpg
│   │   │
│   │   ├── data/
│   │   │   └── plantvillage/
│   │   │       ├── images/
│   │   │       │   ├── train/
│   │   │       │   ├── val/
│   │   │       │   └── test/
│   │   │       ├── labels/
│   │   │       │   ├── train/
│   │   │       │   ├── val/
│   │   │       │   └── test/
│   │   │       └── data.yaml
│   │   │
│   │   ├── notebooks/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── data_loader.py
│   │   │   ├── preprocessing.py
│   │   │   ├── split_dataset.py
│   │   │   ├── train.py
│   │   │   ├── evaluate.py
│   │   │   ├── predict.py
│   │   │   ├── duplicates.py
│   │   │   ├── check_duplicates.py
│   │   │   ├── create_clean_test.py
│   │   │   └── plantdoc_diagnostic.py
│   │   │
│   │   └── weights/
│   │
│   └── forecasting/
│       ├── README.md
│       └── data/
│           └── .gitkeep
│
├── tests/
│   └── __init__.py
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── yolo11n.pt
└── yolov8n.pt
```

> Dataset files, training runs, generated outputs, and model weights should generally remain outside Git tracking because of their size.

---

## 📊 Dataset

### PlantVillage Dataset

The Computer Vision pipeline uses the PlantVillage dataset prepared in YOLO format.

Current dataset information:

- Total images: approximately **54,293**
- Number of classes: **38**
- Image size: **256 × 256**
- Annotation format: YOLO
- Dataset splits:
  - Training: **43,434 images**
  - Validation: **5,429 images**
  - Testing: **5,430 images**

### Dataset split ratio

```text
Training:   80%
Validation: 10%
Testing:    10%
```

The dataset split is generated using a fixed random seed to make the process reproducible.

---

## 🔬 Computer Vision Pipeline

The current Computer Vision workflow is:

```text
PlantVillage Dataset
        │
        ▼
Dataset Validation
        │
        ▼
Train / Validation / Test Split
        │
        ▼
YOLO Dataset Preparation
        │
        ▼
YOLO Model Training
        │
        ▼
Validation and Test Evaluation
        │
        ▼
Image Prediction
        │
        ▼
External PlantDoc Diagnostic Evaluation
```

---

## 🛠️ Computer Vision Scripts

| Script | Purpose |
|---|---|
| `config.py` | Intended location for project and training configuration |
| `data_loader.py` | Intended dataset loading utilities |
| `preprocessing.py` | Intended preprocessing utilities |
| `split_dataset.py` | Splits the dataset into train, validation, and test sets |
| `train.py` | Training entry point for the Computer Vision model |
| `evaluate.py` | Evaluation entry point for model performance |
| `predict.py` | Prediction entry point for individual images |
| `duplicates.py` | Detects duplicate images using image hashes |
| `check_duplicates.py` | Checks duplicate images across dataset splits |
| `create_clean_test.py` | Creates a clean test set by removing cross-split duplicate images |
| `plantdoc_diagnostic.py` | Evaluates the trained model on PlantDoc images |

Some files are currently placeholders and will be expanded as the project develops.

---

## 🧹 Dataset Quality Analysis

A dataset audit was performed to check the reliability of the evaluation process.

The audit examined:

- Exact duplicate images
- Cross-split duplication
- Class imbalance
- Annotation quality
- Image distribution
- External-domain performance

### Important findings

- Exact duplicate groups were found across dataset splits.
- Near-duplicate images were also detected.
- The dataset contains class imbalance.
- Many bounding boxes cover most or all of the leaf image.
- This makes the task behave partly like image classification rather than traditional object localization.
- Random train/test splitting may produce optimistic results.
- External datasets create a significant domain-shift challenge.

Because of these findings, internal validation metrics should not be interpreted as the complete real-world performance of the model.

---

## 📈 Model Performance

The current YOLO-based model achieved strong performance on the internal PlantVillage test set.

| Metric | Result |
|---|---:|
| Precision | Approximately 0.987 |
| Recall | Approximately 0.989 |
| mAP@50 | Approximately 0.994 |
| mAP@50–95 | Approximately 0.983 |

These results represent performance on the prepared internal dataset.

They should not be interpreted as guaranteed real-world accuracy because the PlantVillage dataset is relatively controlled and may not represent field conditions.

---

## 🌍 External Evaluation: PlantDoc

The model was also evaluated diagnostically on a PlantDoc test set to estimate performance under domain shift.

### Diagnostic results

| Metric | Result |
|---|---:|
| Total images | 206 |
| Evaluated images | 197 |
| Images without prediction | 9 |
| Correct predictions | 42 |
| Image-level accuracy | 20.39% |
| Conditional accuracy | 21.32% |

### Interpretation

The PlantDoc results show that the model’s performance decreases significantly on external images.

Possible reasons include:

- Different image backgrounds
- Different lighting conditions
- Different camera quality
- Different crop varieties
- Different disease appearances
- Different annotation and class naming conventions
- Domain difference between PlantVillage and PlantDoc

The PlantDoc script performs an image-level diagnostic evaluation. Its result is **not equivalent to an official object-detection mAP evaluation**.

---

## 🧪 Sample Prediction Images

The repository contains sample leaf images for testing:

```text
ml/computer_vision/test_leaf.jpg
ml/computer_vision/test_leaf_2.jpg
ml/computer_vision/test_leaf_3.jpg
```

These images can be used to verify the prediction workflow after the model weights and dependencies are available locally.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/nikunjdixit-ai/agrisentry-core.git
cd agrisentry-core
```

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 📦 Main Dependencies

The project uses the following major libraries:

### Deep Learning and Computer Vision

- Ultralytics
- PyTorch
- Torchvision
- OpenCV
- Pillow

### Machine Learning and Data Processing

- NumPy
- Pandas
- SciPy
- Scikit-learn
- XGBoost

### API and Serving

- FastAPI
- Uvicorn
- Pydantic

### Utilities

- Requests
- HTTPX
- Python-dotenv
- Joblib
- PyYAML
- tqdm

### Development and Visualization

- Jupyter
- Matplotlib
- Seaborn

---

## ▶️ Dataset Splitting

The dataset split script uses the PlantVillage directory inside the Computer Vision module.

Run:

```powershell
python .\ml\computer_vision\src\split_dataset.py
```

The script creates the following directories:

```text
images/train
images/val
images/test

labels/train
labels/val
labels/test
```

The script uses an 80/10/10 split with a fixed random seed.

---

## 🧠 Model Training

The training entry point is:

```powershell
python .\ml\computer_vision\src\train.py
```

Training configuration such as model architecture, image size, batch size, epochs, device, and dataset path should be checked inside the training configuration before execution.

The project has been tested with a YOLO-based model on an NVIDIA RTX 3050 Laptop GPU.

---

## 📊 Model Evaluation

The evaluation entry point is:

```powershell
python .\ml\computer_vision\src\evaluate.py
```

Evaluation should be performed separately on the validation and test splits.

For reliable experimentation, record:

- Model architecture
- Dataset version
- Image size
- Batch size
- Number of epochs
- Training device
- Precision
- Recall
- mAP@50
- mAP@50–95

---

## 🔍 Image Prediction

The prediction entry point is:

```powershell
python .\ml\computer_vision\src\predict.py
```

The prediction script can be used to test individual leaf images after the model weights and required paths are configured.

Example sample images:

```text
ml/computer_vision/test_leaf.jpg
ml/computer_vision/test_leaf_2.jpg
ml/computer_vision/test_leaf_3.jpg
```

---

## 🔎 Duplicate Detection

To inspect duplicate images across dataset splits:

```powershell
python .\ml\computer_vision\src\check_duplicates.py
```

To create a clean test set:

```powershell
python .\ml\computer_vision\src\create_clean_test.py
```

These scripts use image hashing to identify exact duplicate files and reduce the risk of data leakage between training and evaluation sets.

---

## 🌍 PlantDoc Diagnostic Evaluation

The PlantDoc diagnostic script evaluates the trained model on an external PlantDoc test directory.

```powershell
python .\ml\computer_vision\src\plantdoc_diagnostic.py
```

Before running it on another machine, update:

- Model weight path
- PlantDoc dataset path
- Device configuration
- Class mapping, if required

The script reports:

- Total images
- Evaluated images
- Images without prediction
- Correct predictions
- Image-level accuracy
- Conditional accuracy
- Per-class results

---

## 🚧 API Layer

The project contains an initial FastAPI-oriented structure:

```text
api/
├── main.py
├── routes/
├── schemas/
└── services/
```

At the current stage, these files are scaffolds and do not represent a completed production API.

Planned API capabilities include:

- Image upload
- Disease prediction
- Model health check
- Prediction response schema
- Future crop-health analysis
- Future environmental intelligence endpoints

---

## 🌦️ Forecasting Module

The forecasting module currently contains a basic project structure:

```text
ml/forecasting/
├── README.md
└── data/
    └── .gitkeep
```

The forecasting implementation is planned for future development.

Potential future tasks include:

- Weather forecasting
- Temperature and humidity analysis
- Rainfall prediction
- Environmental risk estimation
- Crop disease risk forecasting
- Integration with external weather APIs

---

## 🗺️ Future Roadmap

### Phase 1 — Computer Vision Foundation

- [x] Prepare PlantVillage dataset
- [x] Split dataset into train, validation, and test sets
- [x] Train YOLO-based disease detection model
- [x] Evaluate internal test performance
- [x] Test predictions on sample images
- [x] Analyze duplicate images
- [x] Perform PlantDoc diagnostic evaluation

### Phase 2 — Robustness and Generalization

- [ ] Improve cross-domain performance
- [ ] Evaluate on more field-based datasets
- [ ] Add stronger data augmentation
- [ ] Review class imbalance
- [ ] Improve annotation quality
- [ ] Perform leakage-safe dataset splitting
- [ ] Compare multiple model architectures

### Phase 3 — API and Deployment

- [ ] Implement FastAPI application
- [ ] Add image-upload endpoint
- [ ] Add prediction endpoint
- [ ] Add request and response schemas
- [ ] Add model-loading service
- [ ] Add API testing
- [ ] Containerize the application
- [ ] Deploy the inference service

### Phase 4 — Forecasting and Environmental Intelligence

- [ ] Add weather data ingestion
- [ ] Add forecasting models
- [ ] Add environmental risk analysis
- [ ] Integrate satellite data
- [ ] Add crop-health monitoring
- [ ] Add farmer alerts and recommendations

### Phase 5 — Agentic Agricultural Intelligence

- [ ] Add intelligent decision-making layer
- [ ] Add conversational farmer interface
- [ ] Add contextual recommendations
- [ ] Add memory and feedback mechanisms
- [ ] Add explainable agricultural insights

---

## ⚠️ Current Limitations

The current system has the following limitations:

1. The strongest results are obtained on the internal PlantVillage dataset.
2. External PlantDoc performance is considerably lower.
3. The dataset contains class imbalance.
4. Duplicate and near-duplicate images may affect evaluation reliability.
5. The current model may not generalize well to real field conditions.
6. API implementation is not completed.
7. Forecasting functionality is not implemented yet.
8. Production deployment is not available.
9. The PlantDoc evaluation is diagnostic and not a complete object-detection benchmark.
10. Model weights and datasets are not intended to be committed to Git because of their size.

---

## 🔐 Git and Large Files

The repository ignores large and generated files such as:

- Python virtual environments
- Python cache files
- Dataset files
- Training runs
- Model weights
- Generated outputs
- Logs
- Secrets and environment files

Model weights should be stored locally or through a dedicated model-storage solution.

---

## 👥 Contribution

Contributions are welcome.

Recommended contribution workflow:

```bash
git checkout -b feature/your-feature
```

Make changes, test them, and commit:

```bash
git add .
git commit -m "Describe your change"
git push origin feature/your-feature
```

Then open a pull request.

---

## 📄 License

This project is licensed under the terms specified in the `LICENSE` file.

---

## 👨‍💻 Project

**AgriSentry**  
AI-powered agricultural intelligence and plant disease detection platform.

Repository:

https://github.com/nikunjdixit-ai/agrisentry-core