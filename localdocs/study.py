"""Study question generation and Markdown export."""

from __future__ import annotations

import re
from pathlib import Path

from localdocs.models import Citation, DocumentChunk, StudyQuestion


def generate_study_questions(chunks: list[DocumentChunk], max_questions: int = 20) -> list[StudyQuestion]:
    """Generate simple local study questions from chunks."""

    questions: list[StudyQuestion] = []
    seen: set[tuple[str, str]] = set()

    for chunk in chunks:
        if len(questions) >= max_questions:
            break

        question_text = _question_from_chunk(chunk)
        if not question_text:
            continue

        citation = Citation.from_chunk(chunk)
        key = (question_text.lower(), citation.label())
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
    heading = _first_heading(chunk.text)
    if heading:
        return f"How would you explain {heading}?"

    sentence = _first_sentence(chunk.text)
    if not sentence:
        return ""

    terms = [term for term in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", sentence) if term.lower() not in _STOPWORDS]
    if terms:
        return f"What should you remember about {terms[0]} from {chunk.file_name}?"
    return f"What is the main idea of {chunk.file_name}, chunk {chunk.chunk_index}?"


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _first_sentence(text: str) -> str:
    compact = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
    compact = " ".join(compact.split())
    if not compact:
        return ""
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", compact) if sentence.strip()]
    return sentences[0] if sentences else compact


_STOPWORDS = {
    "about",
    "from",
    "into",
    "local",
    "with",
    "that",
    "this",
    "they",
    "their",
    "there",
}
