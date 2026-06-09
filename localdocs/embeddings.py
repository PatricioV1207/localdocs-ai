"""Optional local embedding providers for semantic retrieval."""

from __future__ import annotations

from typing import Protocol, Sequence

import numpy as np

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingProvider(Protocol):
    """Minimal provider contract used by the local semantic index."""

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        """Encode document chunks as a two-dimensional float array."""

    def encode_query(self, text: str) -> np.ndarray:
        """Encode one search query as a one-dimensional float array."""


class SentenceTransformerProvider:
    """Lazy adapter around the optional sentence-transformers package."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        encoder = getattr(self._model, "encode_document", self._model.encode)
        vectors = encoder(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return _matrix(vectors)

    def encode_query(self, text: str) -> np.ndarray:
        encoder = getattr(self._model, "encode_query", self._model.encode)
        vector = encoder(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return _vector(vector)


def normalized_matrix(values) -> np.ndarray:
    """Return row-normalized embeddings and reject invalid shapes."""

    matrix = _matrix(values)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("Embedding vectors must not be zero.")
    return matrix / norms


def normalized_vector(values) -> np.ndarray:
    """Return one normalized embedding vector."""

    vector = _vector(values)
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("Embedding vector must not be zero.")
    return vector / norm


def _matrix(values) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or not matrix.shape[0] or not matrix.shape[1]:
        raise ValueError("Document embeddings must be a non-empty 2D array.")
    if not np.isfinite(matrix).all():
        raise ValueError("Embedding vectors must contain finite values.")
    return matrix


def _vector(values) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    if vector.ndim == 2 and vector.shape[0] == 1:
        vector = vector[0]
    if vector.ndim != 1 or not vector.shape[0]:
        raise ValueError("Query embedding must be a non-empty 1D array.")
    if not np.isfinite(vector).all():
        raise ValueError("Embedding vectors must contain finite values.")
    return vector
