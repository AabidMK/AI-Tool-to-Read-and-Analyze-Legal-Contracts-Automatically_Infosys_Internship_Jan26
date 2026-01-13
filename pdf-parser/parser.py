import os
from PyPDF2 import PdfReader

input_file = r"C:\Users\RISHIRAJSINGH\Downloads\SOFTWARE-NDA.pdf"
output_file = "output_files/Employment_Agreement.txt"

os.makedirs("output_files", exist_ok=True)

reader = PdfReader(input_file)
text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

with open(output_file, "w", encoding="utf-8") as file:
    file.write(text)

print("PDF parsed and saved as TXT")
