import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import HTMLResponse

from .background_tasks import execute_clause_analysis_task
from .pdf_utils import build_report_pdf
from .schemas import AnalyzeResponse, ResultResponse
from .storage import (
    TaskStatus,
    UPLOAD_DIR,
    ensure_storage,
    read_tasks,
    save_task,
    utc_now,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>ClauseAI</title>
  <style>
    :root {
      --bg: #0b1020;
      --panel: #141b2f;
      --text: #d7def7;
      --muted: #93a0cb;
      --accent: #8b9cff;
      --accent-2: #6f86ff;
      --ok: #30d19a;
      --warn: #ffd479;
      --danger: #ff6d6d;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      color: var(--text);
      background: radial-gradient(1200px 600px at 85% -10%, #23376c33, transparent), var(--bg);
      display: grid;
      place-items: center;
      padding: 24px;
    }
    .shell {
      width: min(980px, 100%);
      background: linear-gradient(160deg, #121930, #0f1528);
      border: 1px solid #2a365f;
      border-radius: 18px;
      padding: 28px;
      box-shadow: 0 20px 40px #00000066;
    }
    h1 { margin: 0 0 6px; font-size: 2rem; letter-spacing: .4px; }
    .sub { margin: 0 0 22px; color: var(--muted); }
    .controls { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 18px; }
    input[type=file] {
      background: var(--panel);
      border: 1px solid #2b3762;
      border-radius: 10px;
      color: var(--text);
      padding: 10px;
      flex: 1;
      min-width: 280px;
    }
    button, .download {
      border: 0;
      background: linear-gradient(180deg, var(--accent), var(--accent-2));
      color: white;
      padding: 11px 16px;
      border-radius: 10px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
    }
    .meta {
      background: var(--panel);
      border: 1px solid #27345d;
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 16px;
      color: var(--muted);
      display: grid;
      gap: 8px;
    }
    .status-ok { color: var(--ok); }
    .status-warn { color: var(--warn); }
    .status-failed { color: var(--danger); }
    .report {
      background: #0d1326;
      border: 1px solid #25335e;
      border-radius: 12px;
      padding: 14px;
      min-height: 280px;
      white-space: pre-wrap;
      line-height: 1.45;
    }
    .actions { margin-top: 12px; display: flex; gap: 10px; }
  </style>
</head>
<body>
  <main class=\"shell\">
    <h1>ClauseAI</h1>
    <p class=\"sub\">Upload a contract, track analysis status, and download the final report as PDF.</p>

    <div class=\"controls\">
      <input type=\"file\" id=\"fileInput\" />
      <label style=\"display:flex;align-items:center;gap:8px;color:var(--muted);font-size:.95rem;\">
        <input type=\"checkbox\" id=\"fastMode\" checked />
        Fast mode (skip expert review)
      </label>
      <button id=\"uploadBtn\">Analyze Document</button>
    </div>

    <section class=\"meta\">
      <div><strong>Task ID:</strong> <span id=\"taskId\">-</span></div>
      <div><strong>Status:</strong> <span id=\"statusText\">Idle</span></div>
      <div><strong>Current Stage:</strong> <span id=\"stageText\">-</span></div>
    </section>

    <section>
      <h3>Report Preview</h3>
      <pre id=\"reportBox\" class=\"report\">No report yet.</pre>
      <div class=\"actions\">
        <a id=\"downloadPdf\" class=\"download\" style=\"display:none\" target=\"_blank\">Download PDF</a>
      </div>
    </section>
  </main>

  <script>
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const statusText = document.getElementById('statusText');
    const stageText = document.getElementById('stageText');
    const taskIdText = document.getElementById('taskId');
    const reportBox = document.getElementById('reportBox');
    const downloadPdf = document.getElementById('downloadPdf');
    const fastMode = document.getElementById('fastMode');

    const POLL_INTERVAL_MS = 1800;
    const MAX_POLL_MS = 12 * 60 * 1000;
    let pollTimer = null;
    let pollStartedAt = null;

    function stopPolling() {
      if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
    }

    function setStatus(text, kind = 'normal') {
      statusText.textContent = text;
      statusText.className =
        kind === 'ok'
          ? 'status-ok'
          : kind === 'warn'
          ? 'status-warn'
          : kind === 'failed'
          ? 'status-failed'
          : '';
    }

    async function fetchResult(taskId) {
      const response = await fetch(`/result/${taskId}?t=${Date.now()}`);
      if (!response.ok) {
        throw new Error(`Status API returned ${response.status}`);
      }
      return response.json();
    }

    function startPolling(taskId) {
      stopPolling();
      pollStartedAt = Date.now();

      pollTimer = setInterval(async () => {
        const elapsed = Date.now() - pollStartedAt;
        if (elapsed > MAX_POLL_MS) {
          setStatus('Still processing (long-running). You can keep waiting or refresh and check later.', 'warn');
          stopPolling();
          return;
        }

        try {
          const data = await fetchResult(taskId);
          setStatus(data.status);
          stageText.textContent = data.stage || '-';

          if (data.status === 'completed') {
            reportBox.textContent = data.report || 'Completed, but no report found.';
            downloadPdf.href = `/result/${taskId}/pdf`;
            downloadPdf.style.display = 'inline-block';
            setStatus('completed', 'ok');
            stopPolling();
          }

          if (data.status === 'failed') {
            reportBox.textContent = `Failed: ${data.error || 'Unknown error'}`;
            setStatus('failed', 'failed');
            downloadPdf.style.display = 'none';
            stopPolling();
          }
        } catch (error) {
          setStatus('Temporary network issue while polling. Retrying...', 'warn');
          stageText.textContent = '-';
        }
      }, POLL_INTERVAL_MS);
    }

    uploadBtn.addEventListener('click', async () => {
      const file = fileInput.files[0];
      if (!file) {
        setStatus('Please choose a file first.', 'failed');
        return;
      }

      stopPolling();
      const formData = new FormData();
      formData.append('file', file);
      formData.append('fast_mode', String(fastMode.checked));

      setStatus('uploading...');
      stageText.textContent = 'Queued';
      reportBox.textContent = 'Waiting for analysis report...';
      downloadPdf.style.display = 'none';

      try {
        const response = await fetch('/analyze', { method: 'POST', body: formData });
        if (!response.ok) {
          throw new Error(`Analyze API returned ${response.status}`);
        }

        const data = await response.json();
        taskIdText.textContent = data.task_id;
        setStatus(data.status);
        stageText.textContent = 'Queued';
        startPolling(data.task_id);
      } catch (error) {
        setStatus('Upload failed. Please try again.', 'failed');
        stageText.textContent = '-';
        reportBox.textContent = String(error);
      }
    });
  </script>
</body>
</html>
"""


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    fast_mode: bool = Form(True),
) -> AnalyzeResponse:
    ensure_storage()

    if not file.filename:
        raise HTTPException(status_code=400, detail="File must include a filename.")

    task_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{task_id}_{Path(file.filename).name}"

    with file_path.open("wb") as file_buffer:
        shutil.copyfileobj(file.file, file_buffer)

    save_task(
        task_id,
        {
            "task_id": task_id,
            "status": TaskStatus.QUEUED,
            "stage": "Queued",
            "mode": "fast" if fast_mode else "full",
            "file_path": str(file_path),
            "result_path": None,
            "error": None,
            "created_at": utc_now(),
            "updated_at": utc_now(),
        },
    )

    include_review = not fast_mode
    background_tasks.add_task(execute_clause_analysis_task, task_id, file_path, include_review)

    return AnalyzeResponse(task_id=task_id, status=TaskStatus.QUEUED)


@router.get("/result/{task_id}", response_model=ResultResponse)
def get_result(task_id: str) -> ResultResponse:
    tasks = read_tasks()
    task = tasks.get(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    response = {
        "task_id": task_id,
        "status": task["status"],
        "stage": task.get("stage"),
        "file_path": task["file_path"],
        "error": task.get("error"),
        "created_at": task.get("created_at"),
        "updated_at": task.get("updated_at"),
        "result_path": None,
        "report": None,
    }

    if task["status"] == TaskStatus.COMPLETED and task.get("result_path"):
        report_path = Path(task["result_path"])
        response["result_path"] = str(report_path)
        response["report"] = report_path.read_text(encoding="utf-8")

    return ResultResponse(**response)


@router.get("/result/{task_id}/pdf")
def download_result_pdf(task_id: str) -> Response:
    tasks = read_tasks()
    task = tasks.get(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.get("status") != TaskStatus.COMPLETED or not task.get("result_path"):
        raise HTTPException(status_code=409, detail="Report is not ready yet")

    report_path = Path(task["result_path"])
    report_text = report_path.read_text(encoding="utf-8")
    pdf_bytes = build_report_pdf(title="ClauseAI Report", report_text=report_text)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{task_id}_report.pdf"'},
    )