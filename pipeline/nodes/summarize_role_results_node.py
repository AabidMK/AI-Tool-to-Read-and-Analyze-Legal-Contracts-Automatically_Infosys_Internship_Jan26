def summarize_role_results_node(state, llm):
    summarized_roles = []

    for role_result in state["role_analysis_results"]:
        prompt = f"""
You are a senior legal reviewer.

Summarize the following role-based contract analysis
into a concise, high-signal legal summary.

Role: {role_result['role']}

Issues:
{role_result['issues']}

Missing Clauses:
{role_result['missing_clauses']}

Suggestions:
{role_result['suggestions']}

Rules:
- Focus on the MOST critical risks
- Keep it concise (150–200 words max)
- Formal legal tone
"""

        response = llm.invoke(prompt)
        summary = response.content if hasattr(response, "content") else response

        summarized_roles.append({
            "role": role_result["role"],
            "summary": summary
        })

    state["summarized_role_results"] = summarized_roles
    return state
