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
