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

    crop_details = state.get("crop_details", {})
    crop = crop_details.get("crop", "unknown")
    region = crop_details.get("region", "unknown")
    disease = crop_details.get("disease") or crop_details.get("disease_display_name")
    language = crop_details.get("language", "en")

    docs = rag.retrieve_agri_context(
        query=state["user_query"],
        crop=crop,
        region=region,
        disease=disease,
        language=language,
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

    primary_doc = docs[0] if docs else None
    primary_content = primary_doc.content if primary_doc else "Consult local agricultural extension officer."
    primary_title = primary_doc.title if primary_doc else "General Advisory"
    source_name = primary_doc.source_name if primary_doc else "ICAR / National Extension"
    source_url = primary_doc.source_url if primary_doc else ""
    retrieval_date = primary_doc.retrieval_date if primary_doc else "2026-09-17"
    match_level = primary_doc.match_level if primary_doc else "fallback"
    is_general = primary_doc.is_general_advisory if primary_doc else True

    existing_diagnosis = state.get("diagnostic_result")
    if existing_diagnosis and isinstance(existing_diagnosis, dict) and existing_diagnosis.get("status") in ("success", "advisory_generated"):
        state["diagnostic_result"] = {
            **existing_diagnosis,
            "weather": weather,
            "treatment_advisories": [doc.title for doc in docs],
            "primary_advisory": primary_content,
            "advisory_title": primary_title,
            "source_name": source_name,
            "source_url": source_url,
            "retrieval_date": retrieval_date,
            "match_level": match_level,
            "is_general_advisory": is_general,
            "advisory_doc": primary_doc.model_dump() if primary_doc else {},
        }
    else:
        state["diagnostic_result"] = {
            "status": "advisory_generated",
            "crop": crop,
            "region": region,
            "weather": weather,
            "suspected_issue": primary_title,
            "actionable_advice": primary_content,
            "treatment_advisories": [doc.title for doc in docs],
            "primary_advisory": primary_content,
            "advisory_title": primary_title,
            "source_name": source_name,
            "source_url": source_url,
            "retrieval_date": retrieval_date,
            "match_level": match_level,
            "is_general_advisory": is_general,
            "advisory_doc": primary_doc.model_dump() if primary_doc else {},
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

    rag_docs = state.get("rag_context", [])
    primary_doc = rag_docs[0] if rag_docs else {}

    match_level = (
        primary_doc.get("match_level", "fallback")
        if isinstance(primary_doc, dict)
        else "fallback"
    )

    if match_level == "exact":
        state["verification_flag"] = True
        state["verification_notes"] = "Verified Exact Crop & Disease Match (Tier 1)"
        state["evidence_score"] = 0.95

    elif match_level == "disease_level":
        state["verification_flag"] = True
        state["verification_notes"] = "General Disease-Level Advisory (Tier 2)"
        state["evidence_score"] = 0.75

    else:
        state["verification_flag"] = False
        state["verification_notes"] = "Safety Fallback Applied — Verification Incomplete (Tier 3)"
        state["evidence_score"] = 0.35
        state["retry_count"] = state.get("retry_count", 0) + 1

    return state


def route_verification(state: AgriSentryState):

    if state.get("verification_flag"):
        return "verified"

    if state.get("retry_count", 0) >= 1:
        return "escalate"

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