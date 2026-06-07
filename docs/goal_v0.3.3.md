# LocalDocs AI v0.3.3 Goal

## Version objective

Fix the remaining LocalDocs AI v0.3.2 quality issues and release the result as v0.3.3.

Continue from the existing codebase. Do not rebuild the project from scratch. Do not add v0.4 features.

This release must focus on making study questions, flashcards, and local extractive answers coherent and useful for technical Spanish documents.

## Main problem

v0.3.2 improved cleaning and CI, but study questions and flashcards are still often incoherent.

Bad examples currently produced by the app:

```txt
Q: What is a key point about circuitos mostrados presentan aplicaciones de muestra?
Q: What is a key point about observar todo ello durante la implementación?
Q: What is a key point about canal estaría en riesgo de descarga accidental?
¿Cuál es la función de circuitos mostrados presentan aplicaciones de muestra?
¿Qué es observar todo ello durante la implementación?
¿Cuál es la función de seguridad sólo está permitido?
¿Qué es ciente volumen de aire disponible antes?
```

These are not acceptable because they are incomplete sentence fragments, weak phrases, legal/commercial content, or phrases without useful learning value.

The app should generate study outputs from meaningful technical concepts, not from arbitrary fragments.

## Scope

This is a bugfix and quality release.

Implement only v0.3.3 fixes.

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

Preserve all existing behavior:

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

## A. Make study questions concept-based

### Problem

Study questions are currently generated from random fragments such as:

```txt
observar todo ello durante la implementación
seguridad sólo está permitido
ciente volumen de aire disponible antes
```

### Requirements

Create or improve a concept extraction pipeline for study questions.

Prefer extracting concepts from:

- Headings
- Section titles
- Bold-like text when available in parsed text
- Sentences containing definitions
- Technical noun phrases
- Known technical domain terms
- Phrases near terms such as:
  - se define como
  - esta función
  - función de seguridad
  - descripción del circuito
  - nivel de prestaciones
  - categoría
  - ISO 13849
  - ISO 12100
  - evaluación de riesgos
  - reducción de riesgos

Reject concepts that are:

- Single weak words
- Sentence fragments without subject
- Legal disclaimers
- Commercial text
- Contact information
- Publisher/brand-only text
- Page numbers or document codes
- Table-of-contents fragments
- Broken OCR fragments

### Spanish weak terms

Expand the weak term list to include at least:

```txt
para, por, con, una, uno, unos, unas, únicamente, solamente,
usuario, usuarios, estudiante, estudiantes, didáctico, didácticos,
manual, ejercicio, ejercicios, soluciones, solución, referencia,
autores, autor, Weber, Festo, Didactic, SMC, Tecnical, página, paginas,
contenido, contenidos, documento, documentos, tabla, figura,
equipo, equipos, componente, componentes, datos, actualizado,
implementación, permitido, mostrados, presentan, muestra, muestras,
información, legal, condiciones, marco, observar, todo, ello,
contacto, dirección, teléfono, www, cat, manresa, lleida, igualada, ripoll
```

### Good concepts

The concept extractor should prefer useful multi-word concepts such as:

```txt
seguridad en sistemas neumáticos
descarga segura del sistema
descarga segura del actuador
prevención de arranque inesperado
parada segura
evaluación de riesgos
reducción de riesgos
plataforma elevadora
aire comprimido
presión residual
relé de seguridad
sensores de presión
circuitos neumáticos
circuitos eléctricos de seguridad
válvula antirretorno
válvula relacionada con la seguridad
unidad de relés de seguridad
técnica de seguridad
alimentación de aire comprimido
alimentación de energía eléctrica
nivel de prestaciones
categoría 1
categoría 3
categoría 4
ISO 13849
ISO 12100
```

### Study question templates

Generate Spanish questions when the document is Spanish.

Preferred templates:

```txt
¿Qué es {concepto}?
¿Cuál es la función de {concepto}?
¿Por qué es importante {concepto}?
¿Cómo contribuye {concepto} a la seguridad del sistema?
¿Qué diferencia existe entre {concepto_a} y {concepto_b}?
¿Qué condiciones deben cumplirse para {concepto}?
¿Qué riesgo ayuda a reducir {concepto}?
```

Avoid templates that produce ungrammatical questions.

Examples of good output:

