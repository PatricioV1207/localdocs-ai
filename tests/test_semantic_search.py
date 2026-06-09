import numpy as np
import pytest

from localdocs.indexer import build_index
from localdocs.models import DocumentChunk
from localdocs.search import search


class FakeEmbeddingProvider:
    def __init__(self, document_vectors, query_vectors):
        self.document_vectors = np.asarray(document_vectors, dtype=float)
        self.query_vectors = {
            text: np.asarray(vector, dtype=float)
            for text, vector in query_vectors.items()
        }

    def encode_documents(self, texts):
        assert len(texts) == len(self.document_vectors)
        return self.document_vectors

    def encode_query(self, text):
        return self.query_vectors[text]


class FailingEmbeddingProvider:
    def encode_documents(self, texts):
        raise RuntimeError("model unavailable")

    def encode_query(self, text):
        raise RuntimeError("model unavailable")


class FailingQueryProvider(FakeEmbeddingProvider):
    def encode_query(self, text):
        raise RuntimeError("query encoding failed")


def _chunks():
    return [
        DocumentChunk(
            text="The automobile needs regular maintenance.",
            file_name="cars.md",
            file_path="cars.md",
            file_type="markdown",
            chunk_index=1,
        ),
        DocumentChunk(
            text="Bread dough rises when yeast produces gas.",
            file_name="bread.md",
            file_path="bread.md",
            file_type="markdown",
            chunk_index=1,
        ),
    ]


def test_semantic_search_retrieves_concept_without_keyword_overlap():
    provider = FakeEmbeddingProvider(
        document_vectors=[[1.0, 0.0], [0.0, 1.0]],
        query_vectors={"car repair": [1.0, 0.0]},
    )
    index = build_index(_chunks(), search_mode="semantic", embedding_provider=provider)

    results = search(index, "car repair", top_k=1)

    assert index.effective_mode == "semantic"
    assert results[0].file_name == "cars.md"
    assert results[0].score == 1.0


def test_hybrid_search_combines_lexical_and_semantic_scores():
    provider = FakeEmbeddingProvider(
        document_vectors=[[1.0, 0.0], [0.0, 1.0]],
        query_vectors={"bread automobile": [1.0, 0.0]},
    )
    index = build_index(
        _chunks(),
        search_mode="hybrid",
        hybrid_semantic_weight=0.8,
        embedding_provider=provider,
    )

    results = search(index, "bread automobile", top_k=2)

    assert index.effective_mode == "hybrid"
    assert results[0].file_name == "cars.md"
    assert results[0].score > results[1].score


def test_semantic_index_falls_back_to_tfidf_when_embeddings_are_unavailable():
    index = build_index(
        _chunks(),
        search_mode="semantic",
        embedding_provider=FailingEmbeddingProvider(),
    )

    results = search(index, "bread yeast", top_k=1)

    assert index.requested_mode == "semantic"
    assert index.effective_mode == "tfidf"
    assert "using TF-IDF" in index.warning
    assert results[0].file_name == "bread.md"


def test_semantic_query_failure_falls_back_for_that_search():
    provider = FailingQueryProvider(
        document_vectors=[[1.0, 0.0], [0.0, 1.0]],
        query_vectors={},
    )
    index = build_index(_chunks(), search_mode="semantic", embedding_provider=provider)

    results = search(index, "bread yeast", top_k=1)

    assert index.effective_mode == "semantic"
    assert "used TF-IDF" in index.last_search_warning
    assert results[0].file_name == "bread.md"


def test_invalid_semantic_configuration_is_rejected():
    with pytest.raises(ValueError, match="search_mode"):
        build_index(_chunks(), search_mode="vector")

    with pytest.raises(ValueError, match="hybrid_semantic_weight"):
        build_index(_chunks(), search_mode="hybrid", hybrid_semantic_weight=1.5)


@pytest.mark.parametrize(
    "document_vectors",
    [
        [[1.0, 0.0]],
        [[0.0, 0.0], [0.0, 1.0]],
        [[np.nan, 0.0], [0.0, 1.0]],
    ],
)
def test_invalid_document_embeddings_trigger_tfidf_fallback(document_vectors):
    provider = FakeEmbeddingProvider(
        document_vectors=document_vectors,
        query_vectors={"bread": [0.0, 1.0]},
    )

    index = build_index(_chunks(), search_mode="semantic", embedding_provider=provider)

    assert index.effective_mode == "tfidf"
    assert index.semantic_ready is False
    assert "using TF-IDF" in index.warning


def test_query_embedding_dimension_mismatch_falls_back_for_that_search():
    provider = FakeEmbeddingProvider(
        document_vectors=[[1.0, 0.0], [0.0, 1.0]],
        query_vectors={"bread yeast": [0.0, 1.0, 0.0]},
    )
    index = build_index(_chunks(), search_mode="semantic", embedding_provider=provider)

    results = search(index, "bread yeast", top_k=1)

    assert results[0].file_name == "bread.md"
    assert "used TF-IDF" in index.last_search_warning
