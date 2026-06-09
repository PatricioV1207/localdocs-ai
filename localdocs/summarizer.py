"""Basic document summaries."""

from __future__ import annotations

import os
from collections import defaultdict

from localdocs.cleaning import (
    appears_spanish,
    best_sentences,
    informative_chunks,
    is_low_value_text,
)
from localdocs.models import Citation, DocumentChunk, DocumentSummary

OPENAI_FALLBACK_NOTE = "OpenAI generation is unavailable, so LocalDocs used local extractive mode."


def summarize_documents(
    chunks: list[DocumentChunk],
    openai_api_key: str | None = None,
    model: str = "gpt-4o-mini",
    use_openai: bool = True,
) -> list[DocumentSummary]:
    """Generate a simple summary per source document."""

    grouped_chunks: dict[str, list[DocumentChunk]] = defaultdict(list)
    for chunk in chunks:
        grouped_chunks[chunk.file_name].append(chunk)

    api_key = (openai_api_key or os.getenv("OPENAI_API_KEY")) if use_openai else None
    summaries: list[DocumentSummary] = []
    for file_name, document_chunks in sorted(grouped_chunks.items()):
        selected_chunks = [
            chunk
            for chunk in informative_chunks(document_chunks)
            if not is_low_value_text(chunk.text)
        ][:4]
        citations: list[Citation] = []
        summary_text = None
        used_llm = False
        note = ""
        if api_key:
            summary_text, note = _try_openai_summary(file_name, selected_chunks, api_key, model)
            used_llm = summary_text is not None
            if summary_text:
                citations = _unique_citations(selected_chunks)

        if not summary_text:
            summary_text, used_chunks = _extractive_summary(file_name, selected_chunks)
            citations = _unique_citations(used_chunks)
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
                        "Do not add outside facts. Keep the summary concise and use the same language as the document."
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
            return None, OPENAI_FALLBACK_NOTE
        return f"{file_name}: {content}", ""
    except Exception:
        return None, OPENAI_FALLBACK_NOTE


def _extractive_summary(
    file_name: str,
    chunks: list[DocumentChunk],
    sentence_limit: int = 3,
) -> tuple[str, list[DocumentChunk]]:
    sentences: list[str] = []
    seen: set[str] = set()
    used_chunks: list[DocumentChunk] = []
    for chunk in informative_chunks(chunks, limit=4):
        for sentence in best_sentences(chunk.text, limit=2):
            key = sentence.lower()
            if key in seen:
                continue
            seen.add(key)
            sentences.append(sentence)
            if chunk not in used_chunks:
                used_chunks.append(chunk)
            if len(sentences) >= sentence_limit:
                break
        if len(sentences) >= sentence_limit:
            break

    if not sentences:
        return f"{file_name}: No summary could be generated from the indexed text.", []

    selected = sentences[:sentence_limit]
    prefix = f"Resumen de {file_name}:" if appears_spanish(" ".join(selected)) else f"{file_name}:"
    return f"{prefix} {' '.join(selected)}", used_chunks


def _unique_citations(chunks: list[DocumentChunk]) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[tuple[str, int, int | None]] = set()
    for chunk in chunks:
        citation = Citation.from_chunk(chunk)
        key = (citation.file_name, citation.chunk_index, citation.page_number)
        if key in seen:
            continue
        seen.add(key)
        citations.append(citation)
    return citations
