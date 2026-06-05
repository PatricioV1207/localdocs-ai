"""Markdown export helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping

from localdocs.models import Answer, Citation, DocumentSummary


def export_summaries(
    summaries: Iterable[DocumentSummary],
    export_dir: str | Path = "exports",
    filename: str = "summaries.md",
) -> Path:
    """Export document summaries to Markdown."""

    export_path = _ensure_export_dir(export_dir) / filename
    summaries = list(summaries)

    lines = [
        "# LocalDocs AI Summaries",
        "",
        f"Generated: {_timestamp()}",
        "",
    ]

    if not summaries:
        lines.extend(["No summaries have been generated yet.", ""])
    else:
        for summary in summaries:
            lines.extend(
                [
                    f"## {summary.file_name}",
                    "",
                    summary.summary.strip(),
                    "",
                    "Sources:",
                    *_citation_lines(summary.citations),
                    "",
                ]
            )

    export_path.write_text("\n".join(lines), encoding="utf-8")
    return export_path


def export_qa_history(
    answers: Iterable[Answer | Mapping],
    export_dir: str | Path = "exports",
    filename: str = "qa_history.md",
) -> Path:
    """Export Q&A history to Markdown."""

    export_path = _ensure_export_dir(export_dir) / filename
    answers = list(answers)

    lines = [
        "# LocalDocs AI Q&A History",
        "",
        f"Generated: {_timestamp()}",
        "",
    ]

    if not answers:
        lines.extend(["No questions have been answered yet.", ""])
    else:
        for number, item in enumerate(answers, start=1):
            answer = _coerce_answer(item)
            lines.extend(
                [
                    f"## Question {number}",
                    "",
                    f"**Q:** {answer.question}",
                    "",
                    f"**A:** {answer.answer.strip()}",
                    "",
                    "Sources:",
                    *_citation_lines(answer.citations),
                    "",
                ]
            )

    export_path.write_text("\n".join(lines), encoding="utf-8")
    return export_path


def _ensure_export_dir(export_dir: str | Path) -> Path:
    path = Path(export_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _citation_lines(citations: Iterable[Citation]) -> list[str]:
    citation_list = list(citations)
    if not citation_list:
        return ["- No sources available."]
    return [f"- {citation.label()}" for citation in citation_list]


def _coerce_answer(item: Answer | Mapping) -> Answer:
    if isinstance(item, Answer):
        return item

    citations = [_coerce_citation(citation) for citation in item.get("citations", [])]
    return Answer(
        question=str(item.get("question", "")),
        answer=str(item.get("answer", "")),
        citations=citations,
    )


def _coerce_citation(item: Citation | Mapping) -> Citation:
    if isinstance(item, Citation):
        return item

    return Citation(
        file_name=str(item.get("file_name", "")),
        chunk_index=int(item.get("chunk_index", 0)),
        page_number=item.get("page_number"),
        file_path=str(item.get("file_path", "")),
    )


def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")
