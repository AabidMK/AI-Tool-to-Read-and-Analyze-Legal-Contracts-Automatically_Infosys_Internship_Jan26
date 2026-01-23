import os
from PyPDF2 import PdfReader
from docx import Document


def parse_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def parse_docx(file_path):
    doc = Document(file_path)
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def save_output(text, output_path):
    folder = os.path.dirname(output_path)

    if folder and not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def parse_file(input_file, output_file):
    print("parse_file FOUND and EXECUTING")

    if not os.path.exists(input_file):
        raise FileNotFoundError("Input file not found")

    extension = os.path.splitext(input_file)[1].lower()

    if extension == ".pdf":
        print("PDF detected")
        text = parse_pdf(input_file)
    elif extension == ".docx":
        print("DOCX detected")
        text = parse_docx(input_file)
    else:
        raise ValueError("Unsupported file format")

    save_output(text, output_file)

