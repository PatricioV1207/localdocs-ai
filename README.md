# LocalDocs AI

LocalDocs AI is an open-source, local-first document intelligence app. It turns PDFs, DOCX files, text notes, and Markdown files into a private searchable knowledge base with cited answers, summaries, and Markdown exports.

Status: v0.2 implemented.

## Why Local-First Matters

People often keep useful knowledge in folders of notes, guides, manuals, and PDFs. A local-first workflow lets users search and reuse those documents without making a cloud service the default place where their information lives.

LocalDocs AI v0.2 keeps the app simple: documents are parsed locally, indexed locally with TF-IDF, and answered locally when no `OPENAI_API_KEY` is configured.

## Supported Formats

- PDF files with extractable text
- DOCX files
- TXT files
- Markdown files (`.md` and `.markdown`)

## Features in v0.2

- PDF parsing with page numbers when text is extractable
- DOCX parsing from readable paragraphs
- TXT parsing
- Markdown and `.markdown` parsing
- Word-based text chunking with configurable chunk size and overlap
- Local TF-IDF search with scikit-learn
- Question answering with source references
- Extractive fallback when no OpenAI API key is configured
- Optional OpenAI answer generation when `OPENAI_API_KEY` exists
- Basic per-document summaries
- Markdown export for summaries and Q&A history
- Streamlit interface with processed-document status and source display
- Local `localdocs_config.toml` settings
- Focused pytest coverage

PDF support means PDFs that already contain selectable text. Scanned PDFs and images need OCR, which is intentionally out of scope for this release.

## Not Included Yet

v0.2 is not a final product. It does not include:

- User accounts
- Login or authentication
- Cloud sync
- Payments
- OCR
- Audio transcription
- Image analysis
- Advanced vector databases
- Desktop packaging
- Mobile app
- Multi-user collaboration

## Installation

Clone the repository and enter the project folder:

```bash
git clone https://github.com/YOUR_USERNAME/localdocs-ai.git
cd localdocs-ai
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Then:

1. Upload PDF, DOCX, TXT, or Markdown documents.
2. Click `Process uploaded documents`.
3. Ask a question about the indexed documents.
4. Review the answer and cited sources.
5. Generate summaries.
6. Export summaries and Q&A history to Markdown.

You can also click `Process sample documents` to try the app with files in `sample_docs/`.

## Configuration

LocalDocs AI reads `localdocs_config.toml` from the project root. If the file is missing or invalid, the app uses sensible defaults and shows readable warnings in the sidebar.

Default settings:

```toml
[chunking]
chunk_size = 220
chunk_overlap = 40

[search]
top_k = 4
minimum_score = 0.05

[exports]
export_dir = "exports"

[llm]
use_openai_if_available = true
```

These values control chunking, search result count, weak-result filtering, export location, and whether OpenAI should be used when an API key exists.

## Optional OpenAI Configuration

LocalDocs AI works without an OpenAI API key.

If you want optional LLM-generated answers and summaries, set:

```bash
export OPENAI_API_KEY=your_api_key_here
```

Or create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

Even when OpenAI is enabled, answers are generated only from retrieved document chunks. If the retrieved chunks do not contain enough evidence, the app should say so.

## Example Workflow

Use the sample documents:

```txt
sample_docs/
├── sample_note.txt
└── sample_guide.md
```

Ask:

```txt
What does LocalDocs AI use for local search?
```

The app should return relevant context and sources, for example:

```md
Sources:
- sample_note.txt, chunk 1
- sample_guide.md, chunk 1
```

## Project Structure

```txt
localdocs-ai/
├── README.md
├── LICENSE
├── requirements.txt
├── localdocs_config.toml
├── CHANGELOG.md
├── app.py
├── AGENTS.md
├── docs/
│   ├── goal_v0.1.md
│   ├── goal_v0.2.md
│   ├── architecture.md
│   └── roadmap.md
├── localdocs/
│   ├── __init__.py
│   ├── config.py
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
    ├── test_config.py
    ├── test_parser.py
    ├── test_chunker.py
    ├── test_search.py
    ├── test_qa.py
    ├── test_summarizer.py
    └── test_export.py
```

## Run Tests

```bash
pytest
```

If your shell does not expose `pytest` directly, run:

```bash
python -m pytest
```

## Roadmap

See `docs/roadmap.md` for the project roadmap.

v0.3 priorities include Obsidian export, Anki flashcard export, a local embeddings option, and improved chunking strategies.

## Current v0.2 Limitations

- PDF parsing depends on extractable text; scanned PDFs are skipped unless they already contain a text layer.
- DOCX parsing reads normal paragraphs only; legacy `.doc` files are not supported.
- Search uses TF-IDF, so it is keyword-oriented rather than semantic.
- Answers use retrieved chunks only. If retrieval is weak, the app says there is not enough evidence.
- Streamlit session state is temporary. Export summaries and Q&A history to Markdown if you want to keep them.
- OpenAI integration is optional and falls back to local extractive behavior if unavailable.

## Contributing

Contributions are welcome. Good first contributions include tests, parser improvements, documentation updates, small UI improvements, and sample documents.

Please keep changes aligned with the project philosophy: local-first, simple, readable, and useful without a required API key.

## License

LocalDocs AI is released under the MIT License. See `LICENSE`.
