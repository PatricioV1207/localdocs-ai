# LocalDocs AI Roadmap

## v0.1 - Completed

- PDF, TXT, and Markdown support
- Local TF-IDF search
- Answers with source references
- Extractive fallback without an OpenAI API key
- Basic summaries
- Markdown export
- Streamlit MVP interface
- Basic tests

## v0.2 - Completed

- DOCX support
- Better UI for document status and source inspection
- Simple configuration file
- More helpful parsing and indexing errors
- More tests for parsing, QA, citations, summaries, export, and config

## v0.3 - Completed

- Obsidian export
- Anki flashcard export
- Study question generation
- Improved chunking strategies
- Study Tools UI section

## v0.3.3 - Completed

- Concept-based study questions
- Same-language Spanish flashcards
- More coherent local extractive QA for multi-concept questions
- Stronger technical-section ranking and noise rejection
- Golden Spanish pneumatic-safety regression coverage

## v0.3.4 - Completed

- Spanish grammatical validation for study questions and flashcards
- Stronger legal, index, product, contact, and marketing filtering
- Flashcard answer-to-concept relevance checks
- Final extractive QA sentence cleanup
- Lower study-tool defaults for fewer, higher-quality items

## v0.3.5 - Completed

- Deterministic quality evaluation for QA, summaries, study tools, and source
  selection
- Stronger rejection of unsupported cross-chunk relationships
- Complete-clause handling for long extractive outputs
- Better treatment of low-value-only documents and mixed PDF footer noise
- Open-source presentation, contribution, security, and demo materials

## v0.4 - Completed

v0.4 establishes optional semantic retrieval without changing the local-first
foundation.

- Optional local Sentence Transformers embeddings
- Semantic retrieval
- Hybrid TF-IDF and semantic ranking
- Automatic TF-IDF fallback
- Deterministic tests with fake embeddings
- General document-type and section-role detection
- Structure-aware study questions and flashcards
- General multidomain evaluation fixtures

Not included in v0.4:

- Authentication or user accounts
- Cloud sync
- OCR
- LangChain, Chroma, FAISS, or another vector database
- Desktop or mobile packaging

## v0.5 - Planned

- Research comparison mode
- Richer review workflows for study questions and flashcards
- Optional persistence for document indexes, scoped before implementation

## v1.0

- Stable Python API
- Plugin system
- More document formats
- Desktop packaging
