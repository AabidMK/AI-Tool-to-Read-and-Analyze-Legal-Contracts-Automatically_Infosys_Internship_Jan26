from typing import TypedDict
from langgraph.graph import StateGraph, END
from retrieval.node import retrieval_node

class RetrievalState(TypedDict):
    query: str
    contract_type: str
    retrieved_clauses: list


def build_retrieval_graph():
    graph = StateGraph(RetrievalState)
    graph.add_node("retrieve", retrieval_node)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", END)
    return graph.compile()