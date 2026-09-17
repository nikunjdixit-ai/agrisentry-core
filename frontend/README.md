# 🌾 AgriSentry Frontend — Agricultural Intelligence Dashboard

Modern React + Vite + TypeScript dashboard for the **AgriSentry** precision agriculture platform.

Provides real-time visual leaf disease diagnosis, localized bounding box rendering, explainable lesion severity metrics, and multi-agent agronomic recommendations (ICAR treatment advisories, 3-day spraying weather, APMC mandi prices, and CIBRC-registered input vendors).

---

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+ or v20+)
- npm (v9+)
- Python virtual environment with FastAPI backend running on port 8000

---

### 1. Installation

From the `frontend/` directory, install all required dependencies:

```bash
cd frontend
npm install
```

---

### 2. Environment Configuration

By default, the frontend connects to the backend at `http://localhost:8000`.

To customize the backend URL, create a `.env` file inside `frontend/`:

```bash
VITE_API_URL=http://localhost:8000
```

---

### 3. Running the Backend Server

Ensure the AgriSentry FastAPI backend is running on port 8000:

```bash
# In the project root (C:\Users\HP\agrisentry-core)
.\.venv\Scripts\Activate.ps1
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 4. Running the Frontend Development Server

Start the Vite development server:

```bash
npm run dev
```

Open your browser at:
`http://localhost:5173`

---

### 5. Production Build

To build the optimized static production bundle:

```bash
npm run build
```

To preview the production build locally:

```bash
npm run preview
```

---

## 🎯 Key Features (Phase 1)

1. **Leaf Image Ingestion:**
   - Drag-and-drop zone and file picker with instant client-side preview.
   - Validates file type (`image/*`) and size ($< 20\text{ MB}$).

2. **Agronomic Parameter Controls:**
   - Crop species selection (with intelligent auto-detection fallback).
   - Regional selector for localized APMC market rates and micro-weather.
   - Custom farmer symptom query input.

3. **Spatial Lesion Bounding Boxes:**
   - Scaled overlay rendering over the uploaded leaf photo.
   - Dynamically calculates scaling factors based on image `naturalWidth` vs `clientWidth`, ensuring precision bounding boxes regardless of input aspect ratio.

4. **Clinical Pathology Metrics:**
   - Disease display name, crop species, and internal taxonomy class.
   - High-precision confidence percentage with dynamic progress bar.
   - Explainable severity heuristic (`low`, `moderate`, `high`) and canopy coverage percentage.
   - CPU inference latency counter ($\sim 60\text{ ms}$).

5. **Multi-Agent Decision Support:**
   - **AgroRAG Advisories:** Actionable ICAR / KVK treatment guidelines.
   - **Weather Forecast:** 3-day temperature, humidity, wind, and spraying suitability indicator.
   - **Mandi Intelligence:** Modal, minimum, and maximum prices per quintal.
   - **Certified Vendors:** CIBRC-registered agricultural dealers and formulations.
   - **Verification Badge:** LangGraph evidence verification flag ($95\%$ confidence).

---

## 🔌 API Contract

The frontend strictly consumes the real backend endpoint:
- **Endpoint:** `POST /diagnosis`
- **Payload:** `multipart/form-data`
- **Fields:**
  - `image`: Binary file (JPEG/PNG/WEBP)
  - `crop`: string (optional, defaults to `"unknown"`)
  - `region`: string (optional, defaults to `"unknown"`)
  - `query`: string (optional, defaults to `""`)

Zero mock data is used; all metrics, bounding boxes, and advisories reflect live inference from `YOLOv8n` and the `LangGraph` agent pipeline.
