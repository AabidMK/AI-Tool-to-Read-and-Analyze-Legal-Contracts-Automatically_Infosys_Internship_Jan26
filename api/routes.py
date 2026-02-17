import os
import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException

from api.storage import create_task, get_task
from api.tasks import run_contract_analysis
from api.schemas import AnalyzeResponse, ResultResponse

from fastapi.responses import FileResponse

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    task_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")

    # Save file
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    create_task(task_id)

    # Run LangGraph in background
    background_tasks.add_task(
        run_contract_analysis,
        task_id,
        file_path
    )

    return {
        "task_id": task_id,
        "status": "processing"
    }


@router.get("/result/{task_id}", response_model=ResultResponse)
def get_result(task_id: str):
    task = get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task_id,
        "status": task["status"],
        "report": task["report"],
        "error": task["error"],
    }

@router.get("/download/{task_id}")
def download_pdf(task_id: str):
    task = get_task(task_id)

    if not task or not task.get("pdf_path"):
        raise HTTPException(status_code=404, detail="PDF not found")

    if not os.path.exists(task["pdf_path"]):
        raise HTTPException(status_code=404, detail="PDF file missing on disk")

    return FileResponse(
        path=task["pdf_path"],
        filename=f"ClauseAI_Report_{task_id}.pdf",
        media_type="application/pdf"
    )