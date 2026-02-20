from typing import Any, Dict

from analyze.graph import build_analyze_graph
from classification.graph import build_classification_graph
from retrieval.graph import build_retrieval_graph
from review.graph import build_review_graph


def run_clause_analysis(contract_text: str, include_review: bool = True) -> Dict[str, Any]:
    classification_graph = build_classification_graph()
    retrieval_graph = build_retrieval_graph()
    analyze_graph = build_analyze_graph()

    classified = classification_graph.invoke({"contract_text": contract_text, "classification": {}})
    retrieved = retrieval_graph.invoke(classified)
    analyzed = analyze_graph.invoke(retrieved)

    if not include_review:
        analyzed["review_roles"] = []
        analyzed["role_reviews"] = []
        return analyzed

    review_graph = build_review_graph()
    reviewed = review_graph.invoke(analyzed)
    return reviewed