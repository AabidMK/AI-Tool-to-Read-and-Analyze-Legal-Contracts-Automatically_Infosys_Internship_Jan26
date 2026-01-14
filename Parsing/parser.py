from docling.document_converter import DocumentConverter

converter = DocumentConverter()
file_path = "./Aditya Bharadwaj Kusumba.pdf"

result = converter.convert(file_path)

if result.errors:
    print("Error")
    for error in result.errors:
        print(error)

doc = result.document
plain_text = doc.export_to_text()
markdown_text = doc.export_to_markdown()

document_json = doc.export_to_dict()

print("\nTEXT OUTPUT\n")
print(plain_text)

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(plain_text)
print("Done")
