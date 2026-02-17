def role_analysis_prompt(role, focus, contract_text, reference_clauses):
    return f"""
You are acting as a {role}, performing a professional legal review.

Your focus areas:
{focus}

Contract Text:
{contract_text}

Reference Clauses (Industry Standard Examples):
{reference_clauses}

INSTRUCTIONS:

You must conduct a structured legal analysis.

For each relevant reference clause:

1. Determine:
   - Fully Present
   - Partially Present
   - Missing

2. If partially present:
   - Identify specific deficiencies
   - Explain what language is insufficient

3. If missing:
   - Explain why this clause is standard for this contract type
   - Explain risk exposure if omitted

For each issue, provide:

- Legal basis (fiduciary, labor, tax, governance, restrictive covenant, etc.)
- Enforceability risk
- Likely litigation trigger
- Severity (Low / Moderate / High / Critical)
- Business consequence

IMPORTANT:
- Do not assign identical severity to all issues.
- Severity must be logically justified.
- Consider executive-level exposure if applicable.

Respond ONLY in raw JSON.
No markdown.
No commentary.

Required JSON format:

{{
  "role": "{role}",
  "issues": [
    {{
      "clause_name": "...",
      "status": "Fully Present / Partially Present / Missing",
      "deficiency": "...",
      "legal_basis": "...",
      "enforceability_risk": "...",
      "litigation_trigger": "...",
      "severity": "Low/Moderate/High/Critical",
      "business_consequence": "..."
    }}
  ],
  "missing_clauses": [
    {{
      "clause_name": "...",
      "why_standard": "...",
      "risk_if_omitted": "...",
      "escalation_scenario": "..."
    }}
  ],
  "suggestions": [
    {{
      "problem": "...",
      "recommended_fix": "...",
      "legal_improvement": "..."
    }}
  ]
}}
"""
