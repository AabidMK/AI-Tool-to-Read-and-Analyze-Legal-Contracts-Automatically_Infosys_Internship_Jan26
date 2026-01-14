# hugging face error it is showing try using google colab
from docling.document_converter import DocumentConverter

source = "inputs/sample.pdf"

converter = DocumentConverter()
result = converter.convert(source)

with open("output.md", "w", encoding="utf-8") as f:
    f.write(result.document.export_to_markdown())
