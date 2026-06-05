# LocalDocs AI v0.1 MVP Goal

## Project name

LocalDocs AI

## One-line description

LocalDocs AI is an open-source, local-first app that turns document folders into private, searchable, AI-assisted knowledge bases.

## Project vision

The goal is to help users understand and reuse their own documents without depending completely on cloud platforms.

The app should be useful for:

- Students
- Researchers
- Teachers
- Developers
- Small teams
- People with folders full of PDFs, notes, manuals, guides, and Markdown files

This project is not just a "chat with PDF" app. It should become a local knowledge base tool with citations, summaries, exports, and study/research workflows.

However, for v0.1, focus only on a functional MVP.

## Very important instruction

Build only v0.1.

Do not try to build the final product.

Do not add advanced features that are not needed for the MVP.

The goal is to create a clean, functional, demonstrable open-source first version.

## MVP objective

Build a Streamlit app that allows users to:

1. Upload PDF, TXT, and Markdown files.
2. Parse those documents locally.
3. Split the text into chunks.
4. Index the chunks using a local search method.
5. Ask questions about the documents.
6. Receive answers with source references.
7. Generate basic summaries.
8. Export summaries and Q&A history to Markdown.

## Core requirement

The app must work without an OpenAI API key.

If `OPENAI_API_KEY` is not configured, the app should use extractive behavior:

- Search the most relevant chunks.
- Return the most relevant text snippets.
- Include source references.
- Clearly say when no strong evidence was found.

If `OPENAI_API_KEY` is configured, the app may generate a more natural answer using retrieved chunks as context.

Even with OpenAI enabled, the app must only answer using retrieved document context.

## Supported files for v0.1

Support only:

- `.pdf`
- `.txt`
- `.md`
- `.markdown`

Do not implement DOCX, CSV, HTML, images, OCR, or audio in v0.1.

## Recommended stack

Use:

- Python
- Streamlit
- pypdf or PyMuPDF
- scikit-learn
- pytest
- python-dotenv, optional
- OpenAI SDK, optional

Prefer simple local TF-IDF search for v0.1.

Do not use ChromaDB, FAISS, LangChain, LlamaIndex, or a complex RAG framework in the first version unless there is a very strong reason.

## Required repository structure

Create this structure:

```txt
localdocs-ai/
├── README.md
├── LICENSE
├── requirements.txt
├── app.py
├── AGENTS.md
├── docs/
│   ├── goal.md
│   ├── architecture.md
│   └── roadmap.md
├── localdocs/
│   ├── __init__.py
│   ├── parser.py
│   ├── chunker.py
│   ├── indexer.py
│   ├── search.py
│   ├── qa.py
│   ├── summarizer.py
│   ├── export.py
│   └── models.py
├── sample_docs/
│   ├── sample_note.txt
│   └── sample_guide.md
├── exports/
└── tests/
    ├── test_parser.py
    ├── test_chunker.py
    ├── test_search.py
    └── test_export.py
```

## Module requirements

### `localdocs/models.py`

Define simple data models.

Suggested models:

- `DocumentBlock`
- `DocumentChunk`
- `SearchResult`
- `Answer`
- `Citation`

Use dataclasses or Pydantic. Prefer dataclasses for simplicity.

Each chunk should include:

- text
- file name
- file path
- file type
- page number, when available
- chunk index

### `localdocs/parser.py`

Implement document parsing.

Requirements:

- Parse TXT files.
- Parse Markdown files.
- Parse PDF files.
- Preserve page number for PDFs when possible.
- Return document blocks with metadata.
- Skip empty pages or empty files gracefully.
- Handle parsing errors with readable error messages.

### `localdocs/chunker.py`

Implement text chunking.

Requirements:

- Configurable chunk size.
- Configurable overlap.
- Avoid empty chunks.
- Preserve metadata from parsed document blocks.
- Add chunk index.
- Keep the implementation simple and easy to test.

### `localdocs/indexer.py`

Build the local index.

Requirements:

- Use TF-IDF from scikit-learn.
- Accept a list of chunks.
- Store the vectorizer, matrix, and chunk list.
- Provide a way to rebuild the index when new files are uploaded.

### `localdocs/search.py`

Implement search.

Requirements:

- Accept a query and indexed chunks.
- Return top K search results.
- Each result should include:
  - text
  - score
  - file name
  - page number, when available
  - chunk index

### `localdocs/qa.py`

Implement question answering.

Requirements:

