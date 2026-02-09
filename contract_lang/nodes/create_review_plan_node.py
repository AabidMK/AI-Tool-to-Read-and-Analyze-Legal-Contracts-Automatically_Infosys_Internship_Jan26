def create_review_plan_node(state: dict) -> dict:
    contract_type = state.get("contract_type", "")

    review_plan = []

    if contract_type == "Employment Agreement":
        review_plan = [
            {
                "role": "Employment Law Expert",
                "focus": "Employee rights, termination, labor law compliance"
            },
            {
                "role": "IP Counsel",
                "focus": "Intellectual property ownership and work-for-hire clauses"
            },
            {
                "role": "Compliance Officer",
                "focus": "Statutory compliance and regulatory risks"
            }
        ]

    elif contract_type == "Government Standard (FAR)":
        review_plan = [
            {
                "role": "Government Contracts Specialist",
                "focus": "FAR compliance and government termination rights"
            },
            {
                "role": "Audit & Compliance Expert",
                "focus": "Audit rights, record retention, reporting obligations"
            }
        ]

    else:  # General / fallback
        review_plan = [
            {
                "role": "Commercial Contracts Expert",
                "focus": "Risk allocation, enforceability, liability clauses"
            }
        ]

    return {"review_plan": review_plan}
