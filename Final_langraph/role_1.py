import os
import json
from typing import TypedDict, Optional, List

from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama

from langgraph.graph import StateGraph, END

load_dotenv()

# =====================================================
# LOCAL MODEL (OLLAMA - MISTRAL)
# =====================================================

# llm = ChatOllama(
#     model="mistral",
#     temperature=0
# )


# from langchain_groq import ChatGroq

# llm = ChatGroq(
#     model="openai/gpt-oss-120b",
#     temperature=0,
# )


from langchain_google_genai import ChatGoogleGenerativeAI
import os

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0,
)




# =====================================================
# GRAPH STATE
# =====================================================

class ContractReviewState(TypedDict):
    file_path: str
    contract_text: Optional[str]
    raw_output: Optional[str]
    contract_type: Optional[str]
    industry: Optional[str]
    retrieved_clauses: Optional[List[dict]]
    analysis_result: Optional[dict]
    review_plan: Optional[List[str]]
    role_reviews: Optional[List[dict]]
    final_report: Optional[str]

class ContractMetadata(BaseModel):
    contract_type: str
    industry: str

# =====================================================
# DOCUMENT LOADER (TOKEN SAFE)
# =====================================================

def load_document(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError("Unsupported file format")

    docs = loader.load()
    text = " ".join(doc.page_content for doc in docs)

    # IMPORTANT: keep under token limits
    text = text[:1500]

    return " ".join(text.split())

# =====================================================
# CLASSIFICATION
# =====================================================

def build_classification_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a legal analyst."),
        ("human",
"""
Extract contract_type and industry.

Return ONLY valid JSON:
{{
 "contract_type":"",
 "industry":""
}}

{text}
""")
    ])
    return prompt | llm

# =====================================================
# VECTOR STORE
# =====================================================

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        "legal_clause_faiss",
        embeddings,
        allow_dangerous_deserialization=True,
    )

# =====================================================
# ANALYSIS
# =====================================================

def build_analysis_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior legal contract reviewer."),
        ("human",
"""
Contract Type: {contract_type}

Contract:
{contract_text}

Reference Clauses:
{reference_clauses}

Return ONLY JSON:
{{
 "similarities":[],
 "suggested_improvements":[],
 "missing_clauses":[]
}}
""")
    ])
    return prompt | llm

# =====================================================
# NODES
# =====================================================

def load_contract_node(state):
    text = load_document(state["file_path"])
    return {**state, "contract_text": text}

def classify_contract_node(state):
    chain = build_classification_chain()
    response = chain.invoke({"text": state["contract_text"]})

    text = response.content if hasattr(response, "content") else str(response)
    return {**state, "raw_output": text}

def parse_output_node(state):
    try:
        parsed = json.loads(state["raw_output"])
        metadata = ContractMetadata(**parsed)
        return {
            **state,
            "contract_type": metadata.contract_type,
            "industry": metadata.industry
        }
    except:
        return {
            **state,
            "contract_type": "Service Agreement",
            "industry": "General"
        }

def retrieve_clauses_node(state):
    vectorstore = load_vectorstore()
    docs = vectorstore.similarity_search(
        f"Standard clauses for {state['contract_type']}", k=6
    )

    clauses = [{
        "clause_title": d.metadata.get("clause_title"),
        "clause_text": d.page_content[:400]
    } for d in docs]

    return {**state, "retrieved_clauses": clauses}

def analyze_contract_node(state):
    chain = build_analysis_chain()

    reference_text = "\n\n".join(
        f"{c['clause_title']}:\n{c['clause_text']}"
        for c in state["retrieved_clauses"]
    )

    response = chain.invoke({
        "contract_type": state["contract_type"],
        "contract_text": state["contract_text"],
        "reference_clauses": reference_text
    })

    text = response.content if hasattr(response, "content") else str(response)

    try:
        analysis = json.loads(text)
    except:
        analysis = {"similarities": [], "suggested_improvements": [], "missing_clauses": []}

    return {**state, "analysis_result": analysis}

# =====================================================
# ROLE PLAN
# =====================================================

def create_review_plan_node(state):
    roles = [
        "Legal Risk Analyst",
        "Compliance Expert",
        "Financial Auditor",
        "Data Privacy Specialist",
        "Contract Structure Reviewer"
    ]
    return {**state, "review_plan": roles}

# =====================================================
# ROLE ANALYSIS
# =====================================================

def execute_step_node(state):
    reviews = []

    reference_text = "\n\n".join(
        f"{c['clause_title']}:\n{c['clause_text']}"
        for c in state["retrieved_clauses"]
    )

    for role in state["review_plan"]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a {role}."),
            ("human",
f"""
Review this contract:

{state['contract_text']}

Reference:
{reference_text}

Provide:
- Findings
- Risks
- Recommendations
""")
        ])

        chain = prompt | llm
        response = chain.invoke({})

        text = response.content if hasattr(response, "content") else str(response)

        reviews.append({
            "role_name": role,
            "analysis": text
        })

    return {**state, "role_reviews": reviews}

# =====================================================
# FINAL REPORT
# =====================================================

def generate_final_report_node(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior legal consultant."),
        ("human",
"""
Create a professional legal report.

FORMAT:

# CONTRACT REVIEW REPORT

## Contract Type
{contract_type}

## Industry
{industry}

## General Analysis
{analysis}

## Expert Reviews
{role_reviews}

## Final Recommendations
Provide bullet points.
""")
    ])

    chain = prompt | llm

    response = chain.invoke({
        "contract_type": state["contract_type"],
        "industry": state["industry"],
        "analysis": json.dumps(state["analysis_result"], indent=2),
        "role_reviews": json.dumps(state["role_reviews"], indent=2)
    })

    text = response.content if hasattr(response, "content") else str(response)

    return {**state, "final_report": text}

# =====================================================
# GRAPH
# =====================================================

def build_contract_graph():
    graph = StateGraph(ContractReviewState)

    graph.add_node("load_contract", load_contract_node)
    graph.add_node("classify_contract", classify_contract_node)
    graph.add_node("parse_output", parse_output_node)
    graph.add_node("retrieve_clauses", retrieve_clauses_node)
    graph.add_node("analyze_contract", analyze_contract_node)
    graph.add_node("create_review_plan", create_review_plan_node)
    graph.add_node("execute_step", execute_step_node)
    graph.add_node("generate_final_report", generate_final_report_node)

    graph.set_entry_point("load_contract")

    graph.add_edge("load_contract", "classify_contract")
    graph.add_edge("classify_contract", "parse_output")
    graph.add_edge("parse_output", "retrieve_clauses")
    graph.add_edge("retrieve_clauses", "analyze_contract")
    graph.add_edge("analyze_contract", "create_review_plan")
    graph.add_edge("create_review_plan", "execute_step")
    graph.add_edge("execute_step", "generate_final_report")
    graph.add_edge("generate_final_report", END)

    return graph.compile()

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    FILE_PATH = "Service_agree_1.pdf"

    app = build_contract_graph()

    result = app.invoke({
        "file_path": FILE_PATH,
        "contract_text": None,
        "raw_output": None,
        "contract_type": None,
        "industry": None,
        "retrieved_clauses": None,
        "analysis_result": None,
        "review_plan": None,
        "role_reviews": None,
        "final_report": None,
    })

    print("\nFINAL REPORT:\n")
    print(result["final_report"])
    print(result["contract_type"])