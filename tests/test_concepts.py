import pytest

from localdocs.concepts import (
    extract_concepts,
    is_valid_concept,
    is_valid_generated_question,
    normalize_generated_question,
    spanish_concept_phrase,
)


def test_extract_concepts_prefers_spanish_technical_phrases():
    text = (
        "# Técnica de seguridad\n"
        "La descarga segura del actuador y la prevención de arranque inesperado son funciones "
        "de seguridad relacionadas con ISO 13849 y la válvula 1V1."
    )

    concepts = extract_concepts(text, limit=5)

    assert "descarga segura del actuador" in [concept.lower() for concept in concepts]
    assert "prevención de arranque inesperado" in [concept.lower() for concept in concepts]
    assert "válvula 1v1" in [concept.lower() for concept in concepts]


def test_extract_concepts_rejects_legal_and_broken_fragments():
    text = (
        "Información legal. Contacto www.example.com. "
        "Observar todo ello durante la implementación. "
        "ciente volumen de aire disponible antes."
    )

    assert extract_concepts(text, limit=10) == []


@pytest.mark.parametrize(
    "concept",
    [
        "descarga segura del actuador",
        "prevención de arranque inesperado",
        "monitorización de presión segura",
        "válvula relacionada con la seguridad 1V1",
        "nivel de prestaciones requerido",
    ],
)
def test_concept_validation_accepts_specific_technical_phrases(concept):
    assert is_valid_concept(concept) is True


@pytest.mark.parametrize(
    "concept",
    [
        "el esta categoría",
        "esta categoría",
        "seguridad sólo está permitido",
        "circuitos mostrados presentan aplicaciones de muestra",
        "observación todo ello durante la implementación",
        "presión residual índice",
    ],
)
def test_concept_validation_rejects_vague_or_broken_phrases(concept):
    assert is_valid_concept(concept) is False


@pytest.mark.parametrize(
    "question",
    [
        "¿Qué es el esta categoría?",
        "¿Cuál es la función de el monitorización de presión segura?",
        "¿Cuál es la función de el unidades de tratamiento de aire?",
        "¿Cuál es la función de el esta categoría?",
        "¿Qué es la sistema?",
        "¿Qué es la circuito?",
    ],
)
def test_generated_question_validation_rejects_malformed_spanish(question):
    assert is_valid_generated_question(question) is False


def test_spanish_articles_and_safe_contractions_are_normalized():
    assert spanish_concept_phrase("monitorización de presión segura") == (
        "la monitorización de presión segura"
    )
    assert spanish_concept_phrase("unidades de tratamiento de aire") == (
        "las unidades de tratamiento de aire"
    )
    assert normalize_generated_question("¿Cuál es la función de el sistema?") == (
        "¿Cuál es la función del sistema?"
    )
