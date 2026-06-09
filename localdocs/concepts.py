"""Deterministic technical concept extraction for study tools and local QA."""

from __future__ import annotations

import re
from dataclasses import dataclass

from localdocs.cleaning import (
    CONCEPT_BOUNDARIES,
    CONCEPT_CONNECTORS,
    TECHNICAL_HINTS,
    WEAK_TERMS,
    informative_terms,
    is_weak_concept,
    sentence_quality_score,
    split_sentences,
)


@dataclass(frozen=True)
class _Candidate:
    phrase: str
    score: float
    position: int


DOMAIN_PATTERNS: list[tuple[str, float]] = [
    (r"\bprevenci[oó]n de arranque inesperado\b", 135.0),
    (r"\bdescarga segura del actuador\b", 134.0),
    (r"\bdescarga segura del sistema\b", 133.0),
    (r"\bvelocidad reducida segura\b", 133.0),
    (r"\bmantenimiento seguro\b", 133.0),
    (r"\bmonitorizaci[oó]n de presi[oó]n segura\b", 133.0),
    (r"\bposici[oó]n segura\b", 133.0),
    (r"\bcircuitos el[eé]ctricos de seguridad\b", 132.0),
    (r"\bv[aá]lvula relacionada con la seguridad(?:\s+\d+[a-z]\d+)?\b", 141.0),
    (r"\bunidad de rel[eé]s de seguridad\b", 133.0),
    (r"\bunidades de tratamiento de aire\b", 130.0),
    (r"\balimentaci[oó]n de energ[ií]a el[eé]ctrica\b", 129.0),
    (r"\balimentaci[oó]n de aire comprimido\b", 128.0),
    (r"\bseguridad en sistemas neum[aá]ticos\b", 127.0),
    (r"\bevaluaci[oó]n de riesgos\b", 126.0),
    (r"\breducci[oó]n de riesgos\b", 125.0),
    (r"\bevacuaci[oó]n de presi[oó]n residual\b", 124.0),
    (r"\bpresi[oó]n residual\b", 123.0),
    (r"\bv[aá]lvula\s+\d+[a-z]\d+\b", 142.0),
    (r"\bv[aá]lvula antirretorno\b", 122.0),
    (r"\brel[eé] de seguridad\b", 121.0),
    (r"\bsensores? de presi[oó]n\b", 120.0),
    (r"\bcircuitos? neum[aá]ticos\b", 119.0),
    (r"\bt[eé]cnica de seguridad\b", 118.0),
    (r"\bniveles? de prestaciones(?: requerido)?\b", 117.0),
    (r"\bcategor[ií]a\s*[134]\b", 116.0),
    (r"\biso\s*13849(?:-\d+)?\b", 115.0),
    (r"\biso\s*12100\b", 114.0),
    (r"\bparada de emergencia\b", 113.0),
    (r"\bparada segura\b", 112.0),
    (r"\bplataforma elevadora\b", 111.0),
    (r"\baire comprimido\b", 110.0),
    (r"\bfunci[oó]n de seguridad\b", 105.0),
    (r"\bpressure sensors?\b", 104.0),
    (r"\bpneumatic actuators?\b", 103.0),
    (r"\bpressure regulation\b", 102.0),
    (r"\bsimple tf-idf search\b", 102.0),
    (r"\btf-idf search\b", 101.0),
    (r"\bsearchable knowledge base\b", 100.0),
    (r"\blocal search\b", 99.0),
    (r"\bchunking strategies\b", 98.0),
    (r"\banki-compatible flashcards\b", 97.0),
    (r"\bobsidian vault export\b", 96.0),
]

GENERIC_HEADINGS = {
    "descripción del circuito",
    "funciones de seguridad típicas",
    "información legal",
    "condiciones marco",
    "productos",
    "índice",
}

GENERIC_CONCEPTS = {
    "categoría",
    "circuito",
    "circuitos",
    "esta categoría",
    "este categoría",
    "norma",
    "sistema",
    "sistemas",
}

