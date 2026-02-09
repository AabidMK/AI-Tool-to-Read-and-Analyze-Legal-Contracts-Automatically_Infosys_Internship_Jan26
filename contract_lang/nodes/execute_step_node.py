from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3")

def execute_step_node(state: dict) -> dict:
    contract_text = state.get("contract_text", "")
    retrieved_clauses = state.get("retrieved_clauses", [])
    review_plan = state.get("review_plan", [])

    reviews = []

    for step in review_plan:
        role = step["role"]
        focus = step["focus"]

        reference_text = "\n\n".join(
            [c.page_content for c in retrieved_clauses]
        )

        prompt = f"""
You are acting as a {role}.

Focus areas:
{focus}

Contract Text:
{contract_text}

Reference Standard Clauses:
{reference_text}

Tasks:
1. Identify risks or weaknesses
2. Highlight missing or weak clauses
3. Provide improvement suggestions
"""

        response = llm.invoke(prompt)

        reviews.append({
            "role": role,
            "analysis": response.content
        })

    return {"role_based_reviews": reviews}
