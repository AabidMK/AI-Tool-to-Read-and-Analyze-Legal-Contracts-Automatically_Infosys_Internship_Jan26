import os
from parser.pdf_parser import parse_pdf
from parser.docx_parser import parse_docx

def save_output(text, filename, output_format):
    os.makedirs("output_files", exist_ok=True)
    path = f"output_files/{filename}.{output_format}"

    with open(path, "w", encoding="utf-8") as file:
        file.write(text)

    return path

def parse_contract(file_path, output_format="txt"):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = parse_pdf(file_path)

    elif ext == ".docx":
        text = parse_docx(file_path)

    else:
        raise ValueError("Unsupported file format")

    if output_format == "md":
        text = "# Parsed Legal Contract\n" + text

    output_path = save_output(text, "parsed_contract", output_format)
    print("✅ Output saved at:", output_path)

if __name__ == "__main__":
    parse_contract("input_files/document.pdf", "md")
