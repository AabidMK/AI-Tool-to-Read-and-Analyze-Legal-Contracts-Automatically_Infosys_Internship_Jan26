from embeddings.embedder import embed_text
from vectorstore.chroma_store import ChromaClauseStore


class ClauseRetriever:
    def __init__(self, store: ChromaClauseStore):
        self.store = store

    def retrieve(self, contract_type: str, top_k: int = 5) -> list[dict]:
        # Query focused on the actual contract content space
        query_text = f"{contract_type} contract clauses"
        query_vector = embed_text(query_text)

        # HARD FILTER by contract_type happens here
        results = self.store.similarity_search(
            query_vector=query_vector,
            top_k=top_k,
            contract_type=contract_type
        )

        clauses = []

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            clauses.append({
                "contract_type": meta["contract_type"],
                "clause_title": meta["clause_title"],
                "clause_text": doc,
                "similarity_score": round(1 - dist, 4)
            })

        return clauses
