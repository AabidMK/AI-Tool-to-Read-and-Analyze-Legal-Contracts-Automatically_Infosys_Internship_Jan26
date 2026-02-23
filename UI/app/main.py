import os
from fastapi import FastAPI, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import Analysis, User
from .auth import router as auth_router, get_db
from .utils import hash_password, verify_password
from .analysis import run_analysis, extract_text
from .exporter import export_report
from .utils import get_current_user

secret = os.environ.get("LEGALAI_SECRET", "changeme-secret")
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=secret, session_cookie="legalai_session", https_only=False, max_age=60*60*8)
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

app.include_router(auth_router)
pwd_ctx = None

def db_dep():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return RedirectResponse("/dashboard")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return RedirectResponse("/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(db_dep)):
    total = db.query(Analysis).count()
    completed = db.query(Analysis).filter(Analysis.status == "Completed").count()
    high_risk = db.query(Analysis).filter(Analysis.risk_level == "High").count()
    recent = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(5).all()
    user = {"name": "Guest"}
    # This month count
    from datetime import datetime
    now = datetime.utcnow()
    this_month = db.query(Analysis).filter(Analysis.created_at >= datetime(now.year, now.month, 1)).count()
    # Distribution
    low = db.query(Analysis).filter(Analysis.risk_level == "Low").count()
    med = db.query(Analysis).filter(Analysis.risk_level == "Medium").count()
    hi = high_risk
    denom = total if total > 0 else 1
    dist = {
        "low": low, "medium": med, "high": hi,
        "low_pct": int(low * 100 / denom),
        "medium_pct": int(med * 100 / denom),
        "high_pct": int(hi * 100 / denom)
    }
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "total": total, "completed": completed, "high_risk": high_risk, "recent": recent, "this_month": this_month, "dist": dist})

@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    return templates.TemplateResponse("analyze.html", {"request": request, "user": {"name": "Guest"}})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_submit(request: Request, file: UploadFile = File(...), features: str = Form("full"), db: Session = Depends(db_dep)):
    content = await file.read()
    tmp_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(tmp_dir, exist_ok=True)
    path = os.path.join(tmp_dir, file.filename)
    with open(path, "wb") as f:
        f.write(content)
    text = await extract_text(path)
    analysis = Analysis(user_id=None, filename=file.filename, status="Analyzing", features=features)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    result = await run_analysis(text, features)
    analysis.summary = result["summary"]
    analysis.classification = result.get("classification_json", "")
    analysis.risk_assessment = result.get("risk_json", "")
    analysis.missing_clauses = result.get("missing_json", "")
    analysis.experts_review = result.get("experts_json", "")
    analysis.suggestions = result.get("suggestions_json", "")
    analysis.json_result = result["full_json"]
    analysis.status = "Completed"
    analysis.contract_type = result.get("contract_type", "-")
    analysis.risk_level = result.get("risk_level", "-")
    db.commit()
    return RedirectResponse(f"/results/{analysis.id}", status_code=303)

@app.get("/results/{analysis_id}", response_class=HTMLResponse)
async def results_page(analysis_id: int, request: Request, db: Session = Depends(db_dep)):
    a = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not a:
        return RedirectResponse("/history")
    import json
    cls = json.loads(a.classification) if a.classification else {}
    risk = json.loads(a.risk_assessment) if a.risk_assessment else {}
    miss = json.loads(a.missing_clauses) if a.missing_clauses else []
    exp = json.loads(a.experts_review) if a.experts_review else []
    sug = json.loads(a.suggestions) if a.suggestions else []
    return templates.TemplateResponse("results.html", {"request": request, "user": {"name":"Guest"}, "item": a, "cls": cls, "risk": risk, "miss": miss, "exp": exp, "sug": sug})

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, db: Session = Depends(db_dep)):
    items = db.query(Analysis).order_by(Analysis.created_at.desc()).all()
    return templates.TemplateResponse("history.html", {"request": request, "user": {"name":"Guest"}, "items": items})

@app.get("/export/{analysis_id}")
async def export(analysis_id: int, fmt: str, request: Request, db: Session = Depends(db_dep)):
    a = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not a:
        return RedirectResponse("/history")
    path = await export_report(a, fmt)
    filename = os.path.basename(path)
    media_type = "application/octet-stream"
    if fmt == "pdf":
        media_type = "application/pdf"
    elif fmt == "txt":
        media_type = "text/plain"
    elif fmt == "docx":
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt == "json":
        media_type = "application/json"
    return FileResponse(path, media_type=media_type, filename=filename)
