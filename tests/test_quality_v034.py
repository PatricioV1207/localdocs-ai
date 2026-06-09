from localdocs.flashcards import generate_flashcards
import pytest

from localdocs.cleaning import is_low_value_text, split_sentences
from localdocs.models import DocumentChunk, SearchResult
from localdocs.qa import answer_question
from localdocs.study import generate_study_questions
from localdocs.summarizer import summarize_documents


def _chunk(text: str, index: int, page: int | None = None) -> DocumentChunk:
    return DocumentChunk(
        text=text,
        file_name="seguridad.pdf",
        file_path="seguridad.pdf",
        file_type="pdf",
        chunk_index=index,
        page_number=page,
    )


@pytest.mark.parametrize(
    "text",
    [
        "Índice. Descarga segura del sistema ........ 25. Contenido técnico ........ 31.",
        "Información legal y condiciones marco para todos los productos del catálogo.",
        "Productos SMC y componentes adecuados para su aplicación industrial.",
        "Expertise – Passion – Automation. En el lado seguro con SMC.",
        "Visite www.tecnical.cat o nuestras oficinas de MANRESA para más información.",
        "Centros comerciales en LLEIDA, IGUALADA y RIPOLL para atención al cliente.",
    ],
)
def test_known_low_value_sections_are_rejected(text):
    assert is_low_value_text(text) is True


def test_study_tools_prefer_technical_sections_over_keyword_heavy_marketing():
    low_value = _chunk(
        "En el lado seguro con SMC. Productos SMC para descarga segura del sistema, "
        "monitorización de presión segura y circuitos neumáticos. "
        "Expertise – Passion – Automation. www.tecnical.cat MANRESA LLEIDA.",
        1,
        1,
    )
    technical = _chunk(
        "# Monitorización de presión segura\n"
        "La monitorización de presión segura controla la presión del circuito y bloquea "
        "el movimiento del actuador cuando detecta una condición insegura.",
        2,
        9,
    )

    questions = generate_study_questions([low_value, technical], max_questions=10)
    cards = generate_flashcards([low_value, technical], max_cards=10)
    summary = summarize_documents([low_value, technical], use_openai=False)[0]

    assert {item.citation.chunk_index for item in questions} == {2}
    assert {item.citation.chunk_index for item in cards} == {2}
    assert {item.chunk_index for item in summary.citations} == {2}
    assert "Expertise" not in summary.summary


def test_flashcards_reject_unrelated_index_legal_and_marketing_answers():
    chunks = [
        _chunk(
            "# Presión residual\n"
            "– En el lado seguro con SMC 3 – Guía básica de seguridad y productos.",
            1,
        ),
        _chunk(
            "# Descarga segura del sistema\n"
            "Descarga segura del sistema ........ 25 Circuitos neumáticos ........ 31.",
            2,
        ),
        _chunk(
            "# ISO 12100\n"
            "Información legal, condiciones marco y copyright del fabricante.",
            3,
        ),
        _chunk(
            "# Circuitos neumáticos\n"
            "Expertise – Passion – Automation. Componentes adecuados para su aplicación.",
            4,
        ),
    ]

    assert generate_flashcards(chunks, max_cards=10) == []


def test_pressure_residual_card_uses_definition_not_unsupported_function_prompt():
    chunk = _chunk(
        "# Presión residual\n"
        "La presión residual es la presión que permanece en las cámaras después de aislar "
        "la alimentación de aire comprimido.",
        1,
    )

    cards = generate_flashcards([chunk], max_cards=10)

    assert len(cards) == 1
    assert cards[0].question == "¿Qué es la presión residual?"
    assert "presión residual" in cards[0].answer.lower()


def test_local_qa_rejects_heading_collisions_and_keeps_complete_evidence(spanish_safety_chunks):
    broken = _chunk(
        "Rango de descarga segura del Funciones de seguridad típicas en neumática.",
        7,
        3,
    )
    results = [SearchResult(chunk=broken, score=0.99)]
    results.extend(
        SearchResult(chunk=chunk, score=score)
        for chunk, score in zip(
            spanish_safety_chunks[2:5],
            [0.90, 0.89, 0.88],
            strict=True,
        )
    )

    answer = answer_question(
        "¿Qué es descarga segura del actuador y prevención de arranque inesperado?",
        results,
        use_openai=False,
    )

    assert answer.enough_evidence is True
    assert "descarga segura del actuador" in answer.answer.lower()
    assert "prevención de arranque inesperado" in answer.answer.lower()
    assert "válvula 1v1" in answer.answer.lower()
    assert "rango de descarga segura del funciones" not in answer.answer.lower()
    assert all(sentence.endswith((".", "?", "!")) for sentence in split_sentences(answer.answer))
    assert {citation.chunk_index for citation in answer.citations} == {3, 4, 5}


def test_local_qa_rejects_multiple_section_titles_without_a_technical_action():
    broken = _chunk(
        "Descarga segura del sistema Prevención de arranque inesperado "
        "Circuitos neumáticos ISO 13849.",
        1,
    )

    answer = answer_question(
        "¿Qué es la descarga segura del sistema?",
        [SearchResult(chunk=broken, score=0.99)],
        use_openai=False,
    )

    assert answer.enough_evidence is False
    assert answer.citations == []
