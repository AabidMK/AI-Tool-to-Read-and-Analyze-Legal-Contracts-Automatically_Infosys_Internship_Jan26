import requests


OLLAMA_URL = "http://localhost:11434/api/generate"


def analyze_contract(document_text, clauses):

    reference = "\n\n".join(
        [f"{c['title']}: {c['text']}" for c in clauses]
    )

    prompt = f"""
You are a legal contract analysis AI.

TASKS:

1. Compare the contract text with standard clauses.
2. Suggest improvements.
3. Identify missing clauses.

REFERENCE CLAUSES:
{reference}

DOCUMENT TEXT:
{document_text}

Return structured response:

IMPROVEMENTS:
...

MISSING CLAUSES:
...
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