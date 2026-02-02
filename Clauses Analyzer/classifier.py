"""
Contract Classification with Clause Retrieval from Qdrant
"""

from typing import TypedDict, Optional, List
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama #type: ignore
from langchain_core.messages import HumanMessage, SystemMessage #type: ignore
from langgraph.graph import StateGraph, START, END #type: ignore
from qdrant_client import QdrantClient #type: ignore
from qdrant_client.models import Filter, FieldCondition, MatchValue #type: ignore
from fastembed import TextEmbedding #type: ignore
from pathlib import Path


# ============================================================
# State and Schema
# ============================================================

class ContractReviewState(TypedDict):
    file_path: str
    contract_text: str
    contract_type: Optional[str]
    industry: Optional[str]
    clauses: List[dict]
    analysis: Optional[dict]


class ClassificationResult(BaseModel):
    contract_type: str = Field(description="Type of contract")
    industry: str = Field(description="Primary industry")

class AnalysisResult(BaseModel):
    """LLM output schema for contract analysis."""
    contextual_analysis: str = Field(description="Comparison of contract text with reference clauses")
    suggestions: List[str] = Field(description="List of improvement suggestions")
    missing_clauses: List[str] = Field(description="List of standard clauses that are missing")
    risk_level: str = Field(description="Overall risk assessment: Low, Medium, or High")



# ============================================================
# Initialize Components
# ============================================================

print("Initializing components...")

# Qdrant LOCAL mode
qdrant_client = QdrantClient(path="./qdrant_db")
collection_name = "contract-clauses"

# Embedding model
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

# LLM
# LLM with explicit configuration
llm = ChatOllama(
    model="qwen2.5:3b",
    base_url="http://127.0.0.1:11434",  # Explicit localhost
    temperature=0,
    timeout=120  # Longer timeout
)

print("✓ Components ready!\n")


# ============================================================
# Nodes
# ============================================================

def extract_text_node(state: ContractReviewState):
    """Extract text from PDF/DOCX/TXT."""
    file_path = state["file_path"]
    path = Path(file_path)
    
    print(f"[Node 1: Extract Text] Loading {path.name}...")
    
    try:
        if path.suffix == '.pdf':
            import fitz #type: ignore
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
        
        elif path.suffix == '.docx':
            from docx import Document #type: ignore
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        
        elif path.suffix in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        else:
            raise ValueError(f"Unsupported format: {path.suffix}")
        
        print(f"  ✓ Extracted {len(text)} characters")
        return {"contract_text": text}
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"contract_text": ""}


def classify_contract_node(state: ContractReviewState):
    """Classify contract using LLM."""
    text = state["contract_text"][:3000]
    
    print("[Node 2: Classify] Running LLM classification...")
    
    messages = [
        SystemMessage(content="You are a legal contract classification expert."),
        HumanMessage(content=f"""Classify this contract. Return JSON with:
- contract_type: specific type (e.g., "Non-Disclosure Agreement", "Employment Agreement")
- industry: primary industry (e.g., "Technology", "Healthcare")

Contract text:
{text}
""")
    ]
    
    try:
        result = llm.with_structured_output(ClassificationResult).invoke(messages)
        
        print(f"  ✓ Type: {result.contract_type}")
        print(f"  ✓ Industry: {result.industry}")
        
        return {
            "contract_type": result.contract_type,
            "industry": result.industry
        }
    
    except Exception as e:
        print(f"  ✗ Classification error: {e}")
        return {
            "contract_type": "Unknown",
            "industry": "Unknown"
        }


def retrieve_clauses_node(state: ContractReviewState):
    """Retrieve relevant clauses from Qdrant with flexible filtering."""
    contract_type = state["contract_type"]
    
    print(f"[Node 3: Retrieve] Searching Qdrant for '{contract_type}' clauses...")
    
    query = f"General Clauses, {contract_type}"
    query_embedding = list(embedding_model.embed([query]))[0]
    
    # Try with filter first
    results = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_embedding.tolist(),
        query_filter=Filter(
            should=[
                FieldCondition(
                    key="contract_type",
                    match=MatchValue(value="General Clauses")
                ),
                FieldCondition(
                    key="contract_type",
                    match=MatchValue(value=contract_type)
                )
            ]
        ),
        limit=10
    )
    
    # If no results with strict filter, search without filter
    if not results.points:
        print("  ⚠️ No exact matches, searching all clauses...")
        results = qdrant_client.query_points(
            collection_name=collection_name,
            query=query_embedding.tolist(),
            limit=10
        )
    
    # Format results
    clauses = []
    for result in results.points:
        clause = {
            "clause_title": result.payload["clause_title"],
            "clause_text": result.payload["clause_text"],
            "contract_type": result.payload["contract_type"],
            "score": result.score
        }
        clauses.append(clause)
    
    print(f"  ✓ Retrieved {len(clauses)} clauses")
    
    return {"clauses": clauses}

