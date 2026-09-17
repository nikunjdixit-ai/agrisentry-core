from typing import Optional

from fastapi import APIRouter, Query

from modules.telemetry_voice.virtual_sensing import get_unified_virtual_sensing
from modules.telemetry_voice.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE


router = APIRouter(
    prefix="/api/telemetry",
    tags=["Telemetry"]
)


@router.get("/")
def get_telemetry(
    latitude: Optional[float] = Query(
        None,
        description="Optional GPS latitude coordinate",
        ge=-90.0,
        le=90.0,
    ),
    longitude: Optional[float] = Query(
        None,
        description="Optional GPS longitude coordinate",
        ge=-180.0,
        le=180.0,
    ),
):
    lat = latitude if latitude is not None else DEFAULT_LATITUDE
    lon = longitude if longitude is not None else DEFAULT_LONGITUDE

    data = get_unified_virtual_sensing(
        lat,
        lon
    )

    return {
        "status": "success",
        "data": data.model_dump()
    }