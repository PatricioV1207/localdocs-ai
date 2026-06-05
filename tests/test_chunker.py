from localdocs.chunker import chunk_blocks
from localdocs.models import DocumentBlock


def test_chunk_blocks_preserves_metadata_and_overlap():
    block = DocumentBlock(
        text="one two three four five six seven eight nine ten",
        file_name="manual.pdf",
        file_path="/docs/manual.pdf",
        file_type="pdf",
        page_number=3,
    )

    chunks = chunk_blocks([block], chunk_size=4, overlap=1)

    assert len(chunks) == 3
    assert chunks[0].text == "one two three four"
    assert chunks[1].text == "four five six seven"
    assert chunks[0].file_name == "manual.pdf"
    assert chunks[0].file_path == "/docs/manual.pdf"
    assert chunks[0].file_type == "pdf"
    assert chunks[0].page_number == 3
    assert chunks[0].chunk_index == 1
    assert chunks[1].chunk_index == 2


def test_chunk_blocks_skips_empty_text():
    block = DocumentBlock(text="   ", file_name="empty.txt", file_path="empty.txt", file_type="txt")

    chunks = chunk_blocks([block])

    assert chunks == []


def test_paragraph_chunking_preserves_metadata():
    block = DocumentBlock(
        text="First paragraph has a key idea.\n\nSecond paragraph has another idea.\n\nThird paragraph closes.",
        file_name="guide.txt",
        file_path="/docs/guide.txt",
        file_type="txt",
    )

    chunks = chunk_blocks([block], chunk_size=6, overlap=0, strategy="paragraph")

    assert len(chunks) == 3
    assert chunks[0].text == "First paragraph has a key idea."
    assert chunks[1].file_name == "guide.txt"
    assert chunks[1].file_path == "/docs/guide.txt"
    assert chunks[1].chunk_index == 2


def test_heading_chunking_splits_markdown_sections():
    block = DocumentBlock(
        text="# Intro\nLocalDocs keeps search local.\n# Export\nObsidian and Anki exports reuse documents.",
        file_name="guide.md",
        file_path="/docs/guide.md",
        file_type="markdown",
    )

    chunks = chunk_blocks([block], chunk_size=20, overlap=0, strategy="heading")

    assert len(chunks) == 2
    assert chunks[0].text.startswith("# Intro")
    assert chunks[1].text.startswith("# Export")
    assert chunks[1].chunk_index == 2
