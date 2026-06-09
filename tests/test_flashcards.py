from localdocs.flashcards import export_anki_tsv, generate_flashcards
from localdocs.models import DocumentChunk


def test_generate_flashcards_includes_source_reference():
    chunks = [
        DocumentChunk(
            text="# Local Search\nLocalDocs AI uses TF-IDF search for local retrieval.",
            file_name="guide.md",
            file_path="guide.md",
            file_type="markdown",
            chunk_index=1,
        )
    ]

    cards = generate_flashcards(chunks, max_cards=5)

    assert len(cards) == 1
    assert cards[0].question == "What is a key point about Local Search?"
    assert "TF-IDF search" in cards[0].answer
    assert cards[0].citation.label() == "guide.md, chunk 1"


def test_export_anki_tsv_writes_three_columns(tmp_path):
    chunk = DocumentChunk(
        text="LocalDocs AI exports Anki-compatible flashcards.",
        file_name="guide.md",
        file_path="guide.md",
        file_type="markdown",
        chunk_index=2,
    )
    cards = generate_flashcards([chunk], max_cards=1)

    path = export_anki_tsv(cards, tmp_path / "flashcards.tsv")

    content = path.read_text(encoding="utf-8").strip()
    fields = content.split("\t")
    assert len(fields) == 3
    assert fields[0].startswith("What is a key point")
    assert fields[2] == "guide.md, chunk 2"


def test_generate_flashcards_filters_duplicates_and_noise():
    chunks = [
        DocumentChunk(
            text="Copyright 2024 Publisher Press. All rights reserved. ISBN 1234567890.",
            file_name="manual.pdf",
            file_path="manual.pdf",
            file_type="pdf",
            chunk_index=1,
        ),
        DocumentChunk(
            text="# Pneumatic Actuator\nA pneumatic actuator converts compressed air into controlled linear motion.",
            file_name="manual.pdf",
            file_path="manual.pdf",
            file_type="pdf",
            chunk_index=2,
        ),
        DocumentChunk(
            text="# Pneumatic Actuator\nA pneumatic actuator converts compressed air into controlled linear motion.",
            file_name="manual.pdf",
            file_path="manual.pdf",
            file_type="pdf",
            chunk_index=3,
        ),
    ]

    cards = generate_flashcards(chunks, max_cards=5)

    assert len(cards) == 1
    assert all("Copyright" not in card.answer for card in cards)
    assert cards[0].citation.label() == "manual.pdf, chunk 2"


def test_generate_flashcards_rejects_weak_terms_and_deduplicates_concepts():
    chunks = [
        DocumentChunk(
            text="Para únicamente el estudiante consulta el manual didáctico de Festo Weber.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=1,
        ),
        DocumentChunk(
            text="# Válvula antirretorno\nLa válvula antirretorno permite el flujo de aire en una sola dirección.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=2,
        ),
        DocumentChunk(
            text="# Válvula antirretorno\nEste componente evita el retorno de aire comprimido hacia la fuente.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=3,
        ),
    ]

    cards = generate_flashcards(chunks, max_cards=10)

    assert len(cards) == 1
    assert "válvula antirretorno" in cards[0].question
    assert cards[0].citation.file_name == "manual_es.pdf"
    assert cards[0].citation.chunk_index in {2, 3}
    assert "Festo" not in cards[0].question


def test_flashcard_long_answer_ends_at_complete_clause():
    chunk = DocumentChunk(
        text=(
            "# Monitorización de presión segura\n"
            "La monitorización de presión segura controla la presión del circuito, "
            "detecta condiciones peligrosas antes del movimiento, bloquea el actuador "
            "cuando el valor supera el límite configurado, registra el estado para el "
            "diagnóstico técnico y mantiene la máquina detenida hasta que una persona "
            "autorizada completa el procedimiento de restablecimiento seguro."
        ),
        file_name="manual.pdf",
        file_path="manual.pdf",
        file_type="pdf",
        chunk_index=1,
    )

    card = generate_flashcards([chunk], max_cards=1)[0]

    assert card.answer.endswith(".")
    assert "..." not in card.answer
    assert len(card.answer) <= 280
