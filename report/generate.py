from typing import Dict, Any


def _format_line(title: str, value: str, indent: int = 0) -> str:
    space = " " * indent
    return f"{space}{title}: {value}"


def _separator(char: str = "=", length: int = 60) -> str:
    return char * length


def generate_final_report(data: Dict[str, Any]) -> str:
    classification = data.get("classification", {})
    clause_analysis = data.get("clause_analysis", [])
    global_analysis = data.get("global_analysis", {})
    role_reviews = data.get("role_reviews", [])

    report = []

    # =========================================================
    # HEADER
    # =========================================================
    report.append(_separator("="))
    report.append("                CONTRACT REVIEW REPORT")
    report.append(_separator("="))
    report.append("")

    # =========================================================
    # OVERVIEW
    # =========================================================
    report.append(_separator("-"))
    report.append("1. CONTRACT OVERVIEW")
    report.append(_separator("-"))
    report.append("")
    report.append(_format_line("Contract Type", classification.get("contract_type", "N/A")))
    report.append(_format_line("Industry", classification.get("industry", "N/A")))
    report.append("")

    # =========================================================
    # CLAUSE LEVEL ANALYSIS
    # =========================================================
    report.append(_separator("-"))
    report.append("2. CLAUSE-LEVEL ANALYSIS")
    report.append(_separator("-"))
    report.append("")

    for idx, clause in enumerate(clause_analysis, 1):
        report.append(f"{idx}. {clause.get('clause_title', 'Unknown Clause')}")
        report.append(_format_line("Presence", clause.get("presence", "N/A"), 4))
        report.append(_format_line("Risk Level", clause.get("risk_level", "N/A"), 4))
        report.append("")

        report.append("    Similarity Summary:")
        report.append(f"        {clause.get('similarity_summary', 'N/A')}")
        report.append("")

        report.append("    Improvement Suggestion:")
        report.append(f"        {clause.get('improvement_suggestion', 'N/A')}")
        report.append("")
        report.append(_separator(".", 60))
        report.append("")

    # =========================================================
    # STRUCTURAL REVIEW
    # =========================================================
    report.append(_separator("-"))
    report.append("3. STRUCTURAL REVIEW")
    report.append(_separator("-"))
    report.append("")

    report.append(
        _format_line(
            "Overall Risk Level",
            global_analysis.get("overall_risk_level", "N/A").upper(),
        )
    )
    report.append("")

    # Missing Clauses
    report.append("Missing Clauses:")
    missing = global_analysis.get("missing_clauses", [])
    if missing:
        for m in missing:
            report.append(f"  - {m}")
    else:
        report.append("  None identified.")
    report.append("")

    # Structural Risks
    report.append("Structural Risks:")
    structural = global_analysis.get("structural_risks", [])
    if structural:
        for r in structural:
            report.append(f"  - {r}")
    else:
        report.append("  None identified.")
    report.append("")

    report.append("Executive Summary:")
    report.append(f"  {global_analysis.get('executive_summary', 'N/A')}")
    report.append("")

    # =========================================================
    # ROLE-BASED REVIEWS
    # =========================================================
    report.append(_separator("-"))
    report.append("4. EXPERT ROLE-BASED REVIEW")
    report.append(_separator("-"))
    report.append("")

    for role in role_reviews:
        report.append(_separator("~", 60))
        report.append(f"Role: {role.get('role', 'Unknown Role')}")
        report.append(
            _format_line(
                "Risk Level",
                role.get("risk_level", "N/A").upper(),
                4
            )
        )
        report.append("")

        # Key Findings
        report.append("    Key Findings:")
        findings = role.get("key_findings", [])

        if findings:
            for f in findings:
                if isinstance(f, dict):
                    issue = f.get("issue", "")
                    desc = f.get("description", "")
                    report.append(f"      - Issue: {issue}")
                    report.append(f"        Description: {desc}")
                else:
                    report.append(f"      - {f}")
        else:
            report.append("      None identified.")
        report.append("")

        # Recommendations
        report.append("    Recommendations:")
        recs = role.get("recommendations", [])

        if recs:
            for r in recs:
                if isinstance(r, dict):
                    action = r.get("action", "")
                    desc = r.get("description", "")
                    report.append(f"      - Action: {action}")
                    report.append(f"        Description: {desc}")
                else:
                    report.append(f"      - {r}")
        else:
            report.append("      None provided.")
        report.append("")

    report.append(_separator("="))
    report.append("END OF REPORT")
    report.append(_separator("="))

    return "\n".join(report)