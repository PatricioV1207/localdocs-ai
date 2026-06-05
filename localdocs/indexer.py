"""Local TF-IDF indexing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from sklearn.feature_extraction.text import TfidfVectorizer

from localdocs.models import DocumentChunk


@dataclass
class LocalIndex:
    """TF-IDF vectorizer, sparse matrix, and indexed chunks."""

    vectorizer: Optional[TfidfVectorizer]
    matrix: Any
    chunks: list[DocumentChunk]

    @property
    def is_ready(self) -> bool:
        return self.vectorizer is not None and self.matrix is not None and bool(self.chunks)


def build_index(chunks: list[DocumentChunk]) -> LocalIndex:
    """Build a local TF-IDF index from chunks."""

    indexed_chunks = [chunk for chunk in chunks if chunk.text.strip()]
    if not indexed_chunks:
        return LocalIndex(vectorizer=None, matrix=None, chunks=[])

    vectorizer = TfidfVectorizer(strip_accents="unicode")
    try:
        matrix = vectorizer.fit_transform(chunk.text for chunk in indexed_chunks)
    except ValueError:
        return LocalIndex(vectorizer=None, matrix=None, chunks=[])

    return LocalIndex(vectorizer=vectorizer, matrix=matrix, chunks=indexed_chunks)
