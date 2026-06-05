from localdocs.parser import parse_path


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
