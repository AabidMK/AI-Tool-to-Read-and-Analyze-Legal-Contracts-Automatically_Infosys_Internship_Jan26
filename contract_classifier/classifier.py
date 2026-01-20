import os
import json
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from pypdf import PdfReader
from docx import Document


# -----------------------------
# 1. State Definition
# -----------------------------
class ContractState(TypedDict):
    document_text: str
    contract_type: str
    industry: str


# -----------------------------
# 2. File Loader
# -----------------------------
def load_contract(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError("Only PDF and DOCX are supported")


# -----------------------------
# 3. LLM Classification Node
# -----------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_template("""
You are a contract analysis expert.

Given the contract text below, identify:
1. Contract Type (e.g., NDA, Employment Agreement, Service Agreement, Lease, SLA, etc.)
2. Industry (e.g., IT, Healthcare, Finance, Manufacturing, Real Estate, etc.)

Return the answer strictly in this JSON format:

{{
  "contract_type": "...",
  "industry": "..."
}}

Contract Text:
----------------
{contract_text}
""")


def classify_contract(state: ContractState):
    chain = prompt | llm
    response = chain.invoke({"contract_text": state["document_text"]})

    result = json.loads(response.content)

    return {
        "contract_type": result["contract_type"],
        "industry": result["industry"]
    }


# -----------------------------
# 4. Build LangGraph
# -----------------------------
graph = StateGraph(ContractState)

graph.add_node("classifier", classify_contract)
graph.set_entry_point("classifier")
graph.add_edge("classifier", END)

app = graph.compile()


# -----------------------------
# 5. Run the Pipeline
# -----------------------------
if __name__ == "__main__":
    file_path = "contract_classifier/data/sample_contract.pdf"

    # Load contract text
    contract_text = load_contract(file_path)

    # Run the classifier
    result = app.invoke({"document_text": contract_text})

    # ✅ Print output with labels
    print("Contract Type:", result["contract_type"])
    print("Industry:", result["industry"])
