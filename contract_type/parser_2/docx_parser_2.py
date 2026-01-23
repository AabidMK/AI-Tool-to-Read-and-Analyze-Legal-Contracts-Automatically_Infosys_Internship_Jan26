from docx import Document

def extract_docx_text(file_path: str) -> dict:
    try:
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)

        if not text.strip():
            return {"success": False, "error": "Empty DOCX"}

        return {"success": True, "text": text}

    except Exception as e:
        return {"success": False, "error": str(e)}
