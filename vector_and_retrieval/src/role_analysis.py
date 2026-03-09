import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def analyze_by_role(role, contract_text):

    prompt = f"""
You are acting as a {role} reviewing a legal contract.

Contract:
{contract_text}

Provide analysis focused on your role.

Include:
- Issues found
- Risk observations
- Recommendations
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

    return response.json()["response"]