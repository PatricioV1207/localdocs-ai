"""Study question generation and Markdown export."""

from __future__ import annotations

from pathlib import Path

from localdocs.cleaning import (
    appears_spanish,
    best_concept,
    first_heading,
    informative_chunks,
    is_low_value_text,
    is_weak_concept,
)
from localdocs.models import Citation, DocumentChunk, StudyQuestion


def generate_study_questions(chunks: list[DocumentChunk], max_questions: int = 20) -> list[StudyQuestion]:
    """Generate simple local study questions from chunks."""

    questions: list[StudyQuestion] = []
    seen: set[str] = set()

    for chunk in informative_chunks(chunks):
        if len(questions) >= max_questions:
            break
        if is_low_value_text(chunk.text):
            continue

        question_text = _question_from_chunk(chunk)
        if not question_text:
            continue

        citation = Citation.from_chunk(chunk)
        key = question_text.lower()
        if key in seen:
            continue

        seen.add(key)
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


def _question_from_chunk(chunk: DocumentChunk) -> str:
    concept = first_heading(chunk.text) or best_concept(chunk.text)
    if not concept or is_weak_concept(concept):
        return ""

    if appears_spanish(chunk.text):
        return _spanish_question(concept, chunk.text)

    if _looks_like_process(chunk.text):
        return f"Why is {concept} important?"
    if _looks_like_function(chunk.text):
        return f"What is the function of {concept}?"
    if _looks_like_recommendation(chunk.text):
        return f"What measures are recommended for {concept}?"
    return f"What is {concept}?"


def _spanish_question(concept: str, text: str) -> str:
    lower = text.lower()
    if "recom" in lower or "medida" in lower:
        return f"¿Qué medidas se recomiendan para {concept}?"
    if "función" in lower or "funcion" in lower:
        return f"¿Cuál es la función de {concept}?"
    if "importante" in lower or "importancia" in lower:
        return f"¿Por qué es importante {concept}?"
    return f"¿Qué es {concept}?"


def _looks_like_process(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in ["important", "importance", "required", "critical", "because"])


def _looks_like_function(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in ["function", "purpose", "role"])


def _looks_like_recommendation(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in ["recommend", "measure", "should", "best practice"])
