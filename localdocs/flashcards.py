"""Flashcard generation and Anki TSV export."""

from __future__ import annotations

from pathlib import Path

from localdocs.cleaning import (
    appears_spanish,
    first_heading,
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
    spanish_concept_phrase,
)
from localdocs.document_types import detect_document_profiles, detect_section_role
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
    "allows",
    "controls",
    "creates",
    "detects",
    "ensures",
    "generates",
    "prevents",
    "provides",
    "requires",
    "supports",
)


def generate_flashcards(chunks: list[DocumentChunk], max_cards: int = 10) -> list[Flashcard]:
    """Generate simple extractive flashcards from document chunks."""

    flashcards: list[Flashcard] = []
    seen_concepts: set[str] = set()
    ranked_chunks = informative_chunks(chunks)
    profiles = detect_document_profiles(chunks)
    has_useful_chunks = any(not is_low_value_text(chunk.text) for chunk in ranked_chunks)

    for chunk in ranked_chunks:
        if len(flashcards) >= max_cards:
            break
        if has_useful_chunks and is_low_value_text(chunk.text):
            continue

        profile = profiles[chunk.file_path or chunk.file_name]
        question, answer = _card_from_chunk(
            chunk,
            profile.document_type,
            detect_section_role(chunk.text),
        )
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


def _card_from_chunk(
    chunk: DocumentChunk,
    document_type: str,
    section_role: str,
) -> tuple[str, str]:
    concepts = extract_concepts(chunk.text, limit=1)
    if not concepts:
        return "", ""
    concept = concepts[0]
    answer = concept_sentence(chunk.text, concept)
    heading_support = concept_key(first_heading(chunk.text)) == concept_key(concept)
    if not answer or (
        not _answer_matches_concept(answer, concept)
        and not (heading_support and is_quality_sentence(answer))
    ):
        return "", ""

    if appears_spanish(chunk.text):
        question = _spanish_card_question(
            concept,
            answer,
            document_type,
            section_role,
        )
    else:
        question = _english_card_question(concept, document_type, section_role)
    if "función" in question.lower() and not _has_function_evidence(answer):
        return "", ""
    return question, truncate_at_clause(answer, 280)


def _english_card_question(concept: str, document_type: str, section_role: str) -> str:
    if document_type == "research_paper" and section_role == "result":
        return f"What result is reported about {concept}?"
    if document_type == "legal_business" and section_role == "obligation":
        return f"What requirement applies to {concept}?"
    if document_type == "academic_practice" and section_role in {"objective", "question"}:
        return f"What should be understood about {concept}?"
    if document_type == "technical_manual" and section_role == "procedure":
        return f"What procedure is specified for {concept}?"
    return f"What is a key point about {concept}?"


def _spanish_card_question(
    concept: str,
    answer: str,
    document_type: str,
    section_role: str,
) -> str:
    label = spanish_concept_phrase(concept)
    if document_type == "research_paper" and section_role == "result":
        return f"¿Qué resultado se informa sobre {label}?"
    if document_type == "legal_business" and section_role == "obligation":
        return f"¿Qué requisito se establece para {label}?"
    if document_type == "academic_practice" and section_role in {"objective", "question"}:
        return f"¿Qué debe comprenderse sobre {label}?"
    if document_type == "technical_manual" and section_role == "procedure":
        return f"¿Qué procedimiento se indica para {label}?"
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
