from localdocs.indexer import build_index
from localdocs.models import DocumentChunk
from localdocs.search import search


def test_search_returns_relevant_result():
    chunks = [
        DocumentChunk(
            text="LocalDocs AI builds a private searchable knowledge base.",
            file_name="guide.md",
            file_path="guide.md",
            file_type="markdown",
            chunk_index=1,
        ),
        DocumentChunk(
            text="This recipe explains how to bake bread with yeast.",
            file_name="recipe.txt",
            file_path="recipe.txt",
            file_type="txt",
            chunk_index=1,
        ),
    ]
    index = build_index(chunks)

    results = search(index, "private knowledge base", top_k=1)

    assert len(results) == 1
    assert results[0].file_name == "guide.md"
    assert results[0].score > 0


def test_search_returns_empty_when_top_k_is_zero():
    chunk = DocumentChunk(
        text="LocalDocs AI builds a private searchable knowledge base.",
        file_name="guide.md",
        file_path="guide.md",
        file_type="markdown",
        chunk_index=1,
    )
    index = build_index([chunk])

    results = search(index, "private knowledge base", top_k=0)

    assert results == []
