import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from src.chroma_config import get_client, COLLECTION_NAME

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLAUSE_FILE = PROJECT_ROOT / "data" / "clause.json"

embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = get_client()
collection = client.get_or_create_collection(name=COLLECTION_NAME)

with open(CLAUSE_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

documents = []
metadatas = []
ids = []

idx = 0

for contract in data:
    contract_type = contract["contract_type"].strip()

    for clause in contract["clauses"]:
        documents.append(clause["clause_text"])

        metadatas.append({
            "contract_type": contract_type,
            "title": clause["clause_title"]
        })

        ids.append(f"clause_{idx}")
        idx += 1

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print("✅ Clauses ingested successfully")