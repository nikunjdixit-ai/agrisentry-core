from pathlib import Path
from typing import List, Dict, Any, Optional, cast

import chromadb
from sentence_transformers import SentenceTransformer

from api.rag.document_loader import DocumentLoader
from api.rag.models import AgriDocument


class AgroRAG:

    def __init__(self):

        # ----------------------------------
        # Project and ChromaDB Configuration
        # ----------------------------------

        project_root = Path(__file__).resolve().parents[2]
        chroma_path = project_root / "chroma_data"

        self.client = chromadb.PersistentClient(
            path=str(chroma_path)
        )

        self.collection = self.client.get_or_create_collection(
            name="agri_documents"
        )

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self._seed_documents()

    # ----------------------------------
    # Seed Knowledge Base
    # ----------------------------------

    def _seed_documents(self) -> None:

        if self.collection.count() > 0:
            print("Knowledge base already exists.")
            return

        loader = DocumentLoader()
        docs = loader.load_documents()

        if not docs:
            print("No knowledge documents found.")
            return

        embeddings = self.embedding_model.encode(
            [doc.content for doc in docs]
        ).tolist()

        self.collection.add(
            ids=[str(i) for i in range(len(docs))],
            documents=[doc.content for doc in docs],
            embeddings=embeddings,
            metadatas=[
                doc.model_dump()
                for doc in docs
            ],
        )

        print(
            f"Loaded {len(docs)} documents into ChromaDB."
        )

    # ----------------------------------
    # Fallback Advisory
    # ----------------------------------

    def _fallback_document(
        self,
        crop: str,
        region: str,
    ) -> AgriDocument:

        return AgriDocument(
            title="National Advisory",
            content=(
                f"No sufficiently relevant advisory was found "
                f"for {crop} in {region}. "
                "Consult the nearest ICAR or Krishi Vigyan "
                "Kendra extension officer before applying "
                "any pesticide or treatment."
            ),
            crop_type=crop,
            region=region,
            problem_category="general",
            compliance_safety_level="standard",
        )

    # ----------------------------------
    # Normalize Text
    # ----------------------------------

    @staticmethod
    def _normalize_text(value: Any) -> str:

        if value is None:
            return ""

        return str(value).strip().lower()

    # ----------------------------------
    # Region Matching
    # ----------------------------------

    def _region_matches(
        self,
        document_region: str,
        requested_region: str,
    ) -> bool:

        document_region = self._normalize_text(
            document_region
        )

        requested_region = self._normalize_text(
            requested_region
        )

        if not document_region or not requested_region:
            return False

        return (
            document_region == requested_region
            or document_region in requested_region
            or requested_region in document_region
        )

    # ----------------------------------
    # Convert Chroma Metadata Safely
    # ----------------------------------

    @staticmethod
    def _convert_metadata(
        metadata: Dict[str, Any],
    ) -> Optional[AgriDocument]:

        try:

            title = str(
                metadata.get("title") or "Agricultural Advisory"
            )

            content = str(
                metadata.get("content") or ""
            )

            crop_type = str(
                metadata.get("crop_type") or "unknown"
            )

            region = str(
                metadata.get("region") or "general"
            )

            problem_category = str(
                metadata.get("problem_category") or "general"
            )

            compliance_safety_level = str(
                metadata.get("compliance_safety_level")
                or "standard"
            )

            return AgriDocument(
                title=title,
                content=content,
                crop_type=crop_type,
                region=region,
                problem_category=problem_category,
                compliance_safety_level=compliance_safety_level,
            )

        except Exception as error:

            print(
                f"Invalid RAG metadata skipped: {error}"
            )

            return None


    def retrieve_agri_context(
        self,
        query: str,
        crop: str,
        region: str,
        similarity_threshold: float = 0.55,
    ) -> List[AgriDocument]:

        crop = self._normalize_text(crop)
        region = self._normalize_text(region)
        query = query.strip()

        if not query:
            query = (
                f"{crop} disease treatment "
                f"in {region}"
            )

        try:

            query_embedding = self.embedding_model.encode(
                query
            ).tolist()

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=10,
                where={
                    "crop_type": crop
                },
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )

            # ChromaDB typing is broad/uncertain.
            # Cast the returned values to safe runtime structures.
            raw_metadatas = cast(
                Any,
                results.get("metadatas")
            )

            raw_distances = cast(
                Any,
                results.get("distances")
            )

            if not raw_metadatas:
                return [
                    self._fallback_document(crop, region)
                ]

            metadatas = raw_metadatas[0] or []

            if raw_distances:
                distances = raw_distances[0] or []
            else:
                distances = []

            if not metadatas:
                return [
                    self._fallback_document(crop, region)
                ]

            region_documents = []
            general_crop_documents = []

            for index, raw_metadata in enumerate(metadatas):

                if not isinstance(raw_metadata, dict):
                    continue

                metadata = cast(
                    Dict[str, Any],
                    raw_metadata
                )

                if index < len(distances):
                    distance_value = distances[index]
                else:
                    distance_value = None

                try:

                    distance = (
                        float(distance_value)
                        if distance_value is not None
                        else 1.0
                    )

                except (TypeError, ValueError):

                    distance = 1.0

                # ChromaDB distance is lower for more similar
                # documents. This is an approximate similarity.
                similarity = 1.0 - distance

                if similarity < similarity_threshold:
                    continue

                document_region = str(
                    metadata.get("region") or ""
                )

                document = self._convert_metadata(
                    metadata
                )

                if document is None:
                    continue

                if self._region_matches(
                    document_region,
                    region,
                ):

                    region_documents.append(
                        (
                            similarity,
                            document,
                        )
                    )

                else:

                    general_crop_documents.append(
                        (
                            similarity,
                            document,
                        )
                    )


            region_documents.sort(
                key=lambda item: item[0],
                reverse=True,
            )

            general_crop_documents.sort(
                key=lambda item: item[0],
                reverse=True,
            )

            selected_documents = [
                document
                for _, document in region_documents
            ]

            # Add same-crop general documents if needed.
            if len(selected_documents) < 3:

                remaining_slots = (
                    3 - len(selected_documents)
                )

                for similarity, document in general_crop_documents:

                    if remaining_slots <= 0:
                        break

                    selected_documents.append(document)
                    remaining_slots -= 1


            if not selected_documents:

                return [
                    self._fallback_document(crop, region)
                ]

            return selected_documents[:5]

        except Exception as error:

            print(
                f"RAG retrieval error: {error}"
            )

            return [
                self._fallback_document(crop, region)
            ]