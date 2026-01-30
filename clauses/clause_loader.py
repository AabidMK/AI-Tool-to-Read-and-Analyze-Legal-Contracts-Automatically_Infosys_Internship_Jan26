import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CLAUSE_FILE_PATH = BASE_DIR / "data" / "clause.json"


def load_clauses() -> list[dict]:
    """
    Loads clause.json and returns a flat list of clauses.
    Each dict = ONE clause.
    """
    with open(CLAUSE_FILE_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    clause_nodes = []

    for contract in raw_data:
        contract_type = contract["contract_type"]

        for clause in contract["clauses"]:
            clause_nodes.append({
                "contract_type": contract_type,
                "clause_title": clause["clause_title"],
                "clause_text": clause["clause_text"]
            })

    return clause_nodes
