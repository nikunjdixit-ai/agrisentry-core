from typing import Optional
from pydantic import BaseModel


class AgriDocument(BaseModel):
    title: str
    content: str
    crop_type: str
    region: str
    problem_category: str
    compliance_safety_level: str
    disease_name: str = ""
    source_name: str = "ICAR / National Extension"
    source_url: str = "https://icar.org.in"
    retrieval_date: str = "2026-09-17"
    is_general_advisory: bool = False
    match_level: str = "exact"  # 'exact', 'disease_level', 'fallback'
    cultural_precautions: str = ""
    sanitation_guidance: str = ""
    moisture_irrigation_guidance: str = ""
    non_chemical_management: str = ""
    chemical_treatment: str = ""
    cibrc_registration_details: str = ""
    phi_safety_limitations: str = ""
    content_hi: str = ""