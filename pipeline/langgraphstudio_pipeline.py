from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, List

from langgraph.graph import StateGraph, END

from parser.parser import extract_contract_text
from classification.classification import classify_contract_node
from vectorstore.chroma_store import ChromaClauseStore
from retrieval.clause_retriever import ClauseRetriever
from analysis.analyze_contract import analyze_contract

from langchain_openai import ChatOpenAI


# --------------------------------------------------
# LLM (LM Studio)
# --------------------------------------------------

llm = ChatOpenAI(
    model="qwen-vl-8b",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    temperature=0
)


# --------------------------------------------------
# State Definition
# --------------------------------------------------

class ContractState(TypedDict):
    input_file: str
    contract_text: str
    result: dict
    matched_clauses: List[dict]
    analysis_result: dict


# --------------------------------------------------
# Dependencies
# --------------------------------------------------

CHROMA_DB_PATH = "chroma_db"

clause_store = ChromaClauseStore(CHROMA_DB_PATH)
clause_retriever = ClauseRetriever(clause_store)


# --------------------------------------------------
# Nodes
# --------------------------------------------------

def classification_node(state: ContractState) -> ContractState:
    contract_text = extract_contract_text(state["input_file"])
    result = classify_contract_node(contract_text)

    return {
        "input_file": state["input_file"],
        "contract_text": contract_text,
        "result": result,
        "matched_clauses": [],
        "analysis_result": {}
    }


def clause_retrieval_node(state: ContractState) -> ContractState:
    contract_type = state["result"].get("contract_type")
    if not contract_type:
        raise ValueError("Missing contract_type")

    matched_clauses = clause_retriever.retrieve(
        contract_type=contract_type,
        top_k=5
    )

    return {
        **state,
        "matched_clauses": matched_clauses
    }


def analyze_contract_node(state: ContractState) -> ContractState:
    analysis = analyze_contract(
        contract_type=state["result"]["contract_type"],
        contract_text=state["contract_text"],
        retrieved_clauses=state["matched_clauses"],
        llm=llm
    )

    return {
        **state,
        "analysis_result": analysis.model_dump()
    }


# --------------------------------------------------
# Build Graph (STUDIO ENTRY)
# --------------------------------------------------

def build_graph():
    graph = StateGraph(ContractState)

    graph.add_node("classify_contract", classification_node)
    graph.add_node("retrieve_clauses", clause_retrieval_node)
    graph.add_node("analyze_contract", analyze_contract_node)

    graph.set_entry_point("classify_contract")
    graph.add_edge("classify_contract", "retrieve_clauses")
    graph.add_edge("retrieve_clauses", "analyze_contract")
    graph.add_edge("analyze_contract", END)

    return graph.compile()



graph = build_graph()
