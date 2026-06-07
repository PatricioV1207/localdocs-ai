from localdocs.concepts import extract_concepts


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
