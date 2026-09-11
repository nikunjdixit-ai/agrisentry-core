# 🌾 AgriSentry

AgriSentry is an AI-powered agricultural intelligence platform designed to help farmers monitor crop health, detect plant diseases, analyze environmental conditions, and receive intelligent agricultural insights.

The platform is being developed as a modular system combining:

- Computer Vision
- Machine Learning
- Environmental and Weather Intelligence
- Forecasting
- API-based Model Serving
- Satellite and Crop Monitoring
- Agentic AI
- Farmer-oriented Recommendations and Alerts

The current implemented foundation is the **Computer Vision pipeline for plant disease detection** using a YOLO-based deep learning model. Other modules, including the API, forecasting, satellite intelligence, and agentic AI layer, are currently under development or maintained as project scaffolds.

---

## 📌 Project Status

| Module | Current Status |
|---|---|
| PlantVillage dataset preparation | Implemented |
| Dataset validation and organization | Implemented |
| Train/validation/test splitting | Implemented |
| YOLO-based plant disease detection | Implemented |
| Model training and evaluation | Implemented |
| Image prediction pipeline | Implemented |
| Duplicate-data analysis | Implemented |
| Clean test-set generation | Implemented |
| PlantDoc external diagnostic evaluation | Implemented |
| Prediction pipeline reliability testing | Implemented |
| Evaluation report generation | Implemented |
| API structure | Scaffold |
| Image prediction API | Planned |
| Forecasting module | Scaffold |
| Weather data integration | Planned |
| Environmental risk analysis | Planned |
| Satellite analysis | Planned |
| Crop monitoring | Planned |
| Agentic AI layer | Planned |
| Farmer recommendation system | Planned |
| Production deployment | Not implemented |

---

## 🎯 Project Objectives

AgriSentry aims to develop an intelligent agricultural platform capable of:

- Detecting plant diseases from leaf images
- Identifying disease classes using deep learning
- Supporting crop health monitoring
- Evaluating model performance on internal and external datasets
- Analyzing environmental and weather conditions
- Predicting possible crop-related risks
- Providing image-based agricultural insights
- Supporting future satellite-based crop monitoring
- Generating farmer-oriented recommendations
- Providing alerts related to crop health and environmental risks
- Exposing machine learning capabilities through APIs
- Building a foundation for an intelligent agricultural assistant

---

## 🌱 Problem Statement

Farmers often face difficulties in identifying plant diseases at an early stage. Manual diagnosis can be slow, expensive, and dependent on expert availability.

Environmental factors such as temperature, humidity, rainfall, and air conditions can also influence crop health and disease development.

AgriSentry aims to address these challenges by combining visual disease detection with future environmental intelligence and intelligent recommendations.

The long-term goal is to create a modular platform that can assist farmers in making better-informed crop management decisions.

---

## 🧠 Core Project Modules

AgriSentry is organized into multiple major modules.

### 1. Computer Vision

The Computer Vision module detects plant diseases from leaf images using YOLO-based deep learning models.

Current capabilities include:

- Dataset preparation
- Dataset validation
- YOLO-format annotation handling
- Train, validation, and test splitting
- Model training
- Model evaluation
- Single-image prediction
- Folder-based batch prediction
- Duplicate detection
- Clean test-set generation
- External PlantDoc evaluation
- Reliability testing
- Evaluation report generation

### 2. API Layer

The API layer is intended to expose AgriSentry capabilities through HTTP endpoints.

Planned capabilities include:

- Image upload
- Plant disease prediction
- Model health check
- Prediction response schema
- Model-loading service
- Future crop-health analysis
- Future environmental intelligence endpoints

The API layer is currently a scaffold and is not yet a completed production service.

### 3. Forecasting and Environmental Intelligence

The forecasting module is intended to process weather and environmental information.

Potential capabilities include:

- Temperature analysis
- Humidity analysis
- Rainfall forecasting
- Weather data ingestion
- Environmental risk estimation
- Crop disease risk forecasting
- Crop-health trend analysis
- Integration with external weather APIs

This module is currently planned or maintained as a scaffold.

### 4. Satellite and Crop Monitoring

Future versions of AgriSentry may integrate satellite and remote-sensing data to support:

- Crop-area monitoring
- Vegetation analysis
- Crop stress detection
- Field-level health monitoring
- Vegetation-index analysis
- Large-scale agricultural observation

This functionality has not yet been implemented.

### 5. Agentic AI and Farmer Intelligence

The future Agentic AI layer is intended to combine model outputs, environmental information, and farmer inputs.

Potential capabilities include:

- Conversational farmer interface
- Context-aware agricultural recommendations
- Disease explanation
- Crop-risk summaries
- Farmer alerts
- Memory and feedback mechanisms
- Intelligent decision support
- Explainable agricultural insights

This module is planned for future development.

---

## 🏗️ High-Level Architecture

```text
                         AgriSentry
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
   Computer Vision       Environmental       Farmer Interface
          │               Intelligence              │
          │                   │                   │
          ▼                   ▼                   ▼
   Plant Disease         Weather Data          API Layer
     Detection           and Forecasting             │
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
                    Intelligence Layer
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
       Risk Analysis   Recommendations     Alerts
                              │
                              ▼
                       Future Agentic AI