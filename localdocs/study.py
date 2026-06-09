"""Study question generation and Markdown export."""

from __future__ import annotations

import re
from pathlib import Path

from localdocs.cleaning import (
    appears_spanish,
    informative_chunks,
    is_low_value_text,
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
from localdocs.models import Citation, DocumentChunk, StudyQuestion


def generate_study_questions(chunks: list[DocumentChunk], max_questions: int = 10) -> list[StudyQuestion]:
    """Generate simple local study questions from chunks."""

    questions: list[StudyQuestion] = []
    seen_concepts: set[str] = set()
    ranked_chunks = informative_chunks(chunks)
    profiles = detect_document_profiles(chunks)
    has_useful_chunks = any(not is_low_value_text(chunk.text) for chunk in ranked_chunks)

    for chunk in ranked_chunks:
        if len(questions) >= max_questions:
            break
        if has_useful_chunks and is_low_value_text(chunk.text):
            continue

        concepts = extract_concepts(chunk.text, limit=1)
        if not concepts:
            continue
        concept = concepts[0]
        concept_id = concept_key(concept)
        if concept_id in seen_concepts:
            continue

        profile = profiles[chunk.file_path or chunk.file_name]
        question_text = _question_from_chunk(
            chunk,
            concept,
            profile.document_type,
            detect_section_role(chunk.text),
        )
        question_text = normalize_generated_question(question_text)
        if not question_text or not is_valid_generated_question(question_text):
            continue

        citation = Citation.from_chunk(chunk)
        seen_concepts.add(concept_id)
        questions.append(StudyQuestion(question=question_text, citation=citation))

    return questions


def export_study_questions_markdown(
    questions: list[StudyQuestion],
    export_dir: str | Path = "exports",
    filename: str = "study_questions.md",
) -> Path:
    """Export generated study questions to Markdown."""

    export_path = Path(export_dir) / filename
    export_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["# LocalDocs AI Study Questions", ""]
    if not questions:
        lines.extend(["No study questions have been generated yet.", ""])
    else:
        for number, question in enumerate(questions, start=1):
            lines.extend(
                [
                    f"{number}. {question.question}",
                    f"   - Source: {question.citation.label()}",
                ]
            )

    export_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return export_path


def _question_from_chunk(
    chunk: DocumentChunk,
    concept: str,
    document_type: str,
    section_role: str,
) -> str:
    concept_context = concept_sentence(chunk.text, concept) or chunk.text
    if appears_spanish(chunk.text):
        return _spanish_question(concept, concept_context, document_type, section_role)

    if document_type == "research_paper" and section_role == "result":
        return f"What did the document find about {concept}?"
    if document_type == "legal_business" and section_role == "obligation":
        return f"What obligation applies to {concept}?"
    if document_type == "academic_practice" and section_role in {"objective", "question"}:
        return f"What should a learner understand about {concept}?"
    if document_type == "technical_manual" and section_role == "procedure":
        return f"How should {concept} be performed?"
    if _looks_like_process(concept_context):
        return f"Why is {concept} important?"
    if _looks_like_function(concept_context):
        return f"What is the function of {concept}?"
    if _looks_like_recommendation(concept_context):
        return f"What measures are recommended for {concept}?"
    return f'What is meant by "{concept}"?'


def _spanish_question(
    concept: str,
    text: str,
    document_type: str,
    section_role: str,
) -> str:
    lower = text.lower()
    label = spanish_concept_phrase(concept)
    concept_lower = concept.lower()

    if document_type == "research_paper" and section_role == "result":
        return f"¿Qué encontró el documento sobre {label}?"
    if document_type == "legal_business" and section_role == "obligation":
        return f"¿Qué obligación se establece para {label}?"
    if document_type == "academic_practice" and section_role in {"objective", "question"}:
        return f"¿Qué debe comprender el estudiante sobre {label}?"
    if document_type == "technical_manual" and section_role == "procedure":
        return f"¿Cómo debe realizarse {label}?"
    if "se define como" in lower or "es una función" in lower or "consiste en" in lower:
        return f"¿Qué es {label}?"
    if "recom" in lower or "medida" in lower:
        return f"¿Qué medidas se recomiendan para {label}?"
    if any(term in lower for term in ["condición", "condiciones", "debe cumplirse", "deben cumplirse"]):
        return f"¿Qué condiciones deben cumplirse para {label}?"
    if any(term in lower for term in ["reduce el riesgo", "reducir el riesgo", "evita el riesgo", "previene el riesgo"]):
        return f"¿Qué riesgo ayuda a reducir {label}?"
    if re.search(r"\bfunci[oó]n\b", lower) or _is_function_concept(concept_lower):
        return f"¿Cuál es la función de {label}?"
    if "importante" in lower or "importancia" in lower or concept_lower.startswith(("iso ", "evaluación", "reducción")):
        return f"¿Por qué es importante {label}?"
    return f"¿Qué es {label}?"


def _looks_like_process(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in ["important", "importance", "required", "critical", "because"])


def _looks_like_function(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in ["function", "purpose", "role"])


def _looks_like_recommendation(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in ["recommend", "measure", "should", "best practice"])


def _is_function_concept(concept: str) -> bool:
    return False
