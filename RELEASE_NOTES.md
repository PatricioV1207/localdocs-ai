# LocalDocs AI v0.3.5

LocalDocs AI v0.3.5 is a quality and contributor-readiness release for the
local-first Streamlit MVP.

## Highlights

- Deterministic quality evaluation for cited QA, summaries, study questions,
  flashcards, and source selection.
- Stronger protection against unsupported cross-chunk relationships.
- Better filtering of legal, index, commercial, and broken PDF text.
- Safer handling of mixed technical content and PDF footer noise.
- Complete-clause extraction for long answers and flashcards.
- Clearer contributor workflow, CI gates, demo materials, and repository
  templates.

## Local-First Contract

- The application remains useful without `OPENAI_API_KEY`.
- TF-IDF search, extractive QA, summaries, and study tools run locally.
- Every successful document answer includes source references.
- Optional OpenAI generation remains disabled by default.

## Validation

The release gate consists of:

```bash
OPENAI_API_KEY="" python -m pytest
python -m compileall -q app.py localdocs tests scripts
OPENAI_API_KEY="" python scripts/run_quality_eval.py
```

GitHub Actions runs the same gates on Python 3.11 and 3.12.

## Known Limitations

- Scanned PDFs require OCR and are not supported.
- Search is keyword-based TF-IDF rather than semantic retrieval.
- English and Spanish receive the strongest heuristic coverage.
- Streamlit state is temporary.
- Obsidian and Anki outputs are file exports, not live integrations.

## Upgrade Notes

No migration is required. Pull the release, reinstall `requirements.txt` if
needed, and start the app with `streamlit run app.py`.

For detailed changes across versions, see [CHANGELOG.md](CHANGELOG.md).
