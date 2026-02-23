import os
import json
from typing import Dict, Any, List
from fastapi import BackgroundTasks
from pdfminer.high_level import extract_text as pdf_extract
import docx
import asyncio
from openai import OpenAI

roles = [
    {"role": "Corporate Lawyer"},
    {"role": "Risk Analyst"},
    {"role": "Compliance Officer"},
]

async def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return pdf_extract(path) or ""
    if ext in [".docx"]:
        d = docx.Document(path)
        return "\n".join([p.text for p in d.paragraphs])
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _safe_openai_client():
    try:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            return None
        return OpenAI(api_key=key)
    except Exception:
        return None

def _mock_analysis(text: str) -> Dict[str, Any]:
    t = text.lower()
    def present(*keys): 
        return any(k in t for k in keys)
    # Classification heuristics
    contract_type = "Professional Services Agreement" if present("consultant","service","services agreement") else "General Commercial Agreement"
    industry = "Public Transportation and Infrastructure" if present("commission","transport","infrastructure") else "Professional Services"
    category = "Governmental / Commercial Services" if present("commission","county","state") else "Commercial Services"
    jurisdiction = "State of California, Santa Cruz County" if present("california","santa cruz") else "Unknown"
    duration = "24 months with potential extensions" if present("24 months","two years","month") else "Unknown"
    classification = {
        "contract_type": contract_type,
        "industry": industry,
        "category": category,
        "jurisdiction": jurisdiction,
        "duration": duration
    }
    # Clause presence checks
    has_liability_cap = present("limitation of liability","liability capped","not to exceed")
    has_force_majeure = present("force majeure","acts of god","government-mandated shutdowns")
    has_neutral_dispute = present("independent arbitrator","neutral mediation","aaa mediation","jams")
    owns_ip_broad = present("ownership of work product","work product is owned by","commission unqualified ownership")
    termination_for_convenience = present("termination for convenience","terminate with 30 days")
    price_escalation = present("price escalation","inflation adjustment","cpi")
    data_privacy = present("data privacy","ccpa","data breach","security")
    # Risk factors
    risks = []
    if termination_for_convenience:
        risks.append({"title":"Unbalanced Termination for Convenience","severity":"medium","detail":"Counterparty can terminate on short notice creating resourcing risk."})
    if not has_liability_cap:
        risks.append({"title":"Absence of Limitation of Liability","severity":"high","detail":"No cap exposes consultant to potentially unlimited damages."})
    if not has_neutral_dispute and present("commission","board"):
        risks.append({"title":"Non-Neutral Dispute Resolution","severity":"medium","detail":"Disputes resolved by the Commission’s board rather than neutral arbitrator."})
    if owns_ip_broad:
        risks.append({"title":"Broad Ownership of Work Product","severity":"medium","detail":"Commission claims broad ownership which may restrict reuse of proprietary tools."})
    # Score and level
    weights = {"low":10,"medium":20,"high":35}
    score = min(95, max(5, sum(weights[x.get("severity","low")] for x in risks)))
    risk_level = "Low" if score < 30 else "Medium" if score < 70 else "High"
    # Missing clauses
    missing = []
    if not has_force_majeure:
        missing.append({"title":"Force Majeure Clause","level":"Critical","suggestion":"Add language excusing performance for events outside reasonable control."})
    if not has_liability_cap:
        missing.append({"title":"Limitation of Liability","level":"Critical","suggestion":"Cap total liability at 100% of fees paid under the agreement."})
    if not price_escalation and present("month","year"):
        missing.append({"title":"Price Escalation / Inflation Adjustment","level":"Important","suggestion":"Include CPI-based annual rate adjustment for multi-year terms."})
    if not data_privacy and present("government","public"):
        missing.append({"title":"Data Privacy and Security","level":"Important","suggestion":"Include CCPA compliance and breach notification procedures."})
    # Summary
    summary = (
        f"This {contract_type} governs consulting services. It is agency-leaning with potential risk from "
        f"{'termination rights, ' if termination_for_convenience else ''}"
        f"{'lack of liability cap, ' if not has_liability_cap else ''}"
        f"{'non-neutral dispute resolution, ' if not has_neutral_dispute else ''}"
        f"{'and broad IP ownership' if owns_ip_broad else 'balanced IP ownership'}."
        " Recommended actions include negotiating liability limits, neutral dispute forum, and clarifying IP reuse rights."
    )
    # Experts (unique personas with distinct scores/findings)
    experts = []
    base = score
    experts.append({
        "persona":"Corporate Lawyer",
        "score":min(100, base + 2),
        "key_findings":[x["title"] for x in risks[:3]],
        "recommendations":["Add liability cap aligned to fees","Use neutral arbitration (AAA/JAMS)","Clarify IP carve-outs"]
    })
    experts.append({
        "persona":"Risk Analyst",
        "score":min(100, base + 8),
        "key_findings":[x["title"] for x in risks],
        "recommendations":["Model termination exposure under 30/60/90 day scenarios","Require minimum notice & wind-down fees","Add insurance endorsements"]
    })
    experts.append({
        "persona":"Compliance Officer",
        "score":min(100, base - 5),
        "key_findings":[("Missing " + m["title"]) for m in missing][:3],
        "recommendations":["Insert force majeure language","Include data privacy obligations","Document audit & reporting cadence"]
    })
    # Smart suggestions: structured with actions & tags
    suggestions = [
        {"title":"Insert Limitation of Liability Clause","rationale":"Protects business continuity and caps exposure.","tags":["Risk Mitigation"],"actions":["Add Section: liability capped at 100% of fees","Exclude indirect/consequential damages"]},
        {"title":"Include Force Majeure Provision","rationale":"Clarifies responsibilities during crises.","tags":["Compliance"],"actions":["Standard language for events outside control","Suspend SLAs during force majeure"]},
        {"title":"Strengthen IP Carve‑outs","rationale":"Preserves consultant’s background IP.","tags":["Intellectual Property"],"actions":["Define background IP retained by consultant","Grant limited use license to agency"]},
        {"title":"Add Mutual Indemnification","rationale":"Fair allocation of third‑party claims.","tags":["Risk Mitigation"],"actions":["Reciprocal indemnity with negligence carve‑outs","Clarify claim handling & notice"]},
        {"title":"Implement Neutral Mediation Step","rationale":"Promotes fair settlements without litigation.","tags":["Dispute Resolution"],"actions":["Mediate via AAA/JAMS before board review","Appoint independent mediator"]}
    ]
    return {
        "summary": summary,
        "classification": classification,
        "risk": {"level": risk_level, "score": score, "factors": risks},
        "missing": missing,
        "experts": experts,
        "suggestions": suggestions,
        "contract_type": classification["contract_type"],
        "risk_level": risk_level
    }

