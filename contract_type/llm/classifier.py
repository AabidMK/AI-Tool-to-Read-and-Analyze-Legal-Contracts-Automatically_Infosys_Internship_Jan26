import json
import requests
import re

from parser_2 import extract_pdf_text, extract_docx_text

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"


def extract_key_sections(text: str) -> str:
    """
    Extract only important contract parts for fast & accurate classification
    """
    lines = text.splitlines()

    headings = []
    for line in lines:
        if line.isupper() and len(line) < 120:
            headings.append(line)

    first_part = text[:3000]   # first 1–2 pages equivalent

    keywords = []
    KEY_TERMS = [
        "employment", "service", "agreement", "confidential",
        "lease", "license", "payment", "termination",
        "transport", "software", "health", "finance"
    ]

    for word in KEY_TERMS:
        if re.search(word, text, re.IGNORECASE):
            keywords.append(word)

    summary = f"""
FIRST PART:
{first_part}

HEADINGS:
{', '.join(headings[:15])}

KEYWORDS:
{', '.join(set(keywords))}
"""
    return summary


def classify_contract(file_path: str) -> dict:
    # -------- Extract ----------
    if file_path.lower().endswith(".pdf"):
        result = extract_pdf_text(file_path)
    elif file_path.lower().endswith(".docx"):
        result = extract_docx_text(file_path)
    else:
        return {"error": "Only PDF or DOCX supported"}

    if not result["success"]:
        return {"error": result["error"]}

    smart_text = extract_key_sections(result["text"])

    prompt = f"""
You are an expert legal contract classifier.

Analyze the contract information below and return ONLY JSON.

{smart_text}

Return ONLY this JSON:
{{
  "contract_type": "Employment Agreement | NDA | Service Agreement | Lease Agreement | Sales Contract | License Agreement | Purchase Agreement",
  "industry": "IT | Healthcare | Finance | Legal | Real Estate | Manufacturing | Transportation | Education",
  "confidence": 0.0
}}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.05,
                "num_predict": 120
            }
        },
        timeout=90
    )

    raw = response.json()["response"]
    start = raw.find("{")
    end = raw.rfind("}") + 1
    result = json.loads(raw[start:end])

    return {
        "contract_type": result.get("contract_type", "Unknown"),
        "industry": result.get("industry", "Unknown"),
        "confidence": round(float(result.get("confidence", 0.85)), 2)
    }
