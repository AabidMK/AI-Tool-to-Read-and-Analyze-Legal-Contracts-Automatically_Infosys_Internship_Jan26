import json
import asyncio
from langchain_core.messages import SystemMessage, HumanMessage
from config.llm import get_llm
from .state import ReviewState
from .prompts import role_analysis_prompt


llm = get_llm(temperature=0)


async def analyze_single_role(role, contract_text):
    role_name = role.get("role_name")
    focus_area = role.get("focus_area")

    messages = [
        SystemMessage(content=role_analysis_prompt),
        HumanMessage(
            content=f"""
ROLE: {role_name}
FOCUS AREA: {focus_area}

----- CONTRACT TEXT -----
{contract_text}
"""
        )
    ]

    response = await llm.ainvoke(messages)

    try:
        return json.loads(response.content)
    except Exception:
        return {
            "role": role_name,
            "key_findings": ["Parsing failed"],
            "risk_level": "Unknown",
            "recommendations": ["Manual review required"]
        }


def execute_roles_parallel_node(state: ReviewState) -> ReviewState:
    contract_text = state.get("contract_text", "")
    review_roles = state.get("review_roles", [])

    async def run_all():
        tasks = [
            analyze_single_role(role, contract_text)
            for role in review_roles
        ]
        return await asyncio.gather(*tasks)

    role_reviews = asyncio.run(run_all())

    return {
        **state,
        "role_reviews": role_reviews
    }