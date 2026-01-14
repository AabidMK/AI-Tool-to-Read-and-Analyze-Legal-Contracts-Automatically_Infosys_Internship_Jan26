from docx import Document

def parse_docx(file_path):
    document = Document(file_path)
    extracted_text = ""

    for para in document.paragraphs:
        if para.text.strip():
            extracted_text += para.text.strip() + "\n"

    return extracted_text
