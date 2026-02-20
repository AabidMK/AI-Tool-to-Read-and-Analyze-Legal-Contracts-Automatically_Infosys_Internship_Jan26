from pathlib import Path
from classification.graph import build_classification_graph
from retrieval.graph import build_retrieval_graph
from analyze.graph import build_analyze_graph

from review.graph import build_review_graph
from report.generate import generate_final_report


# Load contract
text_path = "data/parsed/EX-10.1_from_unified_parser.txt"
contract_text = Path(text_path).read_text(encoding="utf-8")

# Step 1: Classification
classification_graph = build_classification_graph()
classification_result = classification_graph.invoke({
    "contract_text": contract_text,
    "classification": {}
})

# Step 2: Retrieval
retrieval_graph = build_retrieval_graph()
retrieval_result = retrieval_graph.invoke(classification_result)

# Step 3: Analysis
analyze_graph = build_analyze_graph()
analysis_result = analyze_graph.invoke(retrieval_result)

print("Overall Risk:", analysis_result["global_analysis"]["overall_risk_level"])
print("Missing Clauses:", analysis_result["global_analysis"]["missing_clauses"])

for clause in analysis_result["clause_analysis"]:
    print("\nClause:", clause["clause_title"])
    print("Presence:", clause["presence"])
    print("Risk:", clause["risk_level"])


# Step 4: Multi-Role Review
review_graph = build_review_graph()
review_result = review_graph.invoke(analysis_result)

# Step 5: Final Report
final_report = generate_final_report(review_result)

print("\n===== FINAL REPORT =====\n")
print(final_report)