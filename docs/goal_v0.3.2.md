Fix LocalDocs AI v0.3.1 issues and release as v0.3.2.

Continue from the existing codebase. Do not rebuild the project and do not add v0.4 features.

There are two main problems to fix:

1. App quality problem:
The app still generates poor extractive answers, summaries, study questions, and flashcards. It produces weak questions such as:
- "¿Qué es para?"
- "¿Qué es únicamente?"
- "¿Qué es Weber?"
- "¿Cuál es la función de didáctico?"

This is not acceptable. The app should generate questions from meaningful concepts, not random words.

2. CI problem:
GitHub Actions tests are failing on Python 3.11 and 3.12 even though local tests passed. Fix the workflow/tests/dependencies so CI passes.

Specific tasks:

A. Fix question input behavior
- The question input must start empty.
- Use Streamlit placeholder text instead of value="Your question".
- If the question is empty, too short, or equals placeholder-like text, do not run QA.
- Clear stale answer/results from session state when an invalid question is submitted.
- Add tests for invalid question behavior if possible.

B. Improve OpenAI fallback behavior
- If OPENAI_API_KEY exists but the API returns insufficient_quota, rate limit, authentication, or billing errors, silently fall back to local extractive mode.
- Do not show raw Python/API error payloads in the main UI.
- Show a friendly message such as:
  "OpenAI generation is unavailable, so LocalDocs used local extractive mode."
- Add config option or respect existing config to disable OpenAI by default if desired.
- Tests must not require an OpenAI API key.
- Ensure GitHub Actions never needs OPENAI_API_KEY.

C. Improve study question generation
- Stop generating questions from single weak words.
- Expand Spanish stopwords and weak terms, including:
  para, por, con, una, únicamente, estudiante, estudiantes, didáctico, didácticos, manual, ejercicio, ejercicios, soluciones, referencia, autores, Weber, Festo, Didactic, página, contenido.
- Prefer multi-word technical concepts.
- Examples of good concepts:
  seguridad en sistemas neumáticos
  parada de emergencia
  evaluación de riesgos
  plataforma elevadora
  aire comprimido
  relé de seguridad
  sensores de presión
  circuitos neumáticos
  circuitos eléctricos de seguridad
  válvula antirretorno
  unidad de relés de seguridad
- Avoid duplicate questions.
- Avoid questions where the target concept is one generic word.
- Add tests that explicitly reject examples like "¿Qué es para?", "¿Qué es Weber?", "¿Qué es únicamente?", and "¿Cuál es la función de didáctico?".

D. Improve flashcards
- Do not create flashcards from generic or weak terms.
- Prefer meaningful technical phrases and complete informative sentences.
- Include source references.
- Avoid duplicates.
- Add tests for weak-term rejection and duplicate filtering.

E. Improve summaries
- Summaries should not prioritize cover pages, copyright, reference metadata, table of contents, or publisher information.
- Prefer introduction, objectives, safety instructions, components, exercises, and technical sections.
- For Spanish technical documents, create a concise extractive summary in Spanish.
- Add tests to ensure copyright/front matter is not selected when better content exists.

F. Improve local QA
- If the user asks a real question, answer with concise extracted evidence, not just a dump of chunks.
- If the user question is vague or placeholder-like, block it.
- Keep citations.
- Show relevant chunks only inside an expander.
- Add tests for real question, placeholder question, and weak evidence.

G. Fix GitHub Actions
- Inspect the failing CI behavior.
- Reproduce CI locally as much as possible using Python 3.11 and 3.12 assumptions.
- Ensure requirements.txt includes all dependencies needed by tests.
- Ensure tests do not depend on local files that are not committed.
- Ensure tests do not depend on OPENAI_API_KEY.
- Update .github/workflows/tests.yml only if needed.
- The GitHub workflow should install dependencies and run pytest successfully on Python 3.11 and 3.12.

H. Documentation
- Update CHANGELOG.md with v0.3.2.
- Update README.md if behavior changed.
- Mention that OpenAI API billing is separate from ChatGPT and local mode works without an API key.

Validation:
- Run pytest.
- Run compileall.
- If possible, run tests with Python 3.11 and/or 3.12.
- Confirm Streamlit starts.
- Confirm "Your question" does not produce an answer.
- Confirm generated study questions are based on meaningful technical concepts.

Do not add:
- vector databases
- embeddings
- OCR
- LangChain
- LlamaIndex
- auth
- cloud sync
- desktop app
- v0.4 features

At the end, summarize:
- what was fixed
- tests run
- whether CI should pass
- how to manually verify with a Spanish PDF