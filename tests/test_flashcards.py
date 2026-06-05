from localdocs.flashcards import export_anki_tsv, generate_flashcards
from localdocs.models import DocumentChunk


def test_generate_flashcards_includes_source_reference():
    chunks = [
        DocumentChunk(
            text="# Local Search\nLocalDocs AI uses TF-IDF search for local retrieval.",
            file_name="guide.md",
            file_path="guide.md",
            file_type="markdown",
            chunk_index=1,
        )
    ]

    cards = generate_flashcards(chunks, max_cards=5)

    assert len(cards) == 1
    assert cards[0].question == "What is a key point from Local Search?"
    assert "TF-IDF search" in cards[0].answer
    assert cards[0].citation.label() == "guide.md, chunk 1"


def test_export_anki_tsv_writes_three_columns(tmp_path):
    chunk = DocumentChunk(
        text="LocalDocs AI exports Anki-compatible flashcards.",
        file_name="guide.md",
        file_path="guide.md",
        file_type="markdown",
        chunk_index=2,
    )
    cards = generate_flashcards([chunk], max_cards=1)

    path = export_anki_tsv(cards, tmp_path / "flashcards.tsv")

    content = path.read_text(encoding="utf-8").strip()
    fields = content.split("\t")
    assert len(fields) == 3
    assert fields[0].startswith("What is a key point")
    assert fields[2] == "guide.md, chunk 2"
