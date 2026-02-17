import json
from pipeline.prompts.role_analysis_prompt import role_analysis_prompt
import re

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

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            continue  # skip invalid role safely

        json_str = match.group()

        try:
            parsed = json.loads(json_str)
            role_results.append(parsed)
        except json.JSONDecodeError:
            continue

    state["role_analysis_results"] = role_results
    return state
