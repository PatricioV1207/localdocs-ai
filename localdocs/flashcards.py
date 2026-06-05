"""Flashcard generation and Anki TSV export."""

from __future__ import annotations

from pathlib import Path

from localdocs.cleaning import best_concept, best_sentences, informative_chunks, is_low_value_text, is_weak_concept
from localdocs.models import Citation, DocumentChunk, Flashcard


def generate_flashcards(chunks: list[DocumentChunk], max_cards: int = 20) -> list[Flashcard]:
    """Generate simple extractive flashcards from document chunks."""

    flashcards: list[Flashcard] = []
    seen: set[tuple[str, str]] = set()

    for chunk in informative_chunks(chunks):
        if len(flashcards) >= max_cards:
            break
        if is_low_value_text(chunk.text):
            continue

        question, answer = _card_from_chunk(chunk)
        if not question or not answer:
            continue

        citation = Citation.from_chunk(chunk)
        key = (question.lower(), answer.lower())
        if key in seen:
            continue

        seen.add(key)
        flashcards.append(Flashcard(question=question, answer=answer, citation=citation))

    return flashcards


def export_anki_tsv(flashcards: list[Flashcard], path: str | Path = "exports/flashcards.tsv") -> Path:
    """Export flashcards as Question<TAB>Answer<TAB>Source for Anki import."""

    export_path = Path(path)
    export_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    for card in flashcards:
        lines.append(
            "\t".join(
                [
                    _clean_tsv_field(card.question),
                    _clean_tsv_field(card.answer),
                    _clean_tsv_field(card.citation.label()),
                ]
            )
        )

    export_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return export_path


def _card_from_chunk(chunk: DocumentChunk) -> tuple[str, str]:
    concept = best_concept(chunk.text)
    answer = _best_answer(chunk.text)
    if not answer:
        return "", ""

    if concept and not is_weak_concept(concept):
        question = f"What is a key point about {concept}?"
    else:
        question = f"What is a key point from {chunk.file_name}, chunk {chunk.chunk_index}?"

    return question, _truncate(answer, 280)


def _best_answer(text: str) -> str:
    sentences = best_sentences(text, limit=1)
    return sentences[0] if sentences else ""


def _truncate(text: str, max_chars: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."


def _clean_tsv_field(value: str) -> str:
    return " ".join(value.replace("\t", " ").split())
