from embeddings.embedder import embed_text
from vectorstore.chroma_store import ChromaClauseStore


class ClauseRetriever:
    def __init__(self, store: ChromaClauseStore):
        self.store = store

    def retrieve(self, contract_type: str, contract_text: str, top_k: int = 5) -> list[dict]:
        # Query focused on the actual contract content space
        query_text = f"{contract_type}\n\n{contract_text[:2000]}"
        query_vector = embed_text(query_text)

        # HARD FILTER by contract_type happens here
        results = self.store.similarity_search(
            query_vector=query_vector,
            top_k=top_k,
            contract_type=contract_type
        )

        clauses = []
        
        if not results["documents"] or not results["documents"][0]:
            return []

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):  
            score = max(0.0, 1 - dist)
            clauses.append({
                "contract_type": meta["contract_type"],
                "clause_title": meta["clause_title"],
                "clause_text": doc,
                "similarity_score": round(score, 4)
            })

        return clauses
