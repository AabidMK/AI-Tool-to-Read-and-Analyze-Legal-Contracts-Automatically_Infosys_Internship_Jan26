from pathlib import Path
from docling.document_converter import DocumentConverter


class DocumentParser:
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def parse(self, file_path: str, output_format="md"):
        """
        Parse PDF or DOCX and save as .txt or .md
        """
        if output_format not in ["txt", "md"]:
            raise ValueError("Output format must be 'txt' or 'md'")

        file_path = Path(file_path)
        if file_path.suffix.lower() not in [".pdf", ".docx"]:
            raise ValueError("Only PDF and DOCX files are supported")

        converter = DocumentConverter()
        result = converter.convert(str(file_path))

        if output_format == "md":
            content = result.document.export_to_markdown()
        else:
            content = result.document.export_to_text()

        output_file = self.output_dir / f"{file_path.stem}.{output_format}"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        return output_file


# ------------------ Example Usage ------------------
if __name__ == "__main__":
    parser = DocumentParser()
    output = parser.parse("/Users/lakshanagopu/Desktop/parser/715523104028 CN EX3 Q2 copy.pdf", output_format="md")
    print(f"Saved parsed document at: {output}")
