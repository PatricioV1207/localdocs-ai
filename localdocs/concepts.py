"""Deterministic, structure-aware concept extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass

from localdocs.cleaning import (
    CONCEPT_BOUNDARIES,
    CONCEPT_CONNECTORS,
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

ACTION_MARKERS = (
    "are",
    "allows",
    "blocks",
    "controls",
    "converts",
    "creates",
    "detects",
    "ensures",
    "generates",
    "prevents",
    "provides",
    "reduces",
    "regulates",
    "requires",
    "stabilizes",
    "stops",
    "supervises",
    "supports",
    "uses",
    "is",
    "bloquea",
    "controla",
    "convierte",
    "crea",
    "descarga",
    "detecta",
    "detiene",
    "evita",
    "garantiza",
    "genera",
    "permite",
    "previene",
    "proporciona",
    "reduce",
    "regula",
    "requiere",
    "supervisa",
    "utiliza",
    "es",
    "son",
)

OBJECT_MARKERS = {"uses", "utiliza", "requires", "requiere", "includes", "incluye"}


def extract_concepts(text: str, limit: int = 3) -> list[str]:
    """Extract ranked, coherent technical concepts from a text block."""

    if limit <= 0 or not text.strip():
        return []

    candidates: list[_Candidate] = []
    candidates.extend(_question_target_candidates(text))
    candidates.extend(_definition_candidates(text))
    candidates.extend(_heading_candidates(text))
    candidates.extend(_bold_candidates(text))
    candidates.extend(_identifier_candidates(text))
    candidates.extend(_sentence_structure_candidates(text))
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
    lower_text = text.lower()
    return min(
        candidates,
        key=lambda concept: (
            lower_text.find(concept_key(concept))
            if concept_key(concept) in lower_text
            else len(lower_text)
        ),
    )


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


def _question_target_candidates(text: str) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    match = re.search(
        r"(?:what is|what are|define|qu[eé] es|qu[eé] son|defin[ea])\s+(.+?)[?]?$",
        text.strip(" ¿"),
        flags=re.IGNORECASE,
    )
    if not match:
        return candidates
    target = match.group(1).strip(" ?")
    for part in re.split(
        r"\s+(?:and|y|e)\s+(?:the|el|la|los|las|un|una)?\s*",
        target,
        flags=re.IGNORECASE,
    ):
        candidates.append(_Candidate(part, 130.0, match.start(1)))
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


def _identifier_candidates(text: str) -> list[_Candidate]:
    """Extract standards, acronyms, and component-like identifiers generically."""

    candidates: list[_Candidate] = []
    patterns = (
        r"\b[A-Z]{2,}(?:[- ]?\d+(?:-\d+)*)?\b",
        r"\b\d+[A-Za-z]\d+\b",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            prefix = text[max(0, match.start() - 40):match.start()]
            words = [
                word
                for word in re.findall(r"[A-Za-zÀ-ÿ]+", prefix)
                if word.lower() not in CONCEPT_CONNECTORS
                and word.lower() not in WEAK_TERMS
            ]
            label = " ".join(words[-1:] + [match.group()])
            candidates.append(_Candidate(label, 112.0, match.start()))
    return candidates


def _sentence_structure_candidates(text: str) -> list[_Candidate]:
    """Extract grammatical subjects and selected objects around action verbs."""

    candidates: list[_Candidate] = []
    marker_pattern = "|".join(
        re.escape(marker)
        for marker in sorted(ACTION_MARKERS, key=len, reverse=True)
    )
    object_pattern = "|".join(
        re.escape(marker)
        for marker in sorted(OBJECT_MARKERS, key=len, reverse=True)
    )
    for sentence in split_sentences(text):
        position = text.lower().find(sentence.lower())
        subject_match = re.match(
            rf"^(?:the|el|la|los|las|un|una)?\s*(?P<subject>.+?)\s+"
            rf"(?P<verb>{marker_pattern})\b",
            sentence,
            flags=re.IGNORECASE,
        )
        if subject_match:
            subject = subject_match.group("subject")
            for part in re.split(
                r"\s+(?:and|y|e)\s+(?:the|el|la|los|las|un|una)?\s*",
                subject,
                flags=re.IGNORECASE,
            ):
                candidates.append(_Candidate(part, 115.0, position))

        object_match = re.search(
            rf"\b(?:{object_pattern})\s+(?P<object>.+?)(?:\s+(?:so|because|"
            rf"para que|porque)\b|[.;]|$)",
            sentence,
            flags=re.IGNORECASE,
        )
        if object_match:
            candidates.append(_Candidate(object_match.group("object"), 105.0, position))
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
            if phrase and _has_structural_signal(phrase):
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
    if _is_broken_fragment(phrase):
        return False
    if re.match(
        r"^(?:what|which|how|why|where|when|qu[eé]|cu[aá]l|c[oó]mo|por qu[eé])\b",
        phrase,
        flags=re.IGNORECASE,
    ):
        return False
    if concept_key(phrase) in GENERIC_HEADINGS:
        return False
    if concept_key(phrase) in GENERIC_CONCEPTS:
        return False
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", phrase.lower())
    if len(words) > 8:
        return False
    informative = [
        word
        for word in words
        if word not in WEAK_TERMS and word not in CONCEPT_CONNECTORS
    ]
    weak = [
        word
        for word in words
        if word in WEAK_TERMS and word not in CONCEPT_CONNECTORS
    ]
    if weak and len(informative) < 2:
        return False
    if re.search(
        r"\b(copyright|contacto|direcci[oó]n|tel[eé]fono|informaci[oó]n legal|"
        r"condiciones marco|productos?|www|ciente|[ií]ndice)\b",
        phrase,
        flags=re.IGNORECASE,
    ):
        return False
    return _has_structural_signal(phrase)


def _has_structural_signal(phrase: str) -> bool:
    lower = phrase.lower()
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", lower)
    informative = [
        word
        for word in words
        if word not in WEAK_TERMS and word not in CONCEPT_CONNECTORS
    ]
    return len(informative) >= 2 or bool(
        re.search(r"\b[A-Z]{2,}\d*\b|\b\d+[A-Za-z]\d+\b|\b\w+-\w+\b", phrase)
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
