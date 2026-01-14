from parser.docling_loader import DoclingLoader


def extract_contract_text(input_file: str, max_chars: int = 8000) -> str:
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

    if len(text) > max_chars:
        text = text[:max_chars]

    return text
