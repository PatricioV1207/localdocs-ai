from localdocs.export import export_qa_history, export_summaries
from localdocs.models import Answer, Citation, DocumentSummary


def test_export_summaries_writes_markdown(tmp_path):
    summaries = [
        DocumentSummary(
            file_name="guide.md",
            summary="guide.md: LocalDocs AI supports local search.",
            citations=[Citation(file_name="guide.md", chunk_index=1)],
        )
    ]

    path = export_summaries(summaries, export_dir=tmp_path)

    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "# LocalDocs AI Summaries" in content
    assert "guide.md: LocalDocs AI supports local search." in content
    assert "- guide.md, chunk 1" in content


def test_export_qa_history_writes_markdown(tmp_path):
    answers = [
        Answer(
            question="What does it support?",
            answer="It supports local search.",
            citations=[Citation(file_name="guide.md", chunk_index=2)],
        )
    ]

    path = export_qa_history(answers, export_dir=tmp_path)

    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "# LocalDocs AI Q&A History" in content
    assert "**Q:** What does it support?" in content
    assert "- guide.md, chunk 2" in content
