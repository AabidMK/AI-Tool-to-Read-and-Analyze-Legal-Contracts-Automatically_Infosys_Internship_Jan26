from parser.document_parser import ContractDocumentParser

parser = ContractDocumentParser()

md_path = parser.parse_to_markdown(
    input_path="EX-10.11.pdf"
)

print("Saved markdown at:", md_path)