- Input:
  - user question
  - search results
  - optional LLM configuration
- If no LLM is configured:
  - Return an extractive answer using the most relevant chunks.
  - Include citations.
- If OpenAI is configured:
  - Use only retrieved chunks as context.
  - Generate a concise answer.
  - Include citations based on retrieved chunks.
- If the search results are weak or empty:
  - Return a message saying there is not enough evidence in the documents.

Do not hallucinate.

### `localdocs/summarizer.py`

Implement document summaries.

Requirements:

- Generate a basic summary per document.
- Without LLM:
  - Use simple extractive summarization.
  - For example, select the most informative first chunks or top-ranked chunks.
- With LLM:
  - Optionally generate a better summary using document text.
- Include the source document name in every summary.

### `localdocs/export.py`

Implement Markdown export.

Requirements:

- Export summaries to `exports/summaries.md`.
- Export Q&A history to `exports/qa_history.md`.
- Create the `exports/` folder if it does not exist.
- Use clean Markdown formatting.

## Streamlit app requirements

The app should have:

1. Title:
   - `LocalDocs AI`

2. Short description:
   - "Turn local documents into a private searchable knowledge base."

3. File uploader:
   - Accept PDF, TXT, MD, and Markdown files.

4. Processing button:
   - Parse documents.
   - Chunk documents.
   - Build local search index.
   - Show number of documents and chunks processed.

5. Question input:
   - User can ask a question about uploaded documents.

6. Answer area:
   - Show the answer.
   - Show cited sources.

7. Search results area:
   - Optionally show relevant chunks.

8. Summary button:
   - Generate summaries for uploaded documents.

9. Export button:
   - Export summaries and Q&A history to Markdown.

10. Status messages:
   - Show friendly errors.
   - Show success messages.

## Citation format

Use a simple citation format.

For PDFs:

```md
Sources:
- example.pdf, page 3, chunk 5
```

For TXT or Markdown:

```md
Sources:
- notes.md, chunk 2
```

## README requirements

Create or update `README.md` with:

- Project name.
- Short description.
- Why local-first matters.
- Features in v0.1.
- What is not included yet.
- Installation instructions.
- Usage instructions.
- Example workflow.
- Project structure.
- Roadmap.
- Contributing section.
- License section.

## Documentation requirements

Create:

### `docs/architecture.md`

Explain:

- How files are parsed.
- How chunks are created.
- How local search works.
- How answers and citations are generated.
- Why v0.1 uses TF-IDF instead of a complex vector database.

### `docs/roadmap.md`

Include future versions:

#### v0.1

- PDF/TXT/MD support
- Local TF-IDF search
- Answers with sources
- Summaries
- Markdown export

#### v0.2

- DOCX support
- Better UI
- Better summary quality
- Config file

#### v0.3

- Obsidian export
- Anki flashcard export
- Local embeddings

#### v0.4

- Research comparison mode
- Study mode
- Multi-project knowledge bases

#### v1.0

- Stable API
- Plugin system
- More document formats
- Desktop packaging

## Testing requirements

Add tests for:

- TXT parsing.
- Markdown parsing.
- Chunk creation.
- Search returning relevant results.
- Markdown export.

Tests do not need to be perfect, but they must cover the core MVP behavior.

## Sample documents

Create small sample files in `sample_docs/`.

Example:

- `sample_note.txt`
- `sample_guide.md`

These should allow a new user to test the app quickly.

## Requirements file

Create `requirements.txt`.

Suggested dependencies:

```txt
streamlit
pypdf
scikit-learn
numpy
python-dotenv
pytest
openai
```

The OpenAI dependency can be included, but the app must not fail if no API key is configured.

## License

Add an MIT license file unless there is a strong reason to choose another license.

## What not to build in v0.1

Do not build:

- User accounts
- Login
- Authentication
- Cloud sync
- Payments
- Browser extension
- Desktop packaging
- Mobile app
- OCR
- Audio transcription
- Image analysis
- Advanced vector database
- Large plugin system
- Multi-user collaboration

## Final expected result

At the end, the repository should be usable like this:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then the user should be able to:

1. Open the Streamlit app.
2. Upload documents.
3. Process them.
4. Ask a question.
5. Get an answer with sources.
6. Generate summaries.
7. Export results to Markdown.

## Final response required from Codex

When finished, summarize:

- Files created.
- Main features implemented.
- How to run the app.
- How to run tests.
- Limitations of v0.1.
- Recommended next steps for v0.2.