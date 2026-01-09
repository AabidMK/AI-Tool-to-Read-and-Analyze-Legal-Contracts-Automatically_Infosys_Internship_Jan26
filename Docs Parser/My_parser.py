from docling.document_converter import DocumentConverter

source = "./finalCits.pdf"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
#print(result.document.export_to_text())
# Save to markdown file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(result.document.export_to_markdown())

# Or save to text file
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(result.document.export_to_text())
