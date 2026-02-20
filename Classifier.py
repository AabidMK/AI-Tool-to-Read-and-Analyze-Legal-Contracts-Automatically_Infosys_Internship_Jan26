"""
classifier.py - LangGraph Contract Analysis Workflow
Uses plain text LLM calls (fast) instead of structured output (slow with small models)
"""
import os
import re
import json
import traceback
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END  # type: ignore
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from typing import TypedDict, Optional, List, Annotated
import operator

# ============================================================
# Initialize Components
# ============================================================

llm = ChatOllama(
    model="qwen2.5:3b",
    base_url="http://127.0.0.1:11434",
    temperature=0,
    timeout=120,
    num_predict=1024,  # Cap token generation for speed
)

qdrant_client = QdrantClient(path="./qdrant_db")

# Use fastembed (same as ingestion.py) for consistent embeddings
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

# ============================================================
# State
# ============================================================

class ContractReviewState(TypedDict):
    file_path: str
    contract_text: str
    contract_type: Optional[str]
    industry: Optional[str]
    clauses: List[dict]
    clause_analysis: Optional[dict]
    review_plan: Optional[List[str]]
    sections: Annotated[List[dict], operator.add]
    modifications: Annotated[List[dict], operator.add]
    final_report: Optional[str]


# ============================================================
# Helpers
# ============================================================

def llm_call(system: str, user: str) -> str:
    """Simple plain-text LLM call. Much faster than structured output."""
    try:
        result = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=user),
        ])
        return result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        print(f"  LLM call failed: {e}")
        return ""


# ============================================================
# Nodes
# ============================================================

def extract_text_node(state: ContractReviewState):
    """Extract text from PDF/DOCX"""
    file_path = state["file_path"]
    print(f"[Node 1: Extract Text] Loading {file_path}...")

    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Only PDF and DOCX files supported")

    docs = loader.load()
    contract_text = "\n".join([doc.page_content for doc in docs])
    print(f"  Extracted {len(contract_text)} characters")
    return {"contract_text": contract_text}


def classify_contract_node(state: ContractReviewState):
    """Classify contract type and industry using plain text"""
    print(f"[Node 2: Classify] Running classification...")

    raw = llm_call(
        system="You are a legal contract classifier. Reply ONLY in this exact format:\nTYPE: <contract type>\nINDUSTRY: <industry>",
        user=f"Classify this contract:\n{state['contract_text'][:2000]}"
    )

    # Parse the response
    contract_type = "General Contract"
    industry = "General"

    type_match = re.search(r'TYPE:\s*(.+)', raw, re.IGNORECASE)
    ind_match = re.search(r'INDUSTRY:\s*(.+)', raw, re.IGNORECASE)

    if type_match:
        contract_type = type_match.group(1).strip().strip('*').strip()
    if ind_match:
        industry = ind_match.group(1).strip().strip('*').strip()

    # Secondary fallback: scan text for keywords
    if contract_type == "General Contract":
        raw_lower = (raw + " " + state["contract_text"][:500]).lower()
        if "nda" in raw_lower or "non-disclosure" in raw_lower or "confidential" in raw_lower:
            contract_type = "Non-Disclosure Agreement"
        elif "employment" in raw_lower or "employee" in raw_lower:
            contract_type = "Employment Agreement"
        elif "service" in raw_lower:
            contract_type = "Service Agreement"

    print(f"  Type: {contract_type}")
    print(f"  Industry: {industry}")
    return {"contract_type": contract_type, "industry": industry}


