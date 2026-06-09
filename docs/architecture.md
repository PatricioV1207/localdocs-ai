# LocalDocs AI v0.4.0 Architecture

LocalDocs AI v0.4.0 is a small Streamlit app backed by plain Python modules. It
keeps the existing cited QA and study workflows while adding optional,
in-memory semantic retrieval and deterministic document-structure detection.

## Parsing

`localdocs/parser.py` accepts PDF, DOCX, TXT, Markdown, and `.markdown` files.

- TXT and Markdown files are decoded as text and returned as one document block.
- PDF files are parsed with `pypdf`, one page at a time.
- DOCX files are parsed with `python-docx`; non-empty paragraphs are joined into one document block.
- Empty files and empty PDF pages are skipped.
- PDF blocks keep the page number so answers can cite pages.

Unsupported formats raise readable errors. PDF support depends on extractable text, so scanned PDFs without a text layer are out of scope for v0.3. Legacy `.doc`, OCR, image parsing, audio, and web import are intentionally not included.

## Cleaning and Quality Filtering

`localdocs/cleaning.py` normalizes parsed text and provides shared quality helpers for local extractive workflows.

The cleaning layer removes or reduces obvious noise such as repeated PDF headers and footers, standalone page numbers, copyright lines, excessive underscores, table-of-contents-like text, legal/contact/product sections, commercial slogans, repeated document codes, and very low-information lines. PDF parsing detects repeated lines across pages before cleaning individual page blocks.

Summaries, local QA, flashcards, and study questions use quality scores to
prefer informative chunks. A chunk containing only legal, index, contact, or
commercial noise is not used for summaries or study outputs. A complete
technical sentence remains usable when PDF extraction appends a separate noisy
footer to the same chunk.

`localdocs/concepts.py` provides one deterministic concept pipeline for QA and study tools. It combines headings, definition subjects, bold-like text, bounded noun phrases, and known English/Spanish technical patterns, then rejects weak words, vague concepts, malformed determiners, legal/commercial text, table fragments, and broken OCR. Generated questions pass a final grammatical validator before display or export.

## Chunking

`localdocs/chunker.py` splits parsed blocks into chunks. Each chunk keeps the source file name, path, file type, optional page number, and a per-document chunk index.

v0.3 supports three strategies:

- `word`: the original word-count splitter.
- `paragraph`: groups nearby paragraphs into chunks.
- `heading`: splits Markdown by headings when possible, with paragraph fallback.

This is simple by design. It is good enough for a local search index and easy to test.

## Configuration

`localdocs/config.py` loads `localdocs_config.toml` from the project root. If the file is missing, defaults are used. If the file is invalid or contains bad values, the loader keeps the app running, falls back to defaults for those settings, and exposes warnings for the Streamlit sidebar.

The config controls chunk strategy, chunk size, chunk overlap, search mode,
embedding model, hybrid weight, search result count, minimum search score,
export directories, study tool limits, and whether OpenAI should be used when
an API key exists. OpenAI use is disabled by default.

## Local Search

`localdocs/indexer.py` always builds a TF-IDF matrix with scikit-learn.
`localdocs/embeddings.py` defines a small provider protocol and a lazy adapter
for the optional `sentence-transformers` package. Semantic document vectors are
normalized and stored in memory beside the TF-IDF matrix.

`localdocs/search.py` supports three modes:

- `tfidf`: cosine similarity over the TF-IDF matrix.
- `semantic`: cosine similarity over normalized document and query embeddings.
- `hybrid`: a weighted combination of TF-IDF and semantic scores.

TF-IDF remains the default and is always available. If the optional package or
model cannot load, document embeddings are invalid, or a query cannot be
encoded, the app warns the user and falls back to TF-IDF. No LangChain, Chroma,
FAISS, external embedding API, or persistent vector database is used.

## Document Structure

`localdocs/document_types.py` classifies each source as academic practice,
technical manual, research paper, legal/business, or generic. It also detects
chunk roles such as definition, objective, procedure, result, obligation,
question, example, and overview.

Detection uses marker counts, headings, sentence forms, and list/question
signals. Profiles retain their marker scores for explainability. This is a
heuristic classifier, not a trained model, and unmatched content remains
generic.

## Answers and Citations

`localdocs/qa.py` answers questions using retrieved chunks only.

When `OPENAI_API_KEY` is not configured, the app detects question type and
requested concepts, selects complete high-quality source sentences, and joins
them with minimal language-aware framing. Final validation requires substantive
question terms and requested qualifiers to be present in the evidence. Facts
from separate chunks are not combined into a relationship unless a supporting
sentence establishes it. Long selected evidence ends at a complete clause
instead of a character-level ellipsis.

If search results are missing or weak, the answer says it could not find enough strong evidence in the documents. Every successful answer includes citations such as:

```md
Sources:
- example.pdf, page 3, chunk 5
- notes.md, chunk 2
```

If OpenAI is configured but unavailable or returns an authentication, billing, quota, or rate-limit error, LocalDocs falls back to the same extractive answer path. The UI shows a short friendly note and never exposes the raw API payload.

## Summaries and Export

`localdocs/summarizer.py` creates a basic per-document summary from informative
document chunks, with optional OpenAI summarization when configured.
Documents containing no usable evidence return a no-summary message without
citations. Spanish extractive summaries retain Spanish source sentences.
`localdocs/export.py` writes summaries to `exports/summaries.md` and Q&A
history to `exports/qa_history.md`.

## Flashcards and Study Questions

`localdocs/flashcards.py` generates extractive flashcards from headings,
definitions, grammatical subjects, emphasized terms, and identifiers. Templates
adapt to the detected document and section structure. Answers remain tied to a
supporting sentence in the cited chunk. `export_anki_tsv()` writes question,
answer, and source fields.

`localdocs/study.py` uses the same concept pipeline and chooses language-aware
templates for objectives, procedures, research results, obligations,
definitions, recommendations, conditions, and other common roles. Each
question includes a source citation.

These tools are intentionally local and lightweight in v0.3. The default limit is 10 items, and strict validation can return fewer. They do not build a full learning platform.

## Obsidian Export

`localdocs/obsidian.py` writes a Markdown folder that can be opened as an Obsidian vault. It creates an index, summaries, questions, flashcards, sources, and one document note per source file when chunks are available. The export uses ordinary Markdown files and internal links such as `[[Summaries]]`.

## Streamlit UI State

The app does not store data in a database. Parsed chunks, the local index,
processed file names, summaries, Q&A history, generated flashcards, study
questions, the visible latest answer, and the most recent search results live
in Streamlit session state while the app is running. Invalid question
submissions clear the visible answer and result list without deleting prior Q&A
history. Processing a new or empty document collection clears outputs derived
from the previous collection. Exports are Markdown or TSV files on disk in
configured locations.

## Deterministic Quality Gate

`scripts/run_quality_eval.py` executes synthetic fixture pairs under `evals/`
without network access or an API key. It covers cited QA, summaries, study
questions, flashcards, document types, forbidden-source selection, semantic
retrieval, and embedding fallback. Semantic cases inject fixed fake vectors, so
CI never downloads or executes an embedding model.

`scripts/validate.py` wraps validation in three profiles. `fast` compiles core
modules and runs smoke tests, `focused` maps touched areas to tests and fixtures,
and `full` runs the complete release gate. This changes validation orchestration
only; it does not change application behavior or quality assertions.
