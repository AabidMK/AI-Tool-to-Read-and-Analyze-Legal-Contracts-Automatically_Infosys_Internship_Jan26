from pathlib import Path
from classification.graph import build_classification_graph
from retrieval.graph import build_retrieval_graph


# Load parsed contract
text_path = "data/parsed/EX-10.1_from_unified_parser.txt"
contract_text = Path(text_path).read_text(encoding="utf-8")

# Step 1: Classification
classification_graph = build_classification_graph()

initial_state = {
    "contract_text": contract_text,
    "classification": {}
}

classification_result = classification_graph.invoke(initial_state)

# Step 2: Retrieval
retrieval_graph = build_retrieval_graph()

retrieval_result = retrieval_graph.invoke(classification_result)

print("Contract Type:", retrieval_result["classification"]["contract_type"])
print("Retrieved Clauses:", len(retrieval_result["retrieved_clauses"]))

for clause in retrieval_result["retrieved_clauses"]:
    print("-", clause["clause_title"])