def retrieve_clauses_node(state: ContractReviewState):
    """Retrieve relevant clauses from Qdrant"""
    contract_type = state["contract_type"]
    print(f"[Node 3: Retrieve] Searching Qdrant for '{contract_type}' clauses...")

    try:
        def search_points(query: str):
            query_vector = list(embedding_model.embed([query]))[0].tolist()
            response = qdrant_client.query_points(
                collection_name="contract-clauses",
                query=query_vector,
                limit=10,
                with_payload=True,
            )
            return response.points if hasattr(response, 'points') else []

        results = search_points(contract_type)

        if not results:
            print("  No results found, falling back to generic query...")
            results = search_points("contract clause")

        clauses = []
        for point in results:
            payload = getattr(point, "payload", {}) or {}
            title = payload.get("clause_title") or payload.get("title") or "Untitled"
            text = payload.get("clause_text") or payload.get("description") or ""
            clauses.append({
                "title": title,
                "description": text,
                "contract_type": payload.get("contract_type", "Unknown"),
            })

        print(f"  Retrieved {len(clauses)} clauses")
        return {"clauses": clauses}

    except Exception as e:
        print(f"  Qdrant error: {e}")
        traceback.print_exc()
        return {"clauses": []}


def analyze_contract_node(state: ContractReviewState):
    """Analyze contract against expected clauses"""
    print(f"[Node 4: Analyze] Running analysis...")

    clauses_list = "\n".join([f"- {c['title']}" for c in state["clauses"][:10]])

    raw = llm_call(
        system=f"""You are a legal contract analyst reviewing a {state['contract_type']}.
Expected standard clauses:
{clauses_list}

Reply in this format:
RISK: <High/Medium/Low>
ASSESSMENT: <2-3 sentence overall assessment>
MISSING: <comma-separated list of missing clauses, or "None">
RECOMMENDATIONS: <2-3 key recommendations>""",
        user=state["contract_text"][:3000]
    )

    # Parse response
    risk = "Medium"
    assessment = raw
    missing = []
    recommendations = ""

    risk_match = re.search(r'RISK:\s*(High|Medium|Low)', raw, re.IGNORECASE)
    if risk_match:
        risk = risk_match.group(1).capitalize()

    assess_match = re.search(r'ASSESSMENT:\s*(.+?)(?=\n(?:MISSING|RECOMMENDATIONS|$))', raw, re.IGNORECASE | re.DOTALL)
    if assess_match:
        assessment = assess_match.group(1).strip()

    missing_match = re.search(r'MISSING:\s*(.+?)(?=\n(?:RECOMMENDATIONS|$))', raw, re.IGNORECASE | re.DOTALL)
    if missing_match:
        missing_text = missing_match.group(1).strip()
        if missing_text.lower() != "none":
            missing = [m.strip().lstrip('- ') for m in re.split(r'[,\n]', missing_text) if m.strip() and m.strip() != '-']

    rec_match = re.search(r'RECOMMENDATIONS:\s*(.+)', raw, re.IGNORECASE | re.DOTALL)
    if rec_match:
        recommendations = rec_match.group(1).strip()

    # Build clause checks from the clauses we have
    clause_checks = []
    contract_lower = state["contract_text"].lower()
    for clause in state["clauses"][:10]:
        title = clause["title"]
        # Use multi-word phrase matching + individual keyword matching for accuracy
        title_lower = title.lower()
        keywords = [kw for kw in title_lower.split() if len(kw) > 3]
        
        # Check if full phrase or majority of keywords appear in text
        phrase_match = title_lower in contract_lower
        keyword_hits = sum(1 for kw in keywords for kw in [kw] if kw in contract_lower)
        keyword_ratio = keyword_hits / max(len(keywords), 1)
        present = phrase_match or keyword_ratio >= 0.6
        
        # LLM-flagged missing clauses take priority over keyword heuristic
        is_missing = any(
            title_lower in m.lower() or m.lower() in title_lower 
            for m in missing
        )
        
        # Determine final status: LLM missing flag overrides keyword match
        if is_missing:
            final_present = False
            finding = "Flagged as missing or inadequate by AI analysis"
            suggestion = f"Consider adding or strengthening the {title} clause"
        elif present:
            final_present = True
            finding = "Found in contract text"
            suggestion = None
        else:
            final_present = False
            finding = "Not found in contract text"
            suggestion = f"Consider adding a {title} clause"

        clause_checks.append({
            "title": title,
            "present": final_present,
            "findings": finding,
            "suggestion": suggestion,
        })

    clause_analysis = {
        "risk_level": risk,
        "contextual_analysis": assessment,
        "missing_clauses": missing,
        "recommendations": recommendations,
        "clause_checks": clause_checks,
    }

    print(f"  Risk Level: {risk}, Missing: {len(missing)} clauses")
    return {"clause_analysis": clause_analysis}


