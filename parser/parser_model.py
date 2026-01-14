import fitz

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = []

    for page in doc:
        text.append(page.get_text())

    return "\n".join(text)
