"""Local TF-IDF and optional semantic indexing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from localdocs.embeddings import (
    DEFAULT_EMBEDDING_MODEL,
    EmbeddingProvider,
    SentenceTransformerProvider,
    normalized_matrix,
)
from localdocs.document_types import DocumentProfile, detect_document_profiles
from localdocs.models import DocumentChunk

SEARCH_MODES = {"tfidf", "semantic", "hybrid"}


@dataclass
class LocalIndex:
    """Search matrices, providers, and indexed chunks."""

    vectorizer: Optional[TfidfVectorizer]
    matrix: Any
    chunks: list[DocumentChunk]
    embeddings: np.ndarray | None = None
    embedding_provider: EmbeddingProvider | None = None
    requested_mode: str = "tfidf"
    effective_mode: str = "tfidf"
    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    hybrid_semantic_weight: float = 0.5
    warning: str = ""
    last_search_warning: str = ""
    document_profiles: dict[str, DocumentProfile] | None = None

    @property
    def is_ready(self) -> bool:
        return self.vectorizer is not None and self.matrix is not None and bool(self.chunks)

    @property
    def semantic_ready(self) -> bool:
        return (
            self.embeddings is not None
            and self.embedding_provider is not None
            and len(self.embeddings) == len(self.chunks)
        )


def build_index(
    chunks: list[DocumentChunk],
    search_mode: str = "tfidf",
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    hybrid_semantic_weight: float = 0.5,
    embedding_provider: EmbeddingProvider | None = None,
) -> LocalIndex:
    """Build TF-IDF and, when requested, optional local semantic embeddings."""

    if search_mode not in SEARCH_MODES:
        raise ValueError(f"search_mode must be one of: {', '.join(sorted(SEARCH_MODES))}.")
    if not 0 <= hybrid_semantic_weight <= 1:
        raise ValueError("hybrid_semantic_weight must be between 0 and 1.")

    indexed_chunks = [chunk for chunk in chunks if chunk.text.strip()]
    if not indexed_chunks:
        return LocalIndex(
            vectorizer=None,
            matrix=None,
            chunks=[],
            requested_mode=search_mode,
            effective_mode="tfidf",
            embedding_model=embedding_model,
            hybrid_semantic_weight=hybrid_semantic_weight,
        )

    vectorizer = TfidfVectorizer(strip_accents="unicode")
    try:
        matrix = vectorizer.fit_transform(chunk.text for chunk in indexed_chunks)
    except ValueError:
        return LocalIndex(
            vectorizer=None,
            matrix=None,
            chunks=[],
            requested_mode=search_mode,
            effective_mode="tfidf",
            embedding_model=embedding_model,
            hybrid_semantic_weight=hybrid_semantic_weight,
        )

    index = LocalIndex(
        vectorizer=vectorizer,
        matrix=matrix,
        chunks=indexed_chunks,
        requested_mode=search_mode,
        effective_mode="tfidf",
        embedding_model=embedding_model,
        hybrid_semantic_weight=hybrid_semantic_weight,
        document_profiles=detect_document_profiles(indexed_chunks),
    )
    if search_mode == "tfidf":
        return index

    try:
        provider = embedding_provider or SentenceTransformerProvider(embedding_model)
        embeddings = normalized_matrix(
            provider.encode_documents([chunk.text for chunk in indexed_chunks])
        )
        if len(embeddings) != len(indexed_chunks):
            raise ValueError("Embedding count does not match indexed chunk count.")
    except Exception:
        index.warning = (
            f"{search_mode.title()} search is unavailable. "
            "LocalDocs is using TF-IDF search instead."
        )
        return index

    index.embeddings = embeddings
    index.embedding_provider = provider
    index.effective_mode = search_mode
    return index
