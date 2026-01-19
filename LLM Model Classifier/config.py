"""
Configuration and data models for contract classification system.
Defines output schemas and system settings.
"""

from pydantic import BaseModel, Field
from typing import TypedDict, Optional


class ContractClassification(BaseModel):
    """
    Output schema for contract classification.
    Represents the structured result from LLM analysis.
    """
    contract_type: str = Field(
        description="Specific type of legal contract (e.g., Non-Disclosure Agreement, Employment Agreement)"
    )
    industry: str = Field(
        description="Primary industry the contract relates to (e.g., Technology, Healthcare, Finance)"
    )


# LangGraph State Schema
class ContractState(TypedDict):
    """State container for LangGraph workflow."""
    file_path: str
    contract_text: str
    contract_type: str
    industry: str
    status: str
    error: Optional[str]


class Config:
    """System configuration constants."""
    
    # Ollama settings
    OLLAMA_MODEL = "qwen2.5:3b"  # Change to your model
    OLLAMA_BASE_URL = "http://localhost:11434"
    
    # LLM parameters
    TEMPERATURE = 0
    MAX_TOKENS = 300
    
    # Text processing
    MAX_CHARS = 3000
    
    # Supported file formats
    SUPPORTED_FORMATS = ['.txt', '.md']
    
    # Prompt templates
    SYSTEM_PROMPT = """You are a legal AI assistant specialized in contract classification.

Your task: Analyze the contract and identify:
1. Contract Type (be specific: "Non-Disclosure Agreement", not just "NDA")
2. Primary Industry it relates to

{format_instructions}

Be accurate and concise."""
    
    USER_PROMPT = """Classify this legal contract:

CONTRACT TEXT:
---
{contract_text}
---

Provide classification:"""
