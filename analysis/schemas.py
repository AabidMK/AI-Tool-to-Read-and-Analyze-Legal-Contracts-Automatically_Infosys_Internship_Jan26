from typing import List, Optional
from pydantic import BaseModel


class ClauseAnalysis(BaseModel):
    clause_name: str
    status: str  # present | weak | missing
    risk_level: str  # low | medium | high
    observations: str
    suggested_revision: Optional[str] = None


class MissingClause(BaseModel):
    clause_name: str
    why_important: str
    suggested_text: str


class OverallSummary(BaseModel):
    risk_score: int
    key_concerns: List[str]


class AnalyzeOutput(BaseModel):
    contract_type: str
    clause_analysis: List[ClauseAnalysis]
    missing_clauses: List[MissingClause]
    overall_summary: OverallSummary