```txt
¿Qué es la descarga segura del actuador?
¿Cuál es la función de la prevención de arranque inesperado?
¿Qué diferencia existe entre descarga segura del sistema y descarga segura del actuador?
¿Cómo contribuye la válvula 1V1 a la descarga segura del actuador?
¿Por qué el fabricante debe evaluar caso por caso el nivel de descarga segura?
¿Qué riesgo ayuda a reducir la evacuación de presión residual?
```

### Hard rejection tests

Add tests to ensure these are never generated:

```txt
¿Qué es para?
¿Qué es Weber?
¿Qué es únicamente?
¿Cuál es la función de didáctico?
¿Cuál es la función de circuitos mostrados presentan aplicaciones de muestra?
¿Qué es observar todo ello durante la implementación?
¿Cuál es la función de seguridad sólo está permitido?
¿Qué es ciente volumen de aire disponible antes?
```

## B. Make flashcards concept-based and same-language

### Problem

Flashcards currently use English prompts for Spanish documents:

```txt
Q: What is a key point about ...
```

They also use broken concepts and mismatched answers.

### Requirements

For Spanish documents, flashcards must be in Spanish.

Use Spanish format:

```txt
Pregunta: ¿Qué es {concepto}?
Respuesta: {respuesta breve basada en el documento}
Fuente: {source}
```

The Anki TSV fields can remain:

```txt
Question<TAB>Answer<TAB>Source
```

But the content should be Spanish when the document is Spanish.

### Flashcard generation rules

Prefer flashcards from:

- Definition sentences
- Safety function descriptions
- Circuit descriptions
- ISO/risk-reduction concepts
- Cause/effect technical explanations
- Meaningful headings with supporting text

Reject flashcards from:

- Legal disclaimers
- Contact info
- Commercial marketing text
- Source/publisher information
- Single weak terms
- Truncated phrases
- Table-of-contents entries
- Low-quality chunks

### Good examples

```txt
Pregunta: ¿Qué es la descarga segura del actuador?
Respuesta: Es una función de seguridad que garantiza la purga segura de los actuadores neumáticos.
Fuente: document.pdf, page 7, chunk X
```

```txt
Pregunta: ¿Qué es la prevención de arranque inesperado?
Respuesta: Es una función de seguridad que previene el arranque inesperado de los actuadores situados en el lado de salida mediante aislamiento de la energía.
Fuente: document.pdf, page 8, chunk X
```

```txt
Pregunta: ¿Qué función cumple la válvula 1V1 en la descarga segura del actuador?
Respuesta: La válvula 1V1 descarga las cámaras de presión del actuador neumático y previene el flujo de energía neumática hacia el actuador.
Fuente: document.pdf, page 12, chunk X
```

### Tests

Add tests for:

- Spanish flashcards use Spanish question text, not English.
- Flashcards reject weak/broken concepts.
- Flashcards include source references.
- Flashcards avoid duplicates.
- Flashcard answer is related to the question concept.
- Legal/commercial chunks are not selected when better technical chunks exist.

## C. Improve local extractive QA

### Problem

The QA answer currently retrieves relevant evidence but still reads like a chunk dump.

Example output:

```txt
Based on the strongest retrieved evidence:

Rango de descarga segura del Funciones de seguridad típicas...
El nivel de descarga segura proporcionado...
Descarga segura y prevención...
```

This is partially relevant, but not well synthesized.

### Requirements

For local extractive mode, generate a concise answer using sentence selection and light synthesis.

For definitional questions such as:

```txt
¿Qué es descarga segura del actuador y prevención de arranque inesperado?
```

The answer should:

1. Define each requested concept separately.
2. Mention how they relate in the circuit if evidence exists.
3. Keep citations.
4. Avoid dumping long chunks as the main answer.

Expected answer style:

```txt
La descarga segura del actuador es una función de seguridad que purga las cámaras de presión del actuador neumático para reducir de forma segura la fuerza o el par. La prevención de arranque inesperado evita que vuelva a fluir energía neumática hacia el actuador cuando el sistema está en estado seguro. En el circuito descrito, la válvula 1V1 descarga las cámaras de presión del actuador y bloquea el flujo de energía neumática hacia él.
```

Keep the answer extractive and grounded. Do not hallucinate.

### Implementation ideas

Improve `localdocs/qa.py` with:

- Question type detection:
  - definition question
  - comparison question
  - function question
  - list/process question
- Query concept extraction from the user question.
- Sentence selection by:
  - concept overlap
  - technical quality
  - source relevance
  - avoiding low-value chunks
- Light Spanish answer templates.

### Tests

Add tests for:

