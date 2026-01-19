from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

llm = Ollama(model="llama3")

prompt = PromptTemplate(
    input_variables=["contract_text"],
    template="""
You are a legal AI.

Read the contract below and identify:
1. Contract Type
2. Industry

Return ONLY valid JSON in this format:
{{
  "contract_type": "...",
  "industry": "..."
}}

Contract:
{contract_text}
"""
)

def classify_contract_node(state: dict):
    chain = prompt | llm
    response = chain.invoke({"contract_text": state["contract_text"]})
    return {"classification": response}
