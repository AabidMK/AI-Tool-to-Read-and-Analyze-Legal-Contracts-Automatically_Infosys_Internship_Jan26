from clauses.clause_loader import load_clauses
from embeddings.embedder import embed_text

clauses = load_clauses()

sample_clause = clauses[0]

embedding_input = (
    f"{sample_clause['contract_type']} | "
    f"{sample_clause['clause_title']} | "
    f"{sample_clause['clause_text']}"
)

vector = embed_text(embedding_input)

print("Embedding length:", len(vector))
print("First 5 values:", vector[:5])
