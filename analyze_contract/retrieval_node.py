from vector_store import load_clauses


def retrieve_clauses(query, contract_type, json_path="clause.json", k=5):
    clauses = load_clauses(json_path)

    query_words = set(query.lower().split())
    scored = []

    for clause in clauses:
        if clause["contract_type"] != contract_type:
            continue

        clause_words = set(clause["full_text"].lower().split())
        score = len(query_words & clause_words)  # word overlap

        scored.append((score, clause))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [c[1] for c in scored[:k]]
