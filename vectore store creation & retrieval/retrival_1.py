import os
import json
from typing import TypedDict, Optional, List

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
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



# ENV


load_dotenv()



# GRAPH STATE


class ContractReviewState(TypedDict):
    file_path: str
    contract_text: Optional[str]
    raw_output: Optional[str]
    contract_type: Optional[str]
    industry: Optional[str]
    retrieved_clauses: Optional[List[dict]]



# OUTPUT SCHEMA


class ContractMetadata(BaseModel):
    contract_type: str = Field(description="Type of legal contract")
    industry: str = Field(description="Primary industry")



# DOCUMENT LOADER


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



# LLM CHAIN (CLASSIFICATION)


def build_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior legal analyst specializing in contract classification.",
            ),
            (
                "human",
                """
Extract the MOST ACCURATE contract type and the PRIMARY industry.

Rules:
- Choose ONE contract type that will end with agreement ex: Service agreement
- Choose ONE industry
- If unclear, use "Other" or "General"
- Do NOT explain

Respond ONLY in valid JSON EXACTLY like this:
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
    
    #llm = ChatGoogleGenerativeAI(model='gemini-2.5-pro')
    return prompt | llm




# def build_chain():
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 "You are a senior legal analyst specializing in contract classification.",
#             ),
#             (
#                 "human",
#                 """
# Extract the MOST ACCURATE contract type and the PRIMARY industry.

# Rules:
# - Choose ONE contract type
# - Choose ONE industry
# - If unclear, use "Other" or "General"
# - Do NOT explain

# Respond ONLY in valid JSON EXACTLY like this:
# {{
#   "contract_type": "",
#   "industry": ""
# }}

# CONTRACT TEXT:
# {text}
# """,
#             ),
#         ]
#     )

#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         temperature=0
#     )

#     return prompt | llm





# VECTOR STORE LOADER


def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        "legal_clause_faiss",
        embeddings,
        allow_dangerous_deserialization=True
    )



# GRAPH NODES


def load_contract_node(state: ContractReviewState) -> ContractReviewState:
    text = load_document(state["file_path"])
    return {**state, "contract_text": text}


def classify_contract_node(state: ContractReviewState) -> ContractReviewState:
    chain = build_chain()
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


def retrieve_clauses_node(state: ContractReviewState) -> ContractReviewState:
    vectorstore = load_vectorstore()

    query = f"Key legal clauses for a {state['contract_type']}"

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": {
                "contract_type": state["contract_type"]
            }
        }
    )

    docs = retriever.invoke(query)

    clauses = [
        {
            "clause_title": doc.metadata.get("clause_title"),
            "clause_text": doc.page_content,
            "source": doc.metadata.get("source"),
            "jurisdiction": doc.metadata.get("jurisdiction"),
        }
        for doc in docs
    ]

    return {**state, "retrieved_clauses": clauses}



# BUILD LANGGRAPH


def build_contract_graph():
    graph = StateGraph(ContractReviewState)

    graph.add_node("load_contract", load_contract_node)
    graph.add_node("classify_contract", classify_contract_node)
    graph.add_node("parse_output", parse_output_node)
    graph.add_node("retrieve_clauses", retrieve_clauses_node)

    graph.set_entry_point("load_contract")

    graph.add_edge("load_contract", "classify_contract")
    graph.add_edge("classify_contract", "parse_output")
    graph.add_edge("parse_output", "retrieve_clauses")
    graph.add_edge("retrieve_clauses", END)

    return graph.compile()



# MAIN


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
        }
    )

    print("\nCONTRACT ANALYSIS RESULT\n")
    print("Contract Type:", result["contract_type"])
    print("Industry:", result["industry"])

    print("\nRELEVANT CLAUSES:\n")
    for i, clause in enumerate(result["retrieved_clauses"], 1):
        print(f"{i}. {clause['clause_title']}")
        print(clause["clause_text"])
        print("Source:", clause["source"])
        print("Jurisdiction:", clause["jurisdiction"])
        print("-" * 60)
