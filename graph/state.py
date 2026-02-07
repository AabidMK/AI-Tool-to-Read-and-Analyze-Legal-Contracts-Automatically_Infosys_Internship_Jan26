from typing import TypedDict, Optional, List, Dict, Any

class ContractState(TypedDict):
    # Input
    file_path: str

    # Extracted content
    contract_text: Optional[str]

    # Classification
    classification: Optional[Dict[str, Any]]
    contract_type: Optional[str]
    industry: Optional[str]

    # Retrieval + analysis
    retrieved_clauses: Optional[List[Dict[str, Any]]]
    analysis_report: Optional[Dict[str, Any]]
    clause_comparison: Optional[List[Dict[str, Any]]]
    missing_clauses: Optional[List[str]]
    suggestions: Optional[List[str]]

    # Review planning
    review_plan: Optional[List[str]]   # list of roles

    all_role_reviews: Optional[List[Dict[str,Any]]]