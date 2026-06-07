from __future__ import annotations

import os
from pathlib import Path
from typing import Any, MutableMapping

import streamlit as st
from dotenv import load_dotenv

from localdocs.chunker import chunk_blocks
from localdocs.cleaning import appears_spanish, invalid_question_message, is_valid_question
from localdocs.config import DEFAULT_CONFIG_PATH, load_config
from localdocs.export import export_qa_history, export_summaries
from localdocs.flashcards import export_anki_tsv, generate_flashcards
from localdocs.indexer import build_index
from localdocs.obsidian import export_obsidian_vault
from localdocs.parser import parse_path, parse_uploaded_file
from localdocs.qa import answer_question
from localdocs.search import search
from localdocs.study import export_study_questions_markdown, generate_study_questions
from localdocs.summarizer import summarize_documents

SAMPLE_DOCS_DIR = Path("sample_docs")
SUPPORTED_TYPES = ["pdf", "docx", "txt", "md", "markdown"]


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="LocalDocs AI", page_icon="LD", layout="wide")
    _init_state()
    config = load_config()

    st.title("LocalDocs AI")
    st.write("Turn local documents into a private searchable knowledge base.")

    with st.sidebar:
        st.header("Settings")
        st.caption(f"Config: {DEFAULT_CONFIG_PATH}")
        for warning in config.warnings:
            st.warning(warning)

        with st.expander("Advanced settings"):
            chunk_strategy = st.selectbox(
                "Chunking strategy",
                options=["word", "paragraph", "heading"],
                index=["word", "paragraph", "heading"].index(config.chunking.strategy),
                help="How parsed text is split before indexing. Word is safest; paragraph keeps blocks together; heading works best for Markdown.",
            )
            chunk_size = st.number_input(
                "Chunk size",
                min_value=1,
                max_value=max(2000, config.chunking.chunk_size),
                value=config.chunking.chunk_size,
                step=10,
                help="Approximate maximum words per chunk. Larger chunks keep more context but can reduce search focus.",
            )
            overlap = st.number_input(
                "Chunk overlap",
                min_value=0,
                max_value=max(1000, config.chunking.chunk_overlap),
                value=config.chunking.chunk_overlap,
                step=10,
                help="Words repeated between word-based chunks. Smaller overlap is faster; larger overlap can preserve context.",
            )
            top_k = st.number_input(
                "Search results",
                min_value=1,
                max_value=max(50, config.search.top_k),
                value=config.search.top_k,
                step=1,
                help="How many matching chunks to retrieve for a question.",
            )
            minimum_score = st.number_input(
                "Minimum search score",
                min_value=0.0,
                max_value=1.0,
                value=config.search.minimum_score,
                step=0.01,
                format="%.2f",
                help="Minimum similarity score required for evidence. Raise it to be stricter; lower it if useful answers are missed.",
            )
        use_openai = st.checkbox("Use OpenAI if available", value=config.llm.use_openai_if_available)
        api_key = os.getenv("OPENAI_API_KEY") if use_openai else None
        if api_key:
            st.caption("OpenAI mode is enabled.")
        elif use_openai:
            st.caption("No OpenAI key found. Using local extractive answers.")
        else:
            st.caption("Using local extractive answers.")
        st.caption(f"Export folder: {config.exports.export_dir}")
        st.caption(f"Obsidian vault: {config.obsidian.vault_dir}")
        st.caption(f"Anki TSV: {config.anki.flashcards_file}")

    st.subheader("Document Upload")
    st.caption("Supported formats: PDF, DOCX, TXT, Markdown.")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, TXT, or Markdown documents",
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
                _store_index(blocks, int(chunk_size), int(overlap), chunk_strategy)

    with sample_col:
        if st.button("Process sample documents", use_container_width=True):
            blocks, errors = _parse_sample_docs()
            _show_errors(errors)
            _store_index(blocks, int(chunk_size), int(overlap), chunk_strategy)

    _show_index_status()

    st.divider()
    st.subheader("Question")
    question = st.text_input("Your question", placeholder="What do these documents say about local search?")

    if st.button("Ask", use_container_width=True):
        if not is_valid_question(question):
            _clear_answer_state(st.session_state)
            st.warning(invalid_question_message())
        elif not _index_ready():
            _clear_answer_state(st.session_state)
            st.warning("Process documents with searchable text before asking a question.")
        else:
            results = search(
                st.session_state.index,
                question,
                top_k=int(top_k),
                min_score=float(minimum_score),
            )
            answer = answer_question(
                question,
                results,
                openai_api_key=api_key,
                use_openai=use_openai,
                min_score=float(minimum_score),
            )
            st.session_state.qa_history.append(answer)
            st.session_state.last_answer = answer
            st.session_state.last_results = answer.context

    _show_latest_answer()

    st.divider()
    st.subheader("Summaries")
    if st.button("Generate summaries", use_container_width=True):
        if not st.session_state.chunks:
            st.warning("Process documents before generating summaries.")
        else:
            st.session_state.summaries = summarize_documents(
                st.session_state.chunks,
                openai_api_key=api_key,
                use_openai=use_openai,
            )

    _show_summaries()

    st.divider()
    _show_study_tools(config)

    st.divider()
    st.subheader("Export")
    if st.button("Export summaries and Q&A history", use_container_width=True):
        if not st.session_state.summaries and not st.session_state.qa_history:
            st.warning("Generate a summary or ask a question before exporting.")
            return

        summaries_path = export_summaries(st.session_state.summaries, export_dir=config.exports.export_dir)
        qa_path = export_qa_history(st.session_state.qa_history, export_dir=config.exports.export_dir)
        st.success(f"Exported to {summaries_path} and {qa_path}.")


