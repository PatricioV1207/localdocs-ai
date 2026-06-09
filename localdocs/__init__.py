"""LocalDocs AI core package."""

from localdocs.chunker import chunk_blocks
from localdocs.config import LocalDocsConfig, load_config
from localdocs.concepts import extract_concepts
from localdocs.document_types import (
    DocumentProfile,
    detect_document_profiles,
    detect_document_type,
    detect_section_role,
)
from localdocs.flashcards import export_anki_tsv, generate_flashcards
from localdocs.embeddings import DEFAULT_EMBEDDING_MODEL, EmbeddingProvider
from localdocs.indexer import LocalIndex, build_index
from localdocs.obsidian import export_obsidian_vault
from localdocs.parser import parse_path, parse_uploaded_file
from localdocs.qa import answer_question
from localdocs.search import search
from localdocs.study import export_study_questions_markdown, generate_study_questions
from localdocs.summarizer import summarize_documents

__all__ = [
    "LocalIndex",
    "LocalDocsConfig",
    "DEFAULT_EMBEDDING_MODEL",
    "EmbeddingProvider",
    "DocumentProfile",
    "answer_question",
    "build_index",
    "chunk_blocks",
    "export_anki_tsv",
    "export_obsidian_vault",
    "export_study_questions_markdown",
    "extract_concepts",
    "detect_document_profiles",
    "detect_document_type",
    "detect_section_role",
    "generate_flashcards",
    "generate_study_questions",
    "load_config",
    "parse_path",
    "parse_uploaded_file",
    "search",
    "summarize_documents",
]
