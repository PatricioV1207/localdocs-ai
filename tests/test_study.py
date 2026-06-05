from localdocs.models import DocumentChunk
from localdocs.study import export_study_questions_markdown, generate_study_questions


def test_generate_study_questions_includes_sources():
    chunks = [
        DocumentChunk(
            text="# Chunking Strategies\nParagraph chunking groups nearby paragraphs.",
            file_name="guide.md",
            file_path="guide.md",
            file_type="markdown",
            chunk_index=1,
        )
    ]

    questions = generate_study_questions(chunks, max_questions=3)

    assert len(questions) == 1
    assert questions[0].question == "How would you explain Chunking Strategies?"
    assert questions[0].citation.label() == "guide.md, chunk 1"


def test_export_study_questions_markdown(tmp_path):
    chunk = DocumentChunk(
        text="LocalDocs AI creates review questions from chunks.",
        file_name="note.txt",
        file_path="note.txt",
        file_type="txt",
        chunk_index=1,
    )
    questions = generate_study_questions([chunk], max_questions=1)

    path = export_study_questions_markdown(questions, export_dir=tmp_path)

    content = path.read_text(encoding="utf-8")
    assert "# LocalDocs AI Study Questions" in content
    assert "Source: note.txt, chunk 1" in content
