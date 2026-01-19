from typing import TypedDict, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

class ContractReviewState(TypedDict):
    file_path: str
    contract_text: str
    contract_type: Optional[str]
    industry: Optional[str]

class ClassificationResult(BaseModel):
    contract_type: str = Field(description="Type of contract like NDA, Employment, Service Agreement")
    industry: str = Field(description="Industry the contract belongs to")    

llm = ChatOpenAI(
    model="qwen/qwen3-4b-thinking-2507",
    base_url="http://localhost:1234/v1",
    api_key="not-needed",
    temperature=0
)


structured_llm = llm.with_structured_output(ClassificationResult)

def extract_text_node(state: ContractReviewState):
    file_path = state["file_path"]

    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file type")

    docs = loader.load()
    text = "\n".join(doc.page_content for doc in docs)

    return {"contract_text": text}

def classify_contract_node(state: ContractReviewState):
    messages = [
        SystemMessage(content="You are a legal contract classification assistant."),
        HumanMessage(content=state["contract_text"])
    ]

    result = structured_llm.invoke(messages)

    return {
        "contract_type": result.contract_type,
        "industry": result.industry
    }

builder = StateGraph(ContractReviewState)

builder.add_node("extract_text", extract_text_node)
builder.add_node("classify_contract", classify_contract_node)

builder.add_edge(START, "extract_text")
builder.add_edge("extract_text", "classify_contract")
builder.add_edge("classify_contract", END)

graph = builder.compile()

initial_state = {
    "file_path": "Employment_Agreement.pdf",
    "contract_text": "",
    "contract_type": None,
    "industry": None
}

result = graph.invoke(initial_state)

print("Contract Type:", result["contract_type"])
print("Industry:", result["industry"])

