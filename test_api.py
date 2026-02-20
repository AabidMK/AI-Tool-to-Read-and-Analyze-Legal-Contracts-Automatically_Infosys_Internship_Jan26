import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app import background_tasks, routes, storage


def test_home_page_renders():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "ClauseAI" in response.text
    assert "Analyze Document" in response.text
    assert "Download PDF" in response.text
    assert "Current Stage" in response.text
    assert "Fast mode (skip expert review)" in response.text


def test_analyze_creates_task_and_saves_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(storage, "OUTPUT_DIR", tmp_path / "outputs")
    monkeypatch.setattr(storage, "TASKS_PATH", tmp_path / "tasks.json")

    captured = {}

    def fake_background(task_id, file_path, include_review):
        captured["task_id"] = task_id
        captured["file_path"] = file_path
        captured["include_review"] = include_review

    monkeypatch.setattr(background_tasks, "execute_clause_analysis_task", fake_background)
    monkeypatch.setattr(routes, "execute_clause_analysis_task", fake_background)

    client = TestClient(app)
    response = client.post(
        "/analyze",
        files={"file": ("contract.docx", b"hello", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == storage.TaskStatus.QUEUED
    task_id = payload["task_id"]

    tasks = json.loads((tmp_path / "tasks.json").read_text(encoding="utf-8"))
    assert task_id in tasks
    assert tasks[task_id]["status"] == storage.TaskStatus.QUEUED
    assert tasks[task_id]["stage"] == "Queued"

    saved_file = Path(tasks[task_id]["file_path"])
    assert saved_file.exists()
    assert saved_file.read_bytes() == b"hello"

    assert captured["task_id"] == task_id
    assert Path(captured["file_path"]) == saved_file
    assert captured["include_review"] is False


def test_result_returns_report_for_completed_task(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(storage, "OUTPUT_DIR", tmp_path / "outputs")
    monkeypatch.setattr(storage, "TASKS_PATH", tmp_path / "tasks.json")

    storage.ensure_storage()

    report_path = tmp_path / "outputs" / "abc.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("final report", encoding="utf-8")

    storage.write_tasks(
        {
            "abc": {
                "task_id": "abc",
                "status": storage.TaskStatus.COMPLETED,
                "stage": "Completed",
                "file_path": "data/uploads/abc_contract.pdf",
                "result_path": str(report_path),
                "error": None,
                "created_at": "now",
                "updated_at": "now",
            }
        }
    )

    client = TestClient(app)
    response = client.get("/result/abc")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == storage.TaskStatus.COMPLETED
    assert payload["report"] == "final report"
    assert payload["stage"] == "Completed"
    assert payload["result_path"] == str(report_path)


def test_result_pdf_download_for_completed_task(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(storage, "OUTPUT_DIR", tmp_path / "outputs")
    monkeypatch.setattr(storage, "TASKS_PATH", tmp_path / "tasks.json")

    storage.ensure_storage()

    report_path = tmp_path / "outputs" / "xyz.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("hello from report", encoding="utf-8")

    storage.write_tasks(
        {
            "xyz": {
                "task_id": "xyz",
                "status": storage.TaskStatus.COMPLETED,
                "stage": "Completed",
                "file_path": "data/uploads/xyz_contract.pdf",
                "result_path": str(report_path),
                "error": None,
                "created_at": "now",
                "updated_at": "now",
            }
        }
    )

    client = TestClient(app)
    response = client.get("/result/xyz/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "attachment; filename=\"xyz_report.pdf\"" == response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


if __name__ == "__main__":
    try:
        import pytest
    except ModuleNotFoundError:
        print("pytest is required to run this test module directly.")
        raise SystemExit(1)

    raise SystemExit(pytest.main(["-q", "--disable-warnings", "-p", "no:warnings", __file__]))