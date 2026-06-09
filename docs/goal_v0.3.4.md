# LocalDocs AI v0.3.4 Goal

## Version objective

Fix the remaining LocalDocs AI v0.3.3 quality issues and release the result as v0.3.4.

Continue from the existing codebase. Do not rebuild the project from scratch. Do not add v0.4 features.

This release must focus on grammar quality, answer relevance, source quality, and better filtering of bad study/flashcard outputs.

## Main problem

v0.3.3 improved concept extraction, but the app still produces outputs that are not ready for a polished open-source demo.

Examples of remaining bad outputs:

```txt
¿Qué es el esta categoría?
¿Cuál es la función de el monitorización de presión segura?
¿Cuál es la función de el unidades de tratamiento de aire?
¿Cuál es la función de la presión residual?
Respuesta: – En el lado seguro con SMC 3 – Guía básica de seguridad...
¿Cuál es la función de la descarga segura del sistema?
Respuesta: Circuitos neumáticos ISO 13849 Función de seguridad...
```

Problems:

- Some questions are grammatically wrong.
- Some answers come from the table of contents, cover pages, legal pages, product pages, or tables.
- Some flashcard answers do not answer the question.
- Some QA answers still include broken fragments.
- The app still prioritizes low-value sections such as index, legal information, contact details, product listings, and conditions sections when better technical content exists.

## Scope

This is a focused quality bugfix release.

Do not add:

- Vector databases
- Embeddings
- OCR
- LangChain
- LlamaIndex
- Authentication
- Cloud sync
- Desktop app
- Mobile app
- v0.4 features

Preserve existing features:

- PDF, DOCX, TXT, and Markdown parsing
- Chunking strategies
- TF-IDF search
- Local extractive QA
- Optional OpenAI fallback behavior
- Summaries
- Study questions
- Flashcards
- Obsidian export
- Anki TSV export
- Configuration
- Tests
- GitHub Actions

## A. Fix grammar quality in generated questions

### Requirements

Generated Spanish questions must not contain malformed phrases such as:

```txt
¿Qué es el esta categoría?
¿Cuál es la función de el monitorización de presión segura?
¿Cuál es la función de el unidades de tratamiento de aire?
```

Add a grammar/quality validation step before a study question or flashcard is accepted.

Reject generated questions containing patterns such as:

```txt
de el
de la el
de el la
el esta
la este
el monitorización
el unidades
el descarga
el evacuación
el prevención
la sistema
la circuito
la actuador
```

Reject questions where the target concept starts with weak determiners or fragments:

```txt
el esta
la esta
el este
la este
este categoría
esta categoría
de el
de la
de los
de las
```

Normalize articles when possible:

```txt
de el -> del
a el -> al
```

But do not rely only on normalization. If the result is still unnatural, reject it.

### Tests

Add tests to ensure these questions are never generated:

```txt
¿Qué es el esta categoría?
¿Cuál es la función de el monitorización de presión segura?
¿Cuál es la función de el unidades de tratamiento de aire?
¿Cuál es la función de el esta categoría?
¿Qué es la sistema?
¿Qué es la circuito?
```

## B. Improve concept validation

### Requirements

A concept should be accepted only if it is useful and complete.

Reject concepts that:

- Start with an article followed by a demonstrative, such as `el esta`, `la este`, `los estos`.
- Are mostly legal/commercial text.
- Are only a generic phrase such as `esta categoría`, `el sistema`, `los circuitos`, `la norma`, unless expanded with a meaningful qualifier.
- Are table fragments.
- Are page/index fragments.
- Are product catalog fragments.
- Are too vague to be studied by themselves.

Prefer concepts with technical specificity:

```txt
descarga segura del actuador
prevención de arranque inesperado
descarga segura del sistema
parada segura
velocidad reducida segura
mantenimiento seguro
monitorización de presión segura
posición segura
evaluación de riesgos
reducción de riesgos
nivel de prestaciones requerido
categoría 1
categoría 3
categoría 4
válvula relacionada con la seguridad 1V1
válvula antirretorno
presión residual
aire comprimido
ISO 13849
ISO 12100
```

### Tests

Create tests for concept acceptance and rejection.

Accepted examples:

```txt
descarga segura del actuador
prevención de arranque inesperado
monitorización de presión segura
válvula relacionada con la seguridad 1V1
nivel de prestaciones requerido
```

Rejected examples:

```txt
el esta categoría
esta categoría
seguridad sólo está permitido
circuitos mostrados presentan aplicaciones de muestra
observación todo ello durante la implementación
presión residual índice
```

## C. Better source section scoring

### Problem

The app still picks chunks from low-value pages:

- Cover page
- Index/table of contents
- Legal information
- Product catalog pages
- Contact information
- Conditions pages
- Marketing pages

### Requirements

Improve source ranking for summaries, flashcards, and study questions.

Strongly deprioritize chunks from sections/pages containing:

```txt
Índice
Información legal
Condiciones marco
Productos SMC
Componentes adecuados para su aplicación
Expertise – Passion – Automation
En el lado seguro con SMC
www.tecnical.cat
MANRESA
LLEIDA
IGUALADA
RIPOLL
```

Do not use these chunks for study questions or flashcards unless no better technical content exists.

Prefer chunks from sections/pages containing:

```txt
Funciones de seguridad típicas en neumática
Descarga segura del sistema
Descarga segura del actuador
Prevención de arranque inesperado
Parada segura
Velocidad reducida segura
Mantenimiento seguro
Monitorización de presión segura
Posición segura
Circuitos neumáticos ISO 13849
Descripción del circuito
Evaluación de riesgos
Reducción de riesgos
Nivel de prestaciones requerido
Categoría
```

