from vectorstore.chroma_store import load_chroma

vectorstore = load_chroma()

def retrieval_node(state: dict):
    query = state["query"]
    contract_type = state["contract_type"].strip()

    results = vectorstore.similarity_search_with_score(
        query=query,
        k=10,
        filter={"contract_type": contract_type}
    )

    seen = set()
    cleaned = []

    for doc, score in results:
        if score > 0.5:
            continue

        key = (doc.metadata["clause_title"], doc.page_content)
        if key in seen:
            continue
        seen.add(key)

        cleaned.append({
            "clause_title": doc.metadata["clause_title"],
            "clause_text": doc.page_content,
            "score": round(score, 4)
        })

    cleaned.sort(key=lambda x: x["score"])

    return {"retrieved_clauses": cleaned}

