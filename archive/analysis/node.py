from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from analysis.schema import ContractAnalysisResult
from classification.llm import get_llm
import re

def clause_exists_in_document(clause_title: str, markdown_text: str) -> bool:
    """
    Conservative presence check using keywords.
    If any key term appears, we treat the clause as present.
    """
    title = clause_title.lower()

    keyword_map = {
        "non-solicitation": [
            "solicit",
            "solicitation",
            "employee covenants",
            "covenant not to compete",
            "restrictive covenant"
        ],
        "intellectual property": [
            "intellectual property",
            "invention",
            "proprietary information",
            "work for hire",
            "assignment"
        ],
        "confidentiality": [
            "confidential",
            "confidential information",
            "non-disclosure"
        ]
    }

    for key, keywords in keyword_map.items():
        if key in title:
            return any(k in markdown_text.lower() for k in keywords)

    return False


def extract_section_titles(markdown_text: str):
    """
    Extract section headings like '## 8. TERMINATION BY THE COMPANY FOR CAUSE'
    """
    return re.findall(r"##\s+(.*)", markdown_text)



llm = get_llm()
parser = PydanticOutputParser(pydantic_object=ContractAnalysisResult)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict JSON generator. "
            "Do not explain. Do not add markdown. "
            "Return ONLY valid JSON."
            "If you incorrectly mark an existing clause as missing, the output is invalid."

        ),
        (
            "human",
            """
You are a legal contract analysis engine.

IMPORTANT RULE:
- A clause must NOT be listed as missing if the contract text already contains a section that serves the same legal purpose, even if wording differs.
- Use section headings and content in the contract text to verify presence.

EXISTING SECTION HEADINGS:
{existing_sections}

use these section titles to confirm whether a clause already exists.

CLAUSE MATCHING RULES:
- Clause titles in retrieved clauses may not exactly match section titles in the contract.
- You MUST treat a clause as PRESENT if the contract contains a section that serves the same legal purpose, even under a different name.
- Example:
  "Non-Solicitation of Employees and Clients" is PRESENT if the contract
  contains sections like "Employee Covenants", "Solicitation of Employees",
  or similar restrictive covenant language.


TASKS:
1. Compare the contract text with each retrieved reference clause.
2. Identify weaknesses, conflicts, or missing legal strength.
3. Suggest improved clause wording where applicable.
4. Identify ONLY standard clauses that are COMPLETELY ABSENT and have NO FUNCTIONAL EQUIVALENT in any contract section or exhibit.

RULES:
- Use retrieved clauses as reference standards
- Missing clauses must be typical for the given contract type
- Be conservative and legally precise

OUTPUT FORMAT:
{format_instructions}

CONTRACT TYPE:
{contract_type}

CONTRACT TEXT:
--------------
{contract_text}

RETRIEVED REFERENCE CLAUSES:
--------------
{retrieved_clauses}
"""
        )
    ]
)

chain = prompt | llm | parser


def analyze_contract_node(state: dict):
    section_titles = extract_section_titles(state["markdown_text"])
    result = chain.invoke(
        {
            "contract_type": state["contract_type"],
            "contract_text": state["markdown_text"][:7000],
            "retrieved_clauses": state["retrieved_clauses"],
            "existing_sections": section_titles,
            "format_instructions": parser.get_format_instructions(),
        }
    )

    analysis = result.dict()
    filtered_missing = []
    for clause in analysis["missing_standard_clauses"]:
        if not clause_exists_in_document(clause, state["markdown_text"]):
            filtered_missing.append(clause)
    analysis["missing_standard_clauses"] = filtered_missing

    if not analysis["missing_standard_clauses"]:
        analysis["overall_risk_summary"] = (
            "No critical standard clauses are missing. "
            "The contract is comprehensive, though some clauses may warrant "
            "strengthening or clarification based on best practices."
        )

    
    return {
        "analysis": analysis
    }
