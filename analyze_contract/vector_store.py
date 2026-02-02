import json
def load_clauses(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clauses = []

    for contract in data:
        contract_type = contract["contract_type"]
        for clause in contract["clauses"]:
            clauses.append({
                "contract_type": contract_type,
                "clause_title": clause["clause_title"],
                "clause_text": clause["clause_text"],
                "full_text": f"{clause['clause_title']}: {clause['clause_text']}"
            })

    return clauses
