from localdocs.models import DocumentChunk, SearchResult
from localdocs.qa import answer_question


def test_extractive_qa_returns_citations_without_openai(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunk = DocumentChunk(
        text="LocalDocs AI uses TF-IDF search for the v0.1 local search index.",
        file_name="guide.md",
        file_path="guide.md",
        file_type="markdown",
        chunk_index=2,
    )

    answer = answer_question(
        "What search does LocalDocs AI use?",
        [SearchResult(chunk=chunk, score=0.8)],
    )

    assert answer.enough_evidence is True
    assert answer.used_llm is False
    assert "TF-IDF search" in answer.answer
    assert len(answer.citations) == 1
    assert answer.citations[0].label() == "guide.md, chunk 2"


def test_qa_says_when_evidence_is_weak(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunk = DocumentChunk(
        text="A weak unrelated result.",
        file_name="note.txt",
        file_path="note.txt",
        file_type="txt",
        chunk_index=1,
    )

    answer = answer_question(
        "What does LocalDocs AI use for search?",
        [SearchResult(chunk=chunk, score=0.001)],
    )

    assert answer.enough_evidence is False
    assert answer.citations == []
    assert "not enough evidence" in answer.answer


def test_pdf_citation_label_includes_page_number():
    chunk = DocumentChunk(
        text="PDF text.",
        file_name="manual.pdf",
        file_path="manual.pdf",
        file_type="pdf",
        page_number=3,
        chunk_index=5,
    )
    result = SearchResult(chunk=chunk, score=0.7)

    assert result.source_label() == "manual.pdf, page 3, chunk 5"
