from localdocs.cleaning import (
    best_concept,
    clean_text,
    informative_chunks,
    is_low_value_text,
    is_valid_question,
    repeated_line_keys,
)
from localdocs.models import DocumentChunk


def test_clean_text_removes_repeated_headers_page_numbers_and_copyright():
    noisy = """
FESTO MANUAL 2024
1
Copyright 2024 Publisher Press. All rights reserved.
__________
Pressure valves regulate compressed air in pneumatic systems.
FESTO MANUAL 2024
2
FESTO MANUAL 2024
3
"""

    cleaned = clean_text(noisy)

    assert "Pressure valves regulate compressed air" in cleaned
    assert "Copyright" not in cleaned
    assert "__________" not in cleaned
    assert "FESTO MANUAL" not in cleaned
    assert "\n1\n" not in cleaned


def test_low_value_chunk_detection_and_informative_fallback():
    noisy = DocumentChunk(
        text="Table of Contents Chapter 1 ........ 1 Chapter 2 ........ 9 Copyright Publisher.",
        file_name="book.pdf",
        file_path="book.pdf",
        file_type="pdf",
        chunk_index=1,
    )
    useful = DocumentChunk(
        text="Directional control valves route compressed air to actuator chambers in a pneumatic system.",
        file_name="book.pdf",
        file_path="book.pdf",
        file_type="pdf",
        chunk_index=2,
    )

    assert is_low_value_text(noisy.text) is True
    assert is_low_value_text(useful.text) is False
    assert informative_chunks([noisy, useful], limit=1) == [useful]


def test_question_validation_rejects_placeholders_and_short_text():
    assert is_valid_question("") is False
    assert is_valid_question("Your question") is False
    assert is_valid_question("Your question here") is False
    assert is_valid_question("¿Qué es para?") is False
    assert is_valid_question("why") is False
    assert is_valid_question("How does pneumatic pressure regulation work?") is True


def test_repeated_line_keys_remove_pdf_like_headers_across_pages():
    pages = [
        "FESTO MANUAL\nPressure valves regulate compressed air.",
        "FESTO MANUAL\nActuators convert pressure into motion.",
    ]

    keys = repeated_line_keys(pages)
    cleaned = clean_text(pages[0], repeated_line_keys=keys)

    assert "FESTO MANUAL" not in cleaned
    assert "Pressure valves regulate compressed air." in cleaned


def test_best_concept_prefers_multiword_technical_phrases():
    assert best_concept("La seguridad en sistemas neumáticos evita movimientos inesperados.") == (
        "seguridad en sistemas neumáticos"
    )
    assert best_concept("La parada de emergencia detiene la plataforma elevadora.") == "parada de emergencia"
    assert best_concept("La unidad de relés de seguridad supervisa el circuito.") == (
        "unidad de relés de seguridad"
    )


def test_best_concept_rejects_weak_spanish_metadata():
    assert best_concept("Para únicamente el estudiante consulta el manual didáctico de Festo Weber.") == ""
