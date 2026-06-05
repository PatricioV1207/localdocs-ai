# AGENTS.md

You are working on LocalDocs AI.

LocalDocs AI is an open-source, local-first document intelligence app. Its goal is to help users turn folders of documents into private, searchable, AI-assisted knowledge bases.

## Main instruction

Build a functional v0.1 MVP, not a final product.

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

## Development commands

Use these commands when possible:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

On Windows, document the alternative activation command:

```bash
.venv\Scripts\activate
```

## Definition of done for v0.1

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
- README.md explains installation and usage.
- The project has a clear roadmap.

## Behavior expectations

Before making major architectural changes, prefer the simplest implementation that satisfies the MVP.

When something is uncertain, make a reasonable implementation decision and document it in the README or docs.

Do not stop to ask for clarification unless the task is impossible without it.

At the end of the task, summarize:

- What was implemented.
- How to run the app.
- Which tests were run.
- What remains for future versions.