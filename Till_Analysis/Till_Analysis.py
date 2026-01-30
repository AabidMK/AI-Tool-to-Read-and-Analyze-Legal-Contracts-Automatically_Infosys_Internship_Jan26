from typing import TypedDict, List
import json
import chromadb
from sentence_transformers import SentenceTransformer
from docling.document_converter import DocumentConverter
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, START, END

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
llm = Ollama(model="gpt-oss:20b")

chroma_client = chromadb.Client()
clause_collection = chroma_client.get_or_create_collection("legal_clauses")

class ContractState(TypedDict):
    legal_text: str
    agreement_type: str
    industry: str
    retrieved_clauses: List[dict]
    analysis: dict

def ingest_clauses():
    with open("clause.json", "r") as f:
        clauses = json.load(f)

    documents, metadatas, ids = [], [], []

    for c in clauses:
        documents.append(c["clause_text"])
        ids.append(c["clause_id"])
        metadatas.append({
            "contract_type": c["contract_type"],
            "clause_title": c["clause_title"],
            "jurisdiction": c["jurisdiction"]
        })

    embeddings = embedding_model.encode(documents).tolist()

    clause_collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

if clause_collection.count() == 0:
    ingest_clauses()

def load_document() -> str:
    converter = DocumentConverter()
    result = converter.convert("./NDA.pdf")
    return result.document.export_to_text()

def classification_node(state: ContractState):
    prompt = ChatPromptTemplate.from_template(
        """
Return ONLY valid JSON.

{{
  "agreement_type": "...",
  "industry": "..."
}}

If unclear:
"Unknown Agreement"
"Unknown Industry"

Document:
{text}
"""
    )

    parser = JsonOutputParser()
    chain = prompt | llm | parser
    output = chain.invoke({"text": state["legal_text"]})

    return {
        "agreement_type": output["agreement_type"],
        "industry": output["industry"]
    }

def retrieval_node(state: ContractState):
    if state["agreement_type"] == "Unknown Agreement":
        return {"retrieved_clauses": []}

    query_embedding = embedding_model.encode(state["legal_text"]).tolist()

    results = clause_collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        where={"contract_type": state["agreement_type"]}
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "clause_id": results["ids"][0][i],
            "clause_title": results["metadatas"][0][i]["clause_title"],
            "clause_text": results["documents"][0][i]
        })

    return {"retrieved_clauses": retrieved}

def analyze_contract_node(state: ContractState):
    prompt = ChatPromptTemplate.from_template(
    """
    You are a legal contract analyst.

    Tasks:
    1. Compare the document with reference clauses
    2. Suggest improved wording where applicable
    3. Identify missing standard clauses

    Return JSON ONLY.

    {{
    "differences": [],
    "suggested_improvements": [],
    "missing_clauses": []
    }}

    Document:
    {document}

    Reference Clauses:
    {clauses}
    """)

    chain = prompt | llm | JsonOutputParser()
    analysis = chain.invoke({"document": state["legal_text"], "clauses": json.dumps(state["retrieved_clauses"])})

    return {"analysis": analysis}

graph = StateGraph(ContractState)
graph.add_node("classification", classification_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("analysis", analyze_contract_node)
graph.add_edge(START, "classification")
graph.add_edge("classification", "retrieval")
graph.add_edge("retrieval", "analysis")
graph.add_edge("analysis", END)

app = graph.compile()
initial_state = {
    "legal_text": load_document()
}
final_state = app.invoke(initial_state)

print("\nAgreement Type:", final_state["agreement_type"])
print("Industry:", final_state["industry"])
print("\nAnalysis Result:\n")
print(json.dumps(final_state["analysis"], indent=2))
