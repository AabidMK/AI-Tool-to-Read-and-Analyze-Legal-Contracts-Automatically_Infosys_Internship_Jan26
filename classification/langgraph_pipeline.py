from typing import TypedDict

from langgraph.graph import StateGraph, END

from parser.parser import extract_contract_text
from classification.classification import classify_contract_node

# 1. Define Graph State
class ContractState(TypedDict):
    input_file: str
    contract_text: str
    result: dict

# 2. Define Classification Node
def classification_node(state: ContractState) -> ContractState:
    """
    LangGraph node:
    - Extracts contract text
    - Sends it to LLM for classification
    """

    print("[LangGraph] Extracting contract text...")
    contract_text = extract_contract_text(state["input_file"])

    print("[LangGraph] Classifying contract...")
    result = classify_contract_node(contract_text)

    return {
        "input_file": state["input_file"],
        "contract_text": contract_text,
        "result": result
    }


# 3. Build Graph
def build_graph():
    graph = StateGraph(ContractState)

    graph.add_node("classify_contract", classification_node)

    graph.set_entry_point("classify_contract")
    graph.add_edge("classify_contract", END)

    return graph.compile()


# 4. Run Graph
if __name__ == "__main__":
    app = build_graph()

    initial_state = {
        "input_file": "data/sample_contracts/Serv_Agree.pdf",
        "contract_text": "",
        "result": {}
    }

    final_state = app.invoke(initial_state)

    print("\n[LangGraph] Final Output:")
    print(final_state["result"])
