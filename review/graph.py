from langgraph.graph import StateGraph, END
from .state import ReviewState
from .plan_node import create_review_plan_node
from .execute_node import execute_roles_parallel_node


def build_review_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("create_review_plan", create_review_plan_node)
    graph.add_node("execute_roles_parallel", execute_roles_parallel_node)

    graph.set_entry_point("create_review_plan")
    graph.add_edge("create_review_plan", "execute_roles_parallel")
    graph.add_edge("execute_roles_parallel", END)

    return graph.compile()
