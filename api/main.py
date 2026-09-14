from fastapi import FastAPI
from pydantic import BaseModel

from api.agents.graph import app as graph_app

app = FastAPI(
    title="AgriSentry Core API",
    version="1.0.0",
    description="Multi-Agent Agricultural Intelligence API"
)


class DiagnoseRequest(BaseModel):
    crop: str
    region: str
    query: str


@app.get("/")
def root():
    return {
        "message": "Welcome to AgriSentry Core API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/diagnose")
def diagnose(request: DiagnoseRequest):

    state = {
        "user_query": request.query,
        "crop_details": {
            "crop": request.crop,
            "region": request.region,
        },
        "diagnostic_result": None,
        "rag_context": [],
        "vendor_options": [],
        "mandi_prices": {},
        "current_step": "",
        "verification_flag": False,
        "retry_count": 0,
        "verification_notes": "",
        "evidence_score": 0.0,
    }

    result = graph_app.invoke(state)

    return result