from pathlib import Path
from typing import List

from .pdf_parser import parse_pdf_to_text
from .docx_parser import parse_docx_to_text

def parse_document(filepath: str) -> List[str]:
    """
    Unified parser entry point
    Routes file to the correct parser based on extension
    """

    suffix = Path(filepath).suffix.lower()

    if suffix == ".pdf":
        return parse_pdf_to_text(filepath)
    
    elif suffix == ".docx":
        return parse_docx_to_text(filepath)
    
    else:
        raise ValueError (f"Unsupported file type: {suffix}")
        