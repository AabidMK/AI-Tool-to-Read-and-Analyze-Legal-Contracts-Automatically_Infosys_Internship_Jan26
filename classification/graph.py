from typing import TypedDict
from langgraph.graph import StateGraph, END

from classification.node import classify_contract
from classification.node import retrieval_node


class GraphState(TypedDict):
    markdown_text: str
    classification: dict


def classification_node(state: GraphState) -> GraphState:
    classification = classify_contract(state["markdown_text"])
    return {
        "markdown_text": state["markdown_text"],
        "classification": classification
    }


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("classify", classification_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_edge("classification", "retrieval")

    graph.set_entry_point("classify")
    graph.add_edge("retrieval", END)

    return graph.compile()
