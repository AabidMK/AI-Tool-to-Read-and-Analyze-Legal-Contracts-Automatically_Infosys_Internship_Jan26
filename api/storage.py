from typing import Dict

TASK_STORE: Dict[str, dict] = {}


def create_task(task_id: str):
    TASK_STORE[task_id] = {
        "status": "processing",
        "report": None,
        "error": None,
        "pdf_path": None
    }


def complete_task(task_id: str, report: str, pdf_path: str):
    TASK_STORE[task_id]["status"] = "completed"
    TASK_STORE[task_id]["report"] = report
    TASK_STORE[task_id]["pdf_path"] = pdf_path


def fail_task(task_id: str, error: str):
    TASK_STORE[task_id]["status"] = "failed"
    TASK_STORE[task_id]["error"] = error


def get_task(task_id: str):
    return TASK_STORE.get(task_id)
