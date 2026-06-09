# Quality Evaluation Decisions

## 001 - Use Deterministic JSON Fixtures

**Decision:** Store compact synthetic document chunks in `evals/fixtures` and
assertions in matching `evals/expected` files.

**Reason:** The quality gate must run locally and in CI without private PDFs,
network access, or an API key. Separating inputs from expectations makes reviews
clearer and prevents expected behavior from being hidden in runner code.

## 002 - Treat Every Expectation as a Hard Gate

**Decision:** The runner exits with status `1` when any assertion fails.

**Reason:** A weighted score could hide a serious grounding or citation failure
behind unrelated passing checks. For this MVP, a small all-pass suite is easier
to understand and safer.

## 003 - Evaluate Public Workflows

**Decision:** The runner calls the same QA, study-question, flashcard, and source
quality functions used by the app.

**Reason:** Evaluating copied logic would allow the app and the quality gate to
drift apart.

## 004 - Inject Retrieval Scores in QA Fixtures

**Decision:** QA cases include deterministic retrieval scores.

**Reason:** This isolates answer and source-selection quality from
scikit-learn-version ranking differences while still testing the real QA
selection path. Search behavior remains covered by unit tests.

## 005 - Prefer Fewer High-Quality Study Items

**Decision:** Expected files define permitted sources and required concepts, not
an obligation to fill the configured maximum.

**Reason:** The product explicitly prefers six useful cards over twenty weak
ones. Exact item counts are asserted only when the fixture requires them.

## 006 - Require Sentence-Level Support for Relations

**Decision:** Local extractive QA must find one sentence covering most
substantive question terms before answering a relational question. Questions
that explicitly enumerate independent concepts with `and` or `y` may still
combine separately supported facts.

**Reason:** Retrieval can return one chunk about a standard and another about a
pressure value without proving that the standard requires that pressure.
Concatenating those facts creates a plausible but unsupported answer even when
each sentence is accurate on its own.

## 007 - Preserve Complete Output Clauses

**Decision:** Long extractive QA and flashcard answers may be shortened only at
a clause boundary. If no suitable boundary exists, keep the complete sentence.

**Reason:** Character-level truncation creates polished-looking fragments that
can omit a condition or outcome while still ending in punctuation.

## 008 - Evaluate Summaries Alongside Study Outputs

**Decision:** Fixtures may define summary expectations, and summary citations
participate in forbidden-source checks.

**Reason:** A local-first quality gate is incomplete if QA is grounded but
summaries can quote legal, index, or marketing-only documents.

## 009 - Preserve Technical Evidence in Mixed PDF Chunks

**Decision:** A chunk with a complete, quality-checked technical action sentence
remains usable even when a separate sentence contains a legal or commercial
footer.

**Reason:** PDF extraction frequently joins body text and footer text. Rejecting
the entire chunk loses valid evidence; downstream sentence filters can remove
the noisy sentence without discarding the technical one.
