"""Text chunking for parsed document blocks."""

from __future__ import annotations

from collections import defaultdict

from localdocs.models import DocumentBlock, DocumentChunk


def chunk_blocks(
    blocks: list[DocumentBlock],
    chunk_size: int = 220,
    overlap: int = 40,
    strategy: str = "word",
) -> list[DocumentChunk]:
    """Split parsed blocks into chunks using a simple local strategy."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0:
        raise ValueError("overlap cannot be negative.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")
    if strategy not in {"word", "paragraph", "heading"}:
        raise ValueError("strategy must be one of: word, paragraph, heading.")

    chunks: list[DocumentChunk] = []
    chunk_counts: dict[str, int] = defaultdict(int)

    for block in blocks:
        text = block.text.strip()
        if not text:
            continue

        for chunk_text in _split_block(block, chunk_size, overlap, strategy):
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


def _split_block(
    block: DocumentBlock,
    chunk_size: int,
    overlap: int,
    strategy: str,
) -> list[str]:
    if strategy == "paragraph":
        return _chunk_paragraphs(block.text, chunk_size)
    if strategy == "heading":
        if block.file_type == "markdown":
            heading_chunks = _chunk_markdown_headings(block.text, chunk_size, overlap)
            if heading_chunks:
                return heading_chunks
        return _chunk_paragraphs(block.text, chunk_size)

    return _chunk_words(" ".join(block.text.split()), chunk_size, overlap)


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


def _chunk_paragraphs(text: str, chunk_size: int) -> list[str]:
    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for paragraph in paragraphs:
        paragraph_words = len(paragraph.split())
        if paragraph_words > chunk_size:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_words = 0
            chunks.extend(_chunk_words(paragraph, chunk_size, overlap=0))
            continue

        if current and current_words + paragraph_words > chunk_size:
            chunks.append("\n\n".join(current))
            current = []
            current_words = 0

        current.append(paragraph)
        current_words += paragraph_words

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def _chunk_markdown_headings(text: str, chunk_size: int, overlap: int) -> list[str]:
    sections: list[str] = []
    current: list[str] = []
    found_heading = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            found_heading = True
            if current:
                sections.append("\n".join(current).strip())
            current = [stripped]
        elif stripped:
            current.append(stripped)

    if current:
        sections.append("\n".join(current).strip())

    if not found_heading:
        return []

    chunks: list[str] = []
    for section in sections:
        if len(section.split()) > chunk_size:
            chunks.extend(_chunk_words(" ".join(section.split()), chunk_size, overlap))
        else:
            chunks.append(section)
    return chunks


def _split_paragraphs(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_paragraphs = [paragraph.strip() for paragraph in normalized.split("\n\n") if paragraph.strip()]
    if len(raw_paragraphs) > 1:
        return [" ".join(paragraph.split()) for paragraph in raw_paragraphs]
    return [" ".join(line.split()) for line in normalized.splitlines() if line.strip()]
