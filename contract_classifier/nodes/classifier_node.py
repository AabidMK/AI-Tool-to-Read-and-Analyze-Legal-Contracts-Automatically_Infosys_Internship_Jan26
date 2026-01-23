# nodes/classifier_node.py

from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

# Local small model (fast)
chat_model = ChatOllama(
    model="gemma:2b",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a legal contract classifier. Return ONLY valid JSON."),
    ("human", """
Classify the following contract.

Return JSON only in this format:
{{
  "contract_type": "...",
  "industry": "..."
}}

Contract Text:
{contract_text}
""")
])

def classify_contract(contract_text: str):
    messages = prompt.format_messages(contract_text=contract_text)
    response = chat_model.invoke(messages)
    return response.content
