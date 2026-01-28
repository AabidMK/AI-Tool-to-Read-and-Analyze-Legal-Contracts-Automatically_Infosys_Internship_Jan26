import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

def ingest_clauses():
    print("🔹 Starting clause ingestion...")

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Load your JSON file
    with open("contract_classifier1/data/clause.json", "r", encoding="utf-8") as f:
        clauses = json.load(f)

    # Convert each clause to a Document object
    documents = []
    for clause in clauses:
        documents.append(
            Document(
                page_content=clause['text'],  # make sure your JSON has a 'text' field
                metadata={"source": clause.get("source", "unknown")}  # optional metadata
            )
        )

    # Create or load Chroma vectorstore
    vectorstore = Chroma(
        collection_name="clauses",
        embedding_function=embeddings
    )

    # Add documents to vectorstore
    vectorstore.add_documents(documents=documents)

    print("✅ Clauses ingested successfully!")

if __name__ == "__main__":
    ingest_clauses()
