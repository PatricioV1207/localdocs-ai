# LocalDocs AI v0.3 Architecture

LocalDocs AI v0.3 is a small Streamlit app backed by plain Python modules. The goal is to add useful study/export workflows without changing the local-first, beginner-friendly architecture.

## Parsing

`localdocs/parser.py` accepts PDF, DOCX, TXT, Markdown, and `.markdown` files.

- TXT and Markdown files are decoded as text and returned as one document block.
- PDF files are parsed with `pypdf`, one page at a time.
- DOCX files are parsed with `python-docx`; non-empty paragraphs are joined into one document block.
- Empty files and empty PDF pages are skipped.
- PDF blocks keep the page number so answers can cite pages.

Unsupported formats raise readable errors. PDF support depends on extractable text, so scanned PDFs without a text layer are out of scope for v0.3. Legacy `.doc`, OCR, image parsing, audio, and web import are intentionally not included.

## Chunking

`localdocs/chunker.py` splits parsed blocks into chunks. Each chunk keeps the source file name, path, file type, optional page number, and a per-document chunk index.

v0.3 supports three strategies:

- `word`: the original word-count splitter.
- `paragraph`: groups nearby paragraphs into chunks.
- `heading`: splits Markdown by headings when possible, with paragraph fallback.

This is simple by design. It is good enough for a local search index and easy to test.

## Configuration

`localdocs/config.py` loads `localdocs_config.toml` from the project root. If the file is missing, defaults are used. If the file is invalid or contains bad values, the loader keeps the app running, falls back to defaults for those settings, and exposes warnings for the Streamlit sidebar.

The config controls chunk strategy, chunk size, chunk overlap, search result count, minimum search score, export directories, study tool limits, and whether OpenAI should be used when an API key exists.

## Local Search

`localdocs/indexer.py` builds a TF-IDF matrix with scikit-learn. `localdocs/search.py` transforms the user's query with the same vectorizer and returns the highest scoring chunks by cosine similarity.

TF-IDF is still used in v0.3 because it is local, fast, dependency-light, understandable, and does not require a model download, API key, or vector database. More advanced retrieval can be explored after the MVP is stable.

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

## Flashcards and Study Questions

`localdocs/flashcards.py` generates simple extractive flashcards from chunks. Each flashcard includes a question, answer, and citation. `export_anki_tsv()` writes Anki-compatible tab-separated rows with three fields: question, answer, and source.

`localdocs/study.py` generates simple study questions from Markdown headings or important-looking chunk text. Each question includes a source citation. Study questions can also be exported to Markdown.

These tools are intentionally local and lightweight in v0.3. They do not build a full learning platform.

## Obsidian Export

`localdocs/obsidian.py` writes a Markdown folder that can be opened as an Obsidian vault. It creates an index, summaries, questions, flashcards, sources, and one document note per source file when chunks are available. The export uses ordinary Markdown files and internal links such as `[[Summaries]]`.

## Streamlit UI State

The app does not store data in a database. Parsed chunks, the local index, processed file names, summaries, Q&A history, generated flashcards, study questions, and the most recent search results live in Streamlit session state while the app is running. Exports are Markdown or TSV files on disk in configured locations.
