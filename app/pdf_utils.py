import textwrap
from typing import List


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _paginate_lines(lines: List[str], max_lines_per_page: int) -> List[List[str]]:
    pages: List[List[str]] = []
    current: List[str] = []

    for line in lines:
        if len(current) >= max_lines_per_page:
            pages.append(current)
            current = []
        current.append(line)

    if current:
        pages.append(current)

    return pages


def build_report_pdf(title: str, report_text: str) -> bytes:
    wrapped_lines: List[str] = []
    for raw_line in report_text.splitlines() or [""]:
        chunks = textwrap.wrap(raw_line, width=95) or [""]
        wrapped_lines.extend(chunks)

    pages = _paginate_lines(wrapped_lines, max_lines_per_page=47)

    objects: List[bytes] = []

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

    page_entries = []

    objects.append(b"")

    font_obj_id = 3 + (len(pages) * 2)

    for index, page_lines in enumerate(pages):
        page_obj_id = 3 + (index * 2)
        content_obj_id = page_obj_id + 1

        stream_lines = [
            "BT",
            "/F1 18 Tf",
            "50 800 Td",
            f"({_escape_pdf_text(title)}) Tj",
            "/F1 11 Tf",
            "0 -26 Td",
        ]

        for line in page_lines:
            stream_lines.append(f"({_escape_pdf_text(line)}) Tj")
            stream_lines.append("0 -14 Td")

        stream_lines.append("ET")
        stream_text = "\n".join(stream_lines).encode("utf-8")

        page_obj = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_obj_id} 0 R >> >> "
            f"/Contents {content_obj_id} 0 R >>"
        ).encode("utf-8")

        content_obj = (
            b"<< /Length "
            + str(len(stream_text)).encode("utf-8")
            + b" >>\nstream\n"
            + stream_text
            + b"\nendstream"
        )

        objects.append(page_obj)
        objects.append(content_obj)
        page_entries.append(f"{page_obj_id} 0 R")

    pages_obj = (
        f"<< /Type /Pages /Kids [{' '.join(page_entries)}] /Count {len(page_entries)} >>"
    ).encode("utf-8")
    objects[1] = pages_obj

    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for obj_id, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{obj_id} 0 obj\n".encode("utf-8"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("utf-8"))
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("utf-8"))

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("utf-8")
    )

    return bytes(pdf)