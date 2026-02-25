from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from enum import Enum
from pathlib import Path
import uuid
import json
from fastapi.middleware.cors import CORSMiddleware

from graph.graph_builder import build_graph  

app = FastAPI(title="AI legal contract analyzer", version="1.0")


# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = Path("inputs")
RESULT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

graph = build_graph()

# Models
class StatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class AnalyzeResponse(BaseModel):
    task_id: str
    status: StatusEnum
    message: str


class StatusResponse(BaseModel):
    task_id: str
    status: StatusEnum
    contract_type: str | None = None
    industry: str | None = None
    error: str | None = None



# Background Task

def run_clause_analysis(task_id: str, file_path: str):
    metadata_path = RESULT_DIR / f"{task_id}.json"

    try:
        # Update status → processing
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        metadata["status"] = StatusEnum.processing
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        # Initial LangGraph state
        initial_state = {
            "file_path": file_path,
            
        }

        result = graph.invoke(initial_state)

        # Save final report
        report_path = RESULT_DIR / f"{task_id}_report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(result["final_report_text"])

        # Update metadata → completed
        metadata.update({
            "status": StatusEnum.completed,
            "contract_type": result.get("contract_type"),
            "industry": result.get("industry")
        })

        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

    except Exception as e:
        metadata["status"] = StatusEnum.failed
        metadata["error"] = str(e)
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)



# API Endpoints

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, "Only PDF or DOCX files allowed")

    task_id = str(uuid.uuid4())[:8]
    file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    metadata = {
        "task_id": task_id,
        "file_name": file.filename,
        "status": StatusEnum.pending,
        "contract_type": None,
        "industry": None,
        "error": None
    }

    with open(RESULT_DIR / f"{task_id}.json", "w") as f:
        json.dump(metadata, f)

    background_tasks.add_task(run_clause_analysis, task_id, str(file_path))

    return AnalyzeResponse(
        task_id=task_id,
        status=StatusEnum.pending,
        message="Analysis started"
    )


@app.get("/status/{task_id}", response_model=StatusResponse)
def get_status(task_id: str):
    metadata_path = RESULT_DIR / f"{task_id}.json"
    if not metadata_path.exists():
        raise HTTPException(404, "Task not found")

    with open(metadata_path) as f:
        return json.load(f)


@app.get("/result/{task_id}")
def get_result(task_id: str):
    report_path = RESULT_DIR / f"{task_id}_report.txt"
    if not report_path.exists():
        raise HTTPException(404, "Report not ready")

    return FileResponse(report_path, media_type="text/plain")


@app.get("/health")
def health():
    return {"status": "healthy"}
