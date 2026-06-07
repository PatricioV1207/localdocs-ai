"""Question answering over retrieved document chunks."""

from __future__ import annotations

import os
import re

from localdocs.cleaning import (
    appears_spanish,
    chunk_quality_score,
    informative_terms,
    invalid_question_message,
    is_low_value_text,
    is_valid_question,
    sentence_quality_score,
    split_sentences,
)
from localdocs.concepts import concept_key, extract_concepts
from localdocs.models import Answer, Citation, SearchResult

MIN_EVIDENCE_SCORE = 0.05
WEAK_EVIDENCE_MESSAGE = "I could not find enough strong evidence in the documents."
OPENAI_FALLBACK_NOTE = "OpenAI generation is unavailable, so LocalDocs used local extractive mode."


def answer_question(
    question: str,
    search_results: list[SearchResult],
    openai_api_key: str | None = None,
    model: str = "gpt-4o-mini",
    min_score: float = MIN_EVIDENCE_SCORE,
    use_openai: bool = True,
) -> Answer:
    """Answer a question using only retrieved document context."""

    if not is_valid_question(question):
        return Answer(
            question=question,
            answer=invalid_question_message(),
            citations=[],
            context=search_results,
            used_llm=False,
            enough_evidence=False,
        )

    strong_results = [result for result in search_results if result.score >= min_score]
    if not strong_results:
        return Answer(
            question=question,
            answer=WEAK_EVIDENCE_MESSAGE,
            citations=[],
            context=search_results,
            used_llm=False,
            enough_evidence=False,
        )

    selected_results = _select_results(strong_results)
    api_key = (openai_api_key or os.getenv("OPENAI_API_KEY")) if use_openai else None

    if api_key:
        llm_answer, llm_error = _try_openai_answer(question, selected_results, api_key, model)
        if llm_answer:
            return Answer(
                question=question,
                answer=llm_answer,
                citations=_unique_citations(selected_results),
                context=selected_results,
                used_llm=True,
                enough_evidence=True,
            )
    else:
        llm_error = ""

    extractive_answer, used_results = _extractive_answer(question, selected_results)
    if not used_results:
        return Answer(
            question=question,
            answer=WEAK_EVIDENCE_MESSAGE,
            citations=[],
            context=selected_results,
            used_llm=False,
            enough_evidence=False,
            note=llm_error,
        )

    return Answer(
        question=question,
        answer=extractive_answer,
        citations=_unique_citations(used_results),
        context=used_results,
        used_llm=False,
        enough_evidence=True,
        note=llm_error,
    )


def _try_openai_answer(
    question: str,
    results: list[SearchResult],
    api_key: str,
    model: str,
) -> tuple[str | None, str]:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You answer questions using only the provided document context. "
                        "If the context does not contain enough evidence, say so clearly. "
                        "Do not add facts from outside the context."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question:\n{question}\n\nDocument context:\n{_context_text(results)}",
                },
            ],
        )
        answer = response.choices[0].message.content or ""
        return answer.strip() or None, ""
    except Exception:
        return None, OPENAI_FALLBACK_NOTE


def _extractive_answer(
    question: str,
    results: list[SearchResult],
) -> tuple[str, list[SearchResult]]:
    concepts = extract_concepts(question, limit=4)
    concepts.sort(key=lambda concept: _concept_position(question, concept))
    question_terms = informative_terms(question)
    question_type = _question_type(question)
    sentence_options = _sentence_options(results, question_terms)
    selected: list[tuple[str, SearchResult]] = []
    seen_sentences: set[str] = set()

    for concept in concepts:
        option = _best_option_for_concept(
            sentence_options,
            concept,
            seen_sentences,
            question_type=question_type,
        )
        if option:
            selected.append(option)
            seen_sentences.add(option[0].lower())

    target_count = 3 if len(concepts) >= 2 else 2
    for sentence, result, _score in sentence_options:
        key = sentence.lower()
        if key in seen_sentences:
            continue
        if selected and _is_redundant(sentence, [item[0] for item in selected]):
            continue
        selected.append((sentence, result))
        seen_sentences.add(key)
        if len(selected) >= target_count:
            break

    if not selected:
        return WEAK_EVIDENCE_MESSAGE, []

    sentences = [_truncate(sentence, 360) for sentence, _result in selected]
    used_results = _unique_results([result for _sentence, result in selected])
    spanish = appears_spanish(question) or appears_spanish(" ".join(sentences))

    if spanish:
        if question_type == "comparison" and len(sentences) > 1:
            answer = f"Según la evidencia del documento, {sentences[0]} {sentences[1]}"
        elif len(sentences) > len(concepts) and len(concepts) >= 2:
            core = " ".join(sentences[: len(concepts)])
            relation = sentences[len(concepts)]
            answer = f"{core} En el circuito descrito, {relation[0].lower() + relation[1:]}"
        else:
            answer = " ".join(sentences)
    else:
        answer = f"According to the strongest document evidence, {' '.join(sentences)}"

    return answer, used_results


