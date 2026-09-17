import json
from pathlib import Path
from typing import List

#from api.rag.agro_rag import AgriDocument
from api.rag.models import AgriDocument


class DocumentLoader:
    """
    Loads agricultural knowledge documents from JSON files.
    """

    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = Path(knowledge_dir)

    def load_documents(self) -> List[AgriDocument]:
        documents: List[AgriDocument] = []

        if not self.knowledge_dir.exists():
            print(f"Knowledge directory not found: {self.knowledge_dir}")
            return documents

        json_files = self.knowledge_dir.rglob("*.json")

        for file in json_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if not isinstance(data, list):
                    continue

                for item in data:
                    documents.append(
                        AgriDocument(
                            title=item.get("title", "Agricultural Advisory"),
                            content=item.get("content", ""),
                            crop_type=item.get("crop_type", "general"),
                            region=item.get("region", "general"),
                            problem_category=item.get("problem_category", "general"),
                            compliance_safety_level=item.get("compliance_safety_level", "standard"),
                            disease_name=item.get("disease_name", ""),
                            source_name=item.get("source_name", "ICAR / National Extension"),
                            source_url=item.get("source_url", "https://icar.org.in"),
                            retrieval_date=item.get("retrieval_date", "2026-09-17"),
                            is_general_advisory=bool(item.get("is_general_advisory", False)),
                            match_level=item.get("match_level", "exact"),
                            cultural_precautions=item.get("cultural_precautions", ""),
                            sanitation_guidance=item.get("sanitation_guidance", ""),
                            moisture_irrigation_guidance=item.get("moisture_irrigation_guidance", ""),
                            non_chemical_management=item.get("non_chemical_management", ""),
                            chemical_treatment=item.get("chemical_treatment", ""),
                            cibrc_registration_details=item.get("cibrc_registration_details", ""),
                            phi_safety_limitations=item.get("phi_safety_limitations", ""),
                            content_hi=item.get("content_hi", ""),
                        )
                    )

            except Exception as e:
                print(f"Error loading {file}: {e}")

        return documents