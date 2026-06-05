from localdocs.chunker import chunk_blocks
from localdocs.models import DocumentBlock


def test_chunk_blocks_preserves_metadata_and_overlap():
    block = DocumentBlock(
        text="one two three four five six seven eight nine ten",
        file_name="note.txt",
        file_path="note.txt",
        file_type="txt",
    )

    chunks = chunk_blocks([block], chunk_size=4, overlap=1)

    assert len(chunks) == 3
    assert chunks[0].text == "one two three four"
    assert chunks[1].text == "four five six seven"
    assert chunks[0].file_name == "note.txt"
    assert chunks[0].chunk_index == 1
    assert chunks[1].chunk_index == 2


def test_chunk_blocks_skips_empty_text():
    block = DocumentBlock(text="   ", file_name="empty.txt", file_path="empty.txt", file_type="txt")

    chunks = chunk_blocks([block])

    assert chunks == []