def _init_state() -> None:
    defaults = {
        "chunks": [],
        "document_names": [],
        "index": None,
        "qa_history": [],
        "last_answer": None,
        "summaries": [],
        "flashcards": [],
        "study_questions": [],
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
            parsed_blocks = parse_uploaded_file(uploaded_file)
            if not parsed_blocks:
                errors.append(f"{uploaded_file.name} had no extractable text and was skipped.")
            blocks.extend(parsed_blocks)
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
            parsed_blocks = parse_path(path)
            if not parsed_blocks:
                errors.append(f"{path.name} had no extractable text and was skipped.")
            blocks.extend(parsed_blocks)
        except ValueError as exc:
            errors.append(str(exc))
    return blocks, errors


def _store_index(blocks: list, chunk_size: int, overlap: int, strategy: str) -> None:
    if overlap >= chunk_size:
        st.error("Chunk overlap must be smaller than chunk size.")
        return

    if not blocks:
        st.session_state.chunks = []
        st.session_state.document_names = []
        st.session_state.index = None
        st.warning("No text was found in the selected documents.")
        return

    try:
        chunks = chunk_blocks(blocks, chunk_size=chunk_size, overlap=overlap, strategy=strategy)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.session_state.chunks = chunks
    st.session_state.document_names = sorted({block.file_name for block in blocks})
    st.session_state.index = build_index(chunks)
    st.session_state.qa_history = []
    st.session_state.last_answer = None
    st.session_state.summaries = []
    st.session_state.flashcards = []
    st.session_state.study_questions = []
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

    st.subheader("Processed Documents")
    metric_col, chunk_col = st.columns(2)
    metric_col.metric("Documents", len(st.session_state.document_names))
    chunk_col.metric("Chunks", len(st.session_state.chunks))
    with st.expander("Processed file names", expanded=True):
        for file_name in st.session_state.document_names:
            st.markdown(f"- {file_name}")


def _show_latest_answer() -> None:
    answer = st.session_state.last_answer
    if answer is None:
        return

    st.subheader("Answer")
    st.markdown(answer.answer)
    st.caption(
        "Answer mode: OpenAI"
        if answer.used_llm
        else "Answer mode: local extractive (heuristic sentence selection)"
    )
    if getattr(answer, "note", ""):
        st.caption(answer.note)

    st.subheader("Sources")
    if answer.citations:
        for citation in answer.citations:
            st.markdown(f"- {citation.label()}")
    else:
        st.markdown("- No sources available.")

    with st.expander("Relevant chunks"):
        if not st.session_state.last_results:
            st.write("No relevant chunks were returned.")
        for result in st.session_state.last_results:
            st.markdown(f"**{result.source_label()} | score {result.score:.3f}**")
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


def _show_study_tools(config) -> None:
    st.subheader("Study Tools")
    st.caption("Questions and flashcards are generated locally from extracted document concepts.")

    if not st.session_state.chunks:
        st.info("Process documents before generating flashcards or study questions.")
    else:
        flashcard_col, question_col = st.columns(2)
        with flashcard_col:
            if st.button("Generate flashcards", use_container_width=True):
                st.session_state.flashcards = generate_flashcards(
                    st.session_state.chunks,
                    max_cards=config.study.max_flashcards,
                )
                if st.session_state.flashcards:
                    st.success(f"Generated {len(st.session_state.flashcards)} flashcard(s).")
                else:
                    st.warning("No flashcards could be generated from the current chunks.")
        with question_col:
            if st.button("Generate study questions", use_container_width=True):
                st.session_state.study_questions = generate_study_questions(
                    st.session_state.chunks,
                    max_questions=config.study.max_questions,
                )
                if st.session_state.study_questions:
                    st.success(f"Generated {len(st.session_state.study_questions)} study question(s).")
                else:
                    st.warning("No study questions could be generated from the current chunks.")

    _show_flashcards()
    _show_study_questions()

    export_col, anki_col, question_export_col = st.columns(3)
    with export_col:
        if st.button("Export Obsidian vault", use_container_width=True):
            if not st.session_state.chunks:
                st.warning("Process documents before exporting an Obsidian vault.")
            else:
                vault_path = export_obsidian_vault(
                    config.obsidian.vault_dir,
                    st.session_state.chunks,
                    summaries=st.session_state.summaries,
                    qa_history=st.session_state.qa_history,
                    flashcards=st.session_state.flashcards,
                    study_questions=st.session_state.study_questions,
                )
                st.success(f"Exported Obsidian vault to {vault_path}.")
    with anki_col:
        if st.button("Export Anki TSV", use_container_width=True):
            if not st.session_state.flashcards:
                st.warning("Generate flashcards before exporting Anki TSV.")
            else:
                anki_path = export_anki_tsv(st.session_state.flashcards, path=config.anki.flashcards_file)
                st.success(f"Exported Anki TSV to {anki_path}.")
    with question_export_col:
        if st.button("Export study questions", use_container_width=True):
            if not st.session_state.study_questions:
                st.warning("Generate study questions before exporting them.")
            else:
                questions_path = export_study_questions_markdown(
                    st.session_state.study_questions,
                    export_dir=config.exports.export_dir,
                )
                st.success(f"Exported study questions to {questions_path}.")


def _show_flashcards() -> None:
    if not st.session_state.flashcards:
        return

    with st.expander("Flashcards preview", expanded=True):
        for card in st.session_state.flashcards:
            if appears_spanish(card.question):
                st.markdown(f"**Pregunta:** {card.question}")
                st.markdown(f"**Respuesta:** {card.answer}")
            else:
                st.markdown(f"**Q:** {card.question}")
                st.markdown(f"**A:** {card.answer}")
            st.caption(f"Source: {card.citation.label()}")


def _show_study_questions() -> None:
    if not st.session_state.study_questions:
        return

    with st.expander("Study questions preview", expanded=True):
        for question in st.session_state.study_questions:
            st.markdown(f"- {question.question}")
            st.caption(f"Source: {question.citation.label()}")


def _show_errors(errors: list[str]) -> None:
    for error in errors:
        st.error(error)


def _clear_answer_state(state: MutableMapping[str, Any]) -> None:
    """Hide a stale answer without erasing exported Q&A history."""

    state["last_answer"] = None
    state["last_results"] = []


def _index_ready() -> bool:
    index = st.session_state.index
    return bool(index and index.is_ready)


if __name__ == "__main__":
    main()
