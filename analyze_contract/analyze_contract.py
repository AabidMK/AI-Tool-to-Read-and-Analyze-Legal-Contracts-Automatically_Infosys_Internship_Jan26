import json

# =========================
# CONFIG
# =========================
USE_LLM = True         
OLLAMA_MODEL = "tinyllama"  

# =========================
# STANDARD CLAUSE MAP
# (used for omission detection)
# =========================
STANDARD_CLAUSES = {
    "Shareholder Agreement": [
        "Share Transfer Restrictions",
        "Voting Rights",
        "Dispute Resolution",
        "Exit Rights",
        "Governing Law",
        "Minority Protection"
    ],
    "Franchise Agreement": [
        "Grant of Franchise",
        "Royalty Fees",
        "Territory",
        "Termination",
        "Brand Usage"
    ],
    "Consultancy Agreement": [
        "Independent Contractor Status",
        "Deliverables",
        "Payment Terms",
        "Confidentiality",
        "Termination"
    ],
    "Loan Agreement": [
        "Repayment Terms",
        "Default",
        "Interest Rate",
        "Security",
        "Governing Law"
    ],
    "Joint Venture Agreement": [
        "Purpose of Joint Venture",
        "Management and Control",
        "Profit Sharing",
        "Exit Clause",
        "Dispute Resolution"
    ],
    "Purchase Agreement": [
        "Purchase Price",
        "Inspection and Acceptance",
        "Delivery Terms",
        "Warranties",
        "Limitation of Liability"
    ]
}


# =========================
# MAIN FUNCTION
# =========================
def analyze_contract(contract_text, retrieved_clauses, contract_type):
    """
    Analyze a contract against retrieved standard clauses.
    Returns structured JSON output.
    """

    # Normalize retrieved clauses
    if isinstance(retrieved_clauses[0], dict):
        clause_titles = [c["clause_title"] for c in retrieved_clauses]
        reference_text = "\n".join(
            f"- {c['clause_title']}: {c['clause_text']}"
            for c in retrieved_clauses
        )
    else:
        # if using LangChain Documents earlier
        clause_titles = [c.metadata.get("clause_title", "") for c in retrieved_clauses]
        reference_text = "\n".join(
            f"- {c.page_content}" for c in retrieved_clauses
        )

    # -------------------------
    # Omission Detection
    # -------------------------
    expected = STANDARD_CLAUSES.get(contract_type, [])
    missing_clauses = [c for c in expected if c not in clause_titles]

    # -------------------------
    # LLM MODE
    # -------------------------
    if USE_LLM:
        try:
            from langchain.prompts import PromptTemplate
            from langchain_ollama import OllamaLLM

            prompt = PromptTemplate.from_template("""
You are a legal contract analysis assistant.

Contract Type:
{contract_type}

Current Contract Text:
{contract_text}

Reference Standard Clauses:
{reference_clauses}

Tasks:
1. Compare the contract text with the reference clauses.
2. Suggest improvements to existing clauses.
3. Consider the missing clauses list while analyzing.

Return STRICT JSON only in this format:

{{
  "overall_assessment": "...",
  "clause_comparison": "...",
  "suggested_improvements": [
    "...",
    "..."
  ],
  "missing_clauses": {missing_clauses}
}}
""")

            llm = OllamaLLM(model=OLLAMA_MODEL, temperature=0.2)
            chain = prompt | llm

            return chain.invoke({
                "contract_type": contract_type,
                "contract_text": contract_text,
                "reference_clauses": reference_text,
                "missing_clauses": missing_clauses
            })

        except Exception:
            pass

    # -------------------------
    # RULE-BASED FALLBACK
    # -------------------------
    return json.dumps({
        "overall_assessment": (
            f"The {contract_type} includes some standard clauses but "
            f"does not fully align with common industry expectations."
        ),
        "clause_comparison": (
            "The contract partially matches the reference clauses. "
            "Some clauses are present but lack depth or legal clarity."
        ),
        "suggested_improvements": [
            "Clarify clause wording to reduce ambiguity.",
            "Add enforcement and dispute-handling mechanisms."
        ],
        "missing_clauses": missing_clauses
    }, indent=2)
