from typing import Literal, Optional

from pydantic import BaseModel


TaskState = Literal["queued", "processing", "completed", "failed"]


class AnalyzeResponse(BaseModel):
    task_id: str
    status: TaskState


class ResultResponse(BaseModel):
    task_id: str
    status: TaskState
    file_path: str
    stage: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    result_path: Optional[str] = None
    report: Optional[str] = None