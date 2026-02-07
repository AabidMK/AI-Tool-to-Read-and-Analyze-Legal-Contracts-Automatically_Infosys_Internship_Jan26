from pipeline.prompts.final_report_prompt import final_report_prompt

def generate_final_report_node(state, llm):
    prompt = final_report_prompt(
        state["contract_type"],
        state["industry"],
        state["summarized_role_results"]
    )

    response = llm.invoke(prompt)
    state["final_report"] = response.content if hasattr(response, "content") else response

    return state
