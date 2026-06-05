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


def test_export_qa_history_accepts_mapping_citations(tmp_path):
    answers = [
        {
            "question": "Where is the PDF evidence?",
            "answer": "The evidence is on page 3.",
            "citations": [{"file_name": "manual.pdf", "page_number": 3, "chunk_index": 5}],
        }
    ]

    path = export_qa_history(answers, export_dir=tmp_path)

    content = path.read_text(encoding="utf-8")
    assert "- manual.pdf, page 3, chunk 5" in content
