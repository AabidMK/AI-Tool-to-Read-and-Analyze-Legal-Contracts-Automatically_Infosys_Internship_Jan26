import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_final_report(analyses):

    combined = ""

    for role, analysis in analyses.items():
        combined += f"\n\nROLE: {role}\n{analysis}"

    prompt = f"""
You are a senior legal consultant.

Create a professional contract review report based on the following analyses.

{combined}

Report Structure:

1. Executive Summary
2. Key Legal Issues
3. Risk Assessment
4. Compliance Review
5. Missing Clauses
6. Recommendations
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