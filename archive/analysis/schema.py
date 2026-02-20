from pydantic import BaseModel, Field
from typing import List


class ClauseComparison(BaseModel):
    clause_title: str
    similarity_score: float
    assessment: str = Field(
        description="Whether the clause is adequate, weak, conflicting, or incomplete"
    )
    suggested_revision: str = Field(
        description="Improved or corrected clause text if needed, else empty string"
    )

class ContractAnalysisResult(BaseModel):
    clause_comparisons: List[ClauseComparison]
    missing_standard_clauses: List[str]
    overall_risk_summary: str