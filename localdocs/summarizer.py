"""Basic document summaries."""

from __future__ import annotations

import os
import re
from collections import defaultdict

from localdocs.models import Citation, DocumentChunk, DocumentSummary


def summarize_documents(
    chunks: list[DocumentChunk],
    openai_api_key: str | None = None,
    model: str = "gpt-4o-mini",
) -> list[DocumentSummary]:
    """Generate a simple summary per source document."""

    grouped_chunks: dict[str, list[DocumentChunk]] = defaultdict(list)
    for chunk in chunks:
        grouped_chunks[chunk.file_name].append(chunk)

    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    summaries: list[DocumentSummary] = []
    for file_name, document_chunks in sorted(grouped_chunks.items()):
        citations = [Citation.from_chunk(chunk) for chunk in document_chunks[:2]]
        summary_text = None
        used_llm = False
        note = ""
        if api_key:
            summary_text, note = _try_openai_summary(file_name, document_chunks, api_key, model)
            used_llm = summary_text is not None

        if not summary_text:
            summary_text = _extractive_summary(file_name, document_chunks)
            used_llm = False

        summaries.append(
            DocumentSummary(
                file_name=file_name,
                summary=summary_text,
                citations=citations,
                used_llm=used_llm,
                note=note,
            )
        )

    return summaries


def _try_openai_summary(
    file_name: str,
    chunks: list[DocumentChunk],
    api_key: str,
    model: str,
) -> tuple[str | None, str]:
    try:
        from openai import OpenAI

        context = "\n\n".join(chunk.text for chunk in chunks[:6])
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize only the provided document text. "
                        "Do not add outside facts. Keep the summary concise."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Document name: {file_name}\n\nDocument text:\n{context}",
                },
            ],
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            return None, "OpenAI summary generation returned an empty response, so LocalDocs used extractive fallback."
        return f"{file_name}: {content}", ""
    except Exception as exc:
        return None, f"OpenAI summary generation failed, so LocalDocs used extractive fallback: {exc}"


def _extractive_summary(file_name: str, chunks: list[DocumentChunk], sentence_limit: int = 3) -> str:
    text = " ".join(chunk.text for chunk in chunks[:4])
    sentences = _split_sentences(text)
    if not sentences:
        return f"{file_name}: No summary could be generated from the indexed text."

    selected = sentences[:sentence_limit]
    return f"{file_name}: {' '.join(selected)}"


def _split_sentences(text: str) -> list[str]:
    compact = " ".join(text.split())
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", compact) if sentence.strip()]
