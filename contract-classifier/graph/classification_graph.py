from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from groq import Groq
import json
import os

load_dotenv()

# LangSmith tracing setup - disabled for now
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "contract-analyzer"

class GraphState(TypedDict):
    contract_text: str
    classification: dict
    retrieved_clauses: list
    analysis: dict
    review_plan: dict
    role_analyses: list
    final_report: dict

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
    
    # Only show missing clauses (present=false)
    missing_clauses = []
    
    # Find retrieved clauses that are NOT in the document
    for retrieved in retrieved_clauses:
        found_match = False
        for extracted in extracted_clauses:
            if retrieved["clause_title"].lower() in extracted.get("clause_title", "").lower() or \
               extracted.get("clause_title", "").lower() in retrieved["clause_title"].lower():
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
            missing_clauses.append(missing_clause)
    
    return {"analysis": {"analyzed_clauses": missing_clauses}}

def create_review_plan_node(state: GraphState) -> GraphState:
    classification = state.get("classification", {})
    contract_type = classification.get("contract_type", "General Contract")
    industry = classification.get("industry", "General")
    
    print(f"\n🔍 NODE 1: CREATE REVIEW PLAN")
    print(f"=" * 50)
    print(f"Contract Type: {contract_type}")
    print(f"Industry: {industry}")
    
    prompt = f"""Generate specialized legal roles for reviewing a {contract_type} in the {industry} industry.

Return JSON with 3-4 distinct legal expert roles:
{{
  "review_plan": {{
    "contract_type": "{contract_type}",
    "industry": "{industry}",
    "roles": [
      {{
        "role_name": "Corporate Lawyer",
        "expertise": "Corporate governance and compliance",
        "focus_areas": ["liability", "corporate structure", "governance"]
      }}
    ]
  }}
}}"""
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    start = content.find('{')
    end = content.rfind('}') + 1
    parsed = json.loads(content[start:end])
    
    review_plan = parsed["review_plan"]
    
    print(f"Generated {len(review_plan.get('roles', []))} Legal Expert Roles:")
    for i, role in enumerate(review_plan.get('roles', []), 1):
        print(f"{i}. {role.get('role_name')} - {role.get('expertise')}")
        print(f"   Focus: {', '.join(role.get('focus_areas', []))}")
    
    return {"review_plan": review_plan}

def execute_step_node(state: GraphState) -> GraphState:
    contract_text = state["contract_text"][:8000]
    review_plan = state.get("review_plan", {})
    roles = review_plan.get("roles", [])
    
    print(f"\n⚖️  NODE 2: EXECUTE PARALLEL ANALYSIS")
    print(f"=" * 50)
    print(f"Analyzing contract from {len(roles)} expert perspectives...")
    
    role_analyses = []
    
    for i, role in enumerate(roles, 1):
        role_name = role.get("role_name")
        expertise = role.get("expertise")
        focus_areas = role.get("focus_areas", [])
        
        print(f"\n[{i}/{len(roles)}] Analyzing as {role_name}...")
        
        prompt = f"""As a {role_name} with expertise in {expertise}, analyze this contract focusing on {', '.join(focus_areas)}.

Contract: {contract_text}

Provide analysis as JSON:
{{
  "role": "{role_name}",
  "key_findings": ["finding1", "finding2"],
  "risks": ["risk1", "risk2"],
  "recommendations": ["rec1", "rec2"],
  "compliance_issues": ["issue1"],
  "rating": "High/Medium/Low Risk"
}}"""
        
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        start = content.find('{')
        end = content.rfind('}') + 1
        analysis = json.loads(content[start:end])
        role_analyses.append(analysis)
        
        print(f"   ✓ {role_name}: {analysis.get('rating', 'No Rating')}")
        print(f"   Findings: {len(analysis.get('key_findings', []))}")
        print(f"   Risks: {len(analysis.get('risks', []))}")
        print(f"   Recommendations: {len(analysis.get('recommendations', []))}")
    
    print(f"\n✅ Completed all {len(role_analyses)} expert analyses")
    return {"role_analyses": role_analyses}

def generate_final_report_node(state: GraphState) -> GraphState:
    classification = state.get("classification", {})
    analysis = state.get("analysis", {})
    role_analyses = state.get("role_analyses", [])
    
    print(f"\n📋 NODE 3: GENERATE FINAL REPORT")
    print(f"=" * 50)
    
    # Aggregate findings
    all_risks = []
    all_recommendations = []
    all_compliance_issues = []
    
    for role_analysis in role_analyses:
        all_risks.extend(role_analysis.get("risks", []))
        all_recommendations.extend(role_analysis.get("recommendations", []))
        all_compliance_issues.extend(role_analysis.get("compliance_issues", []))
    
    # Calculate overall risk
    risk_ratings = [ra.get("rating", "Medium Risk") for ra in role_analyses]
    high_risk_count = sum(1 for r in risk_ratings if "High" in r)
    overall_risk = "High Risk" if high_risk_count > 0 else "Medium Risk" if len(risk_ratings) > 0 else "Low Risk"
    
    final_report = {
        "contract_summary": {
            "type": classification.get("contract_type", "Unknown"),
            "industry": classification.get("industry", "Unknown"),
            "overall_risk_rating": overall_risk
        },
        "expert_analyses": role_analyses,
        "consolidated_findings": {
            "total_risks_identified": len(set(all_risks)),
            "critical_compliance_issues": len(set(all_compliance_issues)),
            "key_recommendations": list(set(all_recommendations))[:5]
        },
        "clause_analysis": analysis.get("analyzed_clauses", []),
        "executive_summary": f"Contract analysis completed by {len(role_analyses)} legal experts. Overall risk assessment: {overall_risk}. {len(set(all_risks))} unique risks identified with {len(set(all_recommendations))} recommendations provided."
    }
    
    print(f"Contract Summary:")
    print(f"  Type: {final_report['contract_summary']['type']}")
    print(f"  Industry: {final_report['contract_summary']['industry']}")
    print(f"  Overall Risk: {final_report['contract_summary']['overall_risk_rating']}")
    
    print(f"\nConsolidated Findings:")
    print(f"  Total Risks: {final_report['consolidated_findings']['total_risks_identified']}")
    print(f"  Compliance Issues: {final_report['consolidated_findings']['critical_compliance_issues']}")
    print(f"  Key Recommendations: {len(final_report['consolidated_findings']['key_recommendations'])}")
    
    print(f"\nExecutive Summary:")
    print(f"  {final_report['executive_summary']}")
    
    print(f"\n✅ Final report generated successfully!")
    
    return {"final_report": final_report}

def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("classify_contract", classification_node)
    graph.add_node("analyze_contract", analyze_contract_node)
    graph.add_node("create_review_plan", create_review_plan_node)
    graph.add_node("execute_step", execute_step_node)
    graph.add_node("generate_final_report", generate_final_report_node)
    
    graph.set_entry_point("classify_contract")
    graph.add_edge("classify_contract", "analyze_contract")
    graph.add_edge("analyze_contract", "create_review_plan")
    graph.add_edge("create_review_plan", "execute_step")
    graph.add_edge("execute_step", "generate_final_report")
    graph.set_finish_point("generate_final_report")
    
    return graph.compile()