- A Spanish definitional question receives a coherent Spanish answer.
- The answer is not just a raw chunk dump.
- The answer contains citations.
- Weak evidence still triggers the weak-evidence message.
- OpenAI fallback still works if API fails.

## D. Improve ranking and filtering for study tools

### Requirements

Study tools should not prioritize:

- Page 1 cover pages
- Page 2 index/table of contents
- Legal pages
- Product/contact pages
- Marketing pages
- Chunks containing mostly phone numbers, URLs, addresses, or brands
- Chunks from sections titled:
  - Información legal
  - Condiciones marco, unless the user explicitly asks about them
  - Productos
  - Índice

However, if the entire document only contains this type of content, keep fallback behavior.

### For technical PDFs

Prefer sections titled or containing:

```txt
Funciones de seguridad típicas
Descarga segura del sistema
Descarga segura del actuador
Prevención de arranque inesperado
Circuitos neumáticos ISO 13849
Descripción del circuito
Evaluación de riesgos
Reducción de riesgos
Niveles de prestaciones
Categoría
```

### Tests

Add tests with mixed high-value and low-value chunks to ensure high-value chunks are selected first.

## E. Add golden sample tests

Create deterministic tests using small in-memory chunks that simulate the Spanish pneumatic safety PDF.

Add a test fixture with chunks containing:

1. A legal/commercial chunk.
2. A table-of-contents chunk.
3. A useful chunk defining descarga segura del actuador.
4. A useful chunk defining prevención de arranque inesperado.
5. A useful chunk describing válvula 1V1.
6. A low-quality broken OCR fragment.

Tests should ensure:

- Study questions come from chunks 3, 4, and 5.
- Flashcards come from chunks 3, 4, and 5.
- QA answers use chunks 3, 4, and 5.
- Low-quality chunks are ignored for study outputs.
- No broken questions are generated.

## F. Improve UI labels and previews

### Requirements

The UI should make clear that:

- Local mode is extractive and heuristic.
- Study questions and flashcards are generated from extracted document concepts.
- If OpenAI is unavailable, the app uses local mode.
- Relevant chunks should remain in an expander, not in the main answer.

For previews:

- Show `Pregunta:` and `Respuesta:` for Spanish flashcards.
- Show source under each item.
- Avoid displaying items that fail quality validation.

## G. Configuration updates

Add optional config settings if useful:

```toml
[quality]
prefer_language = "auto"
min_concept_words = 2
exclude_legal_sections = true
exclude_commercial_sections = true
```

Defaults should be safe and not break old configs.

## H. Documentation

Update:

- `CHANGELOG.md`
- `README.md`
- `docs/architecture.md`

Document:

- v0.3.3 quality improvements
- concept-based study question generation
- Spanish flashcard behavior
- local extractive QA limitations
- remaining limitations

## Validation

Before finishing, run:

```bash
python -m pytest
python -m compileall app.py localdocs tests
```

If possible, verify on Python 3.11, 3.12, and 3.13.

Also confirm Streamlit starts.

## Manual verification with Spanish PDF

Use a Spanish technical PDF about pneumatic safety.

Ask:

```txt
¿Qué es descarga segura del actuador y prevención de arranque inesperado?
```

Expected behavior:

- The answer defines both concepts clearly.
- It mentions 1V1 if the relevant evidence is retrieved.
- It includes citations.
- It does not dump raw chunks as the main answer.
- It does not show raw OpenAI errors.

Generate study questions and flashcards.

Expected study questions:

```txt
¿Qué es la descarga segura del actuador?
¿Cuál es la función de la prevención de arranque inesperado?
¿Qué diferencia existe entre descarga segura del sistema y descarga segura del actuador?
¿Cómo contribuye la válvula 1V1 a la descarga segura del actuador?
¿Qué riesgo ayuda a reducir la evacuación de presión residual?
```

Expected flashcards:

```txt
Pregunta: ¿Qué es la descarga segura del actuador?
Respuesta: Es una función de seguridad que garantiza la purga segura de los actuadores neumáticos.
Fuente: ...
```

Bad outputs must not appear:

```txt
What is a key point about...
¿Qué es para?
¿Qué es Weber?
¿Qué es observar todo ello durante la implementación?
¿Cuál es la función de seguridad sólo está permitido?
¿Qué es ciente volumen de aire disponible antes?
```

## Final response required from Codex

At the end, summarize:

- What was fixed.
- Files changed.
- Tests run.
- Whether CI should pass.
- How to manually verify with a Spanish PDF.
- Remaining limitations.
