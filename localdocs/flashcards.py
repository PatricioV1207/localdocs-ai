"""Flashcard generation and Anki TSV export."""

from __future__ import annotations

from pathlib import Path

from localdocs.cleaning import appears_spanish, informative_chunks, informative_terms, is_low_value_text
from localdocs.concepts import (
    concept_key,
    concept_sentence,
    extract_concepts,
    related_concept,
    spanish_concept_phrase,
)
from localdocs.models import Citation, DocumentChunk, Flashcard


def generate_flashcards(chunks: list[DocumentChunk], max_cards: int = 20) -> list[Flashcard]:
    """Generate simple extractive flashcards from document chunks."""

    flashcards: list[Flashcard] = []
    seen_concepts: set[str] = set()
    ranked_chunks = informative_chunks(chunks)
    has_useful_chunks = any(not is_low_value_text(chunk.text) for chunk in ranked_chunks)

    for chunk in ranked_chunks:
        if len(flashcards) >= max_cards:
            break
        if has_useful_chunks and is_low_value_text(chunk.text):
            continue

        question, answer = _card_from_chunk(chunk)
        if not question or not answer:
            continue

        citation = Citation.from_chunk(chunk)
        concepts = extract_concepts(chunk.text, limit=1)
        concept_id = concept_key(concepts[0]) if concepts else question.lower()
        if concept_id in seen_concepts:
            continue

        seen_concepts.add(concept_id)
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
    concepts = extract_concepts(chunk.text, limit=1)
    if not concepts:
        return "", ""
    concept = concepts[0]
    answer = concept_sentence(chunk.text, concept)
    if not answer or not _answer_matches_concept(answer, concept):
        return "", ""

    if appears_spanish(chunk.text):
        question = _spanish_card_question(chunk.text, concept, answer)
    else:
        question = f"What is a key point about {concept}?"
    return question, _truncate(answer, 280)


def _spanish_card_question(text: str, concept: str, answer: str) -> str:
    label = spanish_concept_phrase(concept)
    if concept.lower().startswith("válvula "):
        related = related_concept(text, concept)
        if related:
            return f"¿Qué función cumple {label} en {spanish_concept_phrase(related)}?"
        return f"¿Qué función cumple {label}?"
    if "se define como" in answer.lower() or "es una función" in answer.lower() or "consiste en" in answer.lower():
        return f"¿Qué es {label}?"
    return f"¿Cuál es la función de {label}?"


def _answer_matches_concept(answer: str, concept: str) -> bool:
    answer_terms = informative_terms(answer)
    concept_terms = informative_terms(concept)
    return bool(answer_terms & concept_terms)


def _truncate(text: str, max_chars: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."


def _clean_tsv_field(value: str) -> str:
    return " ".join(value.replace("\t", " ").split())
