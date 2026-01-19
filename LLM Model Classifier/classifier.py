"""
Legal Contract Classification Engine with LangGraph
Implements: Document → Parser Node → Classification Node → Output
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, END
from pathlib import Path
from typing import Dict, List
import json

from config import ContractClassification, ContractState, Config


# LangGraph Node Functions


def document_loader_node(state: ContractState) -> dict:
    """
    Node 1: Document Loader
    Supports .txt, .md, .pdf, .docx
    """
    file_path = state['file_path']
    path = Path(file_path)
    
    if not path.exists():
        return {
            "status": "error",
            "error": f"File not found: {file_path}"
        }
    
    try:
        # Handle PDF files
        if path.suffix == '.pdf':
            import PyMuPDF  # fitz
            content = ""
            doc = PyMuPDF.open(file_path)
            for page in doc:
                content += page.get_text()
            doc.close()
            
            return {
                "contract_text": content,
                "status": "loaded"
            }
        
        # Handle DOCX files
        elif path.suffix == '.docx':
            from docx import Document
            doc = Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
            
            return {
                "contract_text": content,
                "status": "loaded"
            }
        
        # Handle TXT/MD files
        elif path.suffix in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "contract_text": content,
                "status": "loaded"
            }
        
        else:
            return {
                "status": "error",
                "error": f"Unsupported format: {path.suffix}"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to load file: {str(e)}"
        }


def text_extraction_node(state: ContractState) -> dict:
    """
    Node 2: Text Extraction
    Extracts relevant text for classification.
    """
    content = state['contract_text']
    
    if len(content) > Config.MAX_CHARS:
        extracted = content[:Config.MAX_CHARS] + "\n\n[Document truncated]"
    else:
        extracted = content
    
    return {
        "contract_text": extracted,
        "status": "extracted"
    }


def classification_node(state: ContractState) -> dict:
    """
    Node 3: Classification Node
    Uses LLM to classify the contract.
    """
    try:
        # Initialize LLM
        llm = ChatOllama(
            model=Config.OLLAMA_MODEL,
            temperature=Config.TEMPERATURE,
            num_predict=Config.MAX_TOKENS
        )
        
        # Create parser
        parser = PydanticOutputParser(pydantic_object=ContractClassification)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", Config.SYSTEM_PROMPT),
            ("user", Config.USER_PROMPT)
        ])
        
        # Create chain
        chain = prompt | llm | parser
        
        # Run classification
        result = chain.invoke({
            "contract_text": state['contract_text'],
            "format_instructions": parser.get_format_instructions()
        })
        
        return {
            "contract_type": result.contract_type,
            "industry": result.industry,
            "status": "success"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def should_continue(state: ContractState) -> str:
    """Routing function: check if we should continue or end."""
    if state.get('status') == 'error':
        return "end"
    return "continue"


# ============================================================
# LangGraph Workflow Builder
# ============================================================

def build_classification_graph():
    """Build the LangGraph state machine."""
    
    # Create graph
    workflow = StateGraph(ContractState)
    
    # Add nodes
    workflow.add_node("load_document", document_loader_node)
    workflow.add_node("extract_text", text_extraction_node)
    workflow.add_node("classify", classification_node)
    
    # Define edges (workflow)
    workflow.set_entry_point("load_document")
    workflow.add_edge("load_document", "extract_text")
    workflow.add_edge("extract_text", "classify")
    workflow.add_edge("classify", END)
    
    # Compile graph
    return workflow.compile()


# ============================================================
# Main Classifier Interface
# ============================================================

class ContractClassifier:
    """
    High-level contract classification interface using LangGraph.
    """
    
    def __init__(self):
        """Initialize classifier with LangGraph workflow."""
        self.graph = build_classification_graph()
    
    def classify_file(self, file_path: str) -> Dict:
        """
        Classify a single contract file using LangGraph workflow.
        
        Args:
            file_path: Path to contract file
            
        Returns:
            dict: Classification result
        """
        # Initial state
        initial_state = {
            "file_path": file_path,
            "contract_text": "",
            "contract_type": "",
            "industry": "",
            "status": "pending",
            "error": None
        }
        
        # Run graph
        final_state = self.graph.invoke(initial_state)
        
        # Format output
        return {
            'file': file_path,
            'contract_type': final_state.get('contract_type', 'Unknown'),
            'industry': final_state.get('industry', 'Unknown'),
            'status': final_state.get('status', 'error'),
            'error': final_state.get('error')
        }
    
    def classify_batch(self, file_paths: List[str]) -> List[Dict]:
        """Classify multiple contract files."""
        results = []
        for file_path in file_paths:
            result = self.classify_file(file_path)
            results.append(result)
        return results
    
    def save_results(self, results: List[Dict], output_file: str):
        """Save classification results to JSON file."""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
