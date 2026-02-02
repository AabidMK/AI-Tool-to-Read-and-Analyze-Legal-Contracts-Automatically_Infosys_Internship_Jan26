import json
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def load_clauses(json_path: str):
    """Load clause.json and convert to LangChain Documents"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    for contract in data:
        contract_type = contract["contract_type"]

        for clause in contract["clauses"]:
            content = f"{clause['clause_title']}: {clause['clause_text']}"

            metadata = {
                "contract_type": contract_type,
                "clause_title": clause["clause_title"],
                "jurisdiction": clause["metadata"]["jurisdiction"],
                "version": clause["metadata"]["version"],
                "last_updated": clause["metadata"]["last_updated"],
            }

            documents.append(
                Document(page_content=content, metadata=metadata)
            )

    return documents


def build_vector_store(json_path: str, persist_path="clause_vector_db"):
    """Create and persist FAISS vector store"""
    docs = load_clauses(json_path)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(persist_path)

    return vector_store
