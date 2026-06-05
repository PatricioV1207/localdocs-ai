"""Simple data models for the LocalDocs AI MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class DocumentBlock:
    """Parsed text from a source file, optionally scoped to a PDF page."""

    text: str
    file_name: str
    file_path: str
    file_type: str
    page_number: Optional[int] = None


@dataclass(frozen=True)
class DocumentChunk:
    """Searchable chunk of text with source metadata."""

    text: str
    file_name: str
    file_path: str
    file_type: str
    chunk_index: int
    page_number: Optional[int] = None


@dataclass(frozen=True)
class SearchResult:
    """A matched chunk and its local search score."""

    chunk: DocumentChunk
    score: float

    @property
    def text(self) -> str:
        return self.chunk.text

    @property
    def file_name(self) -> str:
        return self.chunk.file_name

    @property
    def file_path(self) -> str:
        return self.chunk.file_path

    @property
    def page_number(self) -> Optional[int]:
        return self.chunk.page_number

    @property
    def chunk_index(self) -> int:
        return self.chunk.chunk_index

    def source_label(self) -> str:
        return Citation.from_chunk(self.chunk).label()


@dataclass(frozen=True)
class Citation:
    """A source reference shown with answers and summaries."""

    file_name: str
    chunk_index: int
    page_number: Optional[int] = None
    file_path: str = ""

    @classmethod
    def from_chunk(cls, chunk: DocumentChunk) -> "Citation":
        return cls(
            file_name=chunk.file_name,
            file_path=chunk.file_path,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
        )

    def label(self) -> str:
        if self.page_number is not None:
            return f"{self.file_name}, page {self.page_number}, chunk {self.chunk_index}"
        return f"{self.file_name}, chunk {self.chunk_index}"


@dataclass
class Answer:
    """Question answering result with source citations."""

    question: str
    answer: str
    citations: list[Citation] = field(default_factory=list)
    context: list[SearchResult] = field(default_factory=list)
    used_llm: bool = False
    enough_evidence: bool = True
    note: str = ""


@dataclass
class DocumentSummary:
    """Basic summary for a source document."""

    file_name: str
    summary: str
    citations: list[Citation] = field(default_factory=list)
    used_llm: bool = False
    note: str = ""
