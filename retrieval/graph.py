from langgraph.graph import StateGraph, END
from .node import retrieval_node, RetrievalState

def build_retrieval_graph():
    graph = StateGraph(RetrievalState)
    graph.add_node("retrieve_clauses", retrieval_node)

    graph.set_entry_point("retrieve_clauses")
    graph.add_edge("retrieve_clauses", END)

    return graph.compile()