from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from classification.node import classify_contract


class ClassificationState(TypedDict):
    markdown_text: str
    classification: dict

def classification_node(state: ClassificationState):
    return {
        "classification": classify_contract(state["markdown_text"])
    }


def build_classification_graph():
    graph = StateGraph(ClassificationState)
    graph.add_node("classify", classification_node)
    graph.set_entry_point("classify")
    graph.add_edge("classify", END)

    return graph.compile()
