import json
from typing import TypedDict

from pypdf import PdfReader
from docx import Document
import requests

from langgraph.graph import StateGraph, END


class ContractState(TypedDict, total=False):
    file_path: str
    document_text: str
    contract_type: str
    industry: str



def extract_text_node(state: ContractState):
    file_path = state["file_path"]

    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        text = "\n".join(
            page.extract_text() for page in reader.pages if page.extract_text()
        )

    elif file_path.lower().endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError("Only PDF and DOCX files are supported")

    return {"document_text": text}


def classify_contract_node(state: ContractState):
    import json
    import requests

 
    MAX_CHARS = 3000
    text = state["document_text"][:MAX_CHARS]

    prompt = f"""
You are a contract classifier.

From the text below, identify:
- contract_type
- industry

Respond ONLY in JSON.

Text:
{text}

JSON:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3:mini",   # must match `ollama list`
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 200
            }
        },
        timeout=600
    )

    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.text}")

    data = response.json()

    try:
        result = json.loads(data["response"])
    except Exception:
        raise RuntimeError(f"Invalid JSON from model: {data['response']}")

    return {
        "contract_type": result.get("contract_type", "Unknown"),
        "industry": result.get("industry", "Unknown"),
    }


def build_graph():
    graph = StateGraph(ContractState)

    graph.add_node("extract_text", extract_text_node)
    graph.add_node("classify_contract", classify_contract_node)

    graph.set_entry_point("extract_text")
    graph.add_edge("extract_text", "classify_contract")
    graph.add_edge("classify_contract", END)

    return graph.compile()


def main():
    file_path = r"C:\Users\RISHIRAJSINGH\Downloads\sample.pdf"

    app = build_graph()

    result = app.invoke({
        "file_path": file_path
    })

    print("\n CLASSIFICATION RESULT")
    print("Contract Type:", result["contract_type"])
    print("Industry:", result["industry"])


if __name__ == "__main__":
    main()