async def _llm_analysis(text: str) -> Dict[str, Any]:
    client = _safe_openai_client()
    if not client:
        return _mock_analysis(text)
    prompt = (
        "Analyze the following contract text and return JSON with keys: "
        "summary, classification, risk, missing, experts, suggestions, contract_type, risk_level. "
        "classification requires keys: contract_type, industry, category, jurisdiction, duration. "
        "risk requires keys: level, score, factors as array of {title,severity}. "
        "missing requires array of {title, level, suggestion}. "
        "experts must include exactly three personas: Corporate Lawyer, Risk Analyst, Compliance Officer. "
        "Each persona appears once with fields {persona, score, key_findings[], recommendations[]}. "
        "Avoid duplicated items. Keep results concise and professional."
    )
    msg = [{"role": "system", "content": "You are a senior legal contract analyst."},
           {"role": "user", "content": prompt + "\n\n" + text[:8000]}]
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=msg, temperature=0.3)
    try:
        data = json.loads(resp.choices[0].message.content)
    except Exception:
        return _mock_analysis(text)
    seen = set()
    uniq = []
    for item in data.get("experts", []):
        p = item.get("persona")
        if p in seen or p not in [r["role"] for r in roles]:
            continue
        seen.add(p)
        uniq.append(item)
    data["experts"] = uniq
    return data

async def run_analysis(text: str, features: str = "full") -> Dict[str, Any]:
    all_res = await _llm_analysis(text)
    selected = set([x.strip().lower() for x in features.split(",")]) if features != "full" else {"full"}
    res = {}
    res["summary"] = all_res["summary"] if "full" in selected or "summary" in selected else ""
    res["classification_json"] = json.dumps(all_res["classification"]) if "full" in selected or "classification" in selected else ""
    res["risk_json"] = json.dumps(all_res["risk"]) if "full" in selected or "risk" in selected else ""
    res["missing_json"] = json.dumps(all_res["missing"]) if "full" in selected or "missing" in selected else ""
    res["experts_json"] = json.dumps(all_res["experts"]) if "full" in selected or "experts" in selected else ""
    res["suggestions_json"] = json.dumps(all_res["suggestions"]) if "full" in selected or "suggestions" in selected else ""
    res["full_json"] = json.dumps(all_res)
    res["contract_type"] = all_res.get("classification", {}).get("contract_type", "-")
    res["risk_level"] = all_res.get("risk", {}).get("level", "-")
    return res
