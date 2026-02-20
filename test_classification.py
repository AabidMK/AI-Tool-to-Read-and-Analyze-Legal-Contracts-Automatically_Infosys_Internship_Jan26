# test_classification.py

from pathlib import Path
from classification.graph import build_classification_graph

# Read parsed contract
text_path = "data/parsed/EX-10.1_from_unified_parser.txt"
contract_text = Path(text_path).read_text(encoding="utf-8")

graph = build_classification_graph()

initial_state = {
    "contract_text": contract_text,
    "classification": {}
}

result = graph.invoke(initial_state)

print("Contract Type :", result["classification"]["contract_type"])
print("Industry      :", result["classification"]["industry"])
