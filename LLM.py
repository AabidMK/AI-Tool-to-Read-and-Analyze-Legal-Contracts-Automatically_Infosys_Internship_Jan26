from docling.document_converter import DocumentConverter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

converter = DocumentConverter()
file_path = "./NDA.pdf"

result = converter.convert(file_path)

if result.errors:
    print("Error")
    for error in result.errors:
        print(error)

doc = result.document
legal_text = doc.export_to_text()
print("Extracted Text : ")
print(legal_text)


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key={API_KEY})

prompt = ChatPromptTemplate.from_template(
    """
You are a legal document classification expert, return ONLY valid JSON.

Format:
{{
  "agreement_type": "...",
  "industry": "..."
}}

If unclear, use:
"Unknown Agreement"
"Unknown Industry"

Document:
\"\"\"
{legal_text}
\"\"\"
"""
)

parser = JsonOutputParser()

chain = prompt | llm | parser

result = chain.invoke({"legal_text": legal_text})

print(result)
print("\n")
print("Required Details : ")
print("Agreement Type:", result.get("agreement_type"))
print("Industry:", result.get("industry"))

