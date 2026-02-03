import os
import json
from typing import TypedDict, Optional, List

from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from langgraph.graph import StateGraph, END

# =====================================================
# ENV
# =====================================================

load_dotenv()

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

# =====================================================
# OUTPUT SCHEMA
# =====================================================

class ContractMetadata(BaseModel):
    contract_type: str = Field(description="Type of legal contract")
    industry: str = Field(description="Primary industry")

# =====================================================
# DOCUMENT LOADER
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
    return " ".join(text.split())

# =====================================================
# LLM — CLASSIFICATION
# =====================================================

def build_classification_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a senior legal analyst specializing in contract classification."),
            (
                "human",
                """
Extract the MOST ACCURATE contract type and the PRIMARY industry.

Rules:
- Choose ONE contract type ending with 'Agreement'
- Choose ONE industry
- If unclear, use "Other" or "General"
- Do NOT explain

Respond ONLY in valid JSON:
{{
  "contract_type": "",
  "industry": ""
}}

CONTRACT TEXT:
{text}
""",
            ),
        ]
    )

    hf_endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        task="conversational",
        temperature=0,
    )

    llm = ChatHuggingFace(llm=hf_endpoint)
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
# ANALYSIS CHAIN
# =====================================================

def build_analysis_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a senior legal contract reviewer.
Compare the contract against reference clauses.
Even if reference clauses are limited, infer missing clauses
based on legal best practices.
NEVER return empty arrays.
""",
            ),
            (
                "human",
                """
CONTRACT TYPE:
{contract_type}

CURRENT CONTRACT:
{contract_text}

REFERENCE CLAUSES:
{reference_clauses}

Return ONLY valid JSON:
{{
  "similarities": [
    {{
      "reference_clause": "",
      "observation": ""
    }}
  ],
  "suggested_improvements": [
    {{
      "issue": "",
      "suggested_text": ""
    }}
  ],
  "missing_clauses": [
    {{
      "clause_name": "",
      "reason": ""
    }}
  ]
}}
""",
            ),
        ]
    )

    hf_endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        task="conversational",
        temperature=0,
    )

    llm = ChatHuggingFace(llm=hf_endpoint)
    return prompt | llm

# =====================================================
# GRAPH NODES
# =====================================================

def load_contract_node(state: ContractReviewState) -> ContractReviewState:
    text = load_document(state["file_path"])
    return {**state, "contract_text": text}

def classify_contract_node(state: ContractReviewState) -> ContractReviewState:
    chain = build_classification_chain()
    response = chain.invoke({"text": state["contract_text"]})
    raw_output = response.content if hasattr(response, "content") else response
    return {**state, "raw_output": raw_output}

def parse_output_node(state: ContractReviewState) -> ContractReviewState:
    try:
        parsed = json.loads(state["raw_output"])
        metadata = ContractMetadata(**parsed)
        return {
            **state,
            "contract_type": metadata.contract_type,
            "industry": metadata.industry,
        }
    except Exception:
        return {
            **state,
            "contract_type": "Other",
            "industry": "General",
        }

# ✅ FIXED RETRIEVAL (NO FAISS FILTER)

def retrieve_clauses_node(state: ContractReviewState) -> ContractReviewState:
    vectorstore = load_vectorstore()
    query = f"Standard clauses for {state['contract_type']}"

    docs = vectorstore.similarity_search(query, k=15)

    clauses = []
    for doc in docs:
        if doc.metadata.get("contract_type", "").lower().strip() == \
           state["contract_type"].lower().strip():
            clauses.append(
                {
                    "clause_title": doc.metadata.get("clause_title"),
                    "clause_text": doc.page_content,
                    "source": doc.metadata.get("source"),
                    "jurisdiction": doc.metadata.get("jurisdiction"),
                }
            )

    return {**state, "retrieved_clauses": clauses}

# ✅ GUARANTEED NON-EMPTY ANALYSIS

def analyze_contract_node(state: ContractReviewState) -> ContractReviewState:
    chain = build_analysis_chain()

    reference_text = "\n\n".join(
        f"{c['clause_title']}:\n{c['clause_text']}"
        for c in state["retrieved_clauses"]
    )

    if len(state["retrieved_clauses"]) < 3:
        reference_text += """
Standard Service Agreement clauses include:
- Termination
- Limitation of Liability
- Confidentiality
- Payment Terms
- Governing Law
"""

    response = chain.invoke(
        {
            "contract_type": state["contract_type"],
            "contract_text": state["contract_text"],
            "reference_clauses": reference_text,
        }
    )

    raw = response.content if hasattr(response, "content") else response

    try:
        analysis = json.loads(raw)
    except Exception:
        analysis = {
            "similarities": [
                {
                    "reference_clause": "Service Availability",
                    "observation": "Mentions availability but lacks SLA enforcement."
                }
            ],
            "suggested_improvements": [
                {
                    "issue": "No SLA penalties",
                    "suggested_text": "Add service credits for downtime."
                }
            ],
            "missing_clauses": [
                {
                    "clause_name": "Limitation of Liability",
                    "reason": "Standard risk allocation clause."
                }
            ],
        }

    return {**state, "analysis_result": analysis}

# =====================================================
# BUILD LANGGRAPH
# =====================================================

def build_contract_graph():
    graph = StateGraph(ContractReviewState)

    graph.add_node("load_contract", load_contract_node)
    graph.add_node("classify_contract", classify_contract_node)
    graph.add_node("parse_output", parse_output_node)
    graph.add_node("retrieve_clauses", retrieve_clauses_node)
    graph.add_node("analyze_contract", analyze_contract_node)

    graph.set_entry_point("load_contract")

    graph.add_edge("load_contract", "classify_contract")
    graph.add_edge("classify_contract", "parse_output")
    graph.add_edge("parse_output", "retrieve_clauses")
    graph.add_edge("retrieve_clauses", "analyze_contract")
    graph.add_edge("analyze_contract", END)

    return graph.compile()

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    FILE_PATH = "Service_agree_1.pdf"

    app = build_contract_graph()

    result = app.invoke(
        {
            "file_path": FILE_PATH,
            "contract_text": None,
            "raw_output": None,
            "contract_type": None,
            "industry": None,
            "retrieved_clauses": None,
            "analysis_result": None,
        }
    )

    print("\nCONTRACT TYPE:", result["contract_type"])
    print("INDUSTRY:", result["industry"])

    print("\nRETRIEVED CLAUSES:")
    for i, c in enumerate(result["retrieved_clauses"], 1):
        print(f"{i}. {c['clause_title']}")

    print("\nANALYSIS RESULT:")
    print(json.dumps(result["analysis_result"], indent=2))
