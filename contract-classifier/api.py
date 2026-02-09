from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import uuid
import json
from pathlib import Path
from datetime import datetime
from graph.classification_graph import build_graph
from parser.document_parser import parse_document
from retrieval import retrieve_similar_clauses

app = FastAPI(title="Contract Classifier API")

UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

tasks = {}

def generate_markdown_report(report: dict, task_id: str) -> str:
    md_path = RESULTS_DIR / f"{task_id}.md"
    
    with open(md_path, "w") as f:
        f.write("# Comprehensive Contract Review Report\n\n")
        
        summary = report.get('contract_summary', {})
        f.write("## Contract Summary\n\n")
        f.write(f"- **Contract Type:** {summary.get('type', 'Unknown')}\n")
        f.write(f"- **Industry:** {summary.get('industry', 'Unknown')}\n")
        f.write(f"- **Overall Risk Rating:** {summary.get('overall_risk_rating', 'Unknown')}\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write(f"{report.get('executive_summary', 'No summary available')}\n\n")
        
        missing_clauses = [clause for clause in report.get('clause_analysis', []) if not clause.get('present', True)]
        if missing_clauses:
            f.write("## Missing Clauses\n\n")
            for i, clause in enumerate(missing_clauses, 1):
                f.write(f"### {i}. {clause.get('clause_title', 'Unknown Clause')}\n\n")
                f.write(f"**Status:** Not Present\n\n")
                if clause.get('clause_text'):
                    f.write(f"**Recommended Text:**\n```\n{clause.get('clause_text')}\n```\n\n")
                metadata = clause.get('metadata', {})
                if metadata:
                    f.write(f"**Metadata:**\n")
                    f.write(f"- Jurisdiction: {metadata.get('jurisdiction', 'N/A')}\n")
                    f.write(f"- Version: {metadata.get('version', 'N/A')}\n")
                    f.write(f"- Last Updated: {metadata.get('last_updated', 'N/A')}\n\n")
        else:
            f.write("## Missing Clauses\n\n")
            f.write("✅ All recommended clauses are present in the contract.\n\n")
        
        f.write("## Expert Analyses\n\n")
        for i, analysis in enumerate(report.get('expert_analyses', []), 1):
            f.write(f"### {i}. {analysis.get('role', 'Unknown Role')}\n\n")
            f.write(f"**Rating:** {analysis.get('rating', 'No Rating')}\n\n")
            
            key_findings = analysis.get('key_findings', [])
            if key_findings:
                f.write("**Key Findings:**\n")
                for finding in key_findings:
                    f.write(f"- {finding}\n")
                f.write("\n")
            
            risks = analysis.get('risks', [])
            if risks:
                f.write("**Risks:**\n")
                for risk in risks:
                    f.write(f"- {risk}\n")
                f.write("\n")
            
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                f.write("**Recommendations:**\n")
                for rec in recommendations:
                    f.write(f"- {rec}\n")
                f.write("\n")
        
        findings = report.get('consolidated_findings', {})
        f.write("## Consolidated Findings\n\n")
        f.write(f"- **Total Risks Identified:** {findings.get('total_risks_identified', 0)}\n")
        f.write(f"- **Critical Compliance Issues:** {findings.get('critical_compliance_issues', 0)}\n")
        f.write(f"- **Key Recommendations:** {len(findings.get('key_recommendations', []))}\n\n")
        
        key_recs = findings.get('key_recommendations', [])
        if key_recs:
            f.write("### Top Recommendations\n\n")
            for i, rec in enumerate(key_recs, 1):
                f.write(f"{i}. {rec}\n")
    
    return str(md_path)

def process_contract(task_id: str, file_path: str):
    try:
        tasks[task_id]["status"] = "processing"
        
        contract_text = parse_document(file_path)
        contract_text_for_llm = contract_text[:12000]
        
        graph = build_graph()
        result = graph.invoke({"contract_text": contract_text_for_llm})
        
        classification = result["classification"]
        contract_type = classification.get("contract_type", "Unknown")
        
        retrieved_clauses = []
        if contract_type != "Unknown":
            query = f"clauses related to {contract_type}"
            retrieved_clauses = retrieve_similar_clauses(
                query=query,
                contract_type=contract_type,
                top_k=3
            )
        
        final_result = graph.invoke({
            "contract_text": contract_text_for_llm,
            "retrieved_clauses": retrieved_clauses
        })
        
        report = final_result.get("final_report", {})
        
        result_path = RESULTS_DIR / f"{task_id}.json"
        with open(result_path, "w") as f:
            json.dump(report, f, indent=2)
        
        md_path = generate_markdown_report(report, task_id)
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result_path"] = str(result_path)
        tasks[task_id]["md_path"] = md_path
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.post("/analyze")
async def analyze_contract(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    task_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    tasks[task_id] = {
        "task_id": task_id,
        "filename": file.filename,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "file_path": str(file_path)
    }
    
    background_tasks.add_task(process_contract, task_id, str(file_path))
    
    return {"task_id": task_id, "status": "queued"}

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] == "completed":
        result_path = Path(task["result_path"])
        with open(result_path, "r") as f:
            report = json.load(f)
        return {"task_id": task_id, "status": "completed", "report": report}
    
    return {"task_id": task_id, "status": task["status"], "error": task.get("error")}

@app.get("/download/{task_id}")
async def download_report(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Report not ready")
    
    md_path = Path(task["md_path"])
    return FileResponse(md_path, filename=f"contract_report_{task_id}.md", media_type="text/markdown")

@app.get("/health")
async def health():
    return {"status": "healthy"}
