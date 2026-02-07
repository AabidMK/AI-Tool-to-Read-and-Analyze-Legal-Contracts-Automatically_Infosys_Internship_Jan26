from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from parser.parser import extract_contract_text
from classification.classification import classify_contract_node

from vectorstore.chroma_store import ChromaClauseStore
from retrieval.clause_retriever import ClauseRetriever

from pipeline.nodes.create_review_plan_node import create_review_plan_node
from pipeline.nodes.execute_step_node import execute_step_node
from pipeline.nodes.summarize_role_results_node import summarize_role_results_node
from pipeline.nodes.generate_final_report_node import generate_final_report_node

from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    model="qwen-vl-8b",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    temperature=0
)


class ContractState(TypedDict):
    input_file: str
    contract_text: str
    result: dict
    matched_clauses: List[dict]
    review_plan: list
    role_analysis_results: list
    summarized_role_results: list
    final_report: str


CHROMA_DB_PATH = "chroma_db"
clause_store = ChromaClauseStore(CHROMA_DB_PATH)
clause_retriever = ClauseRetriever(clause_store)


def classification_node(state: ContractState) -> ContractState:
    contract_text = extract_contract_text(state["input_file"])
    result = classify_contract_node(contract_text)

    return {
        "input_file": state["input_file"],
        "contract_text": contract_text,
        "result": result,
        "matched_clauses": [],
        "review_plan": [],
        "role_analysis_results": [],
        "summarized_role_results": [],
        "final_report": ""
    }


def clause_retrieval_node(state: ContractState) -> ContractState:
    matched_clauses = clause_retriever.retrieve(
        contract_type=state["result"]["contract_type"],
        top_k=5
    )

    return {**state, "matched_clauses": matched_clauses}


def review_plan_node(state: ContractState) -> ContractState:
    return create_review_plan_node(
        {
            **state,
            "contract_type": state["result"]["contract_type"],
            "industry": state["result"].get("industry", "General")
        },
        llm
    )


def role_analysis_node(state: ContractState) -> ContractState:
    return execute_step_node(
        {
            **state,
            "retrieved_clauses": state["matched_clauses"]
        },
        llm
    )


def summarize_roles_node(state: ContractState) -> ContractState:
    return summarize_role_results_node(state, llm)


def final_report_node(state: ContractState) -> ContractState:
    return generate_final_report_node(
        {
            **state,
            "contract_type": state["result"]["contract_type"],
            "industry": state["result"].get("industry", "General")
        },
        llm
    )


def build_graph():
    graph = StateGraph(ContractState)

    graph.add_node("classify", classification_node)
    graph.add_node("retrieve", clause_retrieval_node)
    graph.add_node("review_plan", review_plan_node)
    graph.add_node("role_analysis", role_analysis_node)
    graph.add_node("summarize_roles", summarize_roles_node)
    graph.add_node("final_report", final_report_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "review_plan")
    graph.add_edge("review_plan", "role_analysis")
    graph.add_edge("role_analysis", "summarize_roles")
    graph.add_edge("summarize_roles", "final_report")
    graph.add_edge("final_report", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    initial_state = {
        "input_file": "data/sample_contracts/legaldoc2.docx",
        "contract_text": "",
        "result": {},
        "matched_clauses": [],
        "review_plan": [],
        "role_analysis_results": [],
        "summarized_role_results": [],
        "final_report": ""
    }

    final_state = app.invoke(initial_state)

    print("\n" + "=" * 80)
    print("FINAL CONTRACT REVIEW REPORT")
    print("=" * 80)
    print(final_state["final_report"])
