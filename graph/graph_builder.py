from langgraph.graph import StateGraph, END
from graph.nodes import extract_text_node, classify_contract_node, retrieve_clauses_node, analyze_contract_node
from graph.state import ContractState

def build_graph():
    builder = StateGraph(ContractState)

    builder.add_node("extract_text", extract_text_node)
    builder.add_node("classify_contract", classify_contract_node)
    builder.add_node("retrieve_clauses",retrieve_clauses_node)
    builder.add_node("analyze_contract", analyze_contract_node)

    builder.set_entry_point("extract_text")
    builder.add_edge("extract_text", "classify_contract")
    builder.add_edge("classify_contract", "retrieve_clauses")
    builder.add_edge("retrieve_clauses", "analyze_contract")
    builder.add_edge("analyze_contract", END)
    return builder.compile()
