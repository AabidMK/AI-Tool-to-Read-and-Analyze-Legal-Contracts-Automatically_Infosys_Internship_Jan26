from typing import TypedDict, List

from langgraph.graph import StateGraph, END

from parser.parser import extract_contract_text
from classification.classification import classify_contract_node

from vectorstore.chroma_store import ChromaClauseStore
from retrieval.clause_retriever import ClauseRetriever

from analysis.analyze_contract import analyze_contract

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-vl-8b",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",   # required but ignored by LM Studio
    temperature=0
)


# --------------------------------------------------
# 1. Define LangGraph State
# --------------------------------------------------

class ContractState(TypedDict):
    input_file: str
    contract_text: str
    result: dict                     # classifier output
    matched_clauses: List[dict]      # retrieved clauses
    analysis_result: dict             # NEW: analysis output


# --------------------------------------------------
# 2. Initialize Clause Retrieval Dependencies
# --------------------------------------------------

CHROMA_DB_PATH = "chroma_db"

clause_store = ChromaClauseStore(CHROMA_DB_PATH)
clause_retriever = ClauseRetriever(clause_store)


# --------------------------------------------------
# 3. Classification Node
# --------------------------------------------------

def classification_node(state: ContractState) -> ContractState:
    print("[LangGraph] Extracting contract text...")
    contract_text = extract_contract_text(state["input_file"])

    print("[LangGraph] Classifying contract...")
    result = classify_contract_node(contract_text)

    return {
        "input_file": state["input_file"],
        "contract_text": contract_text,
        "result": result,
        "matched_clauses": [],
        "analysis_result": {}
    }


# --------------------------------------------------
# 4. Clause Retrieval Node
# --------------------------------------------------

def clause_retrieval_node(state: ContractState) -> ContractState:
    print("[LangGraph] Retrieving relevant clauses...")

    contract_type = state["result"].get("contract_type")
    if not contract_type:
        raise ValueError("Classifier did not return contract_type")

    matched_clauses = clause_retriever.retrieve(
        contract_type=contract_type,
        top_k=5
    )

    return {
        **state,
        "matched_clauses": matched_clauses
    }


# --------------------------------------------------
# 5. Analyze Contract Node (NEW)
# --------------------------------------------------

def analyze_contract_node(state: ContractState) -> ContractState:
    print("[LangGraph] Analyzing contract against standard clauses...")

    contract_type = state["result"].get("contract_type")
    if not contract_type:
        raise ValueError("Missing contract_type for analysis")

    analysis = analyze_contract(
        contract_type=contract_type,
        contract_text=state["contract_text"],
        retrieved_clauses=state["matched_clauses"],
        llm=llm
    )

    return {
        **state,
        "analysis_result": analysis.dict()
    }


# --------------------------------------------------
# 6. Build LangGraph
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


def print_analysis_result(analysis):
    print("\n" + "=" * 60)
    print("CONTRACT ANALYSIS REPORT")
    print("=" * 60)

    # 1. Clause-by-clause analysis
    print("\nCLAUSE-BY-CLAUSE ANALYSIS")
    print("-" * 60)

    for clause in analysis["clause_analysis"]:
        print(f"\nClause Name : {clause['clause_name']}")
        print(f"Status      : {clause['status'].upper()}")
        print(f"Risk Level  : {clause['risk_level'].upper()}")
        print(f"Issues      : {clause['observations']}")

        if clause["suggested_revision"]:
            print("Suggested Improvement:")
            print(f"  {clause['suggested_revision']}")

    # 2. Missing clauses (omission detection)
    print("\nMISSING / OMITTED CLAUSES")
    print("-" * 60)

    if not analysis["missing_clauses"]:
        print("No critical clauses are missing.")
    else:
        for clause in analysis["missing_clauses"]:
            print(f"\nMissing Clause : {clause['clause_name']}")
            print(f"Why Important  : {clause['why_important']}")
            print("Suggested Text:")
            print(f"  {clause['suggested_text']}")

    # 3. Overall risk summary
    print("\nOVERALL RISK SUMMARY")
    print("-" * 60)
    print(f"Risk Score: {analysis['overall_summary']['risk_score']} / 10")

    print("Key Concerns:")
    for concern in analysis["overall_summary"]["key_concerns"]:
        print(f" - {concern}")

    print("\n" + "=" * 60)


# --------------------------------------------------
# 7. Run Graph (Local Test)
# --------------------------------------------------

if __name__ == "__main__":
    app = build_graph()

    initial_state = {
        "input_file": "data/sample_contracts/legaldoc2.docx",
        "contract_text": "",
        "result": {},
        "matched_clauses": [],
        "analysis_result": {}
    }

    final_state = app.invoke(initial_state)

    print("\n[LangGraph] Contract Type:")
    print(final_state["result"]["contract_type"])

    print("\n[LangGraph] Matched Clauses:")
    for clause in final_state["matched_clauses"]:
        print("\n--- CLAUSE ---")
        print("Title :", clause.get("clause_title"))
        print("Score :", clause.get("similarity_score"))
        print("Text  :", clause.get("clause_text", "")[:200], "...")

    print("\n[LangGraph] Analysis Result:")
    
    print_analysis_result(final_state["analysis_result"])