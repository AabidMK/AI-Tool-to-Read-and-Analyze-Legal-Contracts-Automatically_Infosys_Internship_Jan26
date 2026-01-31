from classification.node import retrieval_node

state = {
    "query": "employee must not disclose company information",
    "contract_type": "Employment Agreement"
}

output = retrieval_node(state)

for c in output["retrieved_clauses"]:
    print(c["clause_title"], c["score"])
