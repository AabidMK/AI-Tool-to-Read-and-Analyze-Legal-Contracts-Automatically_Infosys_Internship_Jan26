import uuid
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from pathlib import Path

from src.graph import app as contract_graph
from src.storage import save_task_metadata, save_result, get_result, UPLOAD_DIR

from fastapi.staticfiles import StaticFiles

app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")

app = FastAPI()


# ---------------------------
# Background Processing
# ---------------------------
def process_contract(task_id, file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        document_text = f.read()

    result = contract_graph.invoke({
        "document_text": document_text,
        "contract_type": "Service Agreement",
        "industry": "Technology"
    })

    report = result["final_report"]

    save_result(task_id, report)


# ---------------------------
# Upload & Analyze Endpoint
# ---------------------------
@app.post("/analyze")
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    task_id = str(uuid.uuid4())

    file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    save_task_metadata(task_id, file.filename)

    background_tasks.add_task(
        process_contract,
        task_id,
        file_path
    )

    return {
        "task_id": task_id,
        "status": "processing"
    }


# ---------------------------
# Get Result Endpoint
# ---------------------------
@app.get("/result/{task_id}")
def get_analysis_result(task_id: str):

    result = get_result(task_id)

    if not result:
        return {"error": "task not found"}

    return result