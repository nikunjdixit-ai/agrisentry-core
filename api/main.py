import sys
from pathlib import Path
from typing import Any, Optional, cast

# Ensure project root is on sys.path for absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from api.agents.graph import AgriSentryState, app as graph_app
from api.routes.telemetry import router as telemetry_router
from api.routes.voice import router as voice_router
from api.routes.diagnosis import router as diagnosis_router
from modules.telemetry_voice.config import VOICE_OUTPUT_DIRECTORY


# ----------------------------------
# FastAPI Application
# ----------------------------------

app = FastAPI(
    title="AgriSentry Core API",
    version="1.0.0",
    description="Multi-Agent Agricultural Intelligence API",
)


# ----------------------------------
# Routers
# ----------------------------------

app.include_router(telemetry_router)
app.include_router(voice_router)
app.include_router(diagnosis_router)


# ----------------------------------
# Static Files (Voice Outputs & Frontend Assets)
# ----------------------------------

voice_dir = Path(VOICE_OUTPUT_DIRECTORY)
voice_dir.mkdir(parents=True, exist_ok=True)
app.mount("/voice_outputs", StaticFiles(directory=str(voice_dir)), name="voice_outputs")

frontend_dist_dir = PROJECT_ROOT / "frontend" / "dist"
frontend_assets_dir = frontend_dist_dir / "assets"
if frontend_assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_assets_dir)), name="assets")


# ----------------------------------
# CORS
# ----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ----------------------------------
# Diagnosis Request Model
# ----------------------------------

class DiagnoseRequest(BaseModel):
    crop: str = Field(
        ...,
        min_length=1,
        description="Crop name, for example cotton",
    )

    region: str = Field(
        ...,
        min_length=1,
        description="Agricultural region, for example Lucknow",
    )

    query: str = Field(
        ...,
        min_length=1,
        description="Farmer's agricultural question or symptom",
    )

    language: Optional[str] = Field(
        default="en",
        description="Language code, for example en or hi",
    )


# ----------------------------------
# Root Endpoint (Serves UI Dashboard)
# ----------------------------------

@app.get("/", tags=["System"])
def root() -> Any:
    index_file = frontend_dist_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "message": "Welcome to AgriSentry Core API",
        "docs": "/docs",
    }


@app.get("/api", tags=["System"])
def api_info() -> dict[str, str]:
    return {
        "message": "Welcome to AgriSentry Core API",
        "docs": "/docs",
    }


# ----------------------------------
# Health Check
# ----------------------------------

@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "AgriSentry Core API",
    }


# ----------------------------------
# Diagnosis Endpoint
# ----------------------------------

@app.post("/diagnose", tags=["Diagnosis"])
def diagnose(request: DiagnoseRequest) -> dict[str, Any]:

    # Initial state for Member 1 + Member 2 + Member 3
    state: AgriSentryState = {

        # Farmer query
        "user_query": request.query,

        # Crop and region information
        "crop_details": {
            "crop": request.crop.strip().lower(),
            "region": request.region.strip().lower(),
            "language": (request.language or "en").strip().lower(),
        },

        # Existing diagnosis
        "diagnostic_result": None,

        # RAG context
        "rag_context": [],

        # Procurement information
        "vendor_options": [],

        # Mandi information
        "mandi_prices": {},

        # ----------------------------------
        # Member 3 Telemetry Context
        # ----------------------------------
        "telemetry_context": {},

        # Workflow tracking
        "current_step": "request_received",

        # Verification
        "verification_flag": False,
        "retry_count": 0,
        "verification_notes": "",
        "evidence_score": 0.0,
    }

    # Run complete LangGraph workflow
    result = graph_app.invoke(
        cast(Any, state)
    )

    return cast(
        dict[str, Any],
        result,
    )


# ----------------------------------
# Production Uvicorn Entry Point
# ----------------------------------

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)