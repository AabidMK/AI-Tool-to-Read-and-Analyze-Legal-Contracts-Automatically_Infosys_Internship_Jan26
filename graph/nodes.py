import json
from llm.llm_client import get_llm
from parser.parser_model import extract_text_from_pdf

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

llm = get_llm()


def extract_text_node(state):
    text = extract_text_from_pdf(state["file_path"])
    return {"contract_text": text}


def classify_contract_node(state):
    prompt = f"""
You are a legal contract classifier.

Return output strictly in JSON:
{{
  "contract_type": "...",
  "industry": "..."
}}

Contract:
{state["contract_text"][:3000]}
"""
    response = llm.invoke(prompt)
    raw = response.content.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # minimal cleanup for common LLM junk , coz before code was giving contract type and industry as null
        cleaned = (
            raw.replace("```json", "")
               .replace("```", "")
               .replace("json", "", 1)
               .strip()
        )
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed = {}

    contract_type = parsed.get("contract_type")
    industry = parsed.get("industry")

    return {
        "classification": response.content,  # keep string 
        "contract_type": contract_type,       #  non-null
        "industry": industry,                  #  non-null
    }


# qdrant retrieval setup

client = QdrantClient(host="localhost", port=6333)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = QdrantVectorStore(
    client=client,
    collection_name="contract_clauses",
    embedding=embeddings,
)


def retrieve_clauses_node(state):
    contract_type = state.get("contract_type")

    # Only use contract_type as the semantic query
    if not contract_type:
        # If classification failed, return empty for now (as requested)
        return {"retrieved_clauses": []}

    query = f"{contract_type} contract clauses"

    """ note here there is no code for embedding our query coz langchain makes an internal run for that 
    previously we have done 
    
    vectorstore = QdrantVectorStore(
    client=client,
    collection_name="contract_clauses",
    embedding=embeddings)
    
    langchain internally runs 
    query_vector = embeddings.embed_query(query)
    and vector is sent to qdrant
    client.search(
    collection_name="contract_clauses",
    vector=query_vector,
    limit=5)  """

    results = vectorstore.similarity_search(
        query=query,
        k=5,
    )

    retrieved = [
        {
            "clause_title": doc.metadata.get("clause_title"),
            "text": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in results
    ]

    return {"retrieved_clauses": retrieved}

def analyze_contract_node(state):
    contract_text = state["contract_text"]
    retrieved_clauses = state["retrieved_clauses"]

    clause_texts = "\n\n".join(
        [f"{c['clause_title']}:\n{c['text']}" for c in retrieved_clauses]
    )

    prompt = f"""
You are a legal contract reviewer.

Contract Type: {state.get("contract_type")}

TASK:
1. Compare the contract text with the standard reference clauses.
2. Identify which clauses are missing or incomplete.
3. Suggest improvements or better wording.
4. List missing standard clauses.

Return output strictly in JSON:

{{
  "clause_comparison": [
    {{"clause_title": "...", "status": "Present/Missing/Weak"}}
  ],
  "missing_clauses": ["..."],
  "suggestions": ["..."]
}}

CONTRACT TEXT:
{contract_text[:3000]}

REFERENCE CLAUSES:
{clause_texts}
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    try:
        parsed = json.loads(raw)

    except json.JSONDecodeError:
        cleaned = (
            raw.replace("```json", "")
               .replace("```", "")
               .strip()
        )

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed = {
                "error": "LLM did not return valid JSON",
                "raw_output": raw
            }

    return {
        "analysis_report": parsed
    }

def review_plan_node(state):
    contract_type = state.get("contract_type")
    industry = state.get("industry")

    prompt = f"""
You are a legal contract review planner.

Your task is to generate a review plan where each step is a
specialized legal role that should review the contract.

Return output strictly in JSON:

{{
  "review_plan": [
    "Role 1 Review",
    "Role 2 Review",
    "Role 3 Review"
  ]
}}

Context:
- Contract Type: {contract_type}
- Industry: {industry}

Rules:
1. Generate only 3–5 specialized roles.
2. Roles must be specific legal perspectives.
3. Do NOT include generic roles like "General Review".
4. Roles must match the contract type and industry.

Examples of roles:
- Employment Law Specialist Review
- Intellectual Property Counsel Review
- Compliance Officer Review
- Financial Terms Specialist Review
- Risk Management Review
- Data Privacy Officer Review
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    try:
        parsed = json.loads(raw)

    except json.JSONDecodeError:
        cleaned = (
            raw.replace("```json", "")
               .replace("```", "")
               .strip()
        )

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed = {}

    review_plan = parsed.get("review_plan", [])

    return {
        "review_plan": review_plan,
        
    }


def execute_all_reviews(state):
    roles = state.get("review_plan", [])
    contract_text = state.get("contract_text")

    all_reviews = []

    if not contract_text:
        return {
            "all_role_reviews": [{
                "error": "Contract text missing"
            }]
        }

    for role in roles:
        prompt = f"""
You are a {role}.

Review the contract strictly from your professional legal perspective.

Return ONLY valid JSON:
{{
  "analysis": "Role-specific analysis",
  "modifications": [
    {{
      "original_text": "...",
      "suggested_text": "...",
      "reason": "..."
    }}
  ]
}}

CONTRACT TEXT:
{contract_text[:3000]}
"""

        response = llm.invoke(prompt)
        raw = response.content.strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            try:
                parsed = json.loads(cleaned)
            except:
                parsed = {
                    "analysis": "",
                    "modifications": []
                }

        all_reviews.append({
            "role": role,
            "analysis": parsed.get("analysis", ""),
            "modifications": parsed.get("modifications", [])
        })

    return {
        "all_role_reviews": all_reviews
    }