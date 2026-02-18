from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import shutil
import os
import re

from role import build_contract_graph

app = FastAPI()
graph = build_contract_graph()

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

templates = Jinja2Templates(directory="templates")


# -------------------------
# CLEAN & FORMAT TEXT
# -------------------------
def format_for_html(text: str):
    if not text:
        return "No report generated."

    # Remove markdown headings
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # Convert new lines to HTML breaks
    text = text.replace("\n", "<br/>")

    return text.strip()


def format_for_pdf(text: str):
    if not text:
        return "No report generated."

    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    return text.strip()


# -------------------------
# FRONTEND PAGE
# -------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -------------------------
# FILE UPLOAD + ANALYSIS
# -------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = graph.invoke({
            "file_path": file_path,
            "contract_text": None,
            "raw_output": None,
            "contract_type": None,
            "industry": None,
            "retrieved_clauses": None,
            "analysis_result": None,
            "review_plan": None,
            "role_reviews": None,
            "final_report": None,
        })

        report = format_for_html(result["final_report"])

    except Exception as e:
        report = "Error generating report. Check model or quota."

    return {"report": report}


# -------------------------
# PDF DOWNLOAD
# -------------------------
@app.post("/download-pdf")
async def download_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = graph.invoke({
            "file_path": file_path,
            "contract_text": None,
            "raw_output": None,
            "contract_type": None,
            "industry": None,
            "retrieved_clauses": None,
            "analysis_result": None,
            "review_plan": None,
            "role_reviews": None,
            "final_report": None,
        })

        report_text = format_for_pdf(result["final_report"])

    except Exception:
        report_text = "Error generating report."

    pdf_path = "contract_report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>Contract Review Report</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    # Preserve paragraphs
    for para in report_text.split("\n\n"):
        story.append(Paragraph(para.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 12))

    doc.build(story)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="Contract_Report.pdf"
    )
