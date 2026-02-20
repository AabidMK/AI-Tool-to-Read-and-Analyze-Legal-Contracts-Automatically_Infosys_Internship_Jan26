from langgraph.graph import StateGraph, END
from .node import classification_node, ClassificationState

def build_classification_graph():
    graph = StateGraph(ClassificationState)

    graph.add_node("classify_contract",classification_node)

    graph.set_entry_point("classify_contract")
    graph.add_edge("classify_contract", END)

    return graph.compile()