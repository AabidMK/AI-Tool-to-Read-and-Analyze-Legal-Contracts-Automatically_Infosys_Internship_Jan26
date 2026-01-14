from langgraph.graph import StateGraph, END
from graph.nodes import extract_text_node, classify_contract_node
from graph.state import ContractState

def build_graph():
    builder = StateGraph(ContractState)

    builder.add_node("extract_text", extract_text_node)
    builder.add_node("classify_contract", classify_contract_node)

    builder.set_entry_point("extract_text")
    builder.add_edge("extract_text", "classify_contract")
    builder.add_edge("classify_contract", END)   

    return builder.compile()
