import pytest

from localdocs.models import DocumentChunk


@pytest.fixture
def spanish_safety_chunks() -> list[DocumentChunk]:
    """Small deterministic stand-in for a Spanish pneumatic safety PDF."""

    common = {
        "file_name": "seguridad_neumatica.pdf",
        "file_path": "seguridad_neumatica.pdf",
        "file_type": "pdf",
    }
    return [
        DocumentChunk(
            text=(
                "Información legal y condiciones marco. Productos SMC Tecnical. "
                "Contacto: +34 973 000 000, info@example.com, www.example.com."
            ),
            page_number=1,
            chunk_index=1,
            **common,
        ),
        DocumentChunk(
            text=(
                "Índice. Funciones de seguridad típicas ........ 7. "
                "Descripción del circuito ........ 12. Productos ........ 18."
            ),
            page_number=2,
            chunk_index=2,
            **common,
        ),
        DocumentChunk(
            text=(
                "# Descarga segura del actuador\n"
                "La descarga segura del actuador se define como una función de seguridad que purga "
                "las cámaras de presión del actuador neumático para reducir de forma segura la fuerza o el par."
            ),
            page_number=7,
            chunk_index=3,
            **common,
        ),
        DocumentChunk(
            text=(
                "# Prevención de arranque inesperado\n"
                "La prevención de arranque inesperado es una función de seguridad que evita que vuelva "
                "a fluir energía neumática hacia el actuador cuando el sistema está en estado seguro."
            ),
            page_number=8,
            chunk_index=4,
            **common,
        ),
        DocumentChunk(
            text=(
                "# Descripción del circuito\n"
                "La válvula 1V1 descarga las cámaras de presión del actuador neumático para lograr la "
                "descarga segura del actuador y bloquea el flujo de energía neumática para contribuir "
                "a la prevención de arranque inesperado."
            ),
            page_number=12,
            chunk_index=5,
            **common,
        ),
        DocumentChunk(
            text=(
                "ciente volumen de aire disponible antes seguridad sólo está permitido observar todo "
                "ello durante la implementación circuitos mostrados presentan aplicaciones de muestra"
            ),
            page_number=13,
            chunk_index=6,
            **common,
        ),
    ]
