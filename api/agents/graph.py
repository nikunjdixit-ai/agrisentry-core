from typing import TypedDict, Dict, Any, List, Optional, cast

from langgraph.graph import StateGraph, END

from api.rag.agro_rag import AgroRAG
from api.tools.agri_tools import (
    get_weather_forecast,
    search_vendor_catalog,
    fetch_mandi_prices,
)

from modules.telemetry_voice.virtual_sensing import (
    get_unified_virtual_sensing,
)

from modules.telemetry_voice.config import (
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
)


# ============================================================
# AgriSentry Shared State
# ============================================================

class AgriSentryState(TypedDict):
    user_query: str

    crop_details: Dict[str, Any]

    diagnostic_result: Optional[Dict[str, Any]]

    rag_context: List[Dict[str, Any]]

    vendor_options: List[Dict[str, Any]]

    mandi_prices: Dict[str, Any]

    # Member 3 telemetry context
    telemetry_context: Dict[str, Any]

    current_step: str

    verification_flag: bool

    retry_count: int

    verification_notes: str

    evidence_score: float


# ============================================================
# RAG
# ============================================================

rag = AgroRAG()


# ============================================================
# Diagnostician Agent
# ============================================================

def diagnostician_agent(state: AgriSentryState):

    crop = state["crop_details"]["crop"]
    region = state["crop_details"]["region"]

    # --------------------------------------------------------
    # 1. Get current telemetry
    # --------------------------------------------------------

    telemetry = get_unified_virtual_sensing(
        DEFAULT_LATITUDE,
        DEFAULT_LONGITUDE,
    )

    telemetry_data = telemetry.model_dump()

    # Store telemetry in shared state
    state["telemetry_context"] = telemetry_data

    # --------------------------------------------------------
    # 2. Extract soil + NDVI information
    # --------------------------------------------------------

    soil_data = telemetry_data.get("soil", {})
    ndvi_data = telemetry_data.get("ndvi", {})

    soil_moisture = float(
        soil_data.get("soil_moisture", 0.0)
    )

    soil_temperature = float(
        soil_data.get("soil_temperature", 0.0)
    )

    humidity = float(
        soil_data.get("relative_humidity", 0.0)
    )

    ndvi_mean = float(
        ndvi_data.get("ndvi_mean", 0.0)
    )

    vegetation_class = ndvi_data.get(
        "vegetation_class",
        "Unknown",
    )

    # --------------------------------------------------------
    # 3. Generate field signals
    # --------------------------------------------------------

    field_signals: List[str] = []

    if soil_moisture < 0.20:
        field_signals.append(
            "Low soil moisture detected"
        )

    elif soil_moisture > 0.40:
        field_signals.append(
            "High soil moisture detected"
        )

    else:
        field_signals.append(
            "Soil moisture is in a moderate range"
        )

    # NDVI signal
    if ndvi_mean < 0.30:
        field_signals.append(
            "Vegetation stress signal detected from NDVI"
        )
    else:
        field_signals.append(
            "Vegetation shows relatively healthy NDVI signal"
        )

    # --------------------------------------------------------
    # 4. Build field context
    # --------------------------------------------------------

    field_context = {
        "soil_moisture": soil_moisture,
        "soil_temperature": soil_temperature,
        "relative_humidity": humidity,
        "ndvi_mean": ndvi_mean,
        "vegetation_class": vegetation_class,
        "field_signals": field_signals,
        "ndvi_is_simulated": ndvi_data.get(
            "is_simulated",
            False,
        ),
    }

    # --------------------------------------------------------
    # 5. Build telemetry-aware RAG query
    # --------------------------------------------------------

    telemetry_query = f"""
Farmer query:
{state["user_query"]}

Crop:
{crop}

Region:
{region}

Current field telemetry:
Soil moisture: {soil_moisture}
Soil temperature: {soil_temperature}
Relative humidity: {humidity}
NDVI mean: {ndvi_mean}
Vegetation class: {vegetation_class}

Field signals:
{", ".join(field_signals)}

Use the field telemetry as supporting evidence when retrieving
agricultural advisories. Do not treat simulated NDVI as confirmed
satellite observation.
"""

    # --------------------------------------------------------
    # 6. Retrieve agricultural knowledge
    # --------------------------------------------------------

    docs = rag.retrieve_agri_context(
        query=telemetry_query,
        crop=crop,
        region=region,
    )

    state["rag_context"] = [
        doc.model_dump()
        for doc in docs
    ]

    # --------------------------------------------------------
    # 7. Get weather information
    # --------------------------------------------------------

    weather = get_weather_forecast.invoke(
        {
            "location": region,
            "days": 3,
        }
    )

    # --------------------------------------------------------
    # 8. Generate diagnosis/advisory
    # --------------------------------------------------------

    existing_diagnosis = state.get(
        "diagnostic_result"
    )

    if (
        existing_diagnosis
        and isinstance(existing_diagnosis, dict)
        and existing_diagnosis.get("status") == "success"
    ):

        state["diagnostic_result"] = {
            **existing_diagnosis,
            "weather": weather,
            "telemetry": telemetry_data,
            "field_context": field_context,
            "telemetry_query": telemetry_query,
            "treatment_advisories": [
                doc.title
                for doc in docs
            ],
            "primary_advisory": (
                docs[0].content
                if docs
                else
                "Consult local agricultural extension officer."
            ),
        }

    else:

        state["diagnostic_result"] = {
            "status": "advisory_generated",

            "crop": crop,

            "region": region,

            "weather": weather,

            "telemetry": telemetry_data,

            "field_context": field_context,

            "telemetry_query": telemetry_query,

            "suspected_issue": (
                docs[0].title
                if docs
                else "General Advisory"
            ),

            "actionable_advice": (
                docs[0].content
                if docs
                else
                "Consult local agricultural extension officer."
            ),
        }

    state["current_step"] = "diagnosis_complete"

    return state


