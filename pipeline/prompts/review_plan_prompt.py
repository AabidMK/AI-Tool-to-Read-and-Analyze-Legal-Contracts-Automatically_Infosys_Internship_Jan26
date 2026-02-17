def review_plan_prompt(contract_type: str, industry: str) -> str:
    return f"""
You are a senior legal operations planner.

Contract Type: {contract_type}
Industry: {industry}

Task:
Create a role-based legal contract review plan.

Rules:
- Suggest 3 to 5 legal expert roles
- Each role must have a legal specialization
- Each role must include clear focus areas
- Output ONLY valid raw JSON
- Do not include markdown formatting
- Do not include backticks
- Do not include explanations


Expected JSON format:
[
  {{
    "role": "Role Name",
    "focus": ["area 1", "area 2"]
  }}
]
"""
