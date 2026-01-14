from pdfminer.high_level import extract_text

def extract_text_from_pdf(filepath):
    """Extracts text from a PDF file."""
    try:
        text = extract_text(filepath)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
