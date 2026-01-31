import json
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


# ---------------- CONFIG ----------------
CHROMA_PERSIST_DIR = "chroma_db"
CLAUSE_JSON_PATH = Path("data/clause.json")

INSTRUCTION = "Represent the legal contract clause for semantic retrieval."

embedding_model = HuggingFaceEmbeddings(
    model_name="hkunlp/instructor-base",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# ---------------- INITIALIZE & INGEST ----------------
def initialize_chroma():
    with open(CLAUSE_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    for contract in data:
        contract_type = contract["contract_type"]

        for clause in contract["clauses"]:
            content = f"""
Clause Title: {clause['clause_title']}
Clause Text: {clause['clause_text']}
"""

            metadata = {
                "contract_type": contract_type,
                "clause_title": clause["clause_title"],
                **clause.get("metadata", {})
            }

            documents.append(
                Document(
                    page_content=content.strip(),
                    metadata=metadata
                )
            )

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=CHROMA_PERSIST_DIR
    )

    vectorstore.persist()
    return vectorstore


# ---------------- LOAD EXISTING DB ----------------
def load_chroma():
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_model
    )