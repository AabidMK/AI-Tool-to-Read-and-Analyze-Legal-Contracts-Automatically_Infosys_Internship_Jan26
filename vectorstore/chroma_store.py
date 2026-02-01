import json
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"
CLAUSE_JSON_PATH = BASE_DIR / "data" / "clause.json"


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
        contract_type = contract["contract_type"].strip()

        for clause in contract["clauses"]:
            content = content = clause["clause_text"].strip()

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

    return vectorstore


# ---------------- LOAD EXISTING DB ----------------
def load_chroma():
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_model
    )