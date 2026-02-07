from typing import TypedDict, List

class RoleAnalysisResult(TypedDict):
    role: str
    issues: List[str]
    missing_clauses: List[str]
    suggestions: List[str]
