"""
Ingestion: Load clause.json into Qdrant (LOCAL MODE - NO SERVER!)
"""

from qdrant_client import QdrantClient #type: ignore
from qdrant_client.models import Distance, VectorParams, PointStruct #type: ignore
from fastembed import TextEmbedding #type: ignore
import json

print("="*70)
print("INGESTION: Loading clauses into Qdrant")
print("="*70 + "\n")

# Initialize Qdrant in LOCAL mode (no Docker/server needed)
print("1. Initializing Qdrant (local mode)...")
client = QdrantClient(path="./qdrant_db")  # Stores data locally
collection_name = "contract-clauses"

# Initialize embedding model
print("2. Loading embedding model (BAAI/bge-small-en-v1.5)...")
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Create collection
print("3. Creating Qdrant collection...")
try:
    client.get_collection(collection_name)
    print(f"   Collection '{collection_name}' already exists. Deleting...")
    client.delete_collection(collection_name)
except:
    pass

client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=384,  # bge-small dimension
        distance=Distance.COSINE
    )
)
print(f"   ✓ Created collection: {collection_name}")

# Load clause.json
print("4. Loading clause.json...")
with open("clause.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Generate embeddings and create points
print("5. Generating embeddings...")
points = []
point_id = 0

for contract in data:
    contract_type = contract["contract_type"]
    
    for clause in contract["clauses"]:
        # Create text for embedding
        text = f"Contract Type: {contract_type}\nClause: {clause['clause_title']}\n{clause['clause_text']}"
        
        # Generate embedding
        embedding = list(embedding_model.embed([text]))[0]
        
        # Create point
        point = PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload={
                "contract_type": contract_type,
                "clause_title": clause["clause_title"],
                "clause_text": clause["clause_text"],
                "jurisdiction": clause.get("metadata", {}).get("jurisdiction", "Unknown"),
                "version": clause.get("metadata", {}).get("version", "Unknown"),
                "last_updated": clause.get("metadata", {}).get("last_updated", "Unknown")
            }
        )
        
        points.append(point)
        point_id += 1
        
        if point_id % 5 == 0:
            print(f"   Processed {point_id} clauses...")

# Upload to Qdrant
print(f"6. Uploading {len(points)} clauses to Qdrant...")
client.upsert(collection_name=collection_name, points=points)

print("\n" + "="*70)
print(f"✓ SUCCESS! Added {len(points)} clauses to Qdrant")
print(f"✓ Collection: {collection_name}")
print(f"✓ Vector dimension: 384")
print(f"✓ Database location: ./qdrant_db")
print("="*70)
client.close()