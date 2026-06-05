from localdocs.parser import parse_bytes, parse_path


def test_parse_txt_file(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("LocalDocs AI keeps documents local.", encoding="utf-8")

    blocks = parse_path(path)

    assert len(blocks) == 1
    assert blocks[0].file_name == "note.txt"
    assert blocks[0].file_type == "txt"
    assert "keeps documents local" in blocks[0].text


def test_parse_markdown_file(tmp_path):
    path = tmp_path / "guide.md"
    path.write_text("# Guide\n\nMarkdown is supported.", encoding="utf-8")

    blocks = parse_path(path)

    assert len(blocks) == 1
    assert blocks[0].file_name == "guide.md"
    assert blocks[0].file_type == "markdown"
    assert "Markdown is supported" in blocks[0].text


def test_parse_pdf_file_preserves_page_number():
    blocks = parse_bytes(_simple_pdf_bytes("LocalDocs PDF citation text"), "sample.pdf")

    assert len(blocks) == 1
    assert blocks[0].file_name == "sample.pdf"
    assert blocks[0].file_type == "pdf"
    assert blocks[0].page_number == 1
    assert "LocalDocs PDF citation text" in blocks[0].text


def test_parse_empty_text_file_returns_no_blocks(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("   \n\n", encoding="utf-8")

    blocks = parse_path(path)

    assert blocks == []


def _simple_pdf_bytes(text):
    encoded_text = _escape_pdf_text(text)
    content = f"BT /F1 12 Tf 72 720 Td ({encoded_text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(content)).encode("ascii")
        + b" >>\nstream\n"
        + content
        + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


def _escape_pdf_text(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
