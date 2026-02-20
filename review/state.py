from typing import TypedDict, List, Dict, Any


class ReviewState(TypedDict, total=False):
    contract_text: str
    classification: Dict[str, Any]
    clause_analysis: List[Dict[str, Any]]
    global_analysis: Dict[str, Any]

    review_roles: List[Dict[str, Any]]
    role_reviews: List[Dict[str, Any]]
