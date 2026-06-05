"""Obsidian-friendly Markdown vault export."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from localdocs.models import Answer, DocumentChunk, DocumentSummary, Flashcard, StudyQuestion


def export_obsidian_vault(
    vault_dir: str | Path,
    chunks: list[DocumentChunk],
    summaries: list[DocumentSummary] | None = None,
    qa_history: list[Answer] | None = None,
    flashcards: list[Flashcard] | None = None,
    study_questions: list[StudyQuestion] | None = None,
) -> Path:
    """Create an Obsidian-compatible Markdown folder export."""

    vault_path = Path(vault_dir)
    documents_dir = vault_path / "Documents"
    documents_dir.mkdir(parents=True, exist_ok=True)

    summaries = summaries or []
    qa_history = qa_history or []
    flashcards = flashcards or []
    study_questions = study_questions or []

    document_links = _write_documents(documents_dir, chunks)
    _write_index(vault_path, document_links)
    _write_summaries(vault_path / "Summaries.md", summaries)
    _write_questions(vault_path / "Questions.md", study_questions, qa_history)
    _write_flashcards(vault_path / "Flashcards.md", flashcards)
    _write_sources(vault_path / "Sources.md", chunks)

    return vault_path


def _write_index(vault_path: Path, document_links: list[str]) -> None:
    lines = [
        "# LocalDocs AI Vault",
        "",
        "- [[Summaries]]",
        "- [[Questions]]",
        "- [[Flashcards]]",
        "- [[Sources]]",
        "",
        "## Documents",
        "",
    ]
    if document_links:
        lines.extend(f"- [[Documents/{link}]]" for link in document_links)
    else:
        lines.append("No documents were exported.")
    (vault_path / "00_Index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summaries(path: Path, summaries: list[DocumentSummary]) -> None:
    lines = ["# Summaries", ""]
    if not summaries:
        lines.extend(["No summaries were generated.", ""])
    for summary in summaries:
        lines.extend([f"## {summary.file_name}", "", summary.summary.strip(), "", "Sources:"])
        lines.extend(f"- {citation.label()}" for citation in summary.citations)
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_questions(path: Path, questions: list[StudyQuestion], qa_history: list[Answer]) -> None:
    lines = ["# Questions", "", "## Study Questions", ""]
    if questions:
        for number, question in enumerate(questions, start=1):
            lines.extend([f"{number}. {question.question}", f"   - Source: {question.citation.label()}"])
    else:
        lines.append("No study questions were generated.")

    lines.extend(["", "## Q&A History", ""])
    if qa_history:
        for number, answer in enumerate(qa_history, start=1):
            lines.extend([f"### Question {number}", "", f"**Q:** {answer.question}", "", f"**A:** {answer.answer}", "", "Sources:"])
            lines.extend(f"- {citation.label()}" for citation in answer.citations)
            lines.append("")
    else:
        lines.append("No Q&A history was exported.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_flashcards(path: Path, flashcards: list[Flashcard]) -> None:
    lines = ["# Flashcards", ""]
    if not flashcards:
        lines.extend(["No flashcards were generated.", ""])
    for number, card in enumerate(flashcards, start=1):
        lines.extend(
            [
                f"## Card {number}",
                "",
                f"**Question:** {card.question}",
                "",
                f"**Answer:** {card.answer}",
                "",
                f"Source: {card.citation.label()}",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_sources(path: Path, chunks: list[DocumentChunk]) -> None:
    grouped = _group_chunks(chunks)
    lines = ["# Sources", ""]
    if not grouped:
        lines.append("No sources were exported.")
    for file_name, file_chunks in grouped.items():
        lines.extend([f"## {file_name}", ""])
        for chunk in file_chunks:
            label = f"chunk {chunk.chunk_index}"
            if chunk.page_number is not None:
                label = f"page {chunk.page_number}, {label}"
            lines.append(f"- {label}")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_documents(documents_dir: Path, chunks: list[DocumentChunk]) -> list[str]:
    grouped = _group_chunks(chunks)
    links: list[str] = []
    used_names: set[str] = set()

    for file_name, file_chunks in grouped.items():
        stem = _safe_stem(Path(file_name).stem or "document")
        unique_stem = _unique_stem(stem, used_names)
        used_names.add(unique_stem)
        links.append(unique_stem)

        lines = [f"# {file_name}", "", f"Source file: {file_name}", ""]
        for chunk in file_chunks:
            title = f"Chunk {chunk.chunk_index}"
            if chunk.page_number is not None:
                title += f" - page {chunk.page_number}"
            lines.extend([f"## {title}", "", chunk.text.strip(), ""])
        (documents_dir / f"{unique_stem}.md").write_text("\n".join(lines), encoding="utf-8")

    return links


def _group_chunks(chunks: list[DocumentChunk]) -> dict[str, list[DocumentChunk]]:
    grouped: dict[str, list[DocumentChunk]] = defaultdict(list)
    for chunk in chunks:
        grouped[chunk.file_name].append(chunk)
    return dict(sorted(grouped.items()))


def _safe_stem(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return safe or "document"


def _unique_stem(stem: str, used_names: set[str]) -> str:
    if stem not in used_names:
        return stem
    counter = 2
    while f"{stem}_{counter}" in used_names:
        counter += 1
    return f"{stem}_{counter}"
