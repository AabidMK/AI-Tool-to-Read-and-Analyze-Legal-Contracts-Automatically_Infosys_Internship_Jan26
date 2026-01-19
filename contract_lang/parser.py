from docx import Document
from PyPDF2 import PdfReader

def extract_text(file_path):
    if file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    raise ValueError("Only PDF or DOCX supported")
