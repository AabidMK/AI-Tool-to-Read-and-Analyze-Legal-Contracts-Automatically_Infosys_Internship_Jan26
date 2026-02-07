from langgraph.graph import StateGraph, END
from graph.nodes import (
    extract_text_node,
    classify_contract_node,
    retrieve_clauses_node,
    analyze_contract_node,
    review_plan_node,
    execute_all_reviews,
)
from graph.state import ContractState


def build_graph():
    builder = StateGraph(ContractState)

    # Nodes
    builder.add_node("extract_text", extract_text_node)
    builder.add_node("classify_contract", classify_contract_node)
    builder.add_node("retrieve_clauses", retrieve_clauses_node)
    builder.add_node("analyze_contract", analyze_contract_node)
    builder.add_node("review_plan_node", review_plan_node)
    builder.add_node("execute_all_reviews", execute_all_reviews)

    # Entry
    builder.set_entry_point("extract_text")

    # Linear flow
    builder.add_edge("extract_text", "classify_contract")
    builder.add_edge("classify_contract", "retrieve_clauses")
    builder.add_edge("retrieve_clauses", "analyze_contract")
    builder.add_edge("analyze_contract", "review_plan_node")
    
    builder.add_edge("review_plan_node","execute_all_reviews")
    builder.add_edge("execute_all_reviews",END)

    return builder.compile()