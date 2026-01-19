from typing import TypedDict
from langgraph.graph import StateGraph, END

from classification.node import classify_contract


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
    graph.set_entry_point("classify")
    graph.add_edge("classify", END)

    return graph.compile()
