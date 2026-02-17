import json
from analysis.prompts import CLAUSE_COMPARISON_PROMPT
from analysis.schemas import AnalyzeOutput
import re

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def format_reference_clauses(retrieved_clauses):
    formatted = ""
    for i, clause in enumerate(retrieved_clauses, 1):
        formatted += f"""
Clause {i}:
Name: {clause.get('clause_title')}
Text: {clause.get('clause_text')}
"""
    return formatted


def extract_missing_clauses(clause_analysis):
    missing = []

    for clause in clause_analysis:
        if clause.status == "missing":
            missing.append({
                "clause_name": clause.clause_name,
                "why_important": clause.observations,
                "suggested_text": clause.suggested_revision
            })

    return missing


def normalize_llm_output(llm_output: dict, contract_type: str):
    # Handle non-standard LLM output
    if "clause_analysis" not in llm_output:
        clause_analysis = []

        for _, clause_data in llm_output.items():
            clause_analysis.append({
                "clause_name": clause_data.get("clause_name", "Unknown"),
                "status": clause_data.get("status", clause_data.get("presence", "missing")),
                "risk_level": clause_data.get("risk_level", "medium"),
                "observations": clause_data.get("observations", ""),
                "suggested_revision": clause_data.get("suggested_revision")
            })

        llm_output = {
            "contract_type": contract_type,
            "clause_analysis": clause_analysis,
            "missing_clauses": [],
            "overall_summary": {
                "risk_score": 5,
                "key_concerns": ["Schema normalized from LLM output"]
            }
        }

    return llm_output


# --------------------------------------------------
# Main Analyze Function
# --------------------------------------------------

def analyze_contract(
    contract_type: str,
    contract_text: str,
    retrieved_clauses: list,
    llm
):
    reference_clauses = format_reference_clauses(retrieved_clauses)

    prompt = f"""
{CLAUSE_COMPARISON_PROMPT}

Contract Type:
{contract_type}

Contract Text:
{contract_text}

Reference Standard Clauses:
{reference_clauses}
"""

    response = llm.invoke(prompt)

    try:
        raw_content = response.content

        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if not match:
            raise ValueError("LLM did not return valid JSON.")

        json_str = match.group()

        try:
            llm_output = json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM JSON output.")

        llm_output = normalize_llm_output(llm_output, contract_type)
        parsed_output = AnalyzeOutput(**llm_output)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON output")

    missing_clauses = extract_missing_clauses(parsed_output.clause_analysis)
    parsed_output.missing_clauses = missing_clauses

    return parsed_output
