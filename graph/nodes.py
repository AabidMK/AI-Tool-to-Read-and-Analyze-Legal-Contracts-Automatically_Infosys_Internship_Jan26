from llm.llm_client import get_llm
from parser.parser_model import extract_text_from_pdf

llm = get_llm()

def extract_text_node(state):
    text = extract_text_from_pdf(state["file_path"])
    return {"contract_text": text}

def classify_contract_node(state):
    prompt = f"""
You are a legal contract classifier.

Return output strictly in JSON:
{{
  "contract_type": "...",
  "industry": "..."
}}

Contract:
{state["contract_text"][:800]}
"""
    response = llm.invoke(prompt)
    return {"classification": response.content}
