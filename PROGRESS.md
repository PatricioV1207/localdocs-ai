# Quality Evaluation Progress

## Current State

- Deterministic quality evaluation system added.
- QA, study questions, flashcards, and source quality have fixture-backed gates.
- Spanish pneumatic-safety regressions are represented without storing private
  source documents.
- Relational QA rejects unsupported associations assembled from separate
  technical chunks.
- Spanish study questions no longer confuse the verb `funciona` with the noun
  `función`.
- The evaluation command is integrated into GitHub Actions.
- Open-source presentation materials are aligned with the v0.3.5 MVP.

## Completed

- Cycle 1: required full substantive-term coverage in local QA so qualifiers
  such as `máxima` cannot be silently dropped; 90 tests and 163 quality checks
  passed.
- Cycle 2: prevented summaries from quoting documents made entirely of legal,
  index, or marketing noise; summary evaluation was added to the quality runner;
  91 tests and 191 quality checks passed.
- Cycle 3: processing a document set with no extractable text now clears every
  answer, source, summary, flashcard, and study question from the previous set;
  92 tests and 191 quality checks passed.
- Cycle 4: long QA and flashcard evidence now ends at a complete clause instead
  of a character-level ellipsis; a long-sentence fixture was added; 93 tests and
  223 quality checks passed.
- Cycle 5: mixed PDF chunks keep complete technical evidence even when a
  separate legal or commercial footer is appended; pure noise remains rejected;
  94 tests and 265 quality checks passed.
- Defined hard quality standards in `QUALITY_STANDARD.md`.
- Added fixture and expected-result schemas under `evals/`.
- Added `scripts/run_quality_eval.py`.
- Added automated tests for the quality runner.
- Added a regression fixture for unsupported cross-chunk relationships.
- Documented the contributor workflow in `AGENTS.md` and `README.md`.
- Reworked `README.md` around local-first value, reproducible setup, a
  60-second demo, project badges, current scope, and contributor entry points.
- Added versionable interface previews and screenshot guidance under
  `assets/screenshots/`.
- Added `DEMO.md` and `RELEASE_NOTES.md`.
- Expanded `CONTRIBUTING.md`, `SECURITY.md`, issue templates, and the pull
  request template to match the current quality gates and privacy rules.
- Completed a final maintainer review: corrected version/release wording,
  replaced public placeholder language with sample-based interface previews,
  clarified CI job naming, and updated the ignored local architecture and
  roadmap notes to v0.3.5.

## Validation Checklist

- [x] `python -m pytest` - 94 passed on Python 3.13
- [x] `python -m compileall app.py localdocs tests scripts`
- [x] `python scripts/run_quality_eval.py` - 265 checks passed
- [x] GitHub Actions Python 3.11/3.12 matrix configured to run all gates
- [x] Streamlit smoke test - sample documents processed and cited local answer
  rendered without browser console errors
- [x] Presentation demo - processed 2 sample documents, returned the documented
  TF-IDF answer and citation, then generated summaries, flashcards, and study
  questions without browser warnings or errors
- [x] Documentation audit - internal Markdown links resolve, both interface
  preview SVGs parse, and GitHub templates contain current validation steps
- [x] CI audit - workflow YAML is valid, permissions remain read-only, push,
  pull request, and manual triggers are configured, and the Python 3.11/3.12
  matrix runs pytest, compileall, and deterministic quality evaluations

Update this checklist with the latest verified state when quality behavior or
fixtures change.

## Next Quality Work

- Add fixtures only when a concrete document-quality regression is found.
- Keep expectations deterministic and source-grounded.
- Avoid expanding this system into semantic search, OCR, or other v0.4 features.
