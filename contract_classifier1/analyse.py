import json
from typing import Any, Dict, List

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


ALLOWED_ALIGNMENT = {"aligned", "partially_aligned", "missing", "conflicting"}
ALLOWED_RISK = {"low", "medium", "high"}


def _extract_json(raw: str) -> Dict[str, Any]:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw[start:end + 1])
        raise ValueError(f"LLM did not return valid JSON:\n{raw}")


def _sanitize_alignment(value: str) -> str:
    v = (value or "").strip().lower()
    return v if v in ALLOWED_ALIGNMENT else "missing"


def _sanitize_risk(value: str) -> str:
    v = (value or "").strip().lower()
    return v if v in ALLOWED_RISK else "medium"


def _ensure_list_of_strings(x: Any) -> List[str]:
    """Convert to list[str]. If list contains dicts, convert to best-effort strings."""
    if x is None:
        return []
    if isinstance(x, list):
        out = []
        for item in x:
            if isinstance(item, str):
                s = item.strip()
                if s:
                    out.append(s)
            elif isinstance(item, dict):
                # If model mistakenly returns objects, try to extract a name
                s = str(item.get("clause_name") or item.get("title") or item.get("reference_clause_type") or "").strip()
                if s:
                    out.append(s)
        return out
    if isinstance(x, str):
        s = x.strip()
        return [s] if s else []
    return []


def analyze_clauses(
    query: str,
    contract_type: str,
    retrieved_clauses: List[Dict[str, Any]],
    model_name: str = "qwen2.5:0.5b",
) -> Dict[str, Any]:

    llm = OllamaLLM(model=model_name)

    compare_prompt = ChatPromptTemplate.from_template("""
You are a contract clause analyzer.

Return ONLY valid JSON. No markdown. No extra text.

Choose exactly one value:
- document_alignment: "aligned" OR "partially_aligned" OR "missing" OR "conflicting"
- risk_level: "low" OR "medium" OR "high"

Make key_gaps realistic. Do NOT use placeholder text like "short gap 1".
If there are no gaps, return an empty list [].

INPUT:
query: {query}
contract_type: {contract_type}
reference_clause_type: {clause_type}
reference_text: {reference_text}

OUTPUT JSON:
{{
  "document_alignment": "missing",
  "key_gaps": [],
  "risk_level": "medium",
  "notes": ""
}}
""")

    comparisons: List[Dict[str, Any]] = []

    for c in retrieved_clauses:
        clause_type = (
            c.get("metadata", {}).get("clause_type")
            or c.get("clause_type")
            or "Unknown"
        )
        reference_text = c.get("text") or c.get("clause_text") or ""

        msg = compare_prompt.format_messages(
            query=query,
            contract_type=contract_type,
            clause_type=clause_type,
            reference_text=reference_text,
        )

        raw = llm.invoke(msg)
        data = _extract_json(raw)

        data_out = {
            "reference_clause_type": clause_type,
            "reference_text": reference_text,
            "document_alignment": _sanitize_alignment(data.get("document_alignment", "missing")),
            "key_gaps": data.get("key_gaps", []),
            "risk_level": _sanitize_risk(data.get("risk_level", "medium")),
            "notes": data.get("notes", ""),
        }

        if not isinstance(data_out["key_gaps"], list):
            data_out["key_gaps"] = []
        # remove placeholders if model still outputs them
        data_out["key_gaps"] = [g for g in data_out["key_gaps"] if isinstance(g, str) and "short gap" not in g.lower()]

        if not isinstance(data_out["notes"], str):
            data_out["notes"] = ""

        comparisons.append(data_out)

    suggest_prompt = ChatPromptTemplate.from_template("""
You are a contract improvement assistant.

Return ONLY valid JSON. No markdown. No extra text.

Rules:
- suggestions: 1 to 3 items (must not be empty)
- suggested_text should be simple, realistic clause text (1-4 lines)
- missing_clauses MUST be a list of STRINGS only (clause names), e.g. ["Governing Law", "Dispute Resolution"]

INPUT:
query: {query}
contract_type: {contract_type}
comparisons_json: {comparisons_json}

OUTPUT JSON:
{{
  "suggestions": [
    {{
      "title": "Improve confidentiality scope",
      "why": "Explain what is missing clearly",
      "suggested_text": "Write a short improved clause text"
    }}
  ],
  "missing_clauses": []
}}
""")

    raw2 = llm.invoke(
        suggest_prompt.format_messages(
            query=query,
            contract_type=contract_type,
            comparisons_json=json.dumps(comparisons, ensure_ascii=False),
        )
    )
    sug = _extract_json(raw2)

    suggestions = sug.get("suggestions", [])
    if not isinstance(suggestions, list):
        suggestions = []

    # force missing_clauses to list[str]
    missing_clauses = _ensure_list_of_strings(sug.get("missing_clauses", []))

    return {
        "comparisons": comparisons,
        "suggestions": suggestions,
        "missing_clauses": missing_clauses,
    }
