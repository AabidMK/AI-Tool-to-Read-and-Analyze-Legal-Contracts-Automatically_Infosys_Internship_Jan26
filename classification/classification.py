import json
import requests
import re

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"


PROMPT_TEMPLATE = """
You are a senior legal document classifier.

Analyze the following contract text and determine:

1. contract_type (specific legal category)
2. industry (specific business sector — must NOT be "General")

Industry must be one of:
Information Technology
Healthcare
Energy & Oil
Finance & Banking
Real Estate
Manufacturing
Construction
Government
Telecommunications
Education
Retail & E-commerce
Biotechnology
Transportation
Entertainment
Professional Services
Hospitality
Pharmaceutical
Insurance

Rules:
- Respond ONLY in valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Output format:

{{
  "contract_type": "...",
  "industry": "..."
}}

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
    "model": "qwen2.5-7b-instruct",
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
    "temperature": 0.1,
    "max_tokens": 400
    }


    response = requests.post(LM_STUDIO_URL, json=payload)
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]

    # Extract first JSON object safely
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        raise ValueError("LLM did not return valid JSON.")

    json_str = match.group()

    try:
        result = json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse LLM JSON response.")

    # Basic validation
    if "contract_type" not in result or "industry" not in result:
        raise ValueError("Missing required classification fields.")

    return result

