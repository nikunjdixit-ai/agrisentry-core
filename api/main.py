from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.agents.graph import AgriSentryState, app as graph_app
from api.routes.diagnosis import router as diagnosis_router


app = FastAPI(
    title="AgriSentry Core API",
    version="1.0.0",
    description=(
        "Multi-Agent Agricultural Intelligence API "
        "with crop disease diagnosis and agricultural insights."
    ),
)


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(diagnosis_router)
app.include_router(diagnosis_router, prefix="/api/v1")


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
        description="Farmer's region, for example Uttar Pradesh",
    )

    query: str = Field(
        ...,
        min_length=1,
        description="Farmer's problem or diagnosis query",
    )


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "message": "Welcome to AgriSentry Core API",
        "docs": "/docs",
        "health": "/health",
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
def diagnose(request: DiagnoseRequest) -> dict[str, Any]:
    """
    Run the AgriSentry multi-agent diagnosis workflow.
    """

    state: AgriSentryState = {
        "user_query": request.query,

        "crop_details": {
            "crop": request.crop.strip().lower(),
            "region": request.region.strip().lower(),
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

    # Cast avoids Pylance's generic LangGraph invoke typing warning.
    result = graph_app.invoke(cast(Any, state))

    return cast(dict[str, Any], result)