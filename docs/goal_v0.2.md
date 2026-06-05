# LocalDocs AI v0.2 Goal

## Version objective

LocalDocs AI v0.2 should improve the existing v0.1 MVP without redesigning the whole project.

The goal is to make the app more useful, more stable, and easier to use while preserving the local-first and beginner-friendly architecture.

## Important instruction

Do not rebuild the project from scratch.

Continue from the existing v0.1 codebase.

Preserve the current working features:

- PDF parsing
- TXT parsing
- Markdown parsing
- chunking
- TF-IDF search
- question answering with cited sources
- extractive fallback without `OPENAI_API_KEY`
- optional OpenAI answers
- summaries
- Markdown export
- tests

## v0.2 scope

Implement only the following improvements:

1. DOCX support.
2. Improved Streamlit user interface.
3. Local configuration file.
4. Better error handling.
5. Better tests.
6. Updated documentation.
7. Changelog.

Do not implement v0.3 or future features yet.

## Feature 1: DOCX support

Add support for `.docx` files.

Requirements:

- Add `python-docx` to `requirements.txt`.
- Update the parser to support `.docx`.
- Extract readable text from paragraphs.
- Skip empty paragraphs.
- Preserve metadata:
  - file name
  - file path
  - file type
  - chunk index after chunking
- Add tests for DOCX parsing.

Do not support legacy `.doc` files.

## Feature 2: Improved Streamlit UI

Improve `app.py` without making the UI complex.

The UI should include:

- A document upload section.
- A processed documents summary.
- Number of documents processed.
- Number of chunks created.
- List of processed file names.
- Question input.
- Answer section.
- Sources section.
- Optional expandable section for relevant chunks.
- Summary generation section.
- Export section.
- Clear status messages.

Use Streamlit components such as:

- `st.sidebar`
- `st.expander`
- `st.info`
- `st.warning`
- `st.success`
- `st.error`

Keep the UI simple and clean.

## Feature 3: Configuration file

Add a simple configuration system.

Create a default config file:

```txt
localdocs_config.toml
```

Suggested settings:

```toml
[chunking]
chunk_size = 220
chunk_overlap = 40

[search]
top_k = 4
minimum_score = 0.05

[exports]
export_dir = "exports"

[llm]
use_openai_if_available = true
```

Requirements:

- Add a config loader module if useful, for example `localdocs/config.py`.
- If the config file is missing, use sensible defaults.
- Do not crash if the config is invalid. Show a readable warning and use defaults.
- Use config values in chunking, search, and export behavior where appropriate.

## Feature 4: Better error handling

Improve error handling across the app.

Requirements:

- Empty files should not crash the app.
- Unsupported file types should show a clear message.
- Corrupted or unreadable PDFs should show a clear message.
- DOCX parsing errors should show a clear message.
- Asking a question before processing documents should show a warning.
- Exporting before generating content should show a warning.
- If search results are weak, the answer should clearly say that there is not enough evidence.

## Feature 5: Better tests

Add or improve tests for existing behavior.

Required tests:

- TXT parsing still works.
- Markdown parsing still works.
- PDF parsing works with a small generated or fixture PDF if practical.
- DOCX parsing works.
- Chunking preserves metadata.
- Search returns relevant chunks.
- QA fallback includes citations.
- Summary generation returns non-empty output for valid chunks.
- Markdown export creates files.

All tests must pass with:

```bash
pytest
```

## Feature 6: Documentation updates

Update `README.md`.

The README should include:

- Current status: v0.2 in development or v0.2 implemented.
- Supported formats:
  - PDF
  - TXT
  - Markdown
  - DOCX
- Installation instructions.
- Usage instructions.
- Optional OpenAI configuration.
- Config file explanation.
- Limitations.
- Roadmap.

Update `docs/architecture.md`.

Include:

- How DOCX parsing works.
- How config is loaded.
- How UI state works at a high level.
- Why v0.2 still uses TF-IDF.

Update `docs/roadmap.md`.

Mark v0.1 as completed and v0.2 as current/completed depending on implementation.

## Feature 7: Changelog

Create `CHANGELOG.md`.

Add entries for:

```md
## v0.2.0

### Added
- DOCX support.
- Local config file.
- Improved Streamlit UI.
- More tests.

### Improved
- Error handling.
- Source display.
- Documentation.

### Not included
- OCR.
- Obsidian export.
- Anki export.
- Vector database.
- Multi-user accounts.
```

Also include a short v0.1.0 entry.

## Do not build in v0.2

Do not add:

- Obsidian export
- Anki flashcard export
- Local embeddings
- ChromaDB
- FAISS
- LangChain
- LlamaIndex
- User accounts
- Authentication
- Cloud sync
- Payments
- OCR
- Audio transcription
- Desktop app
- Mobile app
- Multi-user collaboration
- Research comparison mode
- Study mode

Those are future features.

## Validation

Before finishing:

1. Run all tests.
2. Run import/compile checks if practical.
3. Verify the Streamlit app starts.
4. Confirm that v0.1 features still work.
5. Confirm DOCX support works.
6. Update documentation.

## Final response required

When finished, summarize:

- Files changed.
- Features added.
- Tests run.
- How to run the app.
- How to use the config file.
- Current v0.2 limitations.
- Recommended next steps for v0.3.