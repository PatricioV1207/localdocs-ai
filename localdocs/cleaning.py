"""Text cleaning and quality filters for local extractive workflows."""

from __future__ import annotations

import re
from collections import Counter

from localdocs.models import DocumentChunk

LOW_VALUE_PATTERNS = [
    r"\ball rights reserved\b",
    r"\bcopyright\b",
    r"\bisbn\b",
    r"\btable of contents\b",
    r"\bcontents\b",
    r"\b[ií]ndice\b",
    r"\breferences\b",
    r"\bbibliography\b",
    r"\bpublisher\b",
    r"\bpublished by\b",
    r"\bwww\.",
    r"\bdoi\b",
    r"\binformaci[oó]n legal\b",
    r"\baviso legal\b",
    r"\bcondiciones marco\b",
    r"\bdatos de contacto\b",
    r"\btel[eé]fono\b",
    r"\bdirecci[oó]n\b",
    r"\bproductos?\b",
    r"\bmarketing\b",
]

WEAK_TERMS = {
    "about",
    "also",
    "author",
    "authors",
    "autor",
    "autores",
    "actualizado",
    "antes",
    "aplicaciones",
    "aplicación",
    "canal",
    "cat",
    "ciente",
    "chapter",
    "como",
    "cómo",
    "con",
    "componente",
    "componentes",
    "condiciones",
    "contacto",
    "content",
    "contenido",
    "contenidos",
    "contents",
    "copyright",
    "cual",
    "cuál",
    "cuando",
    "cuándo",
    "datos",
    "didactic",
    "didáctico",
    "didácticos",
    "dirección",
    "document",
    "documents",
    "documento",
    "documentos",
    "donde",
    "dónde",
    "edition",
    "durante",
    "ello",
    "ejercicio",
    "ejercicios",
    "equipo",
    "equipos",
    "estaría",
    "estudiante",
    "estudiantes",
    "festo",
    "figure",
    "figura",
    "file",
    "files",
    "folder",
    "folders",
    "from",
    "function",
    "funcion",
    "función",
    "guide",
    "important",
    "importancia",
    "importante",
    "implementación",
    "información",
    "igualada",
    "legal",
    "lleida",
    "localdocs",
    "manresa",
    "marco",
    "mostrados",
    "muestra",
    "muestras",
    "note",
    "notes",
    "observar",
    "page",
    "pages",
    "manual",
    "measure",
    "measures",
    "medida",
    "medidas",
    "pagina",
    "paginas",
    "página",
    "páginas",
    "para",
    "permitido",
    "por",
    "press",
    "presentan",
    "producto",
    "productos",
    "publisher",
    "publishing",
    "question",
    "questions",
    "que",
    "qué",
    "reference",
    "references",
    "referencia",
    "referencias",
    "review",
    "ripoll",
    "rights",
    "section",
    "smc",
    "solamente",
    "solution",
    "solución",
    "solutions",
    "soluciones",
    "solo",
    "sólo",
    "source",
    "student",
    "students",
    "table",
    "tabla",
    "tecnical",
    "teléfono",
    "text",
    "this",
    "todo",
    "una",
    "unas",
    "unicamente",
    "uno",
    "unos",
    "usuario",
    "usuarios",
    "únicamente",
    "weber",
    "www",
    "with",
}

CONCEPT_CONNECTORS = {
    "and",
    "de",
    "del",
    "e",
    "en",
    "in",
    "la",
    "las",
    "los",
    "of",
    "y",
}

CONCEPT_BOUNDARIES = {
    "allows",
    "alimenta",
    "alimentan",
    "asegura",
    "aseguran",
    "can",
    "closes",
    "conecta",
    "conectan",
    "connects",
    "control",
    "controla",
    "controlan",
    "controls",
    "convert",
    "converts",
    "convierte",
    "convierten",
    "create",
    "created",
    "creates",
    "debe",
    "deben",
    "desconecta",
    "desconectan",
    "detecta",
    "detectan",
    "detects",
    "detiene",
    "detienen",
    "ensure",
    "ensures",
    "evita",
    "evitan",
    "exporta",
    "exportan",
    "exports",
    "feeds",
    "generate",
    "generated",
    "generates",
    "genera",
    "generan",
    "helps",
    "include",
    "includes",
    "incluye",
    "incluyen",
    "into",
    "mejora",
    "mejoran",
    "monitors",
    "moves",
    "must",
    "opens",
    "permite",
    "permiten",
    "prevents",
    "protege",
    "protegen",
    "provides",
    "puede",
    "pueden",
    "recomienda",
    "recomiendan",
    "reduce",
    "reducen",
    "regula",
    "regulan",
    "regulate",
    "regulates",
    "requires",
    "requiere",
    "requieren",
    "routes",
    "should",
    "stabilizes",
    "stops",
    "supervisa",
    "supervisan",
    "supervises",
    "supports",
    "turn",
    "turns",
    "use",
    "used",
    "uses",
    "utiliza",
    "utilizan",
}

