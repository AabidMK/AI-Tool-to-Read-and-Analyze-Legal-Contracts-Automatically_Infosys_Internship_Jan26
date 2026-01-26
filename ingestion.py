from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import json


# 1. Qdrant client
client = QdrantClient(host="localhost", port=6333)

collection_name = "contract_clauses"

# Create collection if not exists
if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )


# 2. Local embeddings (noapi,noquota)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 3. Vector store
vectorstore = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)

# 4. Load clause.json
with open("clauses1.json", "r") as f:
    data = json.load(f)

documents = []

for contract in data:
    contract_type = contract["contract_type"]

    for clause in contract["clauses"]:
        text = f"""
Contract Type: {contract_type}
Clause Title: {clause.get('clause_title')}
Clause Text: {clause.get('clause_text')}
"""

        meta = clause.get("metadata", {})

        metadata = {
            "contract_type": contract_type,
            "clause_title": clause.get("clause_title"),
            "jurisdiction": meta.get("jurisdiction"),
            "version": meta.get("version"),
            "last_updated": meta.get("last_updated"),
            "primary_agent": meta.get("primary_agent"),
        }

        doc = Document(page_content=text.strip(), metadata=metadata)
        documents.append(doc)

# 5. Ingest in db
vectorstore.add_documents(documents)

print(f"Ingested {len(documents)} clauses into {collection_name}")
