"""Local document search."""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from localdocs.indexer import LocalIndex
from localdocs.models import SearchResult


def search(index: LocalIndex, query: str, top_k: int = 5, min_score: float = 0.0) -> list[SearchResult]:
    """Search indexed chunks using the index's effective retrieval mode."""

    if top_k <= 0 or not query.strip() or not index.is_ready:
        return []

    index.last_search_warning = ""
    tfidf_scores = _tfidf_scores(index, query)
    if index.effective_mode == "tfidf" or not index.semantic_ready:
        return _rank(index, tfidf_scores, top_k, min_score)

    try:
        semantic_scores = _semantic_scores(index, query)
    except Exception:
        index.last_search_warning = (
            "Semantic query encoding failed. LocalDocs used TF-IDF for this search."
        )
        return _rank(index, tfidf_scores, top_k, min_score)

    if index.effective_mode == "semantic":
        return _rank(index, semantic_scores, top_k, min_score)

    semantic_weight = index.hybrid_semantic_weight
    combined_scores = (1.0 - semantic_weight) * tfidf_scores + semantic_weight * semantic_scores
    return _rank(index, combined_scores, top_k, min_score)


def _tfidf_scores(index: LocalIndex, query: str) -> np.ndarray:
    query_vector = index.vectorizer.transform([query])
    return cosine_similarity(query_vector, index.matrix).ravel()


def _semantic_scores(index: LocalIndex, query: str) -> np.ndarray:
    from localdocs.embeddings import normalized_vector

    query_vector = normalized_vector(index.embedding_provider.encode_query(query))
    if query_vector.shape[0] != index.embeddings.shape[1]:
        raise ValueError("Query and document embedding dimensions do not match.")
    return np.clip(index.embeddings @ query_vector, 0.0, 1.0)


def _rank(
    index: LocalIndex,
    scores: np.ndarray,
    top_k: int,
    min_score: float,
) -> list[SearchResult]:
    ranked_indices = np.argsort(scores)[::-1]

    results: list[SearchResult] = []
    for chunk_index in ranked_indices:
        score = float(scores[chunk_index])
        if score <= min_score:
            continue
        results.append(SearchResult(chunk=index.chunks[int(chunk_index)], score=score))
        if len(results) >= top_k:
            break

    return results