TECHNICAL_HINTS = {
    "actuador",
    "actuadores",
    "actuator",
    "actuators",
    "air",
    "aire",
    "anki",
    "antirretorno",
    "categoría",
    "categoria",
    "circuit",
    "circuits",
    "circuito",
    "circuitos",
    "chunking",
    "compressed",
    "comprimido",
    "control",
    "descarga",
    "eléctrica",
    "eléctrico",
    "eléctricos",
    "elevadora",
    "emergencia",
    "evaluación",
    "evacuación",
    "iso",
    "nivel",
    "neumática",
    "neumático",
    "neumáticos",
    "obsidian",
    "pneumatic",
    "plataforma",
    "parada",
    "pressure",
    "prestaciones",
    "presión",
    "prevención",
    "relé",
    "relés",
    "retrieval",
    "riesgo",
    "riesgos",
    "reducción",
    "residual",
    "safety",
    "search",
    "seguridad",
    "sensor",
    "sensores",
    "sistema",
    "sistemas",
    "system",
    "systems",
    "técnica",
    "unidad",
    "vault",
    "base",
    "knowledge",
    "flashcards",
    "searchable",
    "strategies",
    "válvula",
    "válvulas",
    "valve",
    "valves",
}

PREFERRED_SECTION_PATTERNS = [
    r"\bintroduction\b",
    r"\boverview\b",
    r"\bobjectives?\b",
    r"\bsafety\b",
    r"\bcomponents?\b",
    r"\bexercises?\b",
    r"\btechnical\b",
    r"\bintroducci[oó]n\b",
    r"\bobjetivos?\b",
    r"\bseguridad\b",
    r"\bcomponentes?\b",
    r"\bejercicios?\b",
    r"\bt[eé]cnic[oa]s?\b",
    r"\bfunciones de seguridad t[ií]picas\b",
    r"\bdescarga segura del sistema\b",
    r"\bdescarga segura del actuador\b",
    r"\bprevenci[oó]n de arranque inesperado\b",
    r"\bcircuitos neum[aá]ticos\b",
    r"\biso\s*13849\b",
    r"\bdescripci[oó]n del circuito\b",
    r"\bevaluaci[oó]n de riesgos\b",
    r"\breducci[oó]n de riesgos\b",
    r"\bniveles? de prestaciones\b",
    r"\bcategor[ií]a\s*[134]?\b",
]

SHORT_TECHNICAL_TERMS = {"air", "api", "gas", "iso", "oil", "pdf", "sql"}

SPANISH_HINTS = {
    "el",
    "la",
    "los",
    "las",
    "que",
    "para",
    "por",
    "con",
    "una",
    "medidas",
    "funcion",
    "función",
    "seguridad",
    "sistema",
    "recomiendan",
}


def clean_text(text: str, repeated_line_keys: set[str] | None = None) -> str:
    """Normalize text and remove obvious front-matter/noise lines."""

    repeated_line_keys = repeated_line_keys or set()
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"_{3,}", " ", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)

    raw_lines = [line.strip() for line in normalized.split("\n")]
    line_counts = Counter(_line_key(line) for line in raw_lines if _line_key(line))

    cleaned_lines: list[str] = []
    for line in raw_lines:
        key = _line_key(line)
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
        if _is_noise_line(line, line_counts.get(key, 0), key in repeated_line_keys):
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def is_low_value_text(text: str) -> bool:
    """Return True when text is mostly metadata, TOC, page numbers, or legal noise."""

    compact = " ".join(text.split())
    if not compact:
        return True

    lower = compact.lower()
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", lower)
    if len(words) < 6:
        return True
    if re.match(r"^(?:table of contents|contents|[ií]ndice)\b", lower):
        return True

    pattern_hits = sum(1 for pattern in LOW_VALUE_PATTERNS if re.search(pattern, lower))
    preferred_hits = sum(1 for pattern in PREFERRED_SECTION_PATTERNS if re.search(pattern, lower))
    if pattern_hits >= 2 and preferred_hits == 0:
        return True

    contact_hits = len(
        re.findall(r"(?:https?://|www\.|[\w.+-]+@[\w.-]+\.\w+|\+?\d[\d\s().-]{7,}\d)", lower)
    )
    if contact_hits >= 2 and preferred_hits == 0:
        return True

    numeric_tokens = sum(1 for word in words if word.isdigit() or re.fullmatch(r"[ivxlcdm]+", word))
    if numeric_tokens / max(len(words), 1) > 0.45:
        return True

    if _looks_like_toc(text.lower()):
        return True

    unique_alpha = {word for word in words if any(char.isalpha() for char in word)}
    if len(unique_alpha) <= 3 and len(words) > 10:
        return True

    weak_count = sum(1 for word in words if word in WEAK_TERMS)
    informative_count = sum(1 for word in words if _is_informative_term(word))
    if weak_count >= 3 and weak_count / len(words) >= 0.45 and informative_count < 3:
        return True

    if re.search(r"\bciente\s+volumen\b|\bseguridad\s+s[oó]lo\s+est[aá]\s+permitido\b", lower):
        return True

    return False


