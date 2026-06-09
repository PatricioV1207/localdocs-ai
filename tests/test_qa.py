import sys
from types import SimpleNamespace

from localdocs.models import DocumentChunk, SearchResult
from localdocs.qa import OPENAI_FALLBACK_NOTE, WEAK_EVIDENCE_MESSAGE, answer_question


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
    assert "According to the strongest document evidence" in answer.answer
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
    assert answer.answer == WEAK_EVIDENCE_MESSAGE


def test_invalid_question_does_not_answer(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunk = DocumentChunk(
        text="LocalDocs AI uses TF-IDF search for local retrieval.",
        file_name="guide.md",
        file_path="guide.md",
        file_type="markdown",
        chunk_index=1,
    )

    answer = answer_question("Your question", [SearchResult(chunk=chunk, score=0.9)])

    assert answer.enough_evidence is False
    assert answer.citations == []
    assert "Enter a real question" in answer.answer


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


def test_openai_error_uses_friendly_extractive_fallback(monkeypatch):
    class FailingCompletions:
        def create(self, **_kwargs):
            raise RuntimeError("insufficient_quota: raw billing payload")

    class FakeOpenAI:
        def __init__(self, **_kwargs):
            self.chat = SimpleNamespace(completions=FailingCompletions())

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    chunk = DocumentChunk(
        text="Pressure sensors detect unsafe pneumatic system conditions before actuator movement.",
        file_name="safety.md",
        file_path="safety.md",
        file_type="markdown",
        chunk_index=1,
    )

    answer = answer_question(
        "How do pressure sensors improve pneumatic safety?",
        [SearchResult(chunk=chunk, score=0.9)],
        openai_api_key="test-key",
    )

    assert answer.used_llm is False
    assert answer.note == OPENAI_FALLBACK_NOTE
    assert "insufficient_quota" not in answer.note
    assert "Pressure sensors" in answer.answer
    assert answer.citations[0].label() == "safety.md, chunk 1"


def test_openai_can_be_disabled_even_when_environment_key_exists(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-used")
    chunk = DocumentChunk(
        text="Pressure sensors detect unsafe pneumatic system conditions before actuator movement.",
        file_name="safety.md",
        file_path="safety.md",
        file_type="markdown",
        chunk_index=1,
    )

    answer = answer_question(
        "How do pressure sensors improve pneumatic safety?",
        [SearchResult(chunk=chunk, score=0.9)],
        use_openai=False,
    )

    assert answer.used_llm is False
    assert answer.note == ""


def test_extractive_qa_does_not_invent_relation_between_separate_facts(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    standard = DocumentChunk(
        text="La norma ISO 12100 exige realizar una evaluación de riesgos.",
        file_name="manual.pdf",
        file_path="manual.pdf",
        file_type="pdf",
        chunk_index=1,
    )
    pressure = DocumentChunk(
        text="El circuito neumático funciona con una presión de servicio de 6 bar.",
        file_name="manual.pdf",
        file_path="manual.pdf",
        file_type="pdf",
        chunk_index=2,
    )

    answer = answer_question(
        "¿Qué presión exige la norma ISO 12100?",
        [
            SearchResult(chunk=standard, score=0.9),
            SearchResult(chunk=pressure, score=0.8),
        ],
        use_openai=False,
    )

    assert answer.enough_evidence is False
    assert answer.answer == WEAK_EVIDENCE_MESSAGE
    assert answer.citations == []


def test_extractive_qa_accepts_supported_single_sentence_relation(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunk = DocumentChunk(
        text="El circuito neumático funciona con una presión de servicio de 6 bar.",
        file_name="manual.pdf",
        file_path="manual.pdf",
        file_type="pdf",
        chunk_index=2,
    )

    answer = answer_question(
        "¿Cuál es la presión de servicio del circuito neumático?",
        [SearchResult(chunk=chunk, score=0.9)],
        use_openai=False,
    )

    assert answer.enough_evidence is True
    assert "6 bar" in answer.answer
    assert [citation.chunk_index for citation in answer.citations] == [2]


def test_extractive_qa_requires_requested_qualifier(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chunk = DocumentChunk(
        text="El circuito tiene un sensor de presión que detecta condiciones inseguras.",
        file_name="manual.pdf",
        file_path="manual.pdf",
        file_type="pdf",
        chunk_index=1,
    )

    answer = answer_question(
        "¿Qué presión máxima tiene el circuito?",
        [SearchResult(chunk=chunk, score=0.9)],
        use_openai=False,
    )

    assert answer.enough_evidence is False
    assert answer.answer == WEAK_EVIDENCE_MESSAGE
    assert answer.citations == []
