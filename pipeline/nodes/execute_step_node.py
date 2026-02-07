import json
from pipeline.prompts.role_analysis_prompt import role_analysis_prompt

def execute_step_node(state, llm):
    role_results = []

    for role_plan in state["review_plan"]:
        prompt = role_analysis_prompt(
            role_plan["role"],
            role_plan["focus"],
            state["contract_text"],
            state["retrieved_clauses"]
        )

        response = llm.invoke(prompt)
        text = response.content if hasattr(response, "content") else response

        role_results.append(json.loads(text))

    state["role_analysis_results"] = role_results
    return state