def chunk_quality_score(chunk: DocumentChunk) -> float:
    """Score chunks for summaries, study questions, and flashcards."""

    text = chunk.text.strip()
    if is_low_value_text(text):
        return -1.0

    words = re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9-]{2,}", text)
    sentences = split_sentences(text)
    headings = len([line for line in text.splitlines() if line.strip().startswith("#")])
    technical_terms = sum(1 for word in words if _is_informative_term(word))

    score = min(len(words) / 60, 3.0)
    score += min(len(sentences), 4) * 0.4
    score += min(technical_terms, 12) * 0.15
    score += min(headings, 3) * 0.3
    score += sum(2.0 for pattern in PREFERRED_SECTION_PATTERNS if re.search(pattern, text.lower()))
    score -= sum(1.5 for pattern in LOW_VALUE_PATTERNS if re.search(pattern, text.lower()))
    if chunk.page_number in {1, 2} and not any(
        re.search(pattern, text.lower()) for pattern in PREFERRED_SECTION_PATTERNS
    ):
        score -= 0.75
    return score


def informative_chunks(chunks: list[DocumentChunk], limit: int | None = None) -> list[DocumentChunk]:
    """Return chunks ordered by usefulness, with noisy chunks used only as fallback."""

    scored = sorted(
        ((chunk_quality_score(chunk), index, chunk) for index, chunk in enumerate(chunks)),
        key=lambda item: (-item[0], item[1]),
    )
    useful = [chunk for score, _index, chunk in scored if score >= 0]
    selected = useful if useful else [chunk for _score, _index, chunk in scored]
    if limit is not None:
        return selected[:limit]
    return selected


def split_sentences(text: str) -> list[str]:
    compact = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
    compact = " ".join(compact.split())
    if not compact:
        return []
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?¿¡])\s+", compact) if sentence.strip()]


def best_sentences(text: str, query: str = "", limit: int = 2) -> list[str]:
    sentences = split_sentences(text)
    if not sentences:
        return []

    query_terms = informative_terms(query)
    ranked = sorted(
        sentences,
        key=lambda sentence: sentence_quality_score(sentence, query_terms),
        reverse=True,
    )
    useful = [sentence for sentence in ranked if sentence_quality_score(sentence, query_terms) >= 0]
    if useful:
        ranked = useful
    return ranked[:limit]


def sentence_quality_score(sentence: str, query_terms: set[str] | None = None) -> float:
    """Score a sentence for extractive answers and study content."""

    compact = " ".join(sentence.split())
    lower = compact.lower()
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", lower)
    if len(words) < 4:
        return -3.0
    if any(re.search(pattern, lower) for pattern in LOW_VALUE_PATTERNS):
        return -4.0
    if re.search(r"\bciente\b|\bwww\b|https?://|@\w+|\+?\d[\d\s().-]{7,}\d", lower):
        return -4.0

    terms = informative_terms(compact)
    overlap = len((query_terms or set()) & terms)
    score = overlap * 3.0 + min(len(terms), 12) * 0.2
    if re.search(
        r"\b(se define como|es una funci[oó]n|consiste en|tiene como funci[oó]n|"
        r"previene|evita|reduce|descarga|bloquea|garantiza)\b",
        lower,
    ):
        score += 2.0
    if any(re.search(pattern, lower) for pattern in PREFERRED_SECTION_PATTERNS):
        score += 1.5
    if compact[-1:] in ".!?":
        score += 0.25
    return score


