# graph.py
from langgraph.graph import StateGraph
from typing import TypedDict
from nodes.parser_node import extract_text
from nodes.classifier_node import classify_contract

class ContractState(TypedDict):
    file_path: str
    contract_text: str
    classification: str

def parser_node(state: ContractState):
    text = extract_text(state["file_path"])
    return {"contract_text": text}

def classifier_node(state: ContractState):
    result = classify_contract(state["contract_text"])
    return {"classification": result}

graph = StateGraph(ContractState)

graph.add_node("parser", parser_node)
graph.add_node("classifier", classifier_node)

graph.set_entry_point("parser")
graph.add_edge("parser", "classifier")

app = graph.compile()
