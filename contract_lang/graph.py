from langgraph.graph import StateGraph
from nodes.extract_node import extract_text_node
from nodes.classify_node import classify_contract_node

def build_graph():
    graph = StateGraph(dict)

    graph.add_node("extract", extract_text_node)
    graph.add_node("classify", classify_contract_node)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "classify")
    graph.set_finish_point("classify")

    return graph.compile()
