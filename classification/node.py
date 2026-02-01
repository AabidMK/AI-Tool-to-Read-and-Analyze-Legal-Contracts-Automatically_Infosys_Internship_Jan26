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
    result = chain.invoke({"contract_text": markdown_text[:6000]})
    return result.dict()