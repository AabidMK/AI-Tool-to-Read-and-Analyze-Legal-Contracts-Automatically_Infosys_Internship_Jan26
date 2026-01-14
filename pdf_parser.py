import pdfplumber

def parse_pdf(file_path):
    extracted_text = ""

    with pdfplumber.open(file_path) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                extracted_text += f"\n\n--- Page {page_no} ---\n"
                extracted_text += text.strip() + "\n"

    return extracted_text
