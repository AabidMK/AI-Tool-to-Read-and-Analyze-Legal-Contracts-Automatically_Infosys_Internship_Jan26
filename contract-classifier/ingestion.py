import os
import json
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "contract-clauses"
EMBED_DIM = 1536
LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
LMSTUDIO_API_KEY = os.getenv("LMSTUDIO_API_KEY", "lm-studio")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-ada-002")

def ensure_collection():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )

def build_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        base_url=LMSTUDIO_BASE_URL,
        api_key=LMSTUDIO_API_KEY,
        model=EMBED_MODEL,
        check_embedding_ctx_length=False,
    )

def load_clauses_from_json(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def ingest(clauses_file: str):
    ensure_collection()
    embeddings = build_embeddings()
    
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    
    clauses = load_clauses_from_json(clauses_file)
    
    texts = []
    metadatas = []
    
    for clause in clauses:
        clause_text = f"{clause['clause_title']}\n\n{clause['clause_text']}"
        texts.append(clause_text)
        metadatas.append({
            "clause_title": clause["clause_title"],
            "contract_type": clause["contract_type"],
            "jurisdiction": clause["jurisdiction"],
            "version": clause["version"],
            "last_updated": clause["last_updated"]
        })
    
    vector_store.add_texts(texts=texts, metadatas=metadatas)

def main():
    clauses_file = "data/sample_clauses.json"
    ingest(clauses_file)

if __name__ == "__main__":
    main()
