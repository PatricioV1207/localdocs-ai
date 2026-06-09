# LocalDocs AI Quality Standard

This document defines the deterministic quality gate for local document outputs.
It applies to local extractive QA, summaries, study questions, flashcards, and
source selection. The gate is intentionally small and strict: every checked
expectation must pass.

## Principles

1. **Grounded:** Generated content must be supported by the selected document
   chunks. Successful QA answers and every study item must include source
   citations.
2. **Relevant:** QA sentences and flashcard answers must address the requested
   concept, not merely share a generic word.
3. **Source-aware:** Technical evidence must outrank covers, indexes, legal text,
   contact details, product catalogs, marketing copy, and broken OCR.
4. **Readable:** Spanish questions must be grammatical. Answers must use complete
   sentences and must not contain page artifacts or heading collisions.
5. **Conservative:** Returning fewer high-quality items is better than filling a
   requested limit with weak content.
6. **Local and deterministic:** Quality evaluations run without an OpenAI API key,
   network access, OCR, embeddings, or nondeterministic model output.

## Hard Gates

### Local QA

- The answer includes every concept required by the expected result.
- Forbidden legal, commercial, index, OCR, and heading-collision fragments are
  absent.
- Successful answers have citations and cite only permitted chunks.
- Facts from separate chunks must not be combined into a relationship that no
  individual sentence supports.
- Requested qualifiers such as maximum, minimum, or safe must be present in the
  supporting evidence rather than inferred from a broader topic match.
- Sentences are complete and end with terminal punctuation.
- Weak or unusable evidence produces the weak-evidence response without citations.

### Study Questions

- Questions come only from permitted technical chunks when those chunks exist.
- Every item includes a citation.
- Required technical concepts appear across the generated set.
- Malformed Spanish article/determiner combinations and known bad fragments are
  absent.
- The generator may return fewer than the configured maximum.

### Summaries

- Summary sentences come only from usable document content.
- Documents containing only legal, index, contact, or commercial noise produce
  the no-summary response without citations.
- Every extractive summary citation identifies a chunk actually used.

### Flashcards

- Questions and answers come only from permitted technical chunks.
- Every card includes a citation.
- Answers contain direct or substantial concept evidence.
- Long answers end at a complete clause and never use an ellipsis created by
  character-level truncation.
- Function questions require a supported technical action.
- Index, legal, product, contact, marketing, page-number, and table fragments are
  rejected.

### Source Quality

- Chunks marked low-value in expected files must be classified as low-value.
- Chunks marked technical must remain usable.
- A technical sentence is not discarded merely because PDF extraction appends a
  separate legal or commercial footer to the same chunk.
- QA, study questions, and flashcards must not cite forbidden chunks when
  permitted technical evidence exists.

### UI State

- Processing a new document collection clears outputs derived from the previous
  collection.
- Processing files with no extractable text leaves no stale answer, source,
  summary, flashcard, or study-question output visible.

## Evaluation Data

- `evals/fixtures/*.json` contains synthetic, in-memory document chunks and QA
  retrieval scores.
- `evals/expected/*.json` contains the assertions for the matching fixture.
- Fixture and expected files share the same filename and schema version.

The fixtures contain no private documents. They are compact simulations of the
Spanish pneumatic-safety material that exposed prior quality regressions.

## Commands

```bash
python scripts/run_quality_eval.py
python -m pytest
python -m compileall app.py localdocs tests scripts
```

`run_quality_eval.py` prints one result per quality area and exits with status `1`
if any expectation fails. GitHub Actions runs this command with
`OPENAI_API_KEY` empty.

## Changing the Gate

When behavior changes intentionally:

1. Update the implementation.
2. Add or revise a fixture and its expected result.
3. Record the reason in `DECISIONS.md`.
4. Update `PROGRESS.md`.
5. Run all three validation commands.

Do not weaken an expected result only to make a regression pass.
