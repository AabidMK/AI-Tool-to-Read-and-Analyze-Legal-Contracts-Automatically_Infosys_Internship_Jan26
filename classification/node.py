import json
from typing import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm import get_llm
from .prompt import classification_prompt

class ClassificationState(TypedDict):
    contract_text: str
    classification: dict

llm = get_llm(temperature=0)

def classification_node(state: ClassificationState) -> ClassificationState:
    contract_text = state["contract_text"]

    messages = [
        SystemMessage(content=classification_prompt),
        HumanMessage(content=contract_text)
    ]

    response = llm.invoke(messages)
    classification = json.loads(response.content)

    return {
        "contract_text": contract_text,
        "classification": classification
    }