"""
AgriSentry - Member 3
Virtual Sensing Module

Provides:
1. Open-Meteo soil and weather data
2. NDVI vegetation index processing
3. Realistic offline fallback simulation
4. Pydantic data models
"""

from datetime import datetime, timezone
import random
import time
from typing import Optional

import requests
from pydantic import BaseModel, Field

from .config import (
    OPEN_METEO_URL,
    OPEN_METEO_TIMEOUT,
    OPEN_METEO_RETRIES,
    OPEN_METEO_HOURLY_VARIABLES,
    NDVI_HEALTHY_THRESHOLD,
    NDVI_MODERATE_THRESHOLD,
    NDVI_HEALTHY_LABEL,
    NDVI_MODERATE_LABEL,
    NDVI_STRESSED_LABEL,
)





class SoilTelemetryData(BaseModel):
    """Soil and atmospheric telemetry."""

    latitude: float
    longitude: float

    soil_moisture: float = Field(ge=0.0)
    soil_temperature: float

    ambient_temperature: float
    relative_humidity: float = Field(ge=0.0, le=100.0)
    precipitation: float = Field(ge=0.0)

    timestamp: str
    source: str
    is_simulated: bool = False


class NDVIIndexData(BaseModel):
    """Vegetation health information derived from NDVI."""

    latitude: float
    longitude: float

    ndvi_mean: float = Field(ge=-1.0, le=1.0)
    ndvi_min: float = Field(ge=-1.0, le=1.0)
    ndvi_max: float = Field(ge=-1.0, le=1.0)

    cloud_cover: float = Field(ge=0.0, le=100.0)

    acquisition_date: str
    vegetation_class: str

    source: str
    is_simulated: bool = False


class UnifiedVirtualSensing(BaseModel):
    """Combined soil/weather and vegetation sensing result."""

    latitude: float
    longitude: float

    soil: SoilTelemetryData
    ndvi: NDVIIndexData

    generated_at: str





def classify_ndvi(ndvi: float) -> str:
    """
    Convert an NDVI value into a simple agricultural
    vegetation-health classification.
    """

    if ndvi >= NDVI_HEALTHY_THRESHOLD:
        return NDVI_HEALTHY_LABEL

    if ndvi >= NDVI_MODERATE_THRESHOLD:
        return NDVI_MODERATE_LABEL

    return NDVI_STRESSED_LABEL




def _build_open_meteo_params(
    latitude: float,
    longitude: float,
) -> dict:
    """Build Open-Meteo request parameters."""

    return {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(OPEN_METEO_HOURLY_VARIABLES),
        "forecast_days": 1,
        "timezone": "auto",
    }


def _extract_latest_hourly_value(
    hourly_data: dict,
    variable: str,
) -> Optional[float]:
    """Safely extract the latest available hourly value."""

    values = hourly_data.get(variable)

    if not values:
        return None

    for value in reversed(values):
        if value is not None:
            return float(value)

    return None