### Tests

Create tests with high-value and low-value chunks.

Ensure study/flashcards prefer high-value chunks even if low-value chunks contain keyword overlap.

## D. Improve flashcard answer relevance

### Problem

Some flashcards ask about one concept but answer with an unrelated index/table/legal fragment.

Example:

```txt
Pregunta: ¿Cuál es la función de la presión residual?
Respuesta: – En el lado seguro con SMC 3 – Guía básica...
```

### Requirements

Before accepting a flashcard, validate that the answer is related to the concept.

A flashcard should be rejected if:

- The answer does not contain the concept or meaningful related terms.
- The answer is mostly table of contents text.
- The answer is mostly legal/commercial/product/contact text.
- The answer is a list of page numbers.
- The answer is only a table row fragment.
- The answer is too short or too broken.
- The answer starts with a section/page number artifact such as `25Circuitos...`.

For "función de X" flashcards, the answer should include one of:

```txt
se define como
proporciona
garantiza
previene
lleva a cabo
permite
reduce
evacua
libera
bloquea
conmuta
controla
monitoriza
```

If no relevant answer can be found, do not generate that flashcard.

### Tests

Add tests that reject flashcards where:

- Question is about presión residual but answer is an index.
- Question is about descarga segura del sistema but answer is a table of pages.
- Question is about ISO 12100 but answer is legal disclaimer text.
- Question is about circuitos neumáticos but answer is cover page/marketing text.

## E. Improve local extractive QA synthesis

### Problem

The QA answer still sometimes includes broken text such as:

```txt
En el circuito descrito, rango de descarga segura del Funciones de seguridad típicas...
```

### Requirements

Local QA should never include sentence fragments that look like section-title collisions.

Add final answer cleanup:

- Remove fragments that combine unrelated headings.
- Remove fragments starting with broken phrases.
- Remove repeated section headers.
- Remove contact/legal/index fragments.
- Keep only complete sentences where possible.
- Prefer sentences with direct concept overlap.

For the question:

```txt
¿Qué es descarga segura del actuador y prevención de arranque inesperado?
```

Expected answer should be similar to:

```txt
La descarga segura del actuador es una función de seguridad que garantiza una purga segura de los actuadores neumáticos. Si las cámaras a presión de un actuador se descargan a la vez, la fuerza o el par se reducen de forma segura. La prevención de arranque inesperado evita el arranque inesperado de los actuadores situados en el lado de salida mediante aislamiento de la energía. En el circuito descrito, la válvula 1V1 descarga las cámaras de presión del actuador y previene el flujo de energía neumática hacia él.
```

It is acceptable if the exact wording differs, but it must:

- Define descarga segura del actuador.
- Define prevención de arranque inesperado.
- Mention 1V1 if retrieved.
- Include citations.
- Avoid chunk dumps.
- Avoid broken heading fragments.

### Tests

Add tests for:

- Definitional Spanish QA with two concepts.
- QA output does not include known broken fragments.
- QA uses complete sentences.
- QA still cites sources.

## F. Make preview output stricter

### Requirements

Do not display generated study questions or flashcards that fail validation.

If too many items are rejected, show fewer high-quality items instead of forcing 20 bad items.

It is better to show 6 good flashcards than 20 mediocre ones.

Add UI note:

```txt
LocalDocs may show fewer items when low-quality generated items are filtered out.
```

## G. Improve defaults

### Requirements

Reduce default number of generated study questions and flashcards if needed.

Recommended defaults:

```toml
[study]
max_flashcards = 10
max_questions = 10
```

This avoids displaying many lower-quality items.

If config already has 20, update to 10 unless there is a strong reason not to.

## H. Documentation

Update:

- `CHANGELOG.md`
- `README.md`
- `docs/architecture.md`
- `docs/roadmap.md` if needed

Document:

- v0.3.4 quality improvements.
- Grammatical validation for generated questions.
- Stronger filtering of legal/index/product/contact sections.
- Fewer but higher-quality flashcards/questions.
- Remaining limitations of heuristic local generation.

## I. Validation

Before finishing, run:

```bash
python -m pytest
python -m compileall app.py localdocs tests
```

If possible, verify on Python 3.11, 3.12, and 3.13.

Confirm Streamlit starts.

## Manual verification with Spanish PDF

Use the Spanish pneumatic safety PDF.

Ask:

```txt
¿Qué es descarga segura del actuador y prevención de arranque inesperado?
```

Expected behavior:

- Clear Spanish answer.
- Defines both concepts.
- Mentions 1V1 if evidence is retrieved.
- Includes citations.
- Does not dump raw chunks.
- Does not include broken fragments like `rango de descarga segura del Funciones de seguridad típicas`.

Generate flashcards and study questions.

Good examples:

```txt
¿Qué es la descarga segura del actuador?
¿Cuál es la función de la prevención de arranque inesperado?
¿Qué diferencia existe entre descarga segura del sistema y descarga segura del actuador?
¿Cuál es la función de la válvula 1V1?
¿Qué es la parada segura?
¿Qué es la monitorización de presión segura?
```

Bad examples that must not appear:

```txt
¿Qué es el esta categoría?
¿Cuál es la función de el monitorización de presión segura?
¿Cuál es la función de el unidades de tratamiento de aire?
¿Cuál es la función de la presión residual?
Respuesta: – En el lado seguro con SMC 3 – Guía básica...
¿Cuál es la función de los circuitos neumáticos?
Respuesta: Expertise – Passion –Automation...
```

## Final response required from Codex

At the end, summarize:

- What was fixed.
- Files changed.
- Tests run.
- Whether CI should pass.
- How to manually verify with the Spanish PDF.
- Remaining limitations.
