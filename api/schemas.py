from pydantic import BaseModel
from typing import Optional


class AnalyzeResponse(BaseModel):
    task_id: str
    status: str


class ResultResponse(BaseModel):
    task_id: str
    status: str
    report: Optional[str] = None
    error: Optional[str] = None
