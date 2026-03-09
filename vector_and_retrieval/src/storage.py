import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

UPLOAD_DIR = PROJECT_ROOT / "uploads"
RESULT_DIR = PROJECT_ROOT / "results"

UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)


def save_task_metadata(task_id, filename):

    meta = {
        "task_id": task_id,
        "filename": filename,
        "status": "processing"
    }

    path = RESULT_DIR / f"{task_id}.json"

    with open(path, "w") as f:
        json.dump(meta, f)


def save_result(task_id, report):

    path = RESULT_DIR / f"{task_id}.json"

    with open(path, "r") as f:
        meta = json.load(f)

    meta["status"] = "completed"
    meta["report"] = report

    with open(path, "w") as f:
        json.dump(meta, f)


def get_result(task_id):

    path = RESULT_DIR / f"{task_id}.json"

    if not path.exists():
        return None

    with open(path) as f:
        return json.load(f)