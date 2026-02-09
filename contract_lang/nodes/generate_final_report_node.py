def generate_final_report_node(state: dict) -> dict:
    contract_type = state.get("contract_type", "Unknown")
    reviews = state.get("role_based_reviews", [])
    missing = state.get("missing_clauses", [])
    suggestions = state.get("suggestions", [])

    report = []
    report.append("📄 CONTRACT REVIEW REPORT")
    report.append("=" * 50)
    report.append(f"Contract Type: {contract_type}\n")

    report.append("🔍 ROLE-BASED ANALYSIS\n")
    for r in reviews:
        report.append(f"▶ {r['role']}")
        report.append(r["analysis"])
        report.append("-" * 40)

    if missing:
        report.append("\n⚠️ MISSING CLAUSES")
        for m in missing:
            report.append(f"- {m}")

    if suggestions:
        report.append("\n💡 IMPROVEMENT SUGGESTIONS")
        for s in suggestions:
            report.append(f"- {s}")

    final_text = "\n".join(report)

    print("\n" + final_text)

    return {"final_report": final_text}
