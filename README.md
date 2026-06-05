# LocalDocs AI

[![Tests](https://github.com/PatricioV1207/localdocs-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/PatricioV1207/localdocs-ai/actions/workflows/tests.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Local-first](https://img.shields.io/badge/local--first-yes-brightgreen.svg)

LocalDocs AI is an open-source, local-first document intelligence app. It turns PDFs, DOCX files, text notes, and Markdown files into a private searchable knowledge base with cited answers, summaries, study questions, flashcards, and Markdown exports.

Status: v0.3.1 implemented.

## Why LocalDocs AI?

Many people have useful knowledge scattered across PDFs, notes, manuals, and guides. LocalDocs AI helps make those documents searchable and reusable while keeping the default workflow on your machine.

The app works without an OpenAI API key. If `OPENAI_API_KEY` is configured, LocalDocs can optionally generate more natural answers and summaries, but answers are still based on retrieved document context.

## Features

- Parse PDF, DOCX, TXT, Markdown, and `.markdown` files.
- Chunk documents with `word`, `paragraph`, or Markdown `heading` strategies.
- Search locally with scikit-learn TF-IDF.
- Ask questions and get cited answers.
- Fall back to extractive answers without an API key.
- Generate basic summaries.
- Generate study questions and flashcards with source references.
- Export summaries and Q&A history to Markdown.
- Export an Obsidian-friendly Markdown vault.
- Export Anki-compatible flashcards as TSV.
- Configure behavior with `localdocs_config.toml`.

## Not Included

LocalDocs AI v0.3 intentionally does not include user accounts, authentication, cloud sync, OCR, audio transcription, image analysis, vector databases, desktop/mobile packaging, or multi-user collaboration.

## Supported Formats

- PDF files with extractable text
- DOCX files
- TXT files
- Markdown files (`.md` and `.markdown`)

PDF support means PDFs that already contain selectable text. Scanned PDFs and images need OCR, which is out of scope for v0.3.

## Quick Start

```bash
git clone https://github.com/PatricioV1207/localdocs-ai.git
cd localdocs-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate the virtual environment with:

```bash
.venv\Scripts\activate
```

Then open the Streamlit URL, upload documents or process the sample documents, ask questions, generate summaries, and use the study/export tools.

## Example Workflow

1. Upload PDF, DOCX, TXT, or Markdown documents.
2. Click `Process uploaded documents`.
3. Ask a question about the indexed documents.
4. Review the answer and cited sources.
5. Generate summaries.
6. Generate study questions and flashcards.
7. Export Markdown notes, an Anki TSV, or an Obsidian vault.

You can also click `Process sample documents` to try the files in `sample_docs/`.

## Screenshots

Screenshot placeholders and guidance live in [docs/screenshots](docs/screenshots/README.md).

Suggested future screenshots:

- Document upload and processing state
- Answer with cited sources
- Study Tools section
- Exported Obsidian vault

## Configuration

LocalDocs AI reads `localdocs_config.toml` from the project root. If the file is missing or invalid, the app uses defaults and shows readable warnings in the sidebar.

```toml
[chunking]
strategy = "word"
chunk_size = 220
chunk_overlap = 40

[search]
top_k = 4
minimum_score = 0.05

[exports]
export_dir = "exports"

[llm]
use_openai_if_available = true

[study]
max_flashcards = 20
max_questions = 20

[obsidian]
vault_dir = "exports/obsidian_vault"

[anki]
flashcards_file = "exports/flashcards.tsv"
```

Chunking strategies:

- `word`: default behavior, split by word count.
- `paragraph`: group nearby paragraphs into chunks.
- `heading`: split Markdown by headings when possible, with paragraph fallback.

Chunk and search settings are available in the app sidebar under `Advanced settings`:

- `Chunking strategy`: chooses how parsed text is split before indexing.
- `Chunk size`: controls the approximate maximum words per chunk.
- `Chunk overlap`: repeats words between word-based chunks to preserve context.
- `Search results`: controls how many chunks are retrieved for a question.
- `Minimum search score`: filters weak matches before QA.

The defaults are intentionally conservative. Raise the minimum score for stricter answers, or lower it if useful evidence is being missed.

## Obsidian Export

Process documents, optionally generate summaries, flashcards, and study questions, then click `Export Obsidian vault`.

Default output:

```txt
exports/obsidian_vault/
├── 00_Index.md
├── Summaries.md
├── Questions.md
├── Flashcards.md
├── Sources.md
└── Documents/
```

Open that folder as a vault in Obsidian, or copy it into an existing vault. Obsidian is not required to create the export.

## Anki TSV Export

Generate flashcards, then click `Export Anki TSV`.

Default output:

```txt
exports/flashcards.tsv
```

Import the file into Anki as a tab-separated file and map the fields to question, answer, and source.

## Optional OpenAI Configuration

LocalDocs AI works without OpenAI.

To enable optional LLM-generated answers and summaries:

```bash
export OPENAI_API_KEY=your_api_key_here
```

Or create a local `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env` files or API keys.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

If `pytest` is not on your shell path:

```bash
python -m pytest
```

GitHub Actions runs the test suite on push and pull requests.

## Project Structure

```txt
localdocs-ai/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   └── pull_request_template.md
├── docs/
│   ├── screenshots/
│   ├── architecture.md
│   └── roadmap.md
├── localdocs/
│   ├── parser.py
│   ├── chunker.py
│   ├── indexer.py
│   ├── search.py
│   ├── qa.py
│   ├── summarizer.py
│   ├── export.py
│   ├── flashcards.py
│   ├── study.py
│   ├── obsidian.py
│   └── config.py
├── sample_docs/
├── tests/
├── app.py
├── localdocs_config.toml
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── README.md
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

v0.4 is planned to focus on research comparison mode, richer study workflows, and multi-project knowledge bases while preserving local-first defaults.

## Current Limitations

- PDF parsing depends on extractable text.
- DOCX parsing reads normal paragraphs only; legacy `.doc` files are not supported.
- Search is keyword-oriented TF-IDF, not semantic search.
- Cleaning and quality filtering are heuristic and may still miss some document noise.
- Flashcards and study questions are simple extractive outputs.
- Obsidian export is a Markdown folder export only.
- Anki export is TSV only.
- Streamlit session state is temporary.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

Please keep changes local-first, simple, and useful without requiring an API key.

## Security

Please read [SECURITY.md](SECURITY.md) before reporting vulnerabilities. Do not post private documents, secrets, or API keys in public issues.

## License

LocalDocs AI is released under the MIT License. See [LICENSE](LICENSE).
