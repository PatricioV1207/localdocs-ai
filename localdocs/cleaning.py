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
    r"\breferences\b",
    r"\bbibliography\b",
    r"\bpublisher\b",
    r"\bpublished by\b",
    r"\bwww\.",
    r"\bdoi\b",
]

WEAK_TERMS = {
    "about",
    "also",
    "chapter",
    "content",
    "contents",
    "copyright",
    "document",
    "documents",
    "edition",
    "festo",
    "figure",
    "from",
    "guide",
    "localdocs",
    "page",
    "pages",
    "press",
    "publisher",
    "publishing",
    "rights",
    "section",
    "source",
    "table",
    "text",
    "this",
    "with",
}

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

    pattern_hits = sum(1 for pattern in LOW_VALUE_PATTERNS if re.search(pattern, lower))
    if pattern_hits >= 2:
        return True

    numeric_tokens = sum(1 for word in words if word.isdigit() or re.fullmatch(r"[ivxlcdm]+", word))
    if numeric_tokens / max(len(words), 1) > 0.45:
        return True

    if _looks_like_toc(lower):
        return True

    unique_alpha = {word for word in words if any(char.isalpha() for char in word)}
    if len(unique_alpha) <= 3 and len(words) > 10:
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
    sentences = [sentence for sentence in split_sentences(text) if not is_low_value_text(sentence)]
    if not sentences:
        sentences = split_sentences(text)
    if not sentences:
        return []

    query_terms = informative_terms(query)
    if not query_terms:
        return sentences[:limit]

    def score(sentence: str) -> tuple[int, int]:
        terms = set(informative_terms(sentence))
        return (len(query_terms & terms), len(terms))

    ranked = sorted(sentences, key=score, reverse=True)
    return ranked[:limit]


def informative_terms(text: str) -> set[str]:
    terms: set[str] = set()
    for raw_term in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9-]{2,}", text):
        term = raw_term.lower()
        if _is_informative_term(term):
            terms.add(term)
    return terms


def best_concept(text: str) -> str:
    heading = first_heading(text)
    if heading:
        return heading

    terms = [term for term in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9-]{3,}", text) if _is_informative_term(term)]
    if not terms:
        return ""

    counts = Counter(term for term in terms)
    return counts.most_common(1)[0][0]


def first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading and not is_weak_concept(heading):
                return heading
    return ""


def is_weak_concept(value: str) -> bool:
    compact = " ".join(value.split()).strip(" .:-")
    if not compact:
        return True
    lower = compact.lower()
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", lower)
    if not words:
        return True
    if len(words) == 1 and (words[0] in WEAK_TERMS or len(words[0]) < 4 or re.fullmatch(r"[ivxlcdm]+|\d+", words[0])):
        return True
    if all(word in WEAK_TERMS or re.fullmatch(r"[ivxlcdm]+|\d+", word) for word in words):
        return True
    return False


def appears_spanish(text: str) -> bool:
    terms = {term.lower() for term in re.findall(r"[A-Za-zÀ-ÿ]+", text)}
    accented = bool(re.search(r"[áéíóúñÁÉÍÓÚÑ¿¡]", text))
    return accented or len(terms & SPANISH_HINTS) >= 3


def is_valid_question(question: str) -> bool:
    stripped = " ".join(question.split())
    if len(stripped) < 8:
        return False
    if stripped.lower() in {"your question", "question", "ask a question", "what do these documents say about local search?"}:
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
    if len(lower) < 4:
        return False
    if re.fullmatch(r"\d+|[ivxlcdm]+", lower):
        return False
    return True
