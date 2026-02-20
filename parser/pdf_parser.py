import pdfplumber
from pathlib import Path

def is_header_or_footer(word, page_height):
    return word["top"] < 30 or word["bottom"] > page_height - 60

def parse_pdf_to_text(pdf_path:str) -> list[str]:

    lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = [
                w for w in page.extract_words(
                    x_tolerance=2,
                    y_tolerance=2,
                    keep_blank_chars=False,
                    use_text_flow=True
                )
                if not is_header_or_footer(w, page.height)
            ]

            current_line = []
            last_top = None

            for word in words:
                if last_top is None or abs(word["top"] - last_top) < 3:
                    current_line.append(word["text"])
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word["text"]]
                last_top = word["top"]

            if current_line:
                lines.append(" ".join(current_line))

    return lines