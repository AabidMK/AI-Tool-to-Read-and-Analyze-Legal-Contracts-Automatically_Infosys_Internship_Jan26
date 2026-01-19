from pathlib import Path
from typing import Union

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat


class ContractDocumentParser:
    def __init__(self):
        # Simple, version-stable configuration
        self.converter = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.DOCX,
            ]
        )

    def parse_to_markdown(
        self,
        input_path: Union[str, Path],
        output_dir: Union[str, Path] = "parser/outputs"
    ) -> Path:
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not input_path.exists():
            raise FileNotFoundError(f"{input_path} not found")

        result = self.converter.convert(input_path)
        markdown_text = result.document.export_to_markdown()

        if not markdown_text.strip():
            raise ValueError("Parsed markdown is empty")

        output_path = output_dir / f"{input_path.stem}.md"
        output_path.write_text(markdown_text, encoding="utf-8")

        return output_path

    def parse_and_return_text(self, input_path: Union[str, Path]) -> str:
        result = self.converter.convert(Path(input_path))
        return result.document.export_to_markdown()
