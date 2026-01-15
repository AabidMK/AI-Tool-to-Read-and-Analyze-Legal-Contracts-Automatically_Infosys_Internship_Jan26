from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from parser import parse_document

llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)

classification_prompt = ChatPromptTemplate.from_template("""
You are a legal contract classification system.

Return ONLY valid JSON:
{{
  "contract_type": "...",
  "industry": "..."
}}

Contract text:
{text}
""")


class ContractState(TypedDict):
    file_path: str
    contract_text: str
    classification: str

def parse_node(state: ContractState):
    text = parse_document(state["file_path"])
    return {"contract_text": text}

def classify_node(state: ContractState):
    prompt = classification_prompt.format_messages(
        text=state["contract_text"]
    )
    response = llm.invoke(prompt)
    return {"classification": response.content}

def build_graph():
    graph = StateGraph(ContractState)

    graph.add_node("parse", parse_node)
    graph.add_node("classify", classify_node)

    graph.set_entry_point("parse")
    graph.add_edge("parse", "classify")
    graph.add_edge("classify", END)

    return graph.compile()
