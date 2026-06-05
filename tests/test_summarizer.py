from localdocs.models import DocumentChunk
from localdocs.summarizer import summarize_documents


def test_summarize_documents_returns_source_name_and_citations(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunks = [
        DocumentChunk(
            text="LocalDocs AI keeps document search local. It exports useful Markdown notes.",
            file_name="guide.md",
            file_path="guide.md",
            file_type="markdown",
            chunk_index=1,
        ),
        DocumentChunk(
            text="Answers include source citations.",
            file_name="guide.md",
            file_path="guide.md",
            file_type="markdown",
            chunk_index=2,
        ),
    ]

    summaries = summarize_documents(chunks)

    assert len(summaries) == 1
    assert summaries[0].file_name == "guide.md"
    assert summaries[0].summary.startswith("guide.md:")
    assert "document search local" in summaries[0].summary
    assert [citation.label() for citation in summaries[0].citations] == [
        "guide.md, chunk 1",
        "guide.md, chunk 2",
    ]
