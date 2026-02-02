import os
from typing import List, Dict, Any
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "contract-clauses"
LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
LMSTUDIO_API_KEY = os.getenv("LMSTUDIO_API_KEY", "lm-studio")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-embeddinggemma-300m-qat")

class ClauseRetriever:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            base_url=LMSTUDIO_BASE_URL,
            api_key=LMSTUDIO_API_KEY,
            model=EMBED_MODEL,
            check_embedding_ctx_length=False
        )
        
        self.vector_store = QdrantVectorStore.from_existing_collection(
            embedding=self.embeddings,
            collection_name=COLLECTION_NAME,
            url=QDRANT_URL
        )
    
    def retrieve_similar_clauses(self, query: str, contract_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
        contract_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.contract_type",
                    match=MatchValue(value=contract_type)
                )
            ]
        )
        
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=top_k,
            filter=contract_filter
        )
        
        formatted_results = []
        for doc, score in results:
            result = {
                "clause_title": doc.metadata.get("clause_title", "Unknown"),
                "clause_text": doc.page_content.split("\n\n", 1)[1] if "\n\n" in doc.page_content else doc.page_content,
                "jurisdiction": doc.metadata.get("jurisdiction", "Unknown"),
                "version": doc.metadata.get("version", "Unknown"),
                "last_updated": doc.metadata.get("last_updated", "Unknown"),
                "score": float(score)
            }
            formatted_results.append(result)
        
        return formatted_results

def retrieve_similar_clauses(query: str, contract_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
    retriever = ClauseRetriever()
    return retriever.retrieve_similar_clauses(query, contract_type, top_k)
