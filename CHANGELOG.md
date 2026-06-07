# Changelog

## Unreleased

### Added

- Contributor guide.
- Security policy.
- GitHub issue and pull request templates.
- GitHub Actions test workflow.
- Screenshot placeholder documentation.

### Improved

- README structure for open-source contributors.
- Roadmap clarity for v0.4 plans.
- Ignore rules for local caches, build artifacts, secrets, and generated exports.

## v0.3.3

### Fixed

- Replaced fragment-based study prompts with shared technical concept extraction.
- Generated Spanish flashcard prompts for Spanish source documents and kept answers tied to supporting sentences.
- Reworked local extractive QA to select complete concept-relevant sentences and cite only the evidence used.
- Prevented legal, commercial, contact, table-of-contents, and broken-OCR chunks from outranking useful technical sections.

### Improved

- Added Spanish pneumatic-safety concept coverage, including safety functions, ISO terms, risk concepts, and valve identifiers.
- Added a deterministic six-chunk Spanish regression fixture shared by study, flashcard, and QA tests.
- Clarified heuristic local mode and concept-based study generation in the Streamlit UI.

## v0.3.2

### Fixed

- Cleared stale visible answers and relevant chunks when an invalid or placeholder-like question is submitted.
- Replaced weak single-word study concepts with multi-word technical phrase extraction, including stronger Spanish stopword and metadata filtering.
- Rejected generic flashcard concepts and deduplicated cards by question.
- Improved extractive summaries so technical, objective, component, exercise, and safety sections outrank front matter.
- Hid raw OpenAI authentication, quota, billing, and rate-limit payloads behind a friendly local-fallback message.
- Fixed GitHub Actions test collection on Python 3.11 and 3.12 by running `python -m pytest`.

### Improved

- Made optional OpenAI generation disabled by default and ensured the setting overrides an environment API key.
- Added Spanish extractive summary labeling and source citations tied to selected summary evidence.
- Updated GitHub Actions to Node 24-compatible `checkout` and `setup-python` releases.
- Added regression tests for invalid question state, OpenAI fallback, Spanish technical concepts, weak-term rejection, duplicate filtering, and summary quality.

## v0.3.1

### Fixed

- Improved local extractive answer quality and weak-evidence messaging.
- Rejected empty, too-short, and placeholder questions before QA runs.
- Reduced noisy text from repeated headers, footers, page numbers, copyright/front matter, and table-of-contents-like chunks.
- Improved summaries, flashcards, and study questions so they prefer informative chunks.
- Reduced duplicate or low-value flashcards and study questions.

### Improved

- Moved chunk and search controls into an Advanced settings section with help text.
- Added tests for question validation, text cleaning, low-value chunk filtering, summaries, QA, flashcards, and study questions.

## v0.3.0

### Added

- Obsidian vault export.
- Anki-compatible flashcard export.
- Study question generation.
- Configurable chunking strategies.

### Improved

- Export workflow.
- Study-oriented document reuse.
- Documentation.

### Not Included

- Vector databases.
- Local embeddings.
- OCR.
- Multi-user accounts.
- Cloud sync.
- Desktop packaging.

## v0.2.0

### Added

- DOCX support.
- Local `localdocs_config.toml` file.
- Improved Streamlit UI for document status, source display, summaries, and exports.
- More tests.

### Improved

- Error handling for empty files, unsupported files, parser failures, weak search results, and export-before-content.
- Source display for answers and relevant chunks.
- Documentation for supported formats, configuration, architecture, and roadmap.

### Not Included

- OCR.
- Obsidian export.
- Anki export.
- Vector database.
- Multi-user accounts.

## v0.1.0

### Added

- PDF, TXT, and Markdown parsing.
- Local TF-IDF search.
- Extractive question answering with cited sources.
- Optional OpenAI answers when `OPENAI_API_KEY` is configured.
- Basic summaries.
- Markdown export for summaries and Q&A history.
- Streamlit MVP interface.
