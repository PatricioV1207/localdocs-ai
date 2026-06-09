# LocalDocs AI v0.3 Goal

## Version objective

LocalDocs AI v0.3 should improve the project by adding study/export workflows on top of the existing v0.2 codebase.

The goal is to make LocalDocs AI more useful for students, researchers, teachers, and knowledge workers by allowing them to turn processed documents into reusable notes and flashcards.

## Important instruction

Do not rebuild the project from scratch.

Continue from the existing v0.2 codebase.

Preserve all v0.1 and v0.2 behavior:

- PDF parsing
- TXT parsing
- Markdown parsing
- DOCX parsing
- chunking
- TF-IDF search
- question answering with cited sources
- extractive fallback without `OPENAI_API_KEY`
- optional OpenAI answers if `OPENAI_API_KEY` exists
- summaries
- Markdown export
- configuration file
- improved Streamlit UI
- existing tests

## v0.3 scope

Implement only the following improvements:

1. Obsidian vault export.
2. Anki-compatible flashcard export.
3. Improved chunking strategies.
4. Study question generation.
5. UI section for study/export tools.
6. Tests for the new v0.3 behavior.
7. Documentation updates.

Do not implement v0.4 or future features yet.

## Feature 1: Obsidian vault export

Add an export mode that creates an Obsidian-friendly Markdown vault.

Create a module if useful:

```txt
localdocs/obsidian.py
```

The export should create a folder such as:

```txt
exports/obsidian_vault/
├── 00_Index.md
├── Summaries.md
├── Questions.md
├── Flashcards.md
├── Sources.md
└── Documents/
    ├── document_1.md
    └── document_2.md
```

Requirements:

- Create an index file.
- Export document summaries.
- Export Q&A history.
- Export generated study questions.
- Export flashcards.
- Create one Markdown file per source document when possible.
- Use clean Markdown.
- Use internal Obsidian-style links where useful, for example `[[Summaries]]`.
- Do not require Obsidian to be installed.
- This is only a Markdown folder export.

## Feature 2: Anki-compatible flashcard export

Add flashcard generation and export.

Create a module if useful:

```txt
localdocs/flashcards.py
```

Flashcards should be exportable as a simple `.tsv` file compatible with Anki import.

Suggested output:

```txt
exports/flashcards.tsv
```

Format:

```txt
Question<TAB>Answer<TAB>Source
```

Requirements:

- Generate basic flashcards from document chunks or summaries.
- If no LLM is configured:
  - Generate simple extractive flashcards using headings, first sentences, or important chunks.
- If OpenAI is configured:
  - Optionally generate better question-answer flashcards from retrieved content.
- Every flashcard should include a source reference.
- Avoid empty or duplicate flashcards.
- Add tests for TSV export.

## Feature 3: Improved chunking strategies

Improve chunking without making the project complex.

Current chunking can remain as the default, but add support for strategy selection.

Suggested strategies:

1. `word`
   - Existing behavior.
   - Splits by word count.

2. `paragraph`
   - Groups paragraphs into chunks.
   - Useful for Markdown, TXT, and DOCX.

3. `heading`
   - For Markdown files, prefer splitting by headings when possible.
   - Fallback to paragraph or word chunking if headings are not found.

Update the config file:

```toml
[chunking]
strategy = "word"
chunk_size = 220
chunk_overlap = 40
```

Requirements:

- Keep `word` as the default.
- Do not break existing tests.
- Add tests for paragraph chunking.
- Add tests for Markdown heading-aware chunking if practical.
- Preserve metadata in all chunking strategies.

## Feature 4: Study question generation

Add a simple study question generator.

Create a module if useful:

```txt
localdocs/study.py
```

The app should be able to generate:

- Short-answer questions.
- Basic quiz questions.
- Review questions based on summaries or chunks.

Requirements:

- If no LLM is configured:
  - Generate simple questions from headings, summaries, or important chunks.
- If OpenAI is configured:
  - Optionally generate better questions.
- Every question should include a source reference.
- Export questions to Markdown.
- Include questions in the Obsidian export.

Do not build a full learning platform in v0.3.

## Feature 5: Streamlit UI updates

Update `app.py` to include a simple study/export section.

The UI should include:

- Existing document upload and Q&A workflow.
- Existing summary generation.
- A new section called `Study Tools` or similar.
- Button to generate flashcards.
- Button to generate study questions.
- Button to export Obsidian vault.
- Button to export Anki TSV.
- Success/error messages for each export.
- Expanders to preview flashcards and study questions.

Keep the UI simple.

Do not create a complex frontend or redesign the whole app.

## Feature 6: Configuration updates

Update `localdocs_config.toml`.

Suggested additions:

```toml
[chunking]
strategy = "word"
chunk_size = 220
chunk_overlap = 40

[study]
max_flashcards = 20
max_questions = 20

[obsidian]
vault_dir = "exports/obsidian_vault"

[anki]
flashcards_file = "exports/flashcards.tsv"
```

Requirements:

- Use sensible defaults if config values are missing.
- Do not crash on invalid config.
- Update config tests.

## Feature 7: Documentation updates

Update `README.md`.

Include:

- Current status: v0.3.
- Supported formats.
- Obsidian export instructions.
- Anki TSV export instructions.
- Study tools explanation.
- Chunking strategy configuration.
- Limitations.

Update `docs/architecture.md`.

Add:

- Obsidian export architecture.
- Flashcard generation flow.
- Study question generation flow.
- Chunking strategy design.

Update `docs/roadmap.md`.

Mark:

- v0.1 completed.
- v0.2 completed.
- v0.3 implemented or current.
- v0.4 planned.

Update `CHANGELOG.md`.

Add:

```md
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

### Not included
- Vector databases.
- Local embeddings.
- OCR.
- Multi-user accounts.
- Cloud sync.
- Desktop packaging.
```

## Feature 8: Tests

Add or update tests for:

- Obsidian export folder creation.
- Obsidian index file creation.
- Anki TSV flashcard export.
- Flashcard generation.
- Study question generation.
- Paragraph chunking.
- Markdown heading-aware chunking if practical.
- Config defaults for new v0.3 settings.

All existing tests must continue to pass.

Run:

```bash
pytest
```

## Do not build in v0.3

Do not add:

- ChromaDB
- FAISS
- LangChain
- LlamaIndex
- Local embeddings
- OCR
- Audio transcription
- Image analysis
- User accounts
- Authentication
- Cloud sync
- Payments
- Browser extension
- Desktop app
- Mobile app
- Multi-user collaboration
- Research comparison mode
- Plugin system
- Complex database migrations

Those are future features.

## Validation

Before finishing:

1. Run all tests.
2. Run import/compile checks if practical.
3. Verify the Streamlit app starts.
4. Confirm v0.1 and v0.2 features still work.
5. Confirm Obsidian export creates a usable Markdown folder.
6. Confirm Anki export creates a TSV file.
7. Confirm flashcards and study questions include source references.
8. Update documentation.

## Final expected result

After v0.3, the user should be able to:

1. Upload PDF, TXT, Markdown, or DOCX files.
2. Process them locally.
3. Ask questions with cited sources.
4. Generate summaries.
5. Generate study questions.
6. Generate flashcards.
7. Export summaries and Q&A history to Markdown.
8. Export a small Obsidian-compatible vault.
9. Export Anki-compatible flashcards as TSV.

## Final response required

When finished, summarize:

- Files changed.
- Features added.
- Tests run.
- How to run the app.
- How to use Obsidian export.
- How to import flashcards into Anki.
- Current v0.3 limitations.
- Recommended next steps for v0.4.