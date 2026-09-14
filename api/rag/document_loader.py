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
                            title=item["title"],
                            content=item["content"],
                            crop_type=item["crop_type"],
                            region=item["region"],
                            problem_category=item["problem_category"],
                            compliance_safety_level=item["compliance_safety_level"],
                        )
                    )

            except Exception as e:
                print(f"Error loading {file}: {e}")

        return documents