def _select_results(results: list[SearchResult], limit: int = 5) -> list[SearchResult]:
    ranked = sorted(
        results,
        key=lambda result: (chunk_quality_score(result.chunk) + result.score * 4.0, result.score),
        reverse=True,
    )
    useful = [result for result in ranked if not is_low_value_text(result.text)]
    selected = useful if useful else ranked
    return selected[:limit]


def _sentence_options(
    results: list[SearchResult],
    question_terms: set[str],
) -> list[tuple[str, SearchResult, float]]:
    options: list[tuple[str, SearchResult, float]] = []
    for result in results:
        for sentence in split_sentences(result.text):
            score = sentence_quality_score(sentence, question_terms) + result.score * 3.0
            if score < 0:
                continue
            options.append((sentence, result, score))
    return sorted(options, key=lambda item: item[2], reverse=True)


def _best_option_for_concept(
    options: list[tuple[str, SearchResult, float]],
    concept: str,
    seen_sentences: set[str],
    question_type: str,
) -> tuple[str, SearchResult] | None:
    concept_terms = informative_terms(concept)
    best: tuple[str, SearchResult, float] | None = None
    for sentence, result, base_score in options:
        if sentence.lower() in seen_sentences:
            continue
        sentence_terms = informative_terms(sentence)
        overlap = len(concept_terms & sentence_terms)
        exact = concept_key(concept) in concept_key(sentence)
        if not exact and overlap < max(1, min(2, len(concept_terms))):
            continue
        score = base_score + overlap * 4.0 + (8.0 if exact else 0.0)
        if question_type == "definition":
            lower = sentence.lower()
            if any(
                marker in lower
                for marker in ["se define como", "es una función", "es un sistema", "consiste en"]
            ):
                score += 12.0
            if re.match(
                rf"^(?:el|la|los|las|un|una)?\s*{re.escape(concept_key(concept))}\b",
                concept_key(sentence),
            ):
                score += 4.0
        if best is None or score > best[2]:
            best = (sentence, result, score)
    return (best[0], best[1]) if best else None


def _question_type(question: str) -> str:
    lower = question.lower()
    if any(term in lower for term in ["diferencia", "compar", "difference", "versus", " vs "]):
        return "comparison"
    if any(term in lower for term in ["función", "funcion", "para qué", "purpose", "role"]):
        return "function"
    if any(term in lower for term in ["cómo", "como", "pasos", "proceso", "how", "steps"]):
        return "process"
    if any(term in lower for term in ["qué es", "que es", "define", "definition", "what is"]):
        return "definition"
    return "general"


def _concept_position(text: str, concept: str) -> int:
    position = text.lower().find(concept_key(concept))
    return position if position >= 0 else len(text)


def _is_redundant(sentence: str, selected: list[str]) -> bool:
    terms = informative_terms(sentence)
    for existing in selected:
        existing_terms = informative_terms(existing)
        if terms and len(terms & existing_terms) / len(terms) >= 0.8:
            return True
    return False


def _unique_results(results: list[SearchResult]) -> list[SearchResult]:
    unique: list[SearchResult] = []
    seen: set[tuple[str, int, int | None]] = set()
    for result in results:
        key = (result.file_name, result.chunk_index, result.page_number)
        if key in seen:
            continue
        seen.add(key)
        unique.append(result)
    return unique


def _context_text(results: list[SearchResult]) -> str:
    lines = []
    for number, result in enumerate(results, start=1):
        citation = Citation.from_chunk(result.chunk).label()
        lines.append(f"[{number}] {citation}\n{result.text}")
    return "\n\n".join(lines)


def _unique_citations(results: list[SearchResult]) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[tuple[str, int, int | None]] = set()
    for result in results:
        citation = Citation.from_chunk(result.chunk)
        key = (citation.file_name, citation.chunk_index, citation.page_number)
        if key in seen:
            continue
        seen.add(key)
        citations.append(citation)
    return citations


def _truncate(text: str, max_chars: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."
