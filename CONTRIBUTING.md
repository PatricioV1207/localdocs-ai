# Contributing to LocalDocs AI

Thanks for helping make LocalDocs AI better. This project is local-first,
beginner-friendly, and intentionally small.

## Before You Start

- Search existing issues before opening a new one.
- Use synthetic or public sample text in bug reports and tests.
- Open an issue before investing in a large change or anything outside the
  current MVP scope.
- Keep pull requests focused enough to review in one sitting.

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

During development, run the fast profile:

```bash
python scripts/validate.py fast
```

After changing a specific area, run focused validation:

```bash
python scripts/validate.py focused parsing
python scripts/validate.py focused qa summaries
```

Before opening a pull request, run the full profile once:

```bash
python scripts/validate.py full
```

Focused areas are `core`, `parsing`, `search`, `qa`, `summaries`, `study`,
`flashcards`, `exports`, `ui`, `quality`, and `validation`. Multiple areas may
be combined in one command. For shared cleaning, concept extraction, or source
ranking, combine `qa summaries study flashcards`.

## Good First Contributions

- Improve tests for parsing, chunking, search, exports, and study tools.
- Improve documentation or sample documents.
- Improve error messages.
- Make small UI polish changes that keep the app simple.
- Fix bugs in existing v0.1-v0.3 behavior.
- Add a deterministic fixture for a reproducible quality regression.

## Scope Boundaries

Please do not add major future-scope features without discussion. Current
out-of-scope examples include vector databases, local embeddings, OCR,
authentication, cloud sync, desktop packaging, mobile apps, multi-user
collaboration, and plugin systems.

## Development Workflow

1. Create a focused branch.
2. Add or update a test that demonstrates the intended behavior.
3. Implement the smallest clear change.
4. For QA, summaries, cleaning, study tools, or source selection, add or update
   a matching fixture under `evals/fixtures/` and `evals/expected/`.
5. Run focused validation for the changed areas.
6. Update `CHANGELOG.md` when behavior visible to users changes.
7. Run the full profile once.
8. Open a pull request using the repository template.

## Code and Documentation Style

- Prefer readable functions and established module boundaries.
- Keep local behavior deterministic when possible.
- Do not expose raw API, billing, authentication, or quota payloads to users.
- Preserve source citations and weak-evidence behavior.
- Do not commit `.env`, generated exports, caches, private documents, or
  screenshots containing personal data.
- Use repository sample documents for demos and documentation.

## Pull Request Checklist

- Keep the change focused.
- Add or update tests when behavior changes.
- Run `python scripts/validate.py full`.
- Update `README.md`, `RELEASE_NOTES.md`, or `CHANGELOG.md` when user-facing
  behavior changes.
- Avoid committing generated exports, local virtual environments, caches, or secrets.
- Confirm that the app still works without `OPENAI_API_KEY`.

## Quality Fixtures

Quality fixtures contain synthetic chunks only. Each file under
`evals/fixtures/` must have a matching filename under `evals/expected/`.

Do not weaken an expected result merely to make a regression pass. If an
expectation changes intentionally, explain why in `DECISIONS.md`.

## Reporting Bugs

Use the bug report issue template. Include:

- What you expected to happen.
- What actually happened.
- Steps to reproduce.
- The document format involved, if relevant.
- Any safe-to-share error message.

Do not upload private documents or API keys in issues.

For security-sensitive problems, follow [SECURITY.md](SECURITY.md) instead of
opening a public bug report.