FEMININE_HEADS = {
    "alimentación",
    "categoría",
    "descarga",
    "evaluación",
    "evacuación",
    "función",
    "monitorización",
    "parada",
    "plataforma",
    "posición",
    "presión",
    "prevención",
    "reducción",
    "seguridad",
    "técnica",
    "unidad",
    "válvula",
    "velocidad",
}

PLURAL_FEMININE_HEADS = {"funciones", "unidades", "válvulas"}
PLURAL_MASCULINE_HEADS = {"actuadores", "circuitos", "niveles", "relés", "sensores", "sistemas"}

DEFINITION_MARKERS = (
    "se define como",
    "es una función de seguridad",
    "es una función",
    "es un sistema",
    "es una medida",
    "consiste en",
)


def extract_concepts(text: str, limit: int = 3) -> list[str]:
    """Extract ranked, coherent technical concepts from a text block."""

    if limit <= 0 or not text.strip():
        return []

    candidates: list[_Candidate] = []
    candidates.extend(_domain_candidates(text))
    candidates.extend(_definition_candidates(text))
    candidates.extend(_heading_candidates(text))
    candidates.extend(_bold_candidates(text))
    candidates.extend(_noun_phrase_candidates(text))

    best_by_key: dict[str, _Candidate] = {}
    for candidate in candidates:
        if _has_malformed_start(candidate.phrase):
            continue
        phrase = _clean_phrase(candidate.phrase)
        if not _valid_concept(phrase):
            continue
        normalized = concept_key(phrase)
        current = best_by_key.get(normalized)
        updated = _Candidate(phrase=phrase, score=candidate.score, position=candidate.position)
        if current is None or (updated.score, -updated.position) > (current.score, -current.position):
            best_by_key[normalized] = updated

    ranked = sorted(best_by_key.values(), key=lambda item: (-item.score, item.position, -len(item.phrase)))
    selected: list[str] = []
    selected_keys: list[str] = []
    for candidate in ranked:
        key = concept_key(candidate.phrase)
        if any(key in existing or existing in key for existing in selected_keys):
            continue
        selected.append(candidate.phrase)
        selected_keys.append(key)
        if len(selected) >= limit:
            break
    return selected


def concept_key(concept: str) -> str:
    compact = _clean_phrase(concept).lower()
    compact = re.sub(r"^(?:el|la|los|las|un|una)\s+", "", compact)
    return re.sub(r"\s+", " ", compact)


def concept_sentence(text: str, concept: str) -> str:
    """Return the strongest complete sentence that supports a concept."""

    sentences = split_sentences(text)
    if not sentences:
        return ""

    concept_terms = informative_terms(concept)

    def score(sentence: str) -> tuple[float, int]:
        exact = 8.0 if concept_key(concept) in concept_key(sentence) else 0.0
        overlap = len(concept_terms & informative_terms(sentence)) * 3.0
        return sentence_quality_score(sentence, concept_terms) + exact + overlap, -len(sentence)

    ranked = sorted(sentences, key=score, reverse=True)
    best = ranked[0]
    return best if score(best)[0] >= 0 else ""


def spanish_concept_phrase(concept: str) -> str:
    """Add a simple Spanish article when a concept does not already include one."""

    compact = _clean_phrase(concept)
    if compact and not re.match(r"^(?:ISO\b|\d)", compact):
        compact = compact[0].lower() + compact[1:]
    lower = compact.lower()
    if re.match(r"^(?:el|la|los|las|un|una)\s+", lower):
        return compact
    if lower.startswith("iso "):
        return f"la norma {compact.upper()}"

    head = re.findall(r"[A-Za-zÀ-ÿ]+", lower)
    if not head:
        return compact
    first = head[0]
    if first in PLURAL_FEMININE_HEADS:
        article = "las"
    elif first in PLURAL_MASCULINE_HEADS:
        article = "los"
    elif first in FEMININE_HEADS:
        article = "la"
    else:
        article = "el"
    return f"{article} {compact}"


def normalize_generated_question(question: str) -> str:
    """Normalize safe Spanish contractions without hiding malformed concepts."""

    compact = " ".join(question.split())
    compact = re.sub(r"\bde el\b", "del", compact, flags=re.IGNORECASE)
    compact = re.sub(r"\ba el\b", "al", compact, flags=re.IGNORECASE)
    return compact


