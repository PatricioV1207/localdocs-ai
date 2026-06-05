from localdocs.flashcards import generate_flashcards
from localdocs.models import Answer, Citation, DocumentChunk, DocumentSummary
from localdocs.obsidian import export_obsidian_vault
from localdocs.study import generate_study_questions


def test_export_obsidian_vault_creates_expected_files(tmp_path):
    chunk = DocumentChunk(
        text="LocalDocs AI can export an Obsidian-friendly vault.",
        file_name="guide.md",
        file_path="guide.md",
        file_type="markdown",
        chunk_index=1,
    )
    summary = DocumentSummary(
        file_name="guide.md",
        summary="guide.md: LocalDocs AI exports Markdown vaults.",
        citations=[Citation(file_name="guide.md", chunk_index=1)],
    )
    answer = Answer(
        question="What can it export?",
        answer="It can export an Obsidian-friendly vault.",
        citations=[Citation(file_name="guide.md", chunk_index=1)],
    )
    flashcards = generate_flashcards([chunk])
    questions = generate_study_questions([chunk])

    vault_path = export_obsidian_vault(
        tmp_path / "obsidian_vault",
        [chunk],
        summaries=[summary],
        qa_history=[answer],
        flashcards=flashcards,
        study_questions=questions,
    )

    assert (vault_path / "00_Index.md").exists()
    assert (vault_path / "Summaries.md").exists()
    assert (vault_path / "Questions.md").exists()
    assert (vault_path / "Flashcards.md").exists()
    assert (vault_path / "Sources.md").exists()
    assert (vault_path / "Documents" / "guide.md").exists()

    index = (vault_path / "00_Index.md").read_text(encoding="utf-8")
    assert "[[Summaries]]" in index
    assert "[[Documents/guide]]" in index

    questions_content = (vault_path / "Questions.md").read_text(encoding="utf-8")
    assert "What can it export?" in questions_content
    assert "Source: guide.md, chunk 1" in questions_content
