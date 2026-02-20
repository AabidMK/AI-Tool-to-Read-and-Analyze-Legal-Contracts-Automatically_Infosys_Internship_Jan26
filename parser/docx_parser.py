from docx import Document
from pathlib import Path

def parse_docx_to_text(docx_path: str) -> list[str]:
    lines = []
    docx = Document(docx_path)

    for para in docx.paragraphs:
        text = para.text.strip()
        if text:
            lines.append(text)

    return lines