import uuid
import json
import shutil
from typing import Dict, List, TypedDict
from pathlib import Path
from threading import Thread

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import torch
import chromadb
from sentence_transformers import SentenceTransformer
from docling.document_converter import DocumentConverter
from fastapi.staticfiles import StaticFiles

import google.generativeai as genai
from langgraph.graph import StateGraph, START, END

GEMINI_API_KEY = API_KEY #INSERT API KEY HERE(GEMINI)

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-flash-latest"


def call_gemini(prompt: str):
    model = genai.GenerativeModel(MODEL_NAME)

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )

    return json.loads(response.text)


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device=DEVICE
)

chroma_client = chromadb.Client()
clause_collection = chroma_client.get_or_create_collection(
    name="legal_clauses"
)


class ContractState(TypedDict, total=False):
    legal_text: str
    agreement_type: str
    industry: str
    retrieved_clauses: List[dict]
    analysis: dict
    roles: List[dict]
    insights: List[dict]
    final_report: dict

def ingest_clauses():
    if not Path("clause.json").exists():
        return

    with open("clause.json", "r", encoding="utf-8") as f:
        clauses = json.load(f)

    documents, metadatas, ids = [], [], []

    for c in clauses:
        documents.append(c["clause_text"])
        ids.append(c["clause_id"])
        metadatas.append({
            "contract_type": c["contract_type"],
            "clause_title": c["clause_title"],
            "jurisdiction": c["jurisdiction"]
        })

    embeddings = embedding_model.encode(documents).tolist()

    clause_collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )


if clause_collection.count() == 0:
    ingest_clauses()


def classification_node(state: ContractState):
    prompt = f"""
Return ONLY valid JSON:
{{
  "agreement_type": "...",
  "industry": "..."
}}

Document:
{state["legal_text"]}
"""
    return call_gemini(prompt)


def retrieval_node(state: ContractState):
    embedding = embedding_model.encode(state["legal_text"]).tolist()

    results = clause_collection.query(
        query_embeddings=[embedding],
        n_results=3
    )

    retrieved = []

    if results["documents"]:
        for i in range(len(results["documents"][0])):
            retrieved.append({
                "clause_id": results["ids"][0][i],
                "clause_title": results["metadatas"][0][i]["clause_title"],
                "clause_text": results["documents"][0][i]
            })

    return {"retrieved_clauses": retrieved}


def analyze_contract_node(state: ContractState):
    prompt = f"""
Return JSON:
{{
  "differences": [],
  "suggested_improvements": [],
  "missing_clauses": []
}}

Document:
{state["legal_text"]}

Reference Clauses:
{json.dumps(state.get("retrieved_clauses", []))}
"""
    return {"analysis": call_gemini(prompt)}


def create_review_plan_node(state: ContractState):
    prompt = """
Create 3–5 specialized legal review roles.

Return JSON:
{
  "roles": [
    { "role": "", "focus": "" }
  ]
}
"""
    result = call_gemini(prompt)
    return {"roles": result.get("roles", [])}


def execute_step_node(state: ContractState):
    insights = []

    for role in state.get("roles", []):
        prompt = f"""
Return JSON:
{{
  "role": "{role["role"]}",
  "insight": "",
  "risks": [],
  "recommendations": []
}}

Contract:
{state["legal_text"]}
"""
        insights.append(call_gemini(prompt))

    return {"insights": insights}


def generate_final_report_node(state: ContractState):
    prompt = f"""
Return JSON:
{{
  "executive_summary": "",
  "key_risks": [],
  "role_highlights": [],
  "recommended_actions": [],
  "overall_risk_level": "Low | Medium | High"
}}

Analysis:
{json.dumps(state.get("analysis", {}))}

Insights:
{json.dumps(state.get("insights", []))}
"""
    return {"final_report": call_gemini(prompt)}


graph = StateGraph(ContractState)

graph.add_node("classification", classification_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("analysis", analyze_contract_node)
graph.add_node("roles", create_review_plan_node)
graph.add_node("insights", execute_step_node)
graph.add_node("final_report", generate_final_report_node)

graph.add_edge(START, "classification")
graph.add_edge("classification", "retrieval")
graph.add_edge("retrieval", "analysis")
graph.add_edge("analysis", "roles")
graph.add_edge("roles", "insights")
graph.add_edge("insights", "final_report")
graph.add_edge("final_report", END)

compiled_graph = graph.compile()


# =====================================================
# FASTAPI
# =====================================================

app = FastAPI(title="Legal Contract Analyzer - Gemini")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


TASKS: Dict[str, Dict] = {}


def process_contract(task_id: str, file_path: Path):
    try:
        converter = DocumentConverter()
        result = converter.convert(str(file_path))
        text = result.document.export_to_text()

        final_state = compiled_graph.invoke({
            "legal_text": text
        })

        report_path = REPORT_DIR / f"{task_id}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(final_state, f, indent=2)

        TASKS[task_id]["status"] = "completed"
        TASKS[task_id]["result"] = final_state

    except Exception as e:
        TASKS[task_id]["status"] = "failed"
        TASKS[task_id]["result"] = {"error": str(e)}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix
    saved_path = UPLOAD_DIR / f"{task_id}{ext}"

    with open(saved_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    TASKS[task_id] = {"status": "processing", "result": None}

    Thread(target=process_contract, args=(task_id, saved_path), daemon=True).start()

    return {"task_id": task_id}


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task ID not found")
    return task


@app.get("/download/{task_id}")
async def download_report(task_id: str):
    report_path = REPORT_DIR / f"{task_id}.json"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report_path, media_type="application/json")
