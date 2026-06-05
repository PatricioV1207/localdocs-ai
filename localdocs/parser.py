"""Document parsing for PDF, TXT, and Markdown files."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Iterable

from localdocs.models import DocumentBlock

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}


def parse_path(path: str | Path) -> list[DocumentBlock]:
    """Parse a supported file from disk."""

    source_path = Path(path)
    try:
        data = source_path.read_bytes()
    except OSError as exc:
        raise ValueError(f"Could not read {source_path}: {exc}") from exc

    return parse_bytes(data, source_path.name, str(source_path))


def parse_paths(paths: Iterable[str | Path]) -> list[DocumentBlock]:
    """Parse multiple supported files from disk."""

    blocks: list[DocumentBlock] = []
    for path in paths:
        blocks.extend(parse_path(path))
    return blocks


def parse_uploaded_file(uploaded_file) -> list[DocumentBlock]:
    """Parse a Streamlit uploaded file-like object."""

    file_name = getattr(uploaded_file, "name", "uploaded_file")
    if hasattr(uploaded_file, "getvalue"):
        data = uploaded_file.getvalue()
    else:
        data = uploaded_file.read()
    return parse_bytes(data, file_name, file_name)


def parse_bytes(data: bytes, file_name: str, file_path: str | None = None) -> list[DocumentBlock]:
    """Parse bytes from a supported file name."""

    file_path = file_path or file_name
    extension = Path(file_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"{file_name} is not supported. Supported files: {supported}.")

    if extension == ".pdf":
        return _parse_pdf(data, file_name, file_path)

    file_type = "markdown" if extension in {".md", ".markdown"} else "txt"
    text = _clean_text(_decode_text(data, file_name))
    if not text:
        return []

    return [
        DocumentBlock(
            text=text,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
        )
    ]


def _parse_pdf(data: bytes, file_name: str, file_path: str) -> list[DocumentBlock]:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
    except Exception as exc:
        raise ValueError(f"Could not open PDF {file_name}: {exc}") from exc

    blocks: list[DocumentBlock] = []
    for page_index, page in enumerate(reader.pages, start=1):
        try:
            text = _clean_text(page.extract_text() or "")
        except Exception as exc:
            raise ValueError(f"Could not extract text from {file_name}, page {page_index}: {exc}") from exc

        if not text:
            continue

        blocks.append(
            DocumentBlock(
                text=text,
                file_name=file_name,
                file_path=file_path,
                file_type="pdf",
                page_number=page_index,
            )
        )

    return blocks


def _decode_text(data: bytes, file_name: str) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode text in {file_name}.")


def _clean_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n")]
    return "\n".join(line for line in lines if line).strip()
