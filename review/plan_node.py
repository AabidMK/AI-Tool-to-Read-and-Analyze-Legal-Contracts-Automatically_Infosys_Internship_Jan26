import json
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm import get_llm
from .prompts import review_plan_prompt
from .state import ReviewState

llm = get_llm(temperature=0)

def create_review_plan_node(state: ReviewState) -> ReviewState:
    classification = state.get("classification",{})

    messages = [SystemMessage(content=review_plan_prompt),
                HumanMessage(content=f"""
CONTRACT TYPE: {classification.get("contract_type")}
INDUSTRY: {classification.get("industry")}
"""
                )
    ]

    response = llm.invoke(messages)

    try:
        roles_data = json.loads(response.content)
        review_roles = roles_data.get("review_roles",[])
    except Exception:
        review_roles = []

    return {
        **state,
        "review_roles": review_roles,
        "role_reviews": []
    }