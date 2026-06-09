"""General document-type and section-role detection."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from localdocs.models import DocumentChunk

DOCUMENT_TYPES = {
    "academic_practice",
    "technical_manual",
    "research_paper",
    "legal_business",
    "generic",
}

SECTION_ROLES = {
    "definition",
    "objective",
    "procedure",
    "result",
    "obligation",
    "question",
    "example",
    "overview",
    "other",
}

TYPE_MARKERS = {
    "academic_practice": (
        "exercise",
        "exercises",
        "practice",
        "assignment",
        "learning objective",
        "learning objectives",
        "student",
        "worksheet",
        "quiz",
        "ejercicio",
        "ejercicios",
        "práctica",
        "actividad",
        "objetivo de aprendizaje",
        "objetivos de aprendizaje",
        "estudiante",
        "cuestionario",
    ),
    "technical_manual": (
        "installation",
        "operation",
        "maintenance",
        "procedure",
        "warning",
        "caution",
        "troubleshooting",
        "component",
        "specification",
        "step 1",
        "manual",
        "instalación",
        "operación",
        "funcionamiento",
        "mantenimiento",
        "procedimiento",
        "advertencia",
        "precaución",
        "componente",
        "especificación",
        "paso 1",
    ),
    "research_paper": (
        "abstract",
        "methodology",
        "methods",
        "participants",
        "results",
        "discussion",
        "conclusion",
        "hypothesis",
        "limitations",
        "resumen",
        "metodología",
        "métodos",
        "participantes",
        "resultados",
        "discusión",
        "conclusión",
        "hipótesis",
        "limitaciones",
    ),
    "legal_business": (
        "agreement",
        "party",
        "parties",
        "shall",
        "liability",
        "effective date",
        "termination",
        "confidential",
        "revenue",
        "market strategy",
        "business plan",
        "contrato",
        "parte",
        "partes",
        "deberá",
        "deberán",
        "responsabilidad",
        "fecha de vigencia",
        "terminación",
        "confidencial",
        "ingresos",
        "estrategia comercial",
        "plan de negocio",
    ),
}

ROLE_MARKERS = {
    "definition": (
        "is defined as",
        "refers to",
        "means ",
        "consists of",
        "se define como",
        "se refiere a",
        "significa ",
        "consiste en",
    ),
    "objective": (
        "objective",
        "learning outcome",
        "goal",
        "aim",
        "students will",
        "objetivo",
        "resultado de aprendizaje",
        "meta",
        "finalidad",
        "el estudiante podrá",
    ),
    "procedure": (
        "procedure",
        "step ",
        "first,",
        "next,",
        "then ",
        "before ",
        "after ",
        "install",
        "configure",
        "procedimiento",
        "paso ",
        "primero,",
        "después,",
        "antes de",
        "instale",
        "configure",
    ),
    "result": (
        "results",
        "we found",
        "the study found",
        "increased",
        "decreased",
        "showed that",
        "resultados",
        "se encontró",
        "el estudio encontró",
        "aumentó",
        "disminuyó",
        "mostró que",
    ),
    "obligation": (
        " shall ",
        " must ",
        " is required to ",
        " may not ",
        " agrees to ",
        " deberá ",
        " deberán ",
        " debe ",
        " se obliga a ",
        " no podrá ",
    ),
    "question": (
        "question",
        "questions",
        "answer the following",
        "explain why",
        "calculate ",
        "pregunta",
        "preguntas",
        "responda",
        "explique por qué",
        "calcule ",
    ),
    "example": (
        "example",
        "case study",
        "for instance",
        "worked example",
        "ejemplo",
        "caso práctico",
        "por ejemplo",
        "ejemplo resuelto",
    ),
    "overview": (
        "overview",
        "introduction",
        "summary",
        "scope",
        "descripción general",
        "introducción",
        "resumen",
        "alcance",
    ),
}


@dataclass(frozen=True)
class DocumentProfile:
    """Detected document type with transparent marker scores."""

    document_type: str
    scores: dict[str, int]


def detect_document_type(chunks: list[DocumentChunk]) -> DocumentProfile:
    """Classify one document collection using broad structural markers."""

    text = "\n".join(chunk.text for chunk in chunks).lower()
    scores = {
        document_type: sum(text.count(marker) for marker in markers)
        for document_type, markers in TYPE_MARKERS.items()
    }
    highest = max(scores.values(), default=0)
    if highest == 0:
        return DocumentProfile(document_type="generic", scores=scores)

    candidates = [
        document_type
        for document_type, score in scores.items()
        if score == highest
    ]
    document_type = _break_type_tie(candidates, chunks)
    return DocumentProfile(document_type=document_type, scores=scores)


def detect_document_profiles(chunks: list[DocumentChunk]) -> dict[str, DocumentProfile]:
    """Detect one profile per source document."""

    grouped: dict[str, list[DocumentChunk]] = {}
    for chunk in chunks:
        key = chunk.file_path or chunk.file_name
        grouped.setdefault(key, []).append(chunk)
    return {key: detect_document_type(items) for key, items in grouped.items()}


def detect_section_role(text: str) -> str:
    """Classify a chunk by its strongest reusable structural role."""

    compact = " ".join(text.split()).lower()
    heading = _first_heading(text).lower()
    scores = Counter()
    for role, markers in ROLE_MARKERS.items():
        for marker in markers:
            if marker.strip() in heading:
                scores[role] += 3
            scores[role] += compact.count(marker)

    if re.search(r"(?:^|\s)(?:\d+[\).]|[-*])\s+\w+", text, flags=re.MULTILINE):
        scores["procedure"] += 2
    if "?" in text or "¿" in text:
        scores["question"] += 2
    if re.search(r"\b(?:is|are|es|son)\s+(?:a|an|the|el|la|un|una)\b", compact):
        scores["definition"] += 1

    if not scores:
        return "other"
    role, score = scores.most_common(1)[0]
    return role if score > 0 else "other"


def _break_type_tie(candidates: list[str], chunks: list[DocumentChunk]) -> str:
    role_counts = Counter(detect_section_role(chunk.text) for chunk in chunks)
    preferred_roles = {
        "academic_practice": role_counts["question"] + role_counts["objective"],
        "technical_manual": role_counts["procedure"] + role_counts["definition"],
        "research_paper": role_counts["result"] + role_counts["overview"],
        "legal_business": role_counts["obligation"],
    }
    return max(candidates, key=lambda item: (preferred_roles[item], item))


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""
