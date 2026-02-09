from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate


def analyze_contract_node(state: dict):
    """
    Compares contract text with retrieved reference clauses
    1. Contextual analysis
    2. Suggestions for improvement
    3. Missing clause detection
    """

    contract_text = state["contract_text"]
    contract_type = state["contract_type"]
    retrieved_clauses = state["retrieved_clauses"]

    # Combine retrieved clauses into readable context
    reference_clauses = ""
    for c in retrieved_clauses:
        reference_clauses += f"\n--- {c.metadata['clause_title']} ---\n{c.page_content}\n"

    llm = ChatOllama(
        model="llama3",
        temperature=0.2
    )

    prompt = PromptTemplate(
        input_variables=[
            "contract_type",
            "contract_text",
            "reference_clauses"
        ],
        template="""
You are a legal contract analysis assistant.

Contract Type:
{contract_type}

-----------------------
CONTRACT TEXT:
{contract_text}
-----------------------

REFERENCE STANDARD CLAUSES:
{reference_clauses}

TASKS:

1. CONTEXTUAL ANALYSIS
- Compare the contract text with the reference clauses.
- Identify weak, unclear, or risky wording.

2. SUGGESTION ENGINE
- Suggest improved or stronger clause language.
- Clearly show suggested rewritten text.

3. OMISSION DETECTION
- Identify standard clauses expected for this contract type
  that are missing from the contract.
- List them clearly with a short explanation.

OUTPUT FORMAT (STRICT):

Contextual Analysis:
- ...

Suggestions:
- Clause Name:
  Suggested Text:

Missing Clauses:
- Clause Name: Reason
"""
    )

    response = llm.invoke(
        prompt.format(
            contract_type=contract_type,
            contract_text=contract_text,
            reference_clauses=reference_clauses
        )
    )

    print("\n🧠 Contract Analysis Result:\n")
    print(response.content)

    return {
        "analysis_result": response.content
    }
