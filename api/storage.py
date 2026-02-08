from typing import Dict

TASK_STORE: Dict[str, dict] = {}


def create_task(task_id: str, filename: str):
    TASK_STORE[task_id] = {
        "status": "processing",
        "filename": filename,
        "report": None,
        "error": None,
    }


def complete_task(task_id: str, report: str):
    TASK_STORE[task_id]["status"] = "completed"
    TASK_STORE[task_id]["report"] = report


def fail_task(task_id: str, error: str):
    TASK_STORE[task_id]["status"] = "failed"
    TASK_STORE[task_id]["error"] = error


def get_task(task_id: str):
    return TASK_STORE.get(task_id)
