import sys
from types import SimpleNamespace

from localdocs.models import DocumentChunk
from localdocs.summarizer import OPENAI_FALLBACK_NOTE, summarize_documents


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
    ]


def test_summarize_documents_avoids_copyright_front_matter(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunks = [
        DocumentChunk(
            text="Copyright 2024 Publisher Press. All rights reserved. ISBN 1234567890.",
            file_name="manual.pdf",
            file_path="manual.pdf",
            file_type="pdf",
            chunk_index=1,
        ),
        DocumentChunk(
            text="Pneumatic actuators convert compressed air into controlled linear motion. The control valve regulates airflow to extend or retract the actuator safely.",
            file_name="manual.pdf",
            file_path="manual.pdf",
            file_type="pdf",
            chunk_index=2,
        ),
    ]

    summaries = summarize_documents(chunks)

    assert "Pneumatic actuators" in summaries[0].summary
    assert "Copyright" not in summaries[0].summary
    assert [citation.label() for citation in summaries[0].citations] == ["manual.pdf, chunk 2"]


def test_spanish_summary_prefers_technical_sections(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunks = [
        DocumentChunk(
            text="Manual didáctico Festo Weber. Autores, contenido, referencia y soluciones.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=1,
        ),
        DocumentChunk(
            text="# Objetivos\nEl ejercicio identifica los componentes principales de un circuito neumático seguro.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=2,
        ),
        DocumentChunk(
            text="# Seguridad\nLa parada de emergencia evita movimientos inesperados de la plataforma elevadora.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=3,
        ),
    ]

    summary = summarize_documents(chunks)[0]

    assert summary.summary.startswith("Resumen de manual_es.pdf:")
    assert "parada de emergencia" in summary.summary
    assert "Festo" not in summary.summary
    assert {citation.chunk_index for citation in summary.citations} == {2, 3}


def test_summary_openai_error_hides_raw_payload(monkeypatch):
    class FailingCompletions:
        def create(self, **_kwargs):
            raise RuntimeError("authentication_error: raw API payload")

    class FakeOpenAI:
        def __init__(self, **_kwargs):
            self.chat = SimpleNamespace(completions=FailingCompletions())

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    chunk = DocumentChunk(
        text="Pneumatic safety controls stop actuator motion when pressure becomes unsafe.",
        file_name="safety.md",
        file_path="safety.md",
        file_type="markdown",
        chunk_index=1,
    )

    summary = summarize_documents([chunk], openai_api_key="test-key")[0]

    assert summary.used_llm is False
    assert summary.note == OPENAI_FALLBACK_NOTE
    assert "authentication_error" not in summary.note
    assert summary.citations[0].label() == "safety.md, chunk 1"


def test_summary_rejects_document_with_only_low_value_text(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunks = [
        DocumentChunk(
            text="Información legal y condiciones marco. Copyright 2026. Todos los derechos reservados.",
            file_name="noise.pdf",
            file_path="noise.pdf",
            file_type="pdf",
            chunk_index=1,
        ),
        DocumentChunk(
            text="Índice. Seguridad neumática ........ 7. Productos ........ 18.",
            file_name="noise.pdf",
            file_path="noise.pdf",
            file_type="pdf",
            chunk_index=2,
        ),
    ]

    summary = summarize_documents(chunks, use_openai=False)[0]

    assert "No summary could be generated" in summary.summary
    assert summary.citations == []