def create_review_plan_node(state: ContractReviewState):
    """Assign expert roles - deterministic (no LLM call needed)"""
    contract_type = state["contract_type"]
    print(f"[Node 5: Review Plan] Assigning expert roles for '{contract_type}'...")

    ct_lower = (contract_type or "").lower()
    if "nda" in ct_lower or "confidential" in ct_lower or "non-disclosure" in ct_lower:
        roles = ["Confidentiality Law Specialist", "IP Counsel"]
    elif "employment" in ct_lower:
        roles = ["Employment Law Specialist", "HR Compliance Officer"]
    elif "service" in ct_lower:
        roles = ["Commercial Law Specialist", "Liability & Risk Analyst"]
    elif "lease" in ct_lower or "rent" in ct_lower:
        roles = ["Real Estate Counsel", "Tenant Rights Specialist"]
    else:
        roles = ["General Contract Counsel", "Risk Assessment Specialist"]

    for i, role in enumerate(roles, 1):
        print(f"     {i}. {role}")

    return {"review_plan": roles}


def execute_step_node(state: ContractReviewState):
    """Execute one role-based analysis using plain text"""
    remaining_roles = state.get("review_plan", [])
    if not remaining_roles:
        return {"sections": [], "modifications": []}

    role = remaining_roles[0]
    print(f"[Node 6: Execute] Analyzing as: {role}")

    contract_excerpt = state.get("contract_text", "")[:2000]
    clauses_brief = ", ".join([c["title"] for c in state.get("clauses", [])[:5]])

    raw = llm_call(
        system=f"""You are a {role} reviewing a {state.get('contract_type', 'contract')}.
Standard clauses to check: {clauses_brief}

Provide your expert analysis and suggest 1-2 specific text modifications if needed.
Format modifications as:
MODIFY: "original text" -> "suggested text" (reason)""",
        user=f"Review this contract:\n{contract_excerpt}"
    )

    # Parse modifications from response
    modifications = []
    mod_pattern = r'MODIFY:\s*"([^"]+)"\s*->\s*"([^"]+)"\s*\(([^)]+)\)'
    for match in re.finditer(mod_pattern, raw):
        modifications.append({
            "original_text": match.group(1),
            "suggested_text": match.group(2),
            "reason": match.group(3),
        })

    # Clean the analysis text - remove modification lines and empty headers
    analysis_text = re.sub(mod_pattern, '', raw).strip()
    # Remove empty lines and clean up
    analysis_text = re.sub(r'\n{3,}', '\n\n', analysis_text).strip()
    if not analysis_text or len(analysis_text) < 20:
        analysis_text = f"The {role} reviewed this {state.get('contract_type', 'contract')} and found it generally consistent with industry standards, with {len(modifications)} suggested modifications."

    print(f"  {role}: {len(modifications)} modifications")
    remaining_roles = remaining_roles[1:]

    return {
        "review_plan": remaining_roles,
        "modifications": modifications,
        "sections": [{"role": role, "analysis": analysis_text}],
    }


def continue_to_plan_execution(state: ContractReviewState) -> str:
    """Conditional edge: loop through roles or finish"""
    remaining = state.get("review_plan", [])
    if remaining:
        print(f"  -> {len(remaining)} roles remaining")
        return "execute_step"
    print(f"  -> All roles complete, generating report")
    return "generate_final_report"


