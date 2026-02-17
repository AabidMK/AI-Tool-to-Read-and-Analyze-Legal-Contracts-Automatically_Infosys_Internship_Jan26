from parser.docling_loader import DoclingLoader
import re



def extract_contract_text(input_file: str, max_chars: int = 15000):
    """
    Extracts text from a contract document using Docling.
    Returns cleaned text suitable for LLM input.
    """

    loader = DoclingLoader(input_file)
    documents = loader.load()

    if not documents:
        raise ValueError("No text could be extracted from the document.")

    text = documents[0].page_content

    text = text.replace("\n\n", "\n").strip()
    
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'\s+', ' ', text)

    if len(text) > max_chars:
        text = text[:max_chars]
        last_period = text.rfind(".")
        if last_period != -1:
            text = text[:last_period + 1]


    return text
