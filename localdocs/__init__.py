"""LocalDocs AI core package."""

from localdocs.chunker import chunk_blocks
from localdocs.indexer import LocalIndex, build_index
from localdocs.parser import parse_path, parse_uploaded_file
from localdocs.qa import answer_question
from localdocs.search import search
from localdocs.summarizer import summarize_documents

__all__ = [
    "LocalIndex",
    "answer_question",
    "build_index",
    "chunk_blocks",
    "parse_path",
    "parse_uploaded_file",
    "search",
    "summarize_documents",
]
