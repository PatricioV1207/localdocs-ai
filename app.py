from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from localdocs.chunker import chunk_blocks
from localdocs.export import export_qa_history, export_summaries
from localdocs.indexer import build_index
from localdocs.parser import parse_path, parse_uploaded_file
from localdocs.qa import answer_question
from localdocs.search import search
from localdocs.summarizer import summarize_documents

SAMPLE_DOCS_DIR = Path("sample_docs")
SUPPORTED_TYPES = ["pdf", "txt", "md", "markdown"]


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="LocalDocs AI", page_icon="LD", layout="wide")
    _init_state()

    st.title("LocalDocs AI")
    st.write("Turn local documents into a private searchable knowledge base.")

    with st.sidebar:
        st.header("Settings")
        chunk_size = st.number_input("Chunk size", min_value=50, max_value=1000, value=220, step=10)
        overlap = st.number_input("Chunk overlap", min_value=0, max_value=300, value=40, step=10)
        top_k = st.number_input("Search results", min_value=1, max_value=10, value=5, step=1)
        api_key = os.getenv("OPENAI_API_KEY")
        st.caption("OpenAI mode is enabled." if api_key else "Using local extractive answers.")

    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or Markdown documents",
        type=SUPPORTED_TYPES,
        accept_multiple_files=True,
    )

    process_col, sample_col = st.columns(2)
    with process_col:
        if st.button("Process uploaded documents", use_container_width=True):
            if not uploaded_files:
                st.warning("Upload at least one supported document first.")
            else:
                blocks, errors = _parse_uploads(uploaded_files)
                _show_errors(errors)
                _store_index(blocks, int(chunk_size), int(overlap))

    with sample_col:
        if st.button("Process sample documents", use_container_width=True):
            blocks, errors = _parse_sample_docs()
            _show_errors(errors)
            _store_index(blocks, int(chunk_size), int(overlap))

    _show_index_status()

    st.divider()
    st.subheader("Ask a Question")
    question = st.text_input("Question", placeholder="What do these documents say about local search?")

    if st.button("Ask", use_container_width=True):
        if not _index_ready():
            st.warning("Process documents with searchable text before asking a question.")
        elif not question.strip():
            st.warning("Enter a question first.")
        else:
            results = search(st.session_state.index, question, top_k=int(top_k))
            answer = answer_question(question, results, openai_api_key=os.getenv("OPENAI_API_KEY"))
            st.session_state.qa_history.append(answer)
            st.session_state.last_results = results

    _show_latest_answer()

    st.divider()
    st.subheader("Summaries")
    if st.button("Generate summaries", use_container_width=True):
        if not st.session_state.chunks:
            st.warning("Process documents before generating summaries.")
        else:
            st.session_state.summaries = summarize_documents(
                st.session_state.chunks,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

    _show_summaries()

    st.divider()
    st.subheader("Export")
    if st.button("Export summaries and Q&A history", use_container_width=True):
        summaries_path = export_summaries(st.session_state.summaries)
        qa_path = export_qa_history(st.session_state.qa_history)
        st.success(f"Exported to {summaries_path} and {qa_path}.")


def _init_state() -> None:
    defaults = {
        "chunks": [],
        "document_names": [],
        "index": None,
        "qa_history": [],
        "summaries": [],
        "last_results": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _parse_uploads(uploaded_files) -> tuple[list, list[str]]:
    blocks = []
    errors = []
    for uploaded_file in uploaded_files:
        try:
            blocks.extend(parse_uploaded_file(uploaded_file))
        except ValueError as exc:
            errors.append(str(exc))
    return blocks, errors


def _parse_sample_docs() -> tuple[list, list[str]]:
    paths = sorted(
        path
        for path in SAMPLE_DOCS_DIR.glob("*")
        if path.suffix.lower().lstrip(".") in SUPPORTED_TYPES
    )
    blocks = []
    errors = []
    for path in paths:
        try:
            blocks.extend(parse_path(path))
        except ValueError as exc:
            errors.append(str(exc))
    return blocks, errors


def _store_index(blocks: list, chunk_size: int, overlap: int) -> None:
    if overlap >= chunk_size:
        st.error("Chunk overlap must be smaller than chunk size.")
        return

    if not blocks:
        st.session_state.chunks = []
        st.session_state.document_names = []
        st.session_state.index = None
        st.warning("No text was found in the selected documents.")
        return

    chunks = chunk_blocks(blocks, chunk_size=chunk_size, overlap=overlap)
    st.session_state.chunks = chunks
    st.session_state.document_names = sorted({block.file_name for block in blocks})
    st.session_state.index = build_index(chunks)
    st.session_state.qa_history = []
    st.session_state.summaries = []
    st.session_state.last_results = []

    if chunks and st.session_state.index.is_ready:
        st.success(f"Processed {len(st.session_state.document_names)} document(s) into {len(chunks)} chunk(s).")
    elif chunks:
        st.warning("Parsed the documents into chunks, but no searchable terms were found.")
    else:
        st.warning("Parsed the documents, but no searchable chunks were created.")


def _show_index_status() -> None:
    if not st.session_state.chunks:
        st.info("Upload documents or process the sample documents to build a local index.")
        return

    if not _index_ready():
        st.warning(
            f"Current documents: {len(st.session_state.document_names)} document(s), "
            f"{len(st.session_state.chunks)} chunk(s). Search is not ready because no searchable terms were found."
        )
        return

    st.info(
        f"Current index: {len(st.session_state.document_names)} document(s), "
        f"{len(st.session_state.chunks)} chunk(s)."
    )


def _show_latest_answer() -> None:
    if not st.session_state.qa_history:
        return

    answer = st.session_state.qa_history[-1]
    st.markdown(answer.answer)
    st.caption("Answer mode: OpenAI" if answer.used_llm else "Answer mode: local extractive")
    if getattr(answer, "note", ""):
        st.caption(answer.note)

    st.markdown("**Sources:**")
    if answer.citations:
        for citation in answer.citations:
            st.markdown(f"- {citation.label()}")
    else:
        st.markdown("- No sources available.")

    if st.checkbox("Show relevant chunks"):
        for result in st.session_state.last_results:
            with st.expander(f"{result.source_label()} | score {result.score:.3f}"):
                st.write(result.text)


def _show_summaries() -> None:
    if not st.session_state.summaries:
        return

    for summary in st.session_state.summaries:
        with st.expander(summary.file_name, expanded=True):
            st.write(summary.summary)
            if getattr(summary, "note", ""):
                st.caption(summary.note)
            st.markdown("**Sources:**")
            if summary.citations:
                for citation in summary.citations:
                    st.markdown(f"- {citation.label()}")
            else:
                st.markdown("- No sources available.")


def _show_errors(errors: list[str]) -> None:
    for error in errors:
        st.error(error)


def _index_ready() -> bool:
    index = st.session_state.index
    return bool(index and index.is_ready)


if __name__ == "__main__":
    main()
