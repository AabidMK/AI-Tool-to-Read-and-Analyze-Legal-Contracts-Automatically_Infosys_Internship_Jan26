from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIR = "vector_db"

def retrieve_clauses_node(state: dict):
    """
    Retrieves relevant clauses from vector DB
    filtered by classified contract type
    """

    contract_type = state["contract_type"]
    contract_text = state["contract_text"]

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    results = db.similarity_search(
        query=contract_text,
        k=5,
        filter={"contract_type": contract_type}
    )

    print("\n✅ Retrieved relevant clauses:\n")

    for r in results:
        print(f"🔹 Clause Title : {r.metadata['clause_title']}")
        print(f"📄 Clause Text  : {r.page_content}")
        print(f"📌 Contract Type: {r.metadata['contract_type']}")
        print("-" * 70)

    return {"retrieved_clauses": results}
