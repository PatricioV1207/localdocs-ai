# Contributing to LocalDocs AI

Thanks for helping make LocalDocs AI better. This project is local-first, beginner-friendly, and intentionally small.

## Project Principles

- Keep document processing local by default.
- Preserve useful behavior without requiring an OpenAI API key.
- Include source references for document-based answers.
- Prefer readable code over clever abstractions.
- Keep each release focused on its documented scope.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
.venv\Scripts\activate
```

Run the app:

```bash
streamlit run app.py
```

Run tests:

```bash
pytest
```

If `pytest` is not on your shell path:

```bash
python -m pytest
```

## Good First Contributions

- Improve tests for parsing, chunking, search, exports, and study tools.
- Improve documentation or sample documents.
- Improve error messages.
- Make small UI polish changes that keep the app simple.
- Fix bugs in existing v0.1-v0.3 behavior.

## Scope Boundaries

Please do not add major future-scope features without discussion. Current out-of-scope examples include vector databases, local embeddings, OCR, authentication, cloud sync, desktop packaging, mobile apps, multi-user collaboration, and plugin systems.

## Pull Request Checklist

- Keep the change focused.
- Add or update tests when behavior changes.
- Run `pytest` before opening the PR.
- Update `README.md`, `docs/architecture.md`, `docs/roadmap.md`, or `CHANGELOG.md` when user-facing behavior changes.
- Avoid committing generated exports, local virtual environments, caches, or secrets.

## Reporting Bugs

Use the bug report issue template. Include:

- What you expected to happen.
- What actually happened.
- Steps to reproduce.
- The document format involved, if relevant.
- Any safe-to-share error message.

Do not upload private documents or API keys in issues.
