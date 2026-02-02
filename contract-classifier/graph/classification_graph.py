from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from groq import Groq
import json
import os

load_dotenv()

# LangSmith tracing setup
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "contract-analyzer"

class GraphState(TypedDict):
    contract_text: str
    classification: dict
    retrieved_clauses: list
    analysis: dict

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classification_node(state: GraphState) -> GraphState:
    contract_text = state["contract_text"][:8000]
    
    prompt_text = f"""Analyze this contract and return only JSON:

Contract: {contract_text}

Return JSON like: {{"contract_type": "Non-Disclosure Agreement (NDA)", "industry": "Technology", "data": [{{"name": "parties", "value": "Company A, Company B"}}]}}"""
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    response_content = response.choices[0].message.content
    start = response_content.find('{')
    end = response_content.rfind('}') + 1
    json_str = response_content[start:end]
    parsed = json.loads(json_str)
    return {"classification": parsed}

def analyze_contract_node(state: GraphState) -> GraphState:
    contract_text = state["contract_text"][:8000]
    retrieved_clauses = state.get("retrieved_clauses", [])
    
    # Extract ALL clauses from the contract text
    extract_prompt = f"""Extract ALL clauses from this contract document. Include every clause, section, and provision found in the text:

Contract: {contract_text}

Return JSON with ALL extracted clauses:
{{
  "extracted_clauses": [
    {{
      "clause_title": "Confidentiality",
      "clause_text": "Full clause text from contract...",
      "metadata": {{
        "jurisdiction": "Contract Specific",
        "version": "1.0",
        "last_updated": "2024-12-30"
      }}
    }}
  ]
}}"""
    
    extract_response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": extract_prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    extract_content = extract_response.choices[0].message.content
    start = extract_content.find('{')
    end = extract_content.rfind('}') + 1
    extract_json = extract_content[start:end]
    extracted_data = json.loads(extract_json)
    extracted_clauses = extracted_data.get("extracted_clauses", [])
    
    # All clauses from document are present=true
    analyzed_clauses = []
    for clause in extracted_clauses:
        analyzed_clause = {
            "clause_title": clause.get("clause_title"),
            "clause_text": clause.get("clause_text"),
            "metadata": clause.get("metadata", {
                "jurisdiction": "Contract Specific",
                "version": "1.0",
                "last_updated": "2024-12-30"
            }),
            "present": True
        }
        analyzed_clauses.append(analyzed_clause)
    
    # Add any retrieved clauses that are NOT in the document as present=false
    for retrieved in retrieved_clauses:
        found_match = False
        for analyzed in analyzed_clauses:
            if retrieved["clause_title"].lower() in analyzed["clause_title"].lower() or \
               analyzed["clause_title"].lower() in retrieved["clause_title"].lower():
                found_match = True
                break
        
        if not found_match:
            missing_clause = {
                "clause_title": retrieved.get("clause_title"),
                "clause_text": retrieved.get("clause_text"),
                "metadata": {
                    "jurisdiction": retrieved.get("jurisdiction"),
                    "version": retrieved.get("version"),
                    "last_updated": retrieved.get("last_updated")
                },
                "present": False
            }
            analyzed_clauses.append(missing_clause)
    
    return {"analysis": {"analyzed_clauses": analyzed_clauses}}

def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("classify_contract", classification_node)
    graph.add_node("analyze_contract", analyze_contract_node)
    graph.set_entry_point("classify_contract")
    graph.add_edge("classify_contract", "analyze_contract")
    graph.set_finish_point("analyze_contract")
    return graph.compile()
