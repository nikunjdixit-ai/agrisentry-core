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
        loader = DocumentLoader()
        docs = loader.load_documents()

        if not docs:
            print("No knowledge documents found.")
            return

        ids = []
        documents = []
        metadatas = []

        for i, doc in enumerate(docs):
            safe_title = "".join(c for c in doc.title if c.isalnum() or c in ("-", "_")).lower()
            doc_id = f"{doc.crop_type}_{safe_title}_{i}"
            ids.append(doc_id)
            documents.append(doc.content)

            raw_meta = doc.model_dump()
            clean_meta = {k: ("" if v is None else v) for k, v in raw_meta.items()}
            metadatas.append(clean_meta)

        embeddings = self.embedding_model.encode(documents).tolist()

        try:
            existing_info = self.collection.get()
            existing_ids = existing_info.get("ids", []) if existing_info else []
            legacy_ids = [eid for eid in existing_ids if eid not in ids]
            if legacy_ids:
                self.collection.delete(ids=legacy_ids)
        except Exception as err:
            print(f"Legacy ID cleanup note: {err}")

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"Indexed {len(docs)} knowledge documents into ChromaDB.")

    # ----------------------------------
    # Fallback Advisory (Tier 3)
    # ----------------------------------

    def _fallback_document(
        self,
        crop: str,
        region: str,
        disease: Optional[str] = None,
        language: str = "en",
    ) -> AgriDocument:
        normalized_lang = self._normalize_text(language)
        display_crop = crop.title() if crop and crop != "unknown" else "Crop"
        display_region = region.title() if region and region != "unknown" else "Region"

        if normalized_lang == "hi":
            content = (
                f"{display_crop} ({display_region}) के लिए कोई पर्याप्त प्रासंगिक परामर्श नहीं मिला।\n\n"
                "तत्काल सावधानियां:\n"
                "• बिना सत्यापन वाले रसायनों के छिड़काव से बचें।\n"
                "• प्रभावित पत्तियों या पौधों को अलग करें और स्वच्छता बनाए रखें।\n"
                "• खेत में जलभराव न होने दें।\n\n"
                "अनुशंसित परामर्श:\n"
                "सटीक निदान और स्थानीय स्तर पर अनुमोदित उपचार के लिए कृपया नजदीकी कृषि विज्ञान केंद्र (KVK) "
                "या राज्य कृषि विश्वविद्यालय (SAU) के विशेषज्ञ से संपर्क करें।\n\n"
                "रासायनिक उपचार: सत्यापित स्रोत में रासायनिक उपचार निर्दिष्ट नहीं है। गैर-रासायनिक स्वच्छता विधियों को प्राथमिकता दें।"
            )
        else:
            content = (
                f"No sufficiently relevant advisory was found for {display_crop} in {display_region}. "
                "Consult the nearest ICAR or Krishi Vigyan Kendra (KVK) extension officer before applying "
                "any pesticide or treatment.\n\n"
                "Immediate Precautions:\n"
                "• Avoid spraying unverified chemicals.\n"
                "• Isolate affected plants and practice field sanitation.\n"
                "• Ensure proper drainage.\n\n"
                "Recommended Consultation:\n"
                "Consult the nearest ICAR institute, State Agricultural University (SAU), or Krishi Vigyan Kendra (KVK) extension officer.\n\n"
                "Chemical Treatment: Not specified in the verified source. Prioritize non-chemical and cultural practices."
            )

        return AgriDocument(
            title="National Extension Safety Fallback",
            content=content,
            crop_type=crop or "unknown",
            region=region or "unknown",
            problem_category="general_safety",
            compliance_safety_level="standard",
            disease_name=disease or "",
            source_name="ICAR / Krishi Vigyan Kendra Extension Network",
            source_url="https://icar.org.in",
            retrieval_date="2026-09-17",
            is_general_advisory=True,
            match_level="fallback",
            cultural_precautions="Isolate affected plants; remove visibly diseased plant parts; ensure field drainage.",
            sanitation_guidance="Disinfect cutting tools; avoid handling wet foliage; clean field perimeter.",
            moisture_irrigation_guidance="Avoid sprinkler water splash; irrigate at soil level.",
            non_chemical_management="Adopt crop rotation with non-host species; maintain clean seed stock.",
            chemical_treatment="Not specified in the verified source.",
            cibrc_registration_details="Consult local KVK or State Agricultural University extension officer for approved local treatment schedule.",
            phi_safety_limitations="Do not apply unverified chemical mixtures without official label approval.",
            content_hi=content if normalized_lang == "hi" else "",
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
        document_region = self._normalize_text(document_region)
        requested_region = self._normalize_text(requested_region)

        if not document_region or not requested_region:
            return False

        return (
            document_region == requested_region
            or document_region in requested_region
            or requested_region in document_region
        )

    # ----------------------------------
    # Convert Chroma Metadata
    # ----------------------------------

    @staticmethod
    def _convert_metadata(
        metadata: Dict[str, Any],
    ) -> Optional[AgriDocument]:
        try:
            return AgriDocument(
                title=str(metadata.get("title") or "Agricultural Advisory"),
                content=str(metadata.get("content") or ""),
                crop_type=str(metadata.get("crop_type") or "unknown"),
                region=str(metadata.get("region") or "general"),
                problem_category=str(metadata.get("problem_category") or "general"),
                compliance_safety_level=str(metadata.get("compliance_safety_level") or "standard"),
                disease_name=str(metadata.get("disease_name") or ""),
                source_name=str(metadata.get("source_name") or "ICAR / National Extension"),
                source_url=str(metadata.get("source_url") or "https://icar.org.in"),
                retrieval_date=str(metadata.get("retrieval_date") or "2026-09-17"),
                is_general_advisory=bool(metadata.get("is_general_advisory", False)),
                match_level=str(metadata.get("match_level") or "exact"),
                cultural_precautions=str(metadata.get("cultural_precautions") or ""),
                sanitation_guidance=str(metadata.get("sanitation_guidance") or ""),
                moisture_irrigation_guidance=str(metadata.get("moisture_irrigation_guidance") or ""),
                non_chemical_management=str(metadata.get("non_chemical_management") or ""),
                chemical_treatment=str(metadata.get("chemical_treatment") or ""),
                cibrc_registration_details=str(metadata.get("cibrc_registration_details") or ""),
                phi_safety_limitations=str(metadata.get("phi_safety_limitations") or ""),
                content_hi=str(metadata.get("content_hi") or ""),
            )
        except Exception as error:
            print(f"Invalid RAG metadata skipped: {error}")
            return None

    # ----------------------------------
    # Convert Chroma Distance
    # ----------------------------------

    def _distance_to_similarity(
        self,
        distance: float,
    ) -> float:
        """
        Convert Chroma distance into an approximate similarity score.
        """
        collection_metadata = self.collection.metadata or {}
        distance_space = collection_metadata.get("hnsw:space", "l2")

        if distance_space == "cosine":
            similarity = 1.0 - distance
        elif distance_space == "ip":
            similarity = 1.0 - distance
        else:
            similarity = 1.0 - ((distance ** 2) / 2.0)

        return max(0.0, min(1.0, similarity))

    # ----------------------------------
    # Agricultural Context Retrieval
    # ----------------------------------

    def retrieve_agri_context(
        self,
        query: str,
        crop: str,
        region: str,
        disease: Optional[str] = None,
        language: str = "en",
        similarity_threshold: float = 0.20,
    ) -> List[AgriDocument]:
        crop = self._normalize_text(crop)
        region = self._normalize_text(region)
        disease_clean = self._normalize_text(disease)
        normalized_lang = self._normalize_text(language) or "en"
        query = query.strip()

        # If crop is unknown or general, infer from disease identifier if possible
        if (not crop or crop in ("unknown", "general")) and disease_clean:
            if "___" in disease_clean:
                raw_crop = disease_clean.split("___")[0]
                crop = raw_crop.replace("pepper,_bell", "bell pepper").replace("_", " ").strip().lower()
            elif " " in disease_clean:
                crop = disease_clean.split(" ")[0].strip().lower()

        # Build embedding query combining symptoms, crop, disease, region, and telemetry signals
        disease_tokens = disease_clean.replace("___", " ").replace("_", " ")
        if not query:
            semantic_query = (
                f"{crop} {disease_tokens} disease symptoms management "
                f"cultural precautions chemical treatment in {region}"
            ).strip()
        else:
            semantic_query = f"{query} {crop} {disease_tokens} {region}".strip()

        retrieval_query = (
            f"Crop: {crop}. "
            f"Region: {region}. "
            f"Agricultural advisory: {query}"
        )

        try:
            print("\n[RAG] Retrieval query:")
            print(retrieval_query)
        except UnicodeEncodeError:
            print(retrieval_query.encode("ascii", "backslashreplace").decode("ascii"))

        try:
            query_embedding = self.embedding_model.encode(semantic_query).tolist()

            # ----------------------------------------------------
            # Tier 1: Exact Crop Match
            # ----------------------------------------------------
            tier1_candidates: List[Any] = []

            if crop and crop != "unknown":
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=10,
                    where={"crop_type": crop},
                    include=["documents", "metadatas", "distances"],
                )

                raw_metadatas = cast(Any, results.get("metadatas"))
                raw_distances = cast(Any, results.get("distances"))

                metadatas = (raw_metadatas[0] or []) if raw_metadatas else []
                distances = (raw_distances[0] or []) if raw_distances else []

                for index, raw_metadata in enumerate(metadatas):
                    if not isinstance(raw_metadata, dict):
                        continue

                    doc = self._convert_metadata(raw_metadata)
                    if doc is None:
                        continue

                    dist = float(distances[index]) if index < len(distances) else 1.0
                    similarity = max(0.0, 1.0 - dist)

                    # Assess disease-specific relevance
                    is_exact_disease = False
                    if disease_clean:
                        doc_dis = self._normalize_text(doc.disease_name)
                        doc_title = self._normalize_text(doc.title)
                        tokens = [t for t in disease_tokens.split() if len(t) > 2 and t not in (crop, "plant", "leaf")]
                        if doc_dis and (disease_clean in doc_dis or doc_dis in disease_clean):
                            is_exact_disease = True
                        elif any(token in doc_title or token in doc_dis for token in tokens):
                            is_exact_disease = True

                    is_region = self._region_matches(doc.region, region)

                    # Calculate ranking score
                    rank_score = similarity
                    if is_exact_disease:
                        rank_score += 2.0
                    if is_region:
                        rank_score += 0.8

                    doc.match_level = "exact"
                    doc.is_general_advisory = False
                    tier1_candidates.append((rank_score, doc))

            if tier1_candidates:
                tier1_candidates.sort(key=lambda item: item[0], reverse=True)
                selected = [item[1] for item in tier1_candidates[:3]]
                return self._apply_localization(selected, normalized_lang)

            # ----------------------------------------------------
            # Tier 2: General Disease-Level Recommendation
            # ----------------------------------------------------
            tier2_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                where={"crop_type": "general"},
                include=["documents", "metadatas", "distances"],
            )

            raw_metadatas_t2 = cast(Any, tier2_results.get("metadatas"))
            raw_distances_t2 = cast(Any, tier2_results.get("distances"))

            metadatas_t2 = (raw_metadatas_t2[0] or []) if raw_metadatas_t2 else []
            distances_t2 = (raw_distances_t2[0] or []) if raw_distances_t2 else []

            tier2_candidates: List[Any] = []
            for index, raw_metadata in enumerate(metadatas_t2):
                if not isinstance(raw_metadata, dict):
                    continue

                doc = self._convert_metadata(raw_metadata)
                if doc is None:
                    continue

                dist = float(distances_t2[index]) if index < len(distances_t2) else 1.0
                similarity = max(0.0, 1.0 - dist)

                doc_dis = self._normalize_text(doc.disease_name)
                doc_prob = self._normalize_text(doc.problem_category)
                doc_title = self._normalize_text(doc.title)

                is_relevant_category = False
                tokens = [t for t in disease_tokens.split() if len(t) > 2 and t not in (crop, "plant", "leaf")]
                if any(t in doc_dis or t in doc_prob or t in doc_title for t in tokens):
                    is_relevant_category = True

                if is_relevant_category:
                    doc.match_level = "disease_level"
                    doc.is_general_advisory = True
                    disclaimer = (
                        "General disease-level advisory — verify local label "
                        "restrictions before chemical application.\n\n"
                    )
                    if not doc.content.startswith("General disease-level advisory"):
                        doc.content = disclaimer + doc.content

                    rank_score = 1.0 / (1.0 + float(dist)) + 1.0
                    tier2_candidates.append((rank_score, doc))

            if tier2_candidates:
                tier2_candidates.sort(key=lambda item: item[0], reverse=True)
                selected = [item[1] for item in tier2_candidates[:2]]
                return self._apply_localization(selected, normalized_lang)

            # ----------------------------------------------------
            # Tier 3: National Extension Safety Fallback
            # ----------------------------------------------------
            return [
                self._fallback_document(
                    crop=crop,
                    region=region,
                    disease=disease,
                    language=normalized_lang,
                )
            ]

        except Exception as error:
            print(f"RAG retrieval error: {error}")
            return [
                self._fallback_document(
                    crop=crop,
                    region=region,
                    disease=disease,
                    language=normalized_lang,
                )
            ]

    @staticmethod
    def _apply_localization(
        docs: List[AgriDocument],
        language: str,
    ) -> List[AgriDocument]:
        if language != "hi":
            return docs

        localized_docs: List[AgriDocument] = []
        for doc in docs:
            if doc.content_hi:
                doc_copy = doc.model_copy()
                doc_copy.content = doc.content_hi
                localized_docs.append(doc_copy)
            else:
                localized_docs.append(doc)

        return localized_docs
