# 🌾 AgriSentry

### Autonomous Farm Resilience & Supply Defense Platform

AgriSentry is an AI-powered farm resilience platform designed to help small and medium-scale farmers detect crop stress, understand environmental risks, plan interventions, and make better procurement and market-timing decisions.

The platform combines **computer vision, machine learning, virtual telemetry, satellite data, and agentic AI** into a unified farm intelligence system.

---

## 🚀 Vision

Traditional farming solutions often work in isolation:

* Disease detection focuses only on visible symptoms.
* IoT-based monitoring requires expensive physical sensors.
* Weather information is separated from crop-health analysis.
* Market information is disconnected from farm-level decisions.

AgriSentry aims to combine these signals into a single intelligent system that can provide actionable farm-level recommendations.

---

## 🎯 Core Objectives

AgriSentry aims to:

* Detect crop diseases and plant-health issues using computer vision.
* Estimate environmental and agricultural risks using machine learning.
* Combine weather, satellite, and image-based signals.
* Generate a unified **Farm Resilience Score (0–100)**.
* Provide evidence-grounded recommendations.
* Connect farmers with procurement and market intelligence.
* Deliver information through accessible interfaces such as WhatsApp and voice.

---

## 🧠 System Overview

```text
Farmer
   │
   ├── Photo
   ├── Voice
   └── WhatsApp
          │
          ▼
┌─────────────────────────┐
│    Virtual Telemetry    │
│ Weather + Satellite     │
│ + Image Data            │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   ML & Perception       │
│                         │
│ • Disease Detection     │
│ • Risk Prediction       │
│ • Forecasting           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     Risk Correlation    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      Agent Swarm        │
│ Diagnose | Procure |    │
│ Market                  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Farm Resilience Score   │
│        0 – 100          │
└────────────┬────────────┘
             │
             ▼
      Farmer Guidance
```

---

# 👨‍💻 Machine Learning & Perception

The Machine Learning & Perception module is responsible for developing the ML systems that transform farm observations into structured intelligence.

### 1. Computer Vision

The computer vision pipeline focuses on crop disease and plant-health detection from images.

Planned technologies:

* YOLOv8
* ResNet
* PyTorch
* OpenCV
* PlantVillage dataset
* PlantDoc dataset

Pipeline:

```text
Plant Image
     │
     ▼
Image Preprocessing
     │
     ▼
ML / Deep Learning Model
     │
     ▼
Disease / Stress Prediction
     │
     ▼
Structured Prediction
```

---

### 2. Agricultural Forecasting

The forecasting module analyzes environmental and weather-related data to estimate agricultural risks.

Planned technologies:

* XGBoost
* LSTM
* Scikit-Learn
* Pandas
* NumPy

Potential prediction targets include:

* Pest risk
* Water-stress risk
* Environmental stress
* Weather-driven crop risk

---

### 3. Model Inference

Trained ML models will be exposed through lightweight API services.

Planned technologies:

* FastAPI
* Pydantic
* Uvicorn

Example inference flow:

```text
Client
  │
  ▼
FastAPI
  │
  ▼
ML Model
  │
  ▼
Prediction
  │
  ▼
JSON Response
```

---

# 🏗️ Project Structure

```text
agrisentry-core/
│
├── README.md
├── .gitignore
├── requirements.txt
├── LICENSE
│
├── ml/
│   ├── computer_vision/
│   │   ├── data/
│   │   ├── notebooks/
│   │   ├── models/
│   │   ├── src/
│   │   └── README.md
│   │
│   ├── forecasting/
│   │   ├── data/
│   │   ├── notebooks/
│   │   ├── models/
│   │   ├── src/
│   │   └── README.md
│   │
│   └── common/
│       └── utils/
│
├── api/
│   ├── main.py
│   ├── routes/
│   ├── schemas/
│   └── services/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── tests/
│
├── scripts/
│
└── docs/
```

---

# 🛠️ Tech Stack

