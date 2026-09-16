from typing import TypedDict, Dict, Any, List, Optional

from langgraph.graph import StateGraph, END

from api.rag.agro_rag import AgroRAG
from api.tools.agri_tools import (
    get_weather_forecast,
    search_vendor_catalog,
    fetch_mandi_prices,
)


class AgriSentryState(TypedDict):

    user_query: str

    crop_details: Dict[str, Any]

    diagnostic_result: Optional[Dict[str, Any]]

    rag_context: List[Dict[str, Any]]

    vendor_options: List[Dict[str, Any]]

    mandi_prices: Dict[str, Any]

    current_step: str

    verification_flag: bool

    retry_count: int

    verification_notes: str

    evidence_score: float


rag = AgroRAG()


def diagnostician_agent(state: AgriSentryState):

    crop = state["crop_details"]["crop"]
    region = state["crop_details"]["region"]

    docs = rag.retrieve_agri_context(
        query=state["user_query"],
        crop=crop,
        region=region,
    )

    weather = get_weather_forecast.invoke(
        {
            "location": region,
            "days": 3,
        }
    )

    state["rag_context"] = [
        doc.model_dump() for doc in docs
    ]

    state["diagnostic_result"] = {
        "status": "pending_model_diagnosis",
        "weather": weather,
        "message": (
            "YOLO diagnosis will be connected "
            "through the diagnosis API."
        ),
    }

    state["current_step"] = "diagnosis_complete"

    return state


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


def verification_gate(state: AgriSentryState):

    if len(state["rag_context"]) > 0:

        state["verification_flag"] = True

        state["verification_notes"] = "Evidence Verified"

        state["evidence_score"] = 0.95

    else:

        state["verification_flag"] = False

        state["verification_notes"] = "Retry Required"

        state["evidence_score"] = 0.40

    return state


def route_verification(state: AgriSentryState):

    if state["verification_flag"]:

        return "verified"

    if state["retry_count"] >= 1:

        return "escalate"

    state["retry_count"] += 1

    return "retry"


# ----------------------------------
# Graph Construction
# ----------------------------------

workflow = StateGraph(AgriSentryState)

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

workflow.set_entry_point("DiagnosticianAgent")

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

workflow.add_conditional_edges(
    "VerificationGate",
    route_verification,
    {
        "verified": END,
        "retry": "DiagnosticianAgent",
        "escalate": END,
    },
)

app = workflow.compile()