def analyze_contract_node(state: ContractReviewState):
    """Analyze contract by comparing with retrieved clauses using LLM."""
    contract_text = state["contract_text"]
    contract_type = state["contract_type"]
    clauses = state["clauses"]
    
    print(f"[Node 4: Analyze] Running LLM analysis...")
    
    # Format retrieved clauses for context
    clause_context = "\n\n".join([
        f"**{clause['clause_title']}** (from {clause['contract_type']})\n{clause['clause_text'][:300]}..."
        for clause in clauses[:5]  # Top 5 most relevant
    ])
    
    # Create analysis prompt
    analysis_prompt = f"""You are a legal contract analyst. Analyze the following contract.

**Contract Type:** {contract_type}

**Contract Text (excerpt):**
{contract_text[:2000]}

**Reference Standard Clauses:**
{clause_context}

Analyze the contract and provide:

1. **Contextual Analysis:** Compare the contract text with the reference clauses. What's present? What's similar/different?

2. **Suggestions:** List 3-5 specific improvements to strengthen this contract (e.g., clarify ambiguous terms, add protective language).

3. **Missing Clauses:** Identify standard clauses for this contract type that are MISSING from the current document. List their titles.

4. **Risk Level:** Assess overall risk (Low/Medium/High) based on missing clauses and weak language.

Return structured JSON output.
"""
    
    messages = [
        SystemMessage(content="You are an expert legal contract analyst specializing in contract review and risk assessment."),
        HumanMessage(content=analysis_prompt)
    ]
    
    try:
        result = llm.with_structured_output(AnalysisResult).invoke(messages)
        
        analysis = {
            "contextual_analysis": result.contextual_analysis,
            "suggestions": result.suggestions,
            "missing_clauses": result.missing_clauses,
            "risk_level": result.risk_level
        }
        
        print(f"  ✓ Analysis complete")
        print(f"  ✓ Risk Level: {result.risk_level}")
        print(f"  ✓ Missing Clauses: {len(result.missing_clauses)}")
        print(f"  ✓ Suggestions: {len(result.suggestions)}")
        
        return {"analysis": analysis}
    
    except Exception as e:
        print(f"  ✗ Analysis error: {e}")
        return {
            "analysis": {
                "contextual_analysis": "Analysis failed",
                "suggestions": [],
                "missing_clauses": [],
                "risk_level": "Unknown"
            }
        }


# ============================================================
# Build LangGraph Workflow
# ============================================================

builder = StateGraph(ContractReviewState)

builder.add_node("extract_text", extract_text_node)
builder.add_node("classify_contract", classify_contract_node)
builder.add_node("retrieve_clauses", retrieve_clauses_node)
builder.add_node("analyze_contract", analyze_contract_node)  # ← ADD THIS

builder.add_edge(START, "extract_text")
builder.add_edge("extract_text", "classify_contract")
builder.add_edge("classify_contract", "retrieve_clauses")
builder.add_edge("retrieve_clauses", "analyze_contract")  # ← ADD THIS
builder.add_edge("analyze_contract", END)  # ← CHANGE THIS

graph = builder.compile()


# ============================================================
# Main Function
# ============================================================

def classify_contract(file_path: str):
    """Run full workflow: extract → classify → retrieve."""
    
    initial_state = {
        "file_path": file_path,
        "contract_text": "",
        "contract_type": None,
        "industry": None,
        "clauses": [],
        "analysis": None
    }
    
    result = graph.invoke(initial_state)
    
    return {
        "file_path": result["file_path"],
        "contract_text": result["contract_text"][:500] + "..." if len(result["contract_text"]) > 500 else result["contract_text"],
        "contract_type": result["contract_type"],
        "industry": result["industry"],
        "clauses": result["clauses"],
        "analysis": result["analysis"]
    }
