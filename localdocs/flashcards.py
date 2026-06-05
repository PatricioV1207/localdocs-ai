"""Flashcard generation and Anki TSV export."""

from __future__ import annotations

import re
from pathlib import Path

from localdocs.models import Citation, DocumentChunk, Flashcard


def generate_flashcards(chunks: list[DocumentChunk], max_cards: int = 20) -> list[Flashcard]:
    """Generate simple extractive flashcards from document chunks."""

    flashcards: list[Flashcard] = []
    seen: set[tuple[str, str, str]] = set()

    for chunk in chunks:
        if len(flashcards) >= max_cards:
            break

        question, answer = _card_from_chunk(chunk)
        if not question or not answer:
            continue

        citation = Citation.from_chunk(chunk)
        key = (question.lower(), answer.lower(), citation.label())
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
    heading = _first_heading(chunk.text)
    answer = _first_sentence_without_heading(chunk.text)
    if not answer:
        return "", ""

    if heading:
        question = f"What is a key point from {heading}?"
    else:
        question = f"What is a key point from {chunk.file_name}, chunk {chunk.chunk_index}?"

    return question, _truncate(answer, 280)


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _first_sentence_without_heading(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    compact = " ".join(" ".join(lines).split())
    if not compact:
        return ""

    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", compact) if sentence.strip()]
    return sentences[0] if sentences else compact


def _truncate(text: str, max_chars: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."


def _clean_tsv_field(value: str) -> str:
    return " ".join(value.replace("\t", " ").split())
