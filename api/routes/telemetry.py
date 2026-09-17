from fastapi import APIRouter

from modules.telemetry_voice.virtual_sensing import get_unified_virtual_sensing
from modules.telemetry_voice.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE


router = APIRouter(
    prefix="/api/telemetry",
    tags=["Telemetry"]
)


@router.get("/")
def get_telemetry():
    data = get_unified_virtual_sensing(
        DEFAULT_LATITUDE,
        DEFAULT_LONGITUDE
    )

    return {
        "status": "success",
        "data": data.model_dump()
    }