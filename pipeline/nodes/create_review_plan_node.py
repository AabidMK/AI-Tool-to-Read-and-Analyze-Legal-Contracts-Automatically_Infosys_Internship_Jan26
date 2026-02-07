import json
from pipeline.prompts.review_plan_prompt import review_plan_prompt

def create_review_plan_node(state, llm):
    prompt = review_plan_prompt(
        state["contract_type"],
        state["industry"]
    )

    response = llm.invoke(prompt)
    text = response.content if hasattr(response, "content") else response

    state["review_plan"] = json.loads(text)
    return state
