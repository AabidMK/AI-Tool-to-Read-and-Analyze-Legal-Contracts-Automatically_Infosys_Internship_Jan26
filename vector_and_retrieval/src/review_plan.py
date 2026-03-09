import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def create_review_plan(contract_type, industry):

    prompt = f"""
You are a legal workflow planner.

Contract Type: {contract_type}
Industry: {industry}

Generate a list of legal experts required to review this contract.

Example roles:
- Contract Lawyer
- Compliance Officer
- Risk Analyst
- Financial Auditor
- Intellectual Property Lawyer

Return ONLY a simple list.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "phi3:mini",
            "prompt": prompt,
            "stream": False
        },
        timeout=300
    )

    roles_text = response.json()["response"]

    roles = [r.strip("- ").strip() for r in roles_text.split("\n") if r.strip()]

    return roles