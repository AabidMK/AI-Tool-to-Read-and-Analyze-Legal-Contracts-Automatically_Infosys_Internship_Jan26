from typing import TypedDict, List, Dict, Any

class GraphState(TypedDict):
    input_file: str
    contract_text: str

    result: Dict[str, Any]
    matched_clauses: List[Dict[str, Any]]

    review_plan: List[Dict[str, Any]]
    role_analysis_results: List[Dict[str, Any]]
    summarized_role_results: List[Dict[str, str]]

    final_report: str