import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

DATA_DIR = Path("data")
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
TASKS_PATH = DATA_DIR / "tasks.json"

_STORE_LOCK = Lock()


class TaskStatus:
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not TASKS_PATH.exists():
        TASKS_PATH.write_text("{}", encoding="utf-8")


def read_tasks() -> dict[str, dict[str, Any]]:
    ensure_storage()

    with TASKS_PATH.open("r", encoding="utf-8") as file_handle:
        try:
            data = json.load(file_handle)
        except json.JSONDecodeError:
            return {}

    return data if isinstance(data, dict) else {}


def write_tasks(tasks: dict[str, dict[str, Any]]) -> None:
    ensure_storage()
    TASKS_PATH.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def save_task(task_id: str, payload: dict[str, Any]) -> None:
    with _STORE_LOCK:
        tasks = read_tasks()
        tasks[task_id] = payload
        write_tasks(tasks)


def update_task(task_id: str, **fields: Any) -> None:
    with _STORE_LOCK:
        tasks = read_tasks()
        if task_id not in tasks:
            return

        tasks[task_id].update(fields)
        tasks[task_id]["updated_at"] = utc_now()
        write_tasks(tasks)