from typing import List

import chromadb
#from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from api.rag.document_loader import DocumentLoader
from api.rag.models import AgriDocument


#class AgriDocument(BaseModel):
   # title: str
    #content: str
    #crop_type: str
    #region: str
    #problem_category: str
    #compliance_safety_level: str


class AgroRAG:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="./chromadb"
        )

        self.collection = self.client.get_or_create_collection(
            name="agri_documents"
        )

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self._seed_documents()

    def _seed_documents(self):

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
            ]
        )

        print(f"Loaded {len(docs)} documents into ChromaDB.")

    def retrieve_agri_context(
        self,
        query: str,
        crop: str,
        region: str,
        similarity_threshold: float = 0.55,
    ) -> List[AgriDocument]:

        query_embedding = self.embedding_model.encode(
            query
        ).tolist()

        try:

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                where={
                    "crop_type": crop
                }
            )

        except Exception:

            return [
                AgriDocument(
                    title="National Advisory",
                    content="Consult nearest ICAR extension officer.",
                    crop_type=crop,
                    region=region,
                    problem_category="general",
                    compliance_safety_level="standard"
                )
            ]

        if (
            not results["metadatas"]
            or len(results["metadatas"][0]) == 0
        ):

            return [
                AgriDocument(
                    title="National Advisory",
                    content="Consult nearest ICAR extension officer.",
                    crop_type=crop,
                    region=region,
                    problem_category="general",
                    compliance_safety_level="standard"
                )
            ]

        documents = []

        for metadata in results["metadatas"][0]:

            documents.append(
                AgriDocument(**metadata)
            )

        return documents