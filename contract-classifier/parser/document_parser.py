from pathlib import Path
from docling.document_converter import DocumentConverter


def parse_document(file_path: str) -> str:
    """
    Parse PDF or DOCX and return the text content
    """
    file_path = Path(file_path)
    if file_path.suffix.lower() not in [".pdf", ".docx"]:
        raise ValueError("Only PDF and DOCX files are supported")

    converter = DocumentConverter()
    result = converter.convert(str(file_path))

    # Return the markdown content as text
    return result.document.export_to_markdown()