def fetch_open_meteo(
    latitude: float,
    longitude: float,
) -> SoilTelemetryData:
    """
    Fetch soil and weather information from Open-Meteo.

    Retries automatically when a temporary network error occurs.
    """

    params = _build_open_meteo_params(latitude, longitude)

    last_error = None

    for attempt in range(OPEN_METEO_RETRIES):

        try:
            response = requests.get(
                OPEN_METEO_URL,
                params=params,
                timeout=OPEN_METEO_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            hourly = data.get("hourly", {})

            soil_moisture = _extract_latest_hourly_value(
                hourly,
                "soil_moisture_0_to_7cm",
            )

            soil_temperature = _extract_latest_hourly_value(
                hourly,
                "soil_temperature_0_to_7cm",
            )

            ambient_temperature = _extract_latest_hourly_value(
                hourly,
                "temperature_2m",
            )

            relative_humidity = _extract_latest_hourly_value(
                hourly,
                "relative_humidity_2m",
            )

            precipitation = _extract_latest_hourly_value(
                hourly,
                "precipitation",
            )

            # Ensure required values exist.
            if any(
                value is None
                for value in [
                    soil_moisture,
                    soil_temperature,
                    ambient_temperature,
                    relative_humidity,
                    precipitation,
                ]
            ):
                raise ValueError(
                    "Open-Meteo response does not contain "
                    "all required telemetry fields."
                )

            return SoilTelemetryData(
                latitude=latitude,
                longitude=longitude,
                soil_moisture=soil_moisture,
                soil_temperature=soil_temperature,
                ambient_temperature=ambient_temperature,
                relative_humidity=relative_humidity,
                precipitation=precipitation,
                timestamp=datetime.now(
                    timezone.utc
                ).isoformat(),
                source="Open-Meteo",
                is_simulated=False,
            )

        except Exception as exc:
            last_error = exc

            if attempt < OPEN_METEO_RETRIES - 1:
                time.sleep(0.5 * (attempt + 1))

    raise RuntimeError(
        f"Open-Meteo request failed after "
        f"{OPEN_METEO_RETRIES} attempts: {last_error}"
    )




def generate_soil_fallback(
    latitude: float,
    longitude: float,
) -> SoilTelemetryData:
    """
    Generate realistic agricultural telemetry when
    Open-Meteo is unavailable.
    """

    random.seed(
        round(latitude * 1000)
        + round(longitude * 1000)
    )

    return SoilTelemetryData(
        latitude=latitude,
        longitude=longitude,
        soil_moisture=round(
            random.uniform(0.18, 0.42),
            3,
        ),
        soil_temperature=round(
            random.uniform(22.0, 31.0),
            2,
        ),
        ambient_temperature=round(
            random.uniform(26.0, 36.0),
            2,
        ),
        relative_humidity=round(
            random.uniform(45.0, 85.0),
            2,
        ),
        precipitation=round(
            random.uniform(0.0, 8.0),
            2,
        ),
        timestamp=datetime.now(
            timezone.utc
        ).isoformat(),
        source="Synthetic Agro-Climatic Simulator",
        is_simulated=True,
    )




def generate_ndvi_fallback(
    latitude: float,
    longitude: float,
) -> NDVIIndexData:
    """
    Generate realistic synthetic satellite vegetation data.

    This keeps the Member 3 demonstration functional without
    requiring a satellite API key.
    """

    random.seed(
        round(latitude * 2000)
        + round(longitude * 2000)
    )

    ndvi_mean = round(
        random.uniform(0.20, 0.82),
        3,
    )

    ndvi_min = round(
        max(-1.0, ndvi_mean - random.uniform(0.05, 0.18)),
        3,
    )

    ndvi_max = round(
        min(1.0, ndvi_mean + random.uniform(0.05, 0.15)),
        3,
    )

    cloud_cover = round(
        random.uniform(5.0, 40.0),
        2,
    )

    return NDVIIndexData(
        latitude=latitude,
        longitude=longitude,
        ndvi_mean=ndvi_mean,
        ndvi_min=ndvi_min,
        ndvi_max=ndvi_max,
        cloud_cover=cloud_cover,
        acquisition_date=datetime.now(
            timezone.utc
        ).date().isoformat(),
        vegetation_class=classify_ndvi(ndvi_mean),
        source="Synthetic Sentinel-2 Reflectance Simulator",
        is_simulated=True,
    )





def get_soil_telemetry(
    latitude: float,
    longitude: float,
) -> SoilTelemetryData:
    """
    Get soil/weather telemetry.

    Uses Open-Meteo first and automatically falls back
    to simulated data.
    """

    try:
        return fetch_open_meteo(
            latitude,
            longitude,
        )

    except Exception:
        return generate_soil_fallback(
            latitude,
            longitude,
        )


def get_ndvi(
    latitude: float,
    longitude: float,
) -> NDVIIndexData:
    """
    Get NDVI information.

    Current implementation uses the resilient synthetic
    Sentinel-2 fallback. A real satellite catalog connector
    can be plugged in later without changing the output model.
    """

    return generate_ndvi_fallback(
        latitude,
        longitude,
    )


def get_unified_virtual_sensing(
    latitude: float,
    longitude: float,
) -> UnifiedVirtualSensing:
    """
    Fetch all virtual sensing information for a GPS location.
    """

    soil = get_soil_telemetry(
        latitude,
        longitude,
    )

    ndvi = get_ndvi(
        latitude,
        longitude,
    )

    return UnifiedVirtualSensing(
        latitude=latitude,
        longitude=longitude,
        soil=soil,
        ndvi=ndvi,
        generated_at=datetime.now(
            timezone.utc
        ).isoformat(),
    )




if __name__ == "__main__":

    latitude = 26.8467
    longitude = 80.9462

    result = get_unified_virtual_sensing(
        latitude,
        longitude,
    )

    print("\n======================================")
    print("AGRISENTRY - VIRTUAL SENSING")
    print("======================================")

    print(f"Location: {latitude}, {longitude}")

    print("\nSOIL / WEATHER")
    print("--------------------------------------")
    print(
        f"Soil Moisture : "
        f"{result.soil.soil_moisture} m³/m³"
    )
    print(
        f"Soil Temp     : "
        f"{result.soil.soil_temperature} °C"
    )
    print(
        f"Temperature   : "
        f"{result.soil.ambient_temperature} °C"
    )
    print(
        f"Humidity      : "
        f"{result.soil.relative_humidity} %"
    )
    print(
        f"Precipitation : "
        f"{result.soil.precipitation} mm"
    )
    print(
        f"Source        : "
        f"{result.soil.source}"
    )

    print("\nVEGETATION / NDVI")
    print("--------------------------------------")
    print(
        f"NDVI Mean     : "
        f"{result.ndvi.ndvi_mean}"
    )
    print(
        f"NDVI Min      : "
        f"{result.ndvi.ndvi_min}"
    )
    print(
        f"NDVI Max      : "
        f"{result.ndvi.ndvi_max}"
    )
    print(
        f"Cloud Cover   : "
        f"{result.ndvi.cloud_cover} %"
    )
    print(
        f"Vegetation    : "
        f"{result.ndvi.vegetation_class}"
    )
    print(
        f"Source        : "
        f"{result.ndvi.source}"
    )

    print("\n======================================")