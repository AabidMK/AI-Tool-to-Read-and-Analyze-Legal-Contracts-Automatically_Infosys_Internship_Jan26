import json
import requests


LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"


PROMPT_TEMPLATE = """
You are an expert legal document classifier.

Analyze the following contract text and identify:
1. The contract type (e.g., Employment Agreement, NDA, Service Agreement, Lease, Government Contract, etc.)
2. The industry or domain the contract belongs to (e.g., Information Technology, Healthcare, Finance, Manufacturing, Real Estate, Government, etc.)

Rules:
- Respond ONLY in valid JSON
- Do NOT include explanations or additional text

Contract Text:
\"\"\"
{contract_text}
\"\"\"
"""


def classify_contract_node(contract_text: str) -> dict:
    """
    Sends contract text to a local LLM via LM Studio
    and returns contract_type and industry as JSON.
    """

    prompt = PROMPT_TEMPLATE.format(contract_text=contract_text)

    payload = {
        "model": "local-model",
        "messages": [
            {
                "role": "system",
                "content": "You are a legal expert specializing in contract classification."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1
    }

    response = requests.post(LM_STUDIO_URL, json=payload)
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]

    return json.loads(content)
