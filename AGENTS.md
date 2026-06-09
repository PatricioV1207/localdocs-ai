# AGENTS.md

You are working on LocalDocs AI.

LocalDocs AI is an open-source, local-first document intelligence app. Its goal is to help users turn folders of documents into private, searchable, AI-assisted knowledge bases.

## Main instruction

Maintain a functional local-first MVP, not a final product.

Do not over-engineer the project. Do not build advanced features unless they are explicitly requested. Focus on a clean, working, testable first version.

## Product principles

- Local-first by default.
- The app must work without requiring an OpenAI API key.
- OpenAI integration can be optional, but the MVP must still be useful without it.
- Every answer based on documents must include source references.
- Never invent information that is not present in the indexed documents.
- If there is not enough evidence in the documents, say so clearly.
- Keep the code simple, modular, and easy for new contributors to understand.
- Prefer readable code over clever code.
- Prefer a working MVP over a complex unfinished architecture.

## MVP tech stack

Use the following stack for v0.1:

- Python
- Streamlit
- pypdf or PyMuPDF for PDF parsing
- scikit-learn TF-IDF for local search
- pytest for tests
- Markdown export files
- Optional OpenAI integration only if `OPENAI_API_KEY` is configured

Do not use the following in v0.1 unless absolutely necessary:

- Next.js
- React
- User accounts
- Cloud database
- Authentication
- Payment systems
- Complex vector databases
- Docker
- Desktop app frameworks
- Multi-user features

## Expected repository structure

Use this structure unless there is a strong reason to improve it:

```txt
localdocs-ai/
├── README.md
├── QUALITY_STANDARD.md
├── PROGRESS.md
├── DECISIONS.md
├── LICENSE
├── requirements.txt
├── requirements-embeddings.txt
├── app.py
├── AGENTS.md
├── evals/
│   ├── fixtures/
│   └── expected/
├── scripts/
│   ├── run_quality_eval.py
│   └── validate.py
├── localdocs/
│   ├── __init__.py
│   ├── parser.py
│   ├── chunker.py
│   ├── indexer.py
│   ├── embeddings.py
│   ├── document_types.py
│   ├── search.py
│   ├── qa.py
│   ├── concepts.py
│   ├── cleaning.py
│   ├── flashcards.py
│   ├── study.py
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

## Development commands

Use these commands when possible:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/validate.py fast
streamlit run app.py
```

On Windows, document the alternative activation command:

```bash
.venv\Scripts\activate
```

## Definition of done

The MVP is complete only when:

- The app runs with `streamlit run app.py`.
- The user can upload or process PDF, TXT, and Markdown documents.
- The documents are parsed into chunks.
- The chunks can be searched locally.
- The user can ask a question.
- The app returns an answer or relevant extracted context.
- Every answer includes source references.
- The user can generate summaries.
- The user can export summaries and Q&A results to Markdown.
- Tests exist and pass.
- The deterministic quality evaluation passes.
- README.md explains installation and usage.
- The project has a clear roadmap.

## Quality evaluation

`QUALITY_STANDARD.md` is the source of truth for QA, summary, study-question,
flashcard, UI-state, and source-selection quality.

Quality artifacts:

- `QUALITY_STANDARD.md`: hard gates and contributor workflow.
- `PROGRESS.md`: current quality-evaluation status.
- `DECISIONS.md`: durable decisions about evaluation design.
- `evals/fixtures/*.json`: synthetic document inputs.
- `evals/expected/*.json`: expected behavior for matching fixtures.
- `scripts/run_quality_eval.py`: deterministic local and CI runner.
- `scripts/validate.py`: fast, focused, and full validation profiles.

## Validation workflow

Use the smallest profile that proves the current change:

1. **During development:** run `python scripts/validate.py fast` after small
   edits. It compiles application modules and runs the essential parsing,
   chunking, search, export, and UI-state smoke tests.
2. **After changing an area:** run focused validation with one or more areas,
   for example `python scripts/validate.py focused qa study`. This runs mapped
   tests and only the relevant deterministic fixtures.
3. **Before commit, release, or final handoff:** run
   `python scripts/validate.py full` exactly once after focused checks pass.
   This is the authoritative release gate.

Focused areas:

```txt
core parsing search qa summaries study flashcards exports ui quality validation
```

For shared cleaning, concept extraction, or source-ranking changes, combine the
affected output areas, usually:

```bash
python scripts/validate.py focused qa summaries study flashcards
```

Use `python scripts/validate.py --dry-run focused qa` to inspect a plan without
running it. Do not repeatedly run `full` while iterating, and do not claim a
full validation from `fast` or `focused` results.

When changing QA, summaries, cleaning, concept extraction, study questions,
flashcards, UI document state, or source ranking:

1. Preserve source grounding and citations.
2. Add or update the smallest relevant fixture and expected file.
3. Record intentional evaluation-policy changes in `DECISIONS.md`.
4. Run the relevant focused profile while iterating:

```bash
python scripts/validate.py focused qa summaries
```

5. Run `python scripts/validate.py full` once before commit, release, or final
   handoff.

Do not weaken an expected result merely to make a regression pass. Prefer fewer
high-quality study items over forcing the configured maximum.

## Behavior expectations

Before making major architectural changes, prefer the simplest implementation that satisfies the MVP.

When something is uncertain, make a reasonable implementation decision and document it in `README.md` or `DECISIONS.md`.

Do not stop to ask for clarification unless the task is impossible without it.

At the end of the task, summarize:

- What was implemented.
- How to run the app.
- Which tests were run.
- What remains for future versions.
