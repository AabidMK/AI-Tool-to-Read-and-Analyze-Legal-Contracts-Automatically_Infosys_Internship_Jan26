def final_report_prompt(contract_type, industry, role_results):

    return f"""
You are a Senior Corporate Counsel drafting a formal executive contract review memorandum for Board-level review.

Contract Type: {contract_type}
Industry: {industry}

Aggregated Role-Based Findings (Multiple Legal Experts May Have Identified Overlapping Issues):

{role_results}

IMPORTANT CONSOLIDATION INSTRUCTION:

- If multiple roles identify the same issue (e.g., Non-Compete deficiency), consolidate them into ONE unified vulnerability analysis.
- Do NOT repeat the same clause under multiple role headings.
- Aggregate severity logically across roles (e.g., Moderate–High if multiple experts flagged it).
- Present a synthesized executive-level view rather than role-by-role repetition.
- Eliminate redundancy.


Generate a professional, analytical contract review memorandum.

CRITICAL LOGIC RULE:
- The Overall Risk Level must logically align with the highest severity issues identified.
- If any issue is marked "Critical", the Overall Risk Level cannot be lower than High unless explicitly justified.
- Do not create internal contradictions between overall rating and issue severity.

The report must demonstrate deep legal reasoning and avoid generic statements.

=================================================
1. EXECUTIVE RISK ASSESSMENT
=================================================

- Overall Risk Level (Low / Moderate / High / Critical)
- Justify the rating with legal reasoning
- Identify enterprise-level exposure (litigation, tax, fiduciary, regulatory)

=================================================
2. LEGAL VULNERABILITY ANALYSIS
=================================================

For each major vulnerability:

- Clause Reference (if applicable)
- Description of Deficiency
- Applicable Legal Framework (e.g., fiduciary duty principles, deferred compensation rules, labor law, restrictive covenant standards)
- Enforceability Risk
- Likely Litigation Trigger
- Severity (Low / Moderate / High / Critical)
- Business Consequence

Do NOT assign the same severity to all issues. Differentiate realistically.

=================================================
3. INDUSTRY-SPECIFIC RISK CONTEXT
=================================================

Explain how the risks interact specifically with the {industry} sector.
Discuss sector-specific exposure (e.g., IP, regulatory oversight, executive governance, capital structure risk).

=================================================
4. MISSING CLAUSE IMPACT ANALYSIS
=================================================

For each missing clause:

- Why it is standard in {contract_type}
- Legal and operational consequences if omitted
- Risk escalation scenario if dispute occurs

=================================================
5. LITIGATION & FINANCIAL EXPOSURE MODEL
=================================================

Assess:
- Probability of dispute (Low / Moderate / High)
- Likely dispute areas
- Financial exposure categories (bonus dispute, tax penalty, fiduciary breach, restrictive covenant challenge)
- Regulatory exposure

=================================================
6. PRIORITIZED REMEDIATION STRATEGY
=================================================

Tier 1 – Immediate Legal Exposure
Tier 2 – Compliance & Governance Alignment
Tier 3 – Structural & Risk Mitigation Enhancements

Tone:
- Formal executive legal analysis
- Precise and analytical
- Structured using the numbered sections above
- No markdown formatting
- No repetition
- No conversational tone
- Do NOT include:
  - To / From / Date / Subject headers
  - Prepared by / Reviewed by sections
  - Signature blocks
  - Placeholder names
  - Model names
  - References to AI, LLM, or system generation
- The output must begin directly with Section 1 (EXECUTIVE RISK ASSESSMENT)
- End the report after Section 6 (PRIORITIZED REMEDIATION STRATEGY)

"""
