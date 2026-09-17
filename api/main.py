from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.agents.graph import AgriSentryState, app as graph_app
from api.routes.telemetry import router as telemetry_router
from api.routes.voice import router as voice_router
from api.routes.diagnosis import router as diagnosis_router


app = FastAPI(
    title="AgriSentry Core API",
    version="1.0.0",
    description="Multi-Agent Agricultural Intelligence API",
)


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(telemetry_router)
app.include_router(voice_router)
app.include_router(diagnosis_router)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request Schema
# --------------------------------------------------

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


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "message": "Welcome to AgriSentry Core API",
        "docs": "/docs",
    }


# --------------------------------------------------
# Health Endpoint
# --------------------------------------------------

@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "AgriSentry Core API",
    }


# --------------------------------------------------
# Diagnosis Endpoint
# --------------------------------------------------

@app.post("/diagnose", tags=["Diagnosis"])
def diagnose(
    request: DiagnoseRequest,
) -> dict[str, Any]:
    """
    Run the AgriSentry multi-agent diagnosis workflow.
    """

    state: AgriSentryState = {
        "user_query": request.query,

        "crop_details": {
            "crop": request.crop,
            "region": request.region,
        },

        "diagnostic_result": None,
        "rag_context": [],
        "vendor_options": [],
        "mandi_prices": {},

        "current_step": "request_received",

        "verification_flag": False,
        "retry_count": 0,
        "verification_notes": "",
        "evidence_score": 0.0,
    }

    # Run multi-agent workflow
    result = graph_app.invoke(
        cast(Any, state)
    )

    return cast(
        dict[str, Any],
        result,
    )