# ============================================================
# Procurement Agent
# ============================================================

def procurement_agent(state: AgriSentryState):

    vendors = search_vendor_catalog.invoke(
        {
            "item_type": "pesticide",
            "region": state["crop_details"]["region"],
        }
    )

    state["vendor_options"] = vendors

    state["current_step"] = "vendor_complete"

    return state


# ============================================================
# Market Agent
# ============================================================

def market_agent(state: AgriSentryState):

    prices = fetch_mandi_prices.invoke(
        {
            "crop": state["crop_details"]["crop"],
            "state": state["crop_details"]["region"],
        }
    )

    state["mandi_prices"] = prices

    state["current_step"] = "market_complete"

    return state


# ============================================================
# Verification Gate
# ============================================================

def verification_gate(state: AgriSentryState):

    rag_context = state.get(
        "rag_context",
        [],
    )

    # --------------------------------------------------------
    # Check whether a specific agricultural advisory exists
    # --------------------------------------------------------

    valid_advisory = any(
        isinstance(doc, dict)
        and doc.get("title")
        and doc.get("title") != "National Advisory"
        for doc in rag_context
    )

    # --------------------------------------------------------
    # Evidence found
    # --------------------------------------------------------

    if valid_advisory:

        state["verification_flag"] = True

        state["verification_notes"] = (
            "Evidence Verified"
        )

        state["evidence_score"] = 0.95

    # --------------------------------------------------------
    # No specific evidence found
    # --------------------------------------------------------

    else:

        state["verification_flag"] = False

        state["verification_notes"] = (
            "No specific evidence found; retry required"
        )

        state["evidence_score"] = 0.40

    return state


# ============================================================
# Verification Routing
# ============================================================

def route_verification(
    state: AgriSentryState,
):

    if state["verification_flag"]:
        return "verified"

    if state["retry_count"] >= 1:
        return "escalate"

    state["retry_count"] += 1

    return "retry"


# ============================================================
# LangGraph Workflow
# ============================================================

workflow = StateGraph(
    AgriSentryState
)


# Add agents
workflow.add_node(
    "DiagnosticianAgent",
    diagnostician_agent,
)

workflow.add_node(
    "ProcurementAgent",
    procurement_agent,
)

workflow.add_node(
    "MarketAgent",
    market_agent,
)

workflow.add_node(
    "VerificationGate",
    verification_gate,
)


# Entry point
workflow.set_entry_point(
    "DiagnosticianAgent"
)


# Main workflow
workflow.add_edge(
    "DiagnosticianAgent",
    "ProcurementAgent",
)

workflow.add_edge(
    "ProcurementAgent",
    "MarketAgent",
)

workflow.add_edge(
    "MarketAgent",
    "VerificationGate",
)


# Verification routing
workflow.add_conditional_edges(
    "VerificationGate",
    route_verification,
    {
        "verified": END,
        "retry": "DiagnosticianAgent",
        "escalate": END,
    },
)


# Compile graph
app = workflow.compile()