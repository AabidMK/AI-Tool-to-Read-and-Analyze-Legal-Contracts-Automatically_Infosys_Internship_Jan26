from nodes.extract_node import extract_text_node
from nodes.classify_node import classify_contract_node
from nodes.retrieve_node import retrieve_clauses_node
from nodes.analyze_node import analyze_contract_node
from nodes.create_review_plan_node import create_review_plan_node
from nodes.execute_step_node import execute_step_node
from nodes.generate_final_report_node import generate_final_report_node


def build_graph(state: dict):
    from nodes.extract_node import extract_text_node
    from nodes.classify_node import classify_contract_node
    from nodes.retrieve_node import retrieve_clauses_node
    from nodes.analyze_node import analyze_contract_node

    state.update(extract_text_node(state))
    state.update(classify_contract_node(state))
    state.update(retrieve_clauses_node(state))
    state.update(analyze_contract_node(state))

    # 🔽 NEW NODES START HERE 🔽
    state.update(create_review_plan_node(state))
    state.update(execute_step_node(state))
    state.update(generate_final_report_node(state))