def informative_terms(text: str) -> set[str]:
    terms: set[str] = set()
    for raw_term in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9-]{2,}", text):
        term = raw_term.lower()
        if _is_informative_term(term):
            terms.add(term)
    return terms


def best_concept(text: str) -> str:
    from localdocs.concepts import extract_concepts

    concepts = extract_concepts(text, limit=1)
    return concepts[0] if concepts else ""


def first_heading(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading and not is_weak_concept(heading):
                return heading

    for line in lines[:8]:
        words = re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9-]*", line)
        if 2 <= len(words) <= 8 and not re.search(r"[.!?;:]$", line) and not is_weak_concept(line):
            return line
    return ""


def is_weak_concept(value: str) -> bool:
    compact = " ".join(value.split()).strip(" .:-")
    if not compact:
        return True
    lower = compact.lower()
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", lower)
    if not words:
        return True
    if re.fullmatch(
        r"(?:iso\s*\d+(?:-\d+)?|categor[ií]a\s*[134]|v[aá]lvula\s*\d+[a-z]\d+)",
        lower,
    ):
        return False
    if any(word in WEAK_TERMS and word not in CONCEPT_CONNECTORS for word in words):
        return True
    if all(word in WEAK_TERMS or re.fullmatch(r"[ivxlcdm]+|\d+", word) for word in words):
        return True
    informative = [word for word in words if _is_informative_term(word)]
    return len(informative) < 2


def appears_spanish(text: str) -> bool:
    terms = {term.lower() for term in re.findall(r"[A-Za-zÀ-ÿ]+", text)}
    accented = bool(re.search(r"[áéíóúñÁÉÍÓÚÑ¿¡]", text))
    return accented or len(terms & SPANISH_HINTS) >= 3


def is_valid_question(question: str) -> bool:
    stripped = " ".join(question.split())
    if len(stripped) < 8:
        return False
    normalized = stripped.lower().strip(" .?!¿¡:")
    if normalized in {
        "your question",
        "your question here",
        "question",
        "ask a question",
        "enter your question",
        "tu pregunta",
        "escribe tu pregunta",
        "what do these documents say about local search",
    }:
        return False
    terms = informative_terms(stripped)
    return len(terms) >= 1


def invalid_question_message() -> str:
    return "Enter a real question with enough detail before asking."


def repeated_line_keys(texts: list[str], min_count: int = 2) -> set[str]:
    """Find repeated short line keys across pages or blocks."""

    counts: Counter[str] = Counter()
    for text in texts:
        seen_in_text: set[str] = set()
        for line in text.splitlines():
            key = _line_key(line)
            if key and len(key) <= 90:
                seen_in_text.add(key)
        counts.update(seen_in_text)
    return {key for key, count in counts.items() if count >= min_count}


def _line_key(line: str) -> str:
    compact = re.sub(r"\d+", "#", line.lower())
    return re.sub(r"\s+", " ", compact).strip()


def _is_noise_line(line: str, repeated_count: int, repeated_across_blocks: bool = False) -> bool:
    lower = line.lower().strip()
    if not lower:
        return False
    if repeated_across_blocks and len(lower) <= 90:
        return True
    if repeated_count >= 3 and len(lower) <= 90:
        return True
    if re.fullmatch(r"[-–—_ ]*\d+[-–—_ ]*", lower):
        return True
    if re.fullmatch(r"[ivxlcdm]+", lower):
        return True
    if re.fullmatch(r"[A-Z0-9][A-Z0-9_.-]{5,}", line.strip()) and len(line.split()) <= 2:
        return True
    if sum(1 for char in line if char == "_") >= 4:
        return True
    if any(re.search(pattern, lower) for pattern in LOW_VALUE_PATTERNS):
        return True
    return False


def _looks_like_toc(lower_text: str) -> bool:
    toc_lines = 0
    for line in lower_text.splitlines():
        if re.search(r"\.{3,}\s*\d+$", line) or re.search(r"\bchapter\s+\d+\b.*\d+$", line):
            toc_lines += 1
    return toc_lines >= 2


def _is_informative_term(term: str) -> bool:
    lower = term.lower().strip(" .,:;!?()[]{}")
    if not lower or lower in WEAK_TERMS:
        return False
    if len(lower) < 4 and lower not in SHORT_TECHNICAL_TERMS:
        return False
    if re.fullmatch(r"\d+|[ivxlcdm]+", lower):
        return False
    return True
