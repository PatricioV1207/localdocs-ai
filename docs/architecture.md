# LocalDocs AI v0.2 Architecture

LocalDocs AI v0.2 is a small Streamlit app backed by plain Python modules. The goal is to improve the v0.1 MVP without changing its local-first, beginner-friendly architecture.

## Parsing

`localdocs/parser.py` accepts PDF, DOCX, TXT, Markdown, and `.markdown` files.

- TXT and Markdown files are decoded as text and returned as one document block.
- PDF files are parsed with `pypdf`, one page at a time.
- DOCX files are parsed with `python-docx`; non-empty paragraphs are joined into one document block.
- Empty files and empty PDF pages are skipped.
- PDF blocks keep the page number so answers can cite pages.

Unsupported formats raise readable errors. PDF support depends on extractable text, so scanned PDFs without a text layer are out of scope for v0.2. Legacy `.doc`, OCR, image parsing, audio, and web import are intentionally not included.

## Chunking

`localdocs/chunker.py` splits parsed blocks into word-based chunks. The chunk size and overlap are configurable. Each chunk keeps the source file name, path, file type, optional page number, and a per-document chunk index.

This is simple by design. It is good enough for a first search index and easy to test.

## Configuration

`localdocs/config.py` loads `localdocs_config.toml` from the project root. If the file is missing, defaults are used. If the file is invalid or contains bad values, the loader keeps the app running, falls back to defaults for those settings, and exposes warnings for the Streamlit sidebar.

The config currently controls chunk size, chunk overlap, search result count, minimum search score, export directory, and whether OpenAI should be used when an API key exists.

## Local Search

`localdocs/indexer.py` builds a TF-IDF matrix with scikit-learn. `localdocs/search.py` transforms the user's query with the same vectorizer and returns the highest scoring chunks by cosine similarity.

TF-IDF is still used in v0.2 because it is local, fast, dependency-light, understandable, and does not require a model download, API key, or vector database. More advanced retrieval can be explored after the MVP is stable.

## Answers and Citations

`localdocs/qa.py` answers questions using retrieved chunks only.

When `OPENAI_API_KEY` is not configured, the app returns extractive snippets from the most relevant chunks. When an API key exists, the app may ask OpenAI to write a concise answer, but the prompt restricts the answer to retrieved document context.

If search results are missing or weak, the answer says there is not enough evidence in the indexed documents. Every successful answer includes citations such as:

```md
Sources:
- example.pdf, page 3, chunk 5
- notes.md, chunk 2
```

If OpenAI is configured but unavailable or errors, LocalDocs falls back to the same extractive answer path and keeps a short note for the Streamlit UI.

## Summaries and Export

`localdocs/summarizer.py` creates a basic per-document summary from early document chunks, with optional OpenAI summarization when configured. `localdocs/export.py` writes summaries to `exports/summaries.md` and Q&A history to `exports/qa_history.md`.

## Streamlit UI State

The app does not store data in a database. Parsed chunks, the local index, processed file names, summaries, Q&A history, and the most recent search results live in Streamlit session state while the app is running. Exports are Markdown files on disk in the configured export directory.
