from localdocs.models import DocumentChunk
from localdocs.study import export_study_questions_markdown, generate_study_questions


def test_generate_study_questions_includes_sources():
    chunks = [
        DocumentChunk(
            text="# Chunking Strategies\nParagraph chunking groups nearby paragraphs.",
            file_name="guide.md",
            file_path="guide.md",
            file_type="markdown",
            chunk_index=1,
        )
    ]

    questions = generate_study_questions(chunks, max_questions=3)

    assert len(questions) == 1
    assert questions[0].question == 'What is meant by "Chunking Strategies"?'
    assert questions[0].citation.label() == "guide.md, chunk 1"


def test_export_study_questions_markdown(tmp_path):
    chunk = DocumentChunk(
        text="Pressure sensors detect unsafe pneumatic system conditions before actuator movement.",
        file_name="note.txt",
        file_path="note.txt",
        file_type="txt",
        chunk_index=1,
    )
    questions = generate_study_questions([chunk], max_questions=1)

    path = export_study_questions_markdown(questions, export_dir=tmp_path)

    content = path.read_text(encoding="utf-8")
    assert "# LocalDocs AI Study Questions" in content
    assert "Source: note.txt, chunk 1" in content


def test_study_question_does_not_treat_funciona_as_funcion():
    chunk = DocumentChunk(
        text=(
            "# Presión de servicio\n"
            "El circuito neumático funciona con una presión de servicio de 6 bar."
        ),
        file_name="manual.pdf",
        file_path="manual.pdf",
        file_type="pdf",
        chunk_index=2,
        page_number=8,
    )

    questions = generate_study_questions([chunk], max_questions=1)

    assert len(questions) == 1
    assert questions[0].question == "¿Qué es la presión de servicio?"


def test_generate_study_questions_avoids_weak_repeated_keywords():
    chunks = [
        DocumentChunk(
            text="Festo Festo Festo Page 1 Publisher Copyright.",
            file_name="manual.pdf",
            file_path="manual.pdf",
            file_type="pdf",
            chunk_index=1,
        ),
        DocumentChunk(
            text="# Pressure Regulation\nPressure regulation stabilizes airflow before a pneumatic actuator moves.",
            file_name="manual.pdf",
            file_path="manual.pdf",
            file_type="pdf",
            chunk_index=2,
        ),
        DocumentChunk(
            text="# Pressure Regulation\nPressure regulation stabilizes airflow before a pneumatic actuator moves.",
            file_name="manual.pdf",
            file_path="manual.pdf",
            file_type="pdf",
            chunk_index=3,
        ),
    ]

    questions = generate_study_questions(chunks, max_questions=5)

    assert len(questions) == 1
    assert all("Festo" not in question.question for question in questions)
    assert questions[0].citation.label() == "manual.pdf, chunk 2"


def test_generate_study_questions_uses_spanish_templates():
    chunks = [
        DocumentChunk(
            text="# Seguridad neumática\nSe recomiendan medidas de bloqueo para evitar movimientos inesperados del actuador.",
            file_name="manual_es.md",
            file_path="manual_es.md",
            file_type="markdown",
            chunk_index=1,
        )
    ]

    questions = generate_study_questions(chunks, max_questions=3)

    assert questions[0].question.startswith("¿Qué medidas se recomiendan para la seguridad neumática?")
    assert questions[0].citation.label() == "manual_es.md, chunk 1"


def test_generate_study_questions_rejects_weak_spanish_single_words():
    chunks = [
        DocumentChunk(
            text="Para únicamente el estudiante consulta el manual didáctico de Festo.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=1,
        ),
        DocumentChunk(
            text="Weber autores contenido página referencia soluciones.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=2,
        ),
        DocumentChunk(
            text="Circuitos mostrados presentan aplicaciones de muestra.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=4,
        ),
        DocumentChunk(
            text="Observar todo ello durante la implementación.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=5,
        ),
        DocumentChunk(
            text="Seguridad sólo está permitido.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=6,
        ),
        DocumentChunk(
            text="ciente volumen de aire disponible antes.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=7,
        ),
        DocumentChunk(
            text="La seguridad en sistemas neumáticos evita movimientos inesperados del actuador.",
            file_name="manual_es.pdf",
            file_path="manual_es.pdf",
            file_type="pdf",
            chunk_index=3,
        ),
    ]

    questions = generate_study_questions(chunks, max_questions=10)
    question_texts = {question.question for question in questions}

    assert "¿Qué es para?" not in question_texts
    assert "¿Qué es Weber?" not in question_texts
    assert "¿Qué es únicamente?" not in question_texts
    assert "¿Cuál es la función de didáctico?" not in question_texts
    assert "¿Cuál es la función de circuitos mostrados presentan aplicaciones de muestra?" not in question_texts
    assert "¿Qué es observar todo ello durante la implementación?" not in question_texts
    assert "¿Cuál es la función de seguridad sólo está permitido?" not in question_texts
    assert "¿Qué es ciente volumen de aire disponible antes?" not in question_texts
    assert len(questions) == 1
    assert "seguridad en sistemas neumáticos" in questions[0].question


def test_generate_study_questions_prefers_multiword_technical_concepts():
    chunks = [
        DocumentChunk(
            text="La parada de emergencia detiene inmediatamente la plataforma elevadora.",
            file_name="seguridad.pdf",
            file_path="seguridad.pdf",
            file_type="pdf",
            chunk_index=1,
        ),
        DocumentChunk(
            text="La unidad de relés de seguridad supervisa circuitos eléctricos de seguridad.",
            file_name="seguridad.pdf",
            file_path="seguridad.pdf",
            file_type="pdf",
            chunk_index=2,
        ),
    ]

    questions = generate_study_questions(chunks, max_questions=5)

    assert len(questions) == 2
    assert any("parada de emergencia" in question.question for question in questions)
    assert any("unidad de relés de seguridad" in question.question for question in questions)
    assert all(question.citation.file_name == "seguridad.pdf" for question in questions)


def test_generate_study_questions_avoids_verbs_and_unrelated_template_cues():
    chunks = [
        DocumentChunk(
            text=(
                "LocalDocs AI turns folders of notes, PDFs, and Markdown files into a private searchable "
                "knowledge base. Every answer should cite source evidence."
            ),
            file_name="guide.md",
            file_path="guide.md",
            file_type="markdown",
            chunk_index=1,
        ),
        DocumentChunk(
            text=(
                "The app uses simple TF-IDF search so retrieval remains local. "
                "Every answer should cite the source document."
            ),
            file_name="note.txt",
            file_path="note.txt",
            file_type="txt",
            chunk_index=1,
        ),
    ]

    questions = generate_study_questions(chunks, max_questions=5)
    question_texts = [question.question for question in questions]

    assert any("knowledge base" in question for question in question_texts)
    assert 'What is meant by "simple TF-IDF search"?' in question_texts
    assert all("What is turns" not in question for question in question_texts)
    assert all("recommended for simple TF-IDF search" not in question for question in question_texts)
