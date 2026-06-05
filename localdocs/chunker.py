"""Text chunking for parsed document blocks."""

from __future__ import annotations

from collections import defaultdict

from localdocs.models import DocumentBlock, DocumentChunk


def chunk_blocks(
    blocks: list[DocumentBlock],
    chunk_size: int = 220,
    overlap: int = 40,
) -> list[DocumentChunk]:
    """Split parsed blocks into word-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0:
        raise ValueError("overlap cannot be negative.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    chunks: list[DocumentChunk] = []
    chunk_counts: dict[str, int] = defaultdict(int)

    for block in blocks:
        text = " ".join(block.text.split())
        if not text:
            continue

        for chunk_text in _chunk_words(text, chunk_size, overlap):
            if not chunk_text.strip():
                continue

            key = block.file_path or block.file_name
            chunk_counts[key] += 1
            chunks.append(
                DocumentChunk(
                    text=chunk_text,
                    file_name=block.file_name,
                    file_path=block.file_path,
                    file_type=block.file_type,
                    page_number=block.page_number,
                    chunk_index=chunk_counts[key],
                )
            )

    return chunks


def _chunk_words(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks
