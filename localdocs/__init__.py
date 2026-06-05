"""LocalDocs AI core package."""

from localdocs.chunker import chunk_blocks
from localdocs.config import LocalDocsConfig, load_config
from localdocs.indexer import LocalIndex, build_index
from localdocs.parser import parse_path, parse_uploaded_file
from localdocs.qa import answer_question
from localdocs.search import search
from localdocs.summarizer import summarize_documents

__all__ = [
    "LocalIndex",
    "LocalDocsConfig",
    "answer_question",
    "build_index",
    "chunk_blocks",
    "load_config",
    "parse_path",
    "parse_uploaded_file",
    "search",
    "summarize_documents",
]
