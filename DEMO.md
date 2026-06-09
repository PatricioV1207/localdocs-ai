# LocalDocs AI Demo

This walkthrough presents the current v0.3.5 MVP in about three minutes using
only repository sample documents.

## Before Presenting

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
OPENAI_API_KEY="" streamlit run app.py
```

Use a clean browser window and leave **Use OpenAI if available** unchecked.

## Demo Script

1. **Set the premise**

   LocalDocs AI turns local documents into a searchable knowledge base. The
   default workflow needs no account, cloud database, or API key.

2. **Process safe sample documents**

   Click **Process sample documents**. Point out the two document names and two
   indexed chunks.

3. **Ask a grounded question**

   Enter:

   ```text
   What search does LocalDocs AI use?
   ```

   The expected answer mentions TF-IDF search. Show the local extractive mode
   caption and the `sample_note.txt, chunk 1` citation.

4. **Show reuse workflows**

   Generate summaries, flashcards, and study questions. Explain that quality
   filtering may return fewer items instead of filling a quota with weak text.

5. **Show portable outputs**

   Mention Markdown Q&A and summary export, Anki-compatible TSV, and the
   Obsidian-friendly vault. Generated exports stay local.

6. **Close with scope**

   v0.3.5 is intentionally an MVP: no accounts, cloud sync, OCR, vector
   database, or multi-user system.

## Presenter Checks

- The answer cites `sample_note.txt, chunk 1`.
- No private documents appear anywhere.
- No API key is visible or required.
- The terminal and browser contain no error messages.
- Generated exports are removed or reviewed before sharing.

## Validation Before a Release Demo

```bash
OPENAI_API_KEY="" python -m pytest
python -m compileall -q app.py localdocs tests scripts
OPENAI_API_KEY="" python scripts/run_quality_eval.py
```
