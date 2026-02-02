from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def retrieve_clauses(
    query: str,
    contract_type: str,
    k: int = 3,
    db_path="clause_vector_db"
):
    """Retrieve most relevant clauses for a given contract type"""

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.load_local(
        db_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    results = vector_store.similarity_search(
        query,
        k=k,
        filter={"contract_type": contract_type}
    )

    return results
