from langgraph.graph import StateGraph, END
from .node import analyze_node, AnalyzeState

def build_analyze_graph():
    graph = StateGraph(AnalyzeState)

    graph.add_node("analyze_contract", analyze_node)
    
    graph.set_entry_point("analyze_contract")
    graph.add_edge("analyze_contract", END)

    return graph.compile()