from typing import TypedDict
from langgraph.graph import StateGraph, END

from src.retrieve import retrieve_similar
from src.analyze import analyze_contract
from src.review_plan import create_review_plan
from src.role_analysis import analyze_by_role
from src.report import generate_final_report


class ContractState(TypedDict):
    document_text: str
    contract_type: str
    industry: str
    clauses: list
    analysis: str
    roles: list
    role_results: dict
    final_report: str



# Retrieve clauses

def retrieve_node(state):

    clauses = retrieve_similar(
        state["document_text"],
        state["contract_type"]
    )

    return {"clauses": clauses}



# Analyze contract vs clauses

def analyze_node(state):

    result = analyze_contract(
        state["document_text"],
        state["clauses"]
    )

    return {"analysis": result}


# Create review plan
def create_review_plan_node(state):

    roles = create_review_plan(
        state["contract_type"],
        state["industry"]
    )

    return {"roles": roles}


# Execute role analysis

def execute_step_node(state):

    results = {}

    for role in state["roles"]:
        results[role] = analyze_by_role(
            role,
            state["document_text"]
        )

    return {"role_results": results}



# Generate final report

def generate_final_report_node(state):

    report = generate_final_report(
        state["role_results"]
    )

    return {"final_report": report}


# Build graph

graph = StateGraph(ContractState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("analyze", analyze_node)
graph.add_node("review_plan", create_review_plan_node)
graph.add_node("role_analysis", execute_step_node)
graph.add_node("final_report", generate_final_report_node)

graph.set_entry_point("retrieve")

graph.add_edge("retrieve", "analyze")
graph.add_edge("analyze", "review_plan")
graph.add_edge("review_plan", "role_analysis")
graph.add_edge("role_analysis", "final_report")
graph.add_edge("final_report", END)

app = graph.compile()