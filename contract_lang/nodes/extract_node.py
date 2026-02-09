from docx import Document
from pypdf import PdfReader

def extract_text_node(state: dict):
    file_path = state["file_path"]
    text = ""

    if file_path.endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text)

    elif file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

    print("✅ Contract text extracted")
    return {"contract_text": text}