def is_valid_generated_question(question: str) -> bool:
    """Validate generated question grammar before it reaches previews or exports."""

    raw_lower = " ".join(question.split()).lower()
    if re.search(
        r"\bde el\s+(?:monitorizaci[oó]n|unidades|descarga|evacuaci[oó]n|prevenci[oó]n)\b|"
        r"\bde la\s+(?:sistema|circuito|actuador)\b",
        raw_lower,
    ):
        return False
    compact = normalize_generated_question(question)
    lower = compact.lower()
    if len(compact) < 10 or not compact.endswith("?"):
        return False
    if re.search(r"\b(?:de la el|de el la|de los el|de las la)\b", lower):
        return False
    if re.search(
        r"\b(?:el|la|los|las)\s+(?:esta|este|estas|estos)\b|"
        r"\b(?:esta|este)\s+categor[ií]a\b",
        lower,
    ):
        return False
    if re.search(
        r"\bel\s+(?:monitorizaci[oó]n|unidades|descarga|evacuaci[oó]n|prevenci[oó]n)\b|"
        r"\bla\s+(?:sistema|circuito|actuador)\b",
        lower,
    ):
        return False
    target_match = re.search(
        r"(?:qu[eé] es|funci[oó]n de|funci[oó]n cumple|para|importante)\s+(.+?)\?$",
        lower,
    )
    if target_match and _has_malformed_start(target_match.group(1)):
        return False
    return True


def is_valid_concept(concept: str) -> bool:
    """Public validation helper used by tests and generation paths."""

    if _has_malformed_start(concept):
        return False
    return _valid_concept(_clean_phrase(concept))


def related_concept(text: str, excluded: str) -> str:
    excluded_key = concept_key(excluded)
    candidates = [
        concept
        for concept in extract_concepts(text, limit=4)
        if concept_key(concept) != excluded_key
    ]
    if not candidates:
        return ""
    domain_candidates = [
        concept
        for concept in candidates
        if any(re.fullmatch(pattern, concept, flags=re.IGNORECASE) for pattern, _score in DOMAIN_PATTERNS)
    ]
    if domain_candidates:
        candidates = domain_candidates
    lower_text = text.lower()
    return min(
        candidates,
        key=lambda concept: (
            lower_text.find(concept_key(concept))
            if concept_key(concept) in lower_text
            else len(lower_text)
        ),
    )


def _domain_candidates(text: str) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    for section in re.finditer(r"[^.!?;\n]+", text):
        if _is_broken_fragment(section.group()):
            continue
        for pattern, score in DOMAIN_PATTERNS:
            for match in re.finditer(pattern, section.group(), flags=re.IGNORECASE):
                candidates.append(
                    _Candidate(
                        _format_domain_phrase(match.group()),
                        score,
                        section.start() + match.start(),
                    )
                )
    return candidates


def _definition_candidates(text: str) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    marker_pattern = "|".join(re.escape(marker) for marker in DEFINITION_MARKERS)
    for sentence in split_sentences(text):
        match = re.match(
            rf"^(?:el|la|los|las|un|una)?\s*(?P<concept>.+?)\s+(?:{marker_pattern})\b",
            sentence,
            flags=re.IGNORECASE,
        )
        if match:
            candidates.append(_Candidate(match.group("concept"), 125.0, text.lower().find(sentence.lower())))
    return candidates


def _heading_candidates(text: str) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    position = 0
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for index, line in enumerate(lines):
        heading = ""
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        elif index < 6 and 2 <= len(line.split()) <= 8 and not re.search(r"[.!?;:]$", line):
            heading = line
        if heading and concept_key(heading) not in GENERIC_HEADINGS:
            candidates.append(_Candidate(heading, 128.0, position))
        position += len(line) + 1
    return candidates


def _bold_candidates(text: str) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    for match in re.finditer(r"(?:\*\*|__)([^*_]{3,90})(?:\*\*|__)", text):
        candidates.append(_Candidate(match.group(1), 126.0, match.start()))
    return candidates


