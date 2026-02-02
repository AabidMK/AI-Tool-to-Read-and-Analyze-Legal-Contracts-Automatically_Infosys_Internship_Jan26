import PyPDF2

def parse_document(file_path: str) -> str:
    """Simple PDF parser using PyPDF2"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""
    
    return text.strip()
