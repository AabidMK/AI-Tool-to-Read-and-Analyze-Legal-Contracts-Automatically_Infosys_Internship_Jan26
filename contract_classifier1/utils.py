import json
from pathlib import Path

def load_contract(file_path: str) -> str:
    """
    Load contract text from a file.
    Supports PDF (via pypdf) and text files.
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if p.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(p))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()

    return p.read_text(encoding="utf-8", errors="ignore")


def extract_json_from_text(text: str):
    """
    Extract the first JSON object from a text response.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in text.")
    return json.loads(text[start:end+1])
