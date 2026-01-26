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