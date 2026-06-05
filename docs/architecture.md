# LocalDocs AI v0.1 Architecture

LocalDocs AI v0.1 is a small Streamlit app backed by plain Python modules. The goal is a functional local-first MVP that new contributors can understand quickly.

## Parsing

`localdocs/parser.py` accepts PDF, TXT, Markdown, and `.markdown` files.

- TXT and Markdown files are decoded as text and returned as one document block.
- PDF files are parsed with `pypdf`, one page at a time.
- Empty files and empty PDF pages are skipped.
- PDF blocks keep the page number so answers can cite pages.

Unsupported formats raise readable errors. v0.1 intentionally does not include DOCX, OCR, image parsing, audio, or web import.

## Chunking

`localdocs/chunker.py` splits parsed blocks into word-based chunks. The chunk size and overlap are configurable. Each chunk keeps the source file name, path, file type, optional page number, and a per-document chunk index.

This is simple by design. It is good enough for a first search index and easy to test.

## Local Search

`localdocs/indexer.py` builds a TF-IDF matrix with scikit-learn. `localdocs/search.py` transforms the user's query with the same vectorizer and returns the highest scoring chunks by cosine similarity.

TF-IDF is used in v0.1 because it is local, fast, dependency-light, understandable, and does not require a model download, API key, or vector database. More advanced retrieval can be explored after the MVP is stable.

## Answers and Citations

`localdocs/qa.py` answers questions using retrieved chunks only.

When `OPENAI_API_KEY` is not configured, the app returns extractive snippets from the most relevant chunks. When an API key exists, the app may ask OpenAI to write a concise answer, but the prompt restricts the answer to retrieved document context.

If search results are missing or weak, the answer says there is not enough evidence in the indexed documents. Every successful answer includes citations such as:

```md
Sources:
- example.pdf, page 3, chunk 5
- notes.md, chunk 2
```

## Summaries and Export

`localdocs/summarizer.py` creates a basic per-document summary from early document chunks, with optional OpenAI summarization when configured. `localdocs/export.py` writes summaries to `exports/summaries.md` and Q&A history to `exports/qa_history.md`.

The app does not store data in a database. Session state lives in Streamlit while the app is running, and exports are Markdown files on disk.
