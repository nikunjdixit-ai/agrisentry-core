from pydantic import BaseModel


class AgriDocument(BaseModel):
    title: str
    content: str
    crop_type: str
    region: str
    problem_category: str
    compliance_safety_level: str