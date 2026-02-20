from typing import TypedDict
from langgraph.graph import StateGraph, END
from analysis.node import analyze_contract_node


class AnalysisState(TypedDict):
    markdown_text: str
    contract_type: str
    retrieved_clauses: list
    analysis: dict


def build_analysis_graph():
    graph = StateGraph(AnalysisState)

    graph.add_node("analyze", analyze_contract_node)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)

    return graph.compile()