from typing import TypedDict, Optional, List, Dict, Any

class ContractState(TypedDict):
    file_path: str
    contract_text: Optional[str]
    classification: Optional[Dict[str, Any]]
    #classification outputs
    contract_type: Optional[str]
    industry: Optional[str]

    #new state 
    retrieved_clauses: Optional[List[Dict[str,Any]]]
    
    analysis_report: Optional[Dict[str, Any]]

    missing_clauses: Optional[List[str]]

    suggestions: Optional[List[str]]

    clause_comparison: Optional[List[Dict[str, Any]]]