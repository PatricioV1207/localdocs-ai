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
- Open-source presentation materials are aligned with the v0.4.0 MVP.
- Validation profiles provide smaller development feedback without weakening
  the final release gate.
- Optional semantic and hybrid retrieval use an injectable local embedding
  provider while retaining TF-IDF as the always-available fallback.
- Semantic quality checks use deterministic fake vectors and require no model
  download.
- General document intelligence detects five document types and reusable
  section roles without topic-specific concept lists.
- Study and flashcard templates now respond to document structure.

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
- Added `scripts/validate.py` with fast, focused, and full profiles plus
  deterministic area-to-test and area-to-fixture mappings.
- Added concise successful output for quality evaluations and documented the
  profile policy for Codex, contributors, CI, demos, and releases.
- Verified the optimized workflow: `fast` passed 18 smoke tests, focused QA
  passed 23 tests and 237 relevant checks, and the single final `full` run
  passed all release gates.
- Added semantic, hybrid, index-failure, query-failure, invalid-vector, and
  dimension-mismatch coverage.
- Added multidomain fixtures for academic practice, a technical procedure,
  research findings, a service agreement, and generic community content.
- Completed the v0.4.0 release gate with 110 pytest tests and 273 deterministic
  quality checks on Python 3.13.
- Completed the general-retrieval v0.4.0 gate with 125 pytest tests and 316
  deterministic quality checks on Python 3.13.

## Validation Checklist

- [x] `python scripts/validate.py fast` - 18 smoke tests passed
- [x] `python scripts/validate.py focused qa` - 23 tests and 237 relevant
  quality checks passed
- [x] `python scripts/validate.py full` - 100 tests passed on Python 3.13
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

- [x] v0.4.0 `python scripts/validate.py full` - 110 tests passed on Python 3.13
- [x] v0.4.0 deterministic quality evaluation - 273 checks passed
- [x] v0.4.0 general retrieval gate - 125 tests and 316 quality checks passed

The v0.3.5 checklist entries remain as historical verification; the v0.4.0
entries are the current release evidence.

## Next Quality Work

- Add fixtures only when a concrete document-quality regression is found.
- Keep expectations deterministic and source-grounded.
- Add retrieval fixtures only for concrete semantic or lexical regressions.
- Keep model-backed retrieval optional and preserve automatic TF-IDF fallback.
- Expand structural markers only from general document patterns, not a single
  subject-matter vocabulary.
