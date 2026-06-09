# LocalDocs AI v0.4.0

LocalDocs AI v0.4.0 adds an optional semantic-search foundation while preserving
the small, local-first Streamlit MVP.

## Highlights

- TF-IDF remains the dependency-light default.
- Optional Sentence Transformers embeddings enable semantic retrieval.
- Hybrid mode combines lexical and semantic similarity with a configurable weight.
- Embedding failures fall back automatically to TF-IDF.
- Tests and deterministic quality fixtures use fake embeddings and need no model.
- Local structural detection recognizes five broad document types.
- Study questions and flashcards adapt to objectives, procedures, findings,
  obligations, definitions, and other common section roles.
- General fixtures exercise unrelated academic, operational, research,
  contractual, and community content.

## Local-First Contract

- The application remains useful without `OPENAI_API_KEY`.
- TF-IDF search, optional embeddings, extractive QA, summaries, and study tools
  run locally.
- Every successful document answer includes source references.
- Optional OpenAI generation remains disabled by default.

## Validation

The release gate consists of:

```bash
python scripts/validate.py full
```

This profile runs pytest, compileall, and every deterministic quality fixture.
GitHub Actions runs the equivalent gates on Python 3.11 and 3.12.

Final v0.4.0 verification results are recorded in `PROGRESS.md`.

## Known Limitations

- Scanned PDFs require OCR and are not supported.
- Semantic search requires the optional dependency and a downloaded or local model.
- Embeddings are kept in memory and rebuilt when documents are processed.
- No persistent vector database is included.
- Document classification is heuristic; mixed documents may use the generic profile.
- English and Spanish receive the strongest heuristic coverage.
- Streamlit state is temporary.
- Obsidian and Anki outputs are file exports, not live integrations.

## Upgrade Notes

No migration is required. Existing installations continue to use TF-IDF.
Install `requirements-embeddings.txt` only when semantic or hybrid retrieval is
wanted, then start the app with `streamlit run app.py`.

For detailed changes across versions, see [CHANGELOG.md](CHANGELOG.md).
