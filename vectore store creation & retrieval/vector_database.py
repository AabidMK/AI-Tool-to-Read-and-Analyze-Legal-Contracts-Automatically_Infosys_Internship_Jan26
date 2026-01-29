import json
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

with open("Legal document/clause.json", "r", encoding="utf-8") as f:
    data = json.load(f)

documents = []


for contract in data:
    contract_type = contract["contract_type"]

    for clause in contract["clauses"]:
        doc = Document(
            page_content=clause["clause_text"],
            metadata={
                "contract_type": contract_type,
                "clause_title": clause["clause_title"],
                "source": clause["metadata"].get("source"),
                "jurisdiction": clause["metadata"].get("jurisdiction"),
                "version": clause["metadata"].get("version"),
                "last_updated": clause["metadata"].get("last_updated")
            }
        )
        documents.append(doc)

print(f"Loaded {len(documents)} clauses")


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vectorstore = FAISS.from_documents(documents, embeddings)


vectorstore.save_local("legal_clause_faiss")

print("Vector database created and saved successfully")
