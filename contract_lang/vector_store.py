import json
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os

PERSIST_DIR = "vector_db"
CLAUSE_FILE = "clause.json"


def init_vector_db():
    print("🔄 Initializing Vector Database...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    with open(CLAUSE_FILE, "r", encoding="utf-8") as f:
        clauses = json.load(f)

    documents = []

    # 🔽 THIS IS WHERE YOUR CODE GOES 🔽
    for group in clauses:
        for clause in group["clauses"]:
            documents.append(
                Document(
                    page_content=clause["clause_text"],
                    metadata={
                        "contract_type": group["contract_type"],
                        "clause_title": clause["clause_title"]
                    }
                )
            )

    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    print("✅ Vector DB created and clauses embedded")
