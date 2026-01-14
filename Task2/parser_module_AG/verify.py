from reportlab.pdfgen import canvas
from docx import Document
import os
import subprocess
import sys

def create_sample_pdf(filepath, text):
    c = canvas.Canvas(filepath)
    c.drawString(100, 750, text)
    c.save()

def create_sample_docx(filepath, text):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filepath)

def verify():
    test_text = "This is a test parsing document."
    pdf_path = "test.pdf"
    docx_path = "test.docx"
    
    # Clean up previous runs
    if os.path.exists(pdf_path): os.remove(pdf_path)
    if os.path.exists(docx_path): os.remove(docx_path)
    if os.path.exists("test_pdf.txt"): os.remove("test_pdf.txt")
    if os.path.exists("test_docx.txt"): os.remove("test_docx.txt")
    
    print("Generating sample files...")
    create_sample_pdf(pdf_path, test_text)
    create_sample_docx(docx_path, test_text)
    
    # Test PDF
    print("Testing PDF Parser...")
    try:
        subprocess.run([sys.executable, "main.py", pdf_path, "--output", "test_pdf.txt"], check=True)
        
        if os.path.exists("test_pdf.txt"):
            with open("test_pdf.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if test_text in content: # PDF extraction might have layout differences/whitespace
                    print("PDF Confirmation: SUCCESS")
                else:
                    print(f"PDF Confirmation: FAILED. Got: '{content}'")
        else:
            print("PDF Confirmation: FAILED (Output file not found)")
    except Exception as e:
        print(f"PDF Parser crashed: {e}")

    # Test DOCX
    print("Testing DOCX Parser...")
    try:
        subprocess.run([sys.executable, "main.py", docx_path, "--output", "test_docx.txt"], check=True)

        if os.path.exists("test_docx.txt"):
            with open("test_docx.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if test_text == content:
                    print("DOCX Confirmation: SUCCESS")
                else:
                    print(f"DOCX Confirmation: FAILED. Got: '{content}'")
        else:
            print("DOCX Confirmation: FAILED (Output file not found)")
    except Exception as e:
         print(f"DOCX Parser crashed: {e}")

if __name__ == "__main__":
    verify()
