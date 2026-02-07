def final_report_prompt(contract_type, industry, role_results):
    return f"""
You are a senior legal reviewer.

Contract Type: {contract_type}
Industry: {industry}

Role-Based Analysis Results:
{role_results}

Generate a professional contract review report with:
- Executive Summary
- Role-wise findings
- Overall recommendations
- Clear and formal legal tone
"""
