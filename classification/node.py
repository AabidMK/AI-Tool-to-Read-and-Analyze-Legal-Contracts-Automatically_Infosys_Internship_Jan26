from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from classification.schema import ContractClassification
from classification.llm import get_llm

llm = get_llm()
parser = PydanticOutputParser(pydantic_object=ContractClassification)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict JSON generator. "
            "Do not explain. Do not summarize. "
            "Return ONLY valid JSON. No markdown. No text."
        ),
        (
            "human",
            """
Classify the contract below.

Rules:
- Output must be VALID JSON
- Output must contain ONLY the keys shown
- Do NOT add extra text

Output format:
{{
  "contract_type": "string",
  "industry": "string"
}}

Contract text:
--------------
{contract_text}
"""
        )
    ]
)


chain = prompt | llm | parser


def classify_contract(markdown_text: str) -> dict:
    MAX_CHARS = 6000  # limit input size for reliable JSON output
    truncated_text = markdown_text[:MAX_CHARS]

    try:
        result = chain.invoke({"contract_text": truncated_text})
        return result.dict()
    except Exception as e:
        raise RuntimeError(
            "LLM did not return valid JSON. "
            "Try reducing input size or strengthening the prompt."
        ) from e


from vectorstore.chroma_store import load_chroma

# Load vector DB once (important)
vectorstore = load_chroma()

def retrieval_node(state: dict) -> dict:
    """
    LangGraph Retrieval Node

    Expected state:
    {
        "query": str,
        "contract_type": str
    }
    """

    query = state["query"]
    contract_type = state["contract_type"]

    results = vectorstore.similarity_search_with_score(
        query=query,
        k=5,
        filter={"contract_type": contract_type}
    )

    retrieved_clauses = []

    for doc, score in results:
        retrieved_clauses.append({
            "clause_title": doc.metadata.get("clause_title"),
            "clause_text": doc.page_content,
            "contract_type": doc.metadata.get("contract_type"),
            "score": round(score, 4)
        })

    return {
        "retrieved_clauses": retrieved_clauses
    }