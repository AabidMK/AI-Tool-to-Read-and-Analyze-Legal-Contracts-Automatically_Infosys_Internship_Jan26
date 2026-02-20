import json
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm import get_llm
from .prompt import analysis_prompt, global_prompt

class AnalyzeState(TypedDict):
    contract_text: str
    classification: Dict
    retrieved_clauses: List[Dict[str,Any]]
    clause_analysis: List[Dict[str, Any]]
    global_analysis: List[Dict[str, Any]]

llm = get_llm(temperature=0)

def analyze_node(state: AnalyzeState) -> AnalyzeState:
    contract_text = state["contract_text"]
    classification = state["classification"]
    retrieved_clauses = state["retrieved_clauses"]

    clause_analysis_result = []

    for clause in retrieved_clauses:
        clause_title = clause["clause_title"]
        clause_text = clause["clause_text"]

        messages = [SystemMessage(content=analysis_prompt),
                    HumanMessage(
                        content=f"""
CONTRACT TYPE: {classification.get("contract_type")}
INDUSTRY: {classification.get("industry")}

-----CONTRACT TEXT-----
{contract_text}

-----REFERENCE CLAUSE-----
Title: {clause_title}
Text:
{clause_text}
"""

                    )
                ]
        response = llm.invoke(messages)

        try:
            result = json.loads(response.content)
        except Exception:
            result = {
                "clause_title": clause_title,
                "presence": "Error",
                "similarity_summary": "LLM output parsing failed",
                "risk_level": "Unknown",
                "improvement_suggestion": "Manual review required"
            }
        
        clause_analysis_result.append(result)

    # -----------------------------
    # Global Structural Analysis
    # -----------------------------

    global_messages = [SystemMessage(content=global_prompt),
                       HumanMessage(content=f"""
CONTRACT TYPE: {classification.get("contract_type")}
INDUSTRY: {classification.get("industry")}

-----CONTRACT TEXT-----
{contract_text}
"""
                       )
    ]

    global_response = llm.invoke(global_messages)

    try:
        global_analysis = json.loads(global_response.content)
    except Exception:
        global_analysis = {
            "missing_clauses": [],
            "structural_risks": ["Global analysis parsing failed"],
            "overall_risk_level": "Unknown",
            "executive_summary": "Manual review required"
        }

    return {
        "contract_text": contract_text,
        "classification": classification,
        "retrieved_clauses": retrieved_clauses,
        "clause_analysis": clause_analysis_result,
        "global_analysis": global_analysis
    }