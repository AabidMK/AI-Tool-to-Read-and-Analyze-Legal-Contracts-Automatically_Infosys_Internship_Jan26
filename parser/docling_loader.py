from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from docling.document_converter import DocumentConverter


class DoclingLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.converter = DocumentConverter()

    def load(self):
        result = self.converter.convert(self.file_path)
        document = result.document

        # Correct way to extract text from Docling
        full_text = document.export_to_text()

        return [
            Document(
                page_content=full_text,
                metadata={"source": self.file_path}
            )
        ]
