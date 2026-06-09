"""Flashcard generation and Anki TSV export."""

from __future__ import annotations

from pathlib import Path

from localdocs.cleaning import (
    appears_spanish,
    informative_chunks,
    informative_terms,
    is_low_value_text,
    is_quality_sentence,
    truncate_at_clause,
)
from localdocs.concepts import (
    concept_key,
    concept_sentence,
    extract_concepts,
    is_valid_generated_question,
    normalize_generated_question,
    related_concept,
    spanish_concept_phrase,
)
from localdocs.models import Citation, DocumentChunk, Flashcard


FUNCTION_ANSWER_MARKERS = (
    "bloquea",
    "conmuta",
    "controla",
    "evacua",
    "evita",
    "garantiza",
    "libera",
    "lleva a cabo",
    "monitoriza",
    "permite",
    "previene",
    "proporciona",
    "reduce",
    "se define como",
)


def generate_flashcards(chunks: list[DocumentChunk], max_cards: int = 10) -> list[Flashcard]:
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
        question = normalize_generated_question(question)
        if not question or not answer or not is_valid_generated_question(question):
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
    if "función" in question.lower() and not _has_function_evidence(answer):
        return "", ""
    return question, truncate_at_clause(answer, 280)


def _spanish_card_question(text: str, concept: str, answer: str) -> str:
    label = spanish_concept_phrase(concept)
    if concept.lower().startswith("válvula "):
        related = related_concept(text, concept)
        if related:
            return f"¿Qué función cumple {label} en {spanish_concept_phrase(related)}?"
        return f"¿Qué función cumple {label}?"
    if "se define como" in answer.lower() or "es una función" in answer.lower() or "consiste en" in answer.lower():
        return f"¿Qué es {label}?"
    if _has_function_evidence(answer):
        return f"¿Cuál es la función de {label}?"
    return f"¿Qué es {label}?"


def _answer_matches_concept(answer: str, concept: str) -> bool:
    if not is_quality_sentence(answer):
        return False
    if len(answer.split()) < 5:
        return False
    if not answer.rstrip().endswith((".", "?", "!")):
        return False
    if answer.lstrip().startswith(("-", "–", "—")):
        return False
    if concept_key(concept) in concept_key(answer):
        return True
    answer_terms = informative_terms(answer)
    concept_terms = informative_terms(concept)
    if not concept_terms:
        return False
    overlap = len(answer_terms & concept_terms)
    return overlap >= 2 and overlap / len(concept_terms) >= 0.5


def _has_function_evidence(answer: str) -> bool:
    lower = answer.lower()
    return any(marker in lower for marker in FUNCTION_ANSWER_MARKERS)


def _clean_tsv_field(value: str) -> str:
    return " ".join(value.replace("\t", " ").split())
