import pdfplumber

def extract_pdf_text(file_path: str) -> dict:
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"

        if not text.strip():
            return {"success": False, "error": "Empty PDF"}

        return {"success": True, "text": text}

    except Exception as e:
        return {"success": False, "error": str(e)}