def _noun_phrase_candidates(text: str) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    for section in re.finditer(r"[^.!?;\n]+", text):
        if _is_broken_fragment(section.group()):
            continue
        tokens = re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9-]*|\d+[A-Za-z]\d+", section.group())
        current: list[str] = []

        def flush() -> None:
            while current and current[-1].lower() in CONCEPT_CONNECTORS:
                current.pop()
            phrase = " ".join(current)
            if phrase and _has_technical_signal(phrase):
                candidates.append(_Candidate(phrase, 60.0, section.start()))
            current.clear()

        for token in tokens:
            lower = token.lower()
            boundary = (
                lower in CONCEPT_BOUNDARIES
                or (lower in WEAK_TERMS and lower not in CONCEPT_CONNECTORS)
                or lower.endswith("mente")
                or lower.endswith("ly")
            )
            if boundary:
                flush()
            elif lower in CONCEPT_CONNECTORS:
                if current:
                    current.append(token)
            elif _informative_token(lower):
                current.append(token)
                if len(current) >= 7:
                    flush()
            else:
                flush()
        flush()
    return candidates


def _valid_concept(phrase: str) -> bool:
    if not phrase or is_weak_concept(phrase):
        return False
    if concept_key(phrase) in GENERIC_HEADINGS:
        return False
    if concept_key(phrase) in GENERIC_CONCEPTS:
        return False
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", phrase.lower())
    if len(words) > 8:
        return False
    if any(word in WEAK_TERMS and word not in CONCEPT_CONNECTORS for word in words):
        return False
    if re.search(
        r"\b(copyright|contacto|direcci[oó]n|tel[eé]fono|informaci[oó]n legal|"
        r"condiciones marco|productos?|www|ciente|[ií]ndice)\b",
        phrase,
        flags=re.IGNORECASE,
    ):
        return False
    return _has_technical_signal(phrase)


def _has_technical_signal(phrase: str) -> bool:
    lower = phrase.lower()
    terms = set(re.findall(r"[A-Za-zÀ-ÿ]+", lower))
    return bool(
        terms & TECHNICAL_HINTS
        or re.search(r"\biso\s*\d+|\bcategor[ií]a\s*[134]|\b\d+[a-z]\d+\b|tf-idf", lower)
    )


def _informative_token(token: str) -> bool:
    if token in WEAK_TERMS or token in CONCEPT_BOUNDARIES:
        return False
    if token in CONCEPT_CONNECTORS:
        return True
    if len(token) >= 4:
        return True
    return token in {"air", "iso"}


def _clean_phrase(value: str) -> str:
    compact = re.sub(r"^[#*_]+\s*|\s*[#*_]+$", "", value.strip())
    compact = re.sub(r"^(?:el|la|los|las|un|una)\s+", "", compact, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", compact).strip(" .,:;-")


def _format_domain_phrase(value: str) -> str:
    compact = _clean_phrase(value)
    if compact.lower().startswith("iso "):
        return compact.upper()
    return re.sub(
        r"(\d+)([a-z])(\d+)",
        lambda match: f"{match.group(1)}{match.group(2).upper()}{match.group(3)}",
        compact,
    )


def _is_broken_fragment(value: str) -> bool:
    lower = value.lower()
    return bool(
        re.search(
            r"\bciente\b|\bseguridad\s+s[oó]lo\s+est[aá]\s+permitido\b|"
            r"\bobserva(?:r|ci[oó]n)\s+todo\s+ello\s+durante\b|"
            r"\bcircuitos\s+mostrados\s+presentan\s+aplicaciones\b|"
            r"\bpresi[oó]n residual\s+[ií]ndice\b",
            lower,
        )
    )


def _has_malformed_start(value: str) -> bool:
    compact = " ".join(value.split()).lower().strip(" .,:;¿?¡!")
    return bool(
        re.match(
            r"^(?:(?:el|la|los|las)\s+(?:esta|este|estas|estos)\b|"
            r"(?:esta|este)\s+categor[ií]a\b|"
            r"de\s+(?:el|la|los|las)\b)",
            compact,
        )
    )
