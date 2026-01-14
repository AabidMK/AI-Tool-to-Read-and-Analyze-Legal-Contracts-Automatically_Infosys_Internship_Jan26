from typing import TypedDict, Optional

class ContractState(TypedDict):
    file_path: str
    contract_text: Optional[str]
    classification: Optional[str]
