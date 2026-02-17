import json
from pipeline.prompts.final_report_prompt import final_report_prompt


def generate_final_report_node(state, llm):

    compressed_roles = []

    for role in state["role_analysis_results"]:
        compressed_roles.append({
            "role": role.get("role"),
            "issues": role.get("issues", [])[:8],
            "missing_clauses": role.get("missing_clauses", [])[:8],
            "suggestions": role.get("suggestions", [])[:8]
        })

    role_results_str = json.dumps(compressed_roles)

    prompt = final_report_prompt(
        state["contract_type"],
        state["industry"],
        role_results_str
    )

    response = llm.invoke(prompt)

    state["final_report"] = (
        response.content if hasattr(response, "content") else response
    )

    return state

