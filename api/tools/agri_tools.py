from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field
from langchain_core.tools import tool


# ----------------------------
# Input Schemas
# ----------------------------

class WeatherForecastInput(BaseModel):
    """Input schema for weather forecast."""

    location: str = Field(
        ...,
        description="Location of the farm (district, state or village)"
    )

    days: int = Field(
        default=3,
        ge=1,
        le=7,
        description="Forecast duration in days"
    )


class VendorCatalogInput(BaseModel):
    """Input schema for vendor catalog search."""

    item_type: str = Field(
        ...,
        description="Type of agricultural input (seed, fertilizer, pesticide)"
    )

    region: str = Field(
        ...,
        description="Region or state"
    )

    compliance_filter: Optional[str] = Field(
        default=None,
        description="Optional compliance filter such as CIBRC Registered"
    )


class MandiPricesInput(BaseModel):
    """Input schema for mandi price lookup."""

    crop: str = Field(
        ...,
        description="Crop name"
    )

    state: str = Field(
        ...,
        description="State name"
    )

    district: Optional[str] = Field(
        default=None,
        description="District name"
    )


# ----------------------------
# LangChain Tools
# ----------------------------

@tool(args_schema=WeatherForecastInput)
def get_weather_forecast(location: str, days: int = 3) -> Dict[str, Any]:
    """
    Returns a mock weather forecast for agricultural planning.
    """

    return {
        "location": location,
        "forecast_days": days,
        "temperature_c": 30,
        "humidity_percent": 68,
        "wind_speed_kmph": 12,
        "precipitation_probability": 20,
        "spraying_suitability": "Suitable",
        "warnings": []
    }


@tool(args_schema=VendorCatalogInput)
def search_vendor_catalog(
    item_type: str,
    region: str,
    compliance_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Returns sample authorized agricultural vendors.
    """

    return [
        {
            "dealer_name": "AgriMart",
            "region": region,
            "item_type": item_type,
            "stock": "Available",
            "cibrc_registration": "CIBRC-123456",
            "formulation": "EC",
            "batch_expiry": "2028-06",
            "unit_price": 850,
            "compliance": compliance_filter or "Standard"
        }
    ]


@tool(args_schema=MandiPricesInput)
def fetch_mandi_prices(
    crop: str,
    state: str,
    district: Optional[str] = None
) -> Dict[str, Any]:
    """
    Returns sample mandi prices.
    """

    return {
        "crop": crop,
        "state": state,
        "district": district,
        "modal_price_per_quintal": 6200,
        "min_price": 6000,
        "max_price": 6450,
        "arrival_trend": "Stable",
        "market_yard": "Sample Mandi"
    }