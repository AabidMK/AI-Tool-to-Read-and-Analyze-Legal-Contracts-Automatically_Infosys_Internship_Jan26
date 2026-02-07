def role_analysis_prompt(role, focus, contract_text, reference_clauses):
    return f"""
You are acting as a {role}.

Your review focus areas:
{focus}

Contract Text:
{contract_text}

Reference Clauses:
{reference_clauses}

Tasks:
1. Identify legal issues or weaknesses
2. Identify missing but standard clauses
3. Suggest concrete improvements

Respond ONLY in JSON format:
{{
  "role": "{role}",
  "issues": [],
  "missing_clauses": [],
  "suggestions": []
}}
"""