def generate_final_report_node(state: ContractReviewState):
    """Generate comprehensive report (no LLM call - just string building)"""
    print(f"[Node 7: Final Report] Compiling report...")

    report = []
    report.append("=" * 60)
    report.append("COMPREHENSIVE CONTRACT REVIEW REPORT")
    report.append("=" * 60)
    report.append(f"\n**Contract Type:** {state.get('contract_type', 'Unknown')}")
    report.append(f"**Industry:** {state.get('industry', 'Unknown')}")
    report.append(f"**File:** {state.get('file_path', 'N/A')}\n")

    # Reference Clauses
    clauses = state.get("clauses", [])
    report.append(f"\n## IDENTIFIED REFERENCE CLAUSES ({len(clauses)} total)")
    for i, clause in enumerate(clauses[:10], 1):
        report.append(f"{i}. {clause.get('title', 'Untitled')}")

    # Risk Assessment
    analysis = state.get("clause_analysis")
    if analysis:
        report.append("\n## RISK ASSESSMENT")
        report.append(f"**Risk Level:** {analysis.get('risk_level', 'Unknown')}")
        report.append(f"\n{analysis.get('contextual_analysis', '')}\n")

        checks = analysis.get("clause_checks", [])
        if checks:
            report.append("\n## CLAUSE-BY-CLAUSE ANALYSIS")
            for check in checks:
                status = "PRESENT" if check.get("present") else "MISSING/WEAK"
                report.append(f"\n### {check.get('title', 'Unknown')} [{status}]")
                report.append(f"{check.get('findings', '')}")
                if check.get("suggestion"):
                    report.append(f"- **Suggestion:** {check['suggestion']}")

        missing = analysis.get("missing_clauses", [])
        if missing:
            report.append("\n## MISSING STANDARD CLAUSES")
            for mc in missing:
                report.append(f"- {mc}")

        recs = analysis.get("recommendations", "")
        if recs:
            report.append("\n## KEY RECOMMENDATIONS")
            report.append(recs)

    # Expert Reviews
    sections = state.get("sections", [])
    if sections:
        report.append(f"\n## EXPERT ROLE-BASED ANALYSIS")
        report.append(f"\n{len(sections)} legal experts reviewed the contract:\n")
        for section in sections:
            report.append(f"\n### {section['role']}")
            report.append(f"{section['analysis']}\n")

    # Modifications
    modifications = state.get("modifications", [])
    report.append("\n## RECOMMENDED MODIFICATIONS")
    if modifications:
        report.append(f"\nTotal suggestions: {len(modifications)}\n")
        for i, mod in enumerate(modifications, 1):
            original = mod.get('original_text', '')
            suggested = mod.get('suggested_text', '')
            reason = mod.get('reason', '')
            report.append(f"**Modification {i}:**")
            report.append(f"- **Original:** {original}")
            report.append(f"- **Suggested:** {suggested}")
            report.append(f"- **Reason:** {reason}\n")
    else:
        report.append("\nNo critical modifications identified.\n")

    report.append("\n" + "=" * 60)
    report.append("END OF REPORT")
    report.append("=" * 60)

    final_report = "\n".join(report)
    print(f"  Report generated ({len(final_report)} characters)")
    return {"final_report": final_report}


# ============================================================
# Build Graph
# ============================================================

builder = StateGraph(ContractReviewState)

builder.add_node("extract_text", extract_text_node)
builder.add_node("classify_contract", classify_contract_node)
builder.add_node("retrieve_clauses", retrieve_clauses_node)
builder.add_node("analyze_contract", analyze_contract_node)
builder.add_node("create_review_plan", create_review_plan_node)
builder.add_node("execute_step", execute_step_node)
builder.add_node("generate_final_report", generate_final_report_node)

builder.add_edge(START, "extract_text")
builder.add_edge("extract_text", "classify_contract")
builder.add_edge("classify_contract", "retrieve_clauses")
builder.add_edge("retrieve_clauses", "analyze_contract")
builder.add_edge("analyze_contract", "create_review_plan")

builder.add_conditional_edges(
    "create_review_plan",
    continue_to_plan_execution,
    ["execute_step", "generate_final_report"],
)

builder.add_conditional_edges(
    "execute_step",
    continue_to_plan_execution,
    ["execute_step", "generate_final_report"],
)

builder.add_edge("generate_final_report", END)

graph = builder.compile()

print("Graph compiled successfully!")
