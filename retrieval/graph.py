from typing import TypedDict
from langgraph.graph import StateGraph, END
from retrieval.node import retrieval_node

class RetrievalState(TypedDict):
    query: str
    contract_type: str
    retrieved_clauses: list


def build_retrieval_graph():
    g = StateGraph(RetrievalState)
    g.add_node("retrieve", retrieval_node)
    g.set_entry_point("retrieve")
    g.add_edge("retrieve", END)
    return g.compile()
