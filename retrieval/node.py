from typing import TypedDict, List, Dict, Any
from vectordb.client import get_vector_collection


class RetrievalState(TypedDict):
    contract_text: str
    classification: dict
    retrieved_clauses: List[Dict[str, Any]]


def retrieval_node(state: RetrievalState) -> RetrievalState:
    """
    Retrieval node:
    - Uses classified contract_type
    - Executes filtered similarity search
    - Returns top relevant standard clauses
    """

    contract_text = state["contract_text"]
    classification = state["classification"]

    contract_type = classification.get("contract_type")

    collection = get_vector_collection()

    # Run similarity search with metadata filter
    results = collection.query(
        query_texts=[contract_text],
        n_results=5,
        where={"contract_type": contract_type}
    )

    retrieved_clauses = []

    # Safety check in case nothing returned
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    if documents and metadatas:
        docs = documents[0]
        metas = metadatas[0]

        for doc, meta in zip(docs, metas):
            retrieved_clauses.append(
                {
                    "clause_title": meta.get("clause_title"),
                    "clause_text": doc,
                    "metadata": meta
                }
            )

    # Fallback to general clauses if no results
    if not retrieved_clauses:
        fallback_results = collection.query(
            query_texts=[contract_text],
            n_results=5,
            where={"contract_type": "General Clauses"}
        )

        documents = fallback_results.get("documents", [])
        metadatas = fallback_results.get("metadatas", [])

        if documents and metadatas:
            docs = documents[0]
            metas = metadatas[0]

            for doc, meta in zip(docs, metas):
                retrieved_clauses.append(
                    {
                        "clause_title": meta.get("clause_title"),
                        "clause_text": doc,
                        "metadata": meta
                    }
                )

    return {
        "contract_text": contract_text,
        "classification": classification,
        "retrieved_clauses": retrieved_clauses
    }