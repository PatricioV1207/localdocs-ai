# LocalDocs AI

[![Tests](https://github.com/PatricioV1207/localdocs-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/PatricioV1207/localdocs-ai/actions/workflows/tests.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Local-first](https://img.shields.io/badge/local--first-yes-brightgreen.svg)

LocalDocs AI is an open-source, local-first document intelligence app. It turns PDFs, DOCX files, text notes, and Markdown files into a private searchable knowledge base with cited answers, summaries, study questions, flashcards, and Markdown exports.

Status: v0.3.4 implemented.

## Why LocalDocs AI?

Many people have useful knowledge scattered across PDFs, notes, manuals, and guides. LocalDocs AI helps make those documents searchable and reusable while keeping the default workflow on your machine.

The app works without an OpenAI API key. OpenAI generation is disabled by default. If `OPENAI_API_KEY` is configured and the sidebar option is enabled, LocalDocs can optionally generate more natural answers and summaries, but answers are still based on retrieved document context.

## Features

- Parse PDF, DOCX, TXT, Markdown, and `.markdown` files.
- Chunk documents with `word`, `paragraph`, or Markdown `heading` strategies.
- Search locally with scikit-learn TF-IDF.
- Ask questions and get cited answers.
- Fall back to concise heuristic extractive answers without an API key.
- Generate basic summaries.
- Generate grammar-validated study questions and same-language flashcards with source references.
- Prefer fewer high-quality study items over filling the configured limit with weak content.
- Export summaries and Q&A history to Markdown.
- Export an Obsidian-friendly Markdown vault.
- Export Anki-compatible flashcards as TSV.
- Configure behavior with `localdocs_config.toml`.
- Run deterministic quality evaluations for QA, study tools, and source selection.

## Not Included

LocalDocs AI v0.3.4 intentionally does not include user accounts, authentication, cloud sync, OCR, audio transcription, image analysis, vector databases, desktop/mobile packaging, or multi-user collaboration.

## Supported Formats

- PDF files with extractable text
- DOCX files
- TXT files
- Markdown files (`.md` and `.markdown`)

PDF support means PDFs that already contain selectable text. Scanned PDFs and images need OCR, which is out of scope for v0.3.4.

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
use_openai_if_available = false

[study]
max_flashcards = 10
max_questions = 10

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

OpenAI API billing is separate from a ChatGPT subscription. Having ChatGPT access does not automatically provide API credits. If the API key is unavailable, invalid, rate-limited, or out of quota, LocalDocs shows a short friendly notice and continues with local extractive mode without exposing the raw API error.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest
```

Running pytest as a Python module also ensures the repository package is importable consistently in local environments and GitHub Actions.

The equivalent direct command remains available when your shell is configured for it:

```bash
pytest
```

Run the deterministic quality gate:

```bash
python scripts/run_quality_eval.py
```

Compile all Python modules:

```bash
python -m compileall app.py localdocs tests scripts
```

GitHub Actions runs pytest, compileall, and the deterministic quality gate on
Python 3.11 and 3.12 for pushes and pull requests. It does not require
`OPENAI_API_KEY`.

## Quality Evaluation

[QUALITY_STANDARD.md](QUALITY_STANDARD.md) defines the hard gates for local QA,
summaries, study questions, flashcards, UI state, and source quality. The
evaluation system uses synthetic JSON chunks, so it does not require private
PDFs, network access, or an OpenAI API key.

```txt
evals/
├── fixtures/
└── expected/
```

Each fixture has a matching expected file. The runner checks grounding,
citations, required concepts, forbidden fragments, grammatical questions,
complete QA sentences, summary evidence, flashcard answer relevance, and
rejection of legal, index, contact, product, marketing, and broken-OCR sources.

See [PROGRESS.md](PROGRESS.md) for current status and
[DECISIONS.md](DECISIONS.md) for design decisions.

## Project Structure

```txt
localdocs-ai/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   └── pull_request_template.md
├── localdocs/
│   ├── parser.py
│   ├── chunker.py
│   ├── cleaning.py
│   ├── concepts.py
│   ├── indexer.py
│   ├── search.py
│   ├── qa.py
│   ├── summarizer.py
│   ├── export.py
│   ├── flashcards.py
│   ├── study.py
│   ├── obsidian.py
│   └── config.py
├── evals/
│   ├── fixtures/
│   └── expected/
├── scripts/
│   └── run_quality_eval.py
├── sample_docs/
├── tests/
├── QUALITY_STANDARD.md
├── PROGRESS.md
├── DECISIONS.md
├── app.py
├── localdocs_config.toml
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── README.md
```

## Roadmap

v0.4 is planned to focus on research comparison mode, richer study workflows, and multi-project knowledge bases while preserving local-first defaults.

## Current Limitations

- PDF parsing depends on extractable text.
- DOCX parsing reads normal paragraphs only; legacy `.doc` files are not supported.
- Search is keyword-oriented TF-IDF, not semantic search.
- Local answers select and join source sentences heuristically; they are not full abstractive summaries.
- Cleaning, grammatical validation, and concept extraction are heuristic and may still miss specialized terminology or unusual layouts.
- Strict quality filters can return fewer study questions or flashcards than the configured maximum.
- Spanish and English are the best-supported study-content languages; mixed-language documents can be inconsistent.
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
