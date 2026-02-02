"""
Configuration and data models for contract classification system.
"""

from pydantic import BaseModel, Field
from typing import TypedDict, Optional, List


class ContractClassification(BaseModel):
    """Output schema for contract classification."""
    contract_type: str = Field(description="Type of contract")
    industry: str = Field(description="Primary industry")


class ClauseData(BaseModel):
    """Schema for extracted clause."""
    clause_title: str = Field(description="Title of the clause")
    clause_text: str = Field(description="Full text of the clause")


class ContractState(TypedDict):
    """LangGraph state for contract processing."""
    file_path: str
    contract_text: str
    contract_type: str
    industry: str
    clauses: List[dict]  # NEW: Extracted clauses
    status: str
    error: Optional[str]


class Config:
    """System configuration."""
    
    # Ollama settings
    OLLAMA_MODEL = "qwen2.5:3b"
    OLLAMA_BASE_URL = "http://localhost:11434"
    
    # LLM parameters
    TEMPERATURE = 0
    MAX_TOKENS = 300
    
    # Text processing
    MAX_CHARS = 3000
    
    # Supported formats
    SUPPORTED_FORMATS = ['.txt', '.md', '.pdf', '.docx']
    
    # Vector DB settings (Qdrant local mode - NO DOCKER!)
    QDRANT_PATH = "./qdrant_db"  # Local storage path
    COLLECTION_NAME = "contract-clauses"
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # FastEmbed model
    VECTOR_SIZE = 384  # Dimension for bge-small
    
    # Prompts
    SYSTEM_PROMPT = """You are a legal AI assistant specialized in contract classification.

Your task: Analyze the contract and identify:
1. Contract Type (be specific)
2. Primary Industry

{format_instructions}

Be accurate and concise."""
    
    USER_PROMPT = """Classify this legal contract:

CONTRACT TEXT:
---
{contract_text}
---

Provide classification:"""
    
    CLAUSE_EXTRACTION_PROMPT = """You are a legal clause extraction expert.

Extract ALL important clauses from this contract. For each clause, provide:
1. clause_title: A clear title (e.g., "Confidentiality Obligations", "Termination Rights")
2. clause_text: The full text of that clause

Contract text:
---
{contract_text}
---

Extract clauses in JSON format:
{format_instructions}"""