| Area                | Technologies                         |
| ------------------- | ------------------------------------ |
| Computer Vision     | YOLOv8, ResNet, PyTorch              |
| Machine Learning    | XGBoost, Scikit-Learn                |
| Forecasting         | XGBoost, LSTM                        |
| Weather Data        | Open-Meteo                           |
| Satellite Data      | Sentinel-2, Google Earth Engine      |
| API                 | FastAPI / Flask                      |
| Data Processing     | Pandas, NumPy                        |
| Visualization       | Matplotlib                           |
| Agent Orchestration | LangGraph / LangChain                |
| Knowledge Base      | ChromaDB / FAISS                     |
| LLM                 | Groq, Llama, Mistral, Gemini         |
| Voice               | Whisper, Edge-TTS / Bhashini         |
| Interface           | WhatsApp / Twilio, Streamlit / React |

---

# 🌐 Data Sources

The platform is designed around publicly available and trusted data sources.

### Open-Meteo

Used for weather and environmental telemetry.

### Sentinel-2

Used for satellite-based vegetation monitoring and NDVI/EVI analysis.

### Agmarknet

Used for agricultural market and mandi price information.

### ICAR Guidelines

Used as a knowledge source for agricultural recommendations and safety considerations.

---

# 📊 Farm Resilience Score

AgriSentry plans to generate a unified **0–100 Farm Resilience Score**.

The score can synthesize multiple signals including:

* Crop health
* Environmental conditions
* Weather risk
* Pest susceptibility
* Water stress
* Input availability
* Market stability

```text
0 ─────────────────────────────── 100
Low Resilience                  High Resilience
```

The exact scoring methodology will be defined and validated during development.

---

# 🔄 Development Roadmap

## Phase 1 — Project Foundation

* [x] Repository structure
* [x] Python environment
* [x] Requirements
* [x] Git configuration
* [ ] API skeleton

## Phase 2 — Computer Vision

* [ ] Dataset preparation
* [ ] Data preprocessing
* [ ] Baseline model
* [ ] YOLOv8 training
* [ ] ResNet baseline
* [ ] Model evaluation
* [ ] Model export

## Phase 3 — Forecasting

* [ ] Weather data collection
* [ ] Feature engineering
* [ ] Baseline ML model
* [ ] XGBoost model
* [ ] LSTM experiment
* [ ] Risk-index generation
* [ ] Model evaluation

## Phase 4 — Inference APIs

* [ ] FastAPI application
* [ ] CV prediction endpoint
* [ ] Forecasting endpoint
* [ ] Input validation
* [ ] Structured JSON responses
* [ ] API testing

## Phase 5 — System Integration

* [ ] Connect ML APIs with agent layer
* [ ] Integrate virtual telemetry
* [ ] Integrate resilience scoring
* [ ] Connect dashboard
* [ ] End-to-end testing

---

# ▶️ Local Setup

### 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd agrisentry-core
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the API

```bash
uvicorn api.main:app --reload
```

---

# 🤝 Team

### Team Hackathon Survivals

| Member          | Responsibility                             |
| --------------- | ------------------------------------------ |
| Yashee Shukla   | Full-Stack Integration & Product Pitch     |
| Nikunj Dixit    | Machine Learning & Perception              |
| Salonika Tiwari | Virtual Telemetry, Edge Simulation & Voice |
| Shreya          | Agentic Brain & Knowledge                  |

---

# 👨‍🔬 ML & Perception Lead

**Nikunj Dixit**

Responsibilities:

* Computer Vision pipeline
* Crop disease detection
* ML model development
* Agricultural forecasting
* Risk prediction
* Model evaluation
* Model inference APIs
* ML integration with the overall AgriSentry platform

---

# 📜 Project Status

🚧 **Active Development**

AgriSentry is currently under development as a hackathon/ideathon project.

The architecture and ML components may evolve as datasets, experiments, evaluation results, and system integrations are developed.

---

# 🔥 Team Hackathon Survivals

**Think. Innovate. Pitch. Impact.**

> Building intelligent, accessible, and resilient agricultural technology for Bharat.
