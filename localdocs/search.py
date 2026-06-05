"""Local document search."""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from localdocs.indexer import LocalIndex
from localdocs.models import SearchResult


def search(index: LocalIndex, query: str, top_k: int = 5, min_score: float = 0.0) -> list[SearchResult]:
    """Search indexed chunks with a text query."""

    if top_k <= 0 or not query.strip() or not index.is_ready:
        return []

    query_vector = index.vectorizer.transform([query])
    scores = cosine_similarity(query_vector, index.matrix).ravel()
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
