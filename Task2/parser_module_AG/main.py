import argparse
import os
import sys
from pdf_parser import extract_text_from_pdf
from docx_parser import extract_text_from_docx

def main():
    parser = argparse.ArgumentParser(description="Parse PDF or DOCX files to text/markdown.")
    parser.add_argument("input_file", help="Path to the input file (PDF or DOCX).")
    parser.add_argument("--format", choices=["txt", "md"], default="txt", help="Output format (txt or md).")
    parser.add_argument("--output", help="Path to the output file. If not provided, uses input filename with new extension.")

    args = parser.parse_args()

    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    file_ext = os.path.splitext(input_path)[1].lower()
    
    text = None
    if file_ext == ".pdf":
        text = extract_text_from_pdf(input_path)
    elif file_ext == ".docx":
        text = extract_text_from_docx(input_path)
    else:
        print(f"Error: Unsupported file type '{file_ext}'. Only .pdf and .docx are supported.")
        sys.exit(1)

    if text is None:
        print("Failed to extract text.")
        sys.exit(1)

    output_path = args.output
    if not output_path:
        output_path = os.path.splitext(input_path)[0] + "." + args.format

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Successfully extracted text to '{output_path}'.")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
