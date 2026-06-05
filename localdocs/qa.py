"""Question answering over retrieved document chunks."""

from __future__ import annotations

import os

from localdocs.cleaning import best_sentences, informative_chunks, invalid_question_message, is_valid_question
from localdocs.models import Answer, Citation, SearchResult

MIN_EVIDENCE_SCORE = 0.05
WEAK_EVIDENCE_MESSAGE = "I could not find enough strong evidence in the documents."


def answer_question(
    question: str,
    search_results: list[SearchResult],
    openai_api_key: str | None = None,
    model: str = "gpt-4o-mini",
    min_score: float = MIN_EVIDENCE_SCORE,
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
    citations = _unique_citations(selected_results)
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    if api_key:
        llm_answer, llm_error = _try_openai_answer(question, selected_results, api_key, model)
        if llm_answer:
            return Answer(
                question=question,
                answer=llm_answer,
                citations=citations,
                context=selected_results,
                used_llm=True,
                enough_evidence=True,
            )
    else:
        llm_error = ""

    return Answer(
        question=question,
        answer=_extractive_answer(question, selected_results),
        citations=citations,
        context=selected_results,
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
    except Exception as exc:
        return None, f"OpenAI answer generation failed, so LocalDocs used extractive fallback: {exc}"


def _extractive_answer(question: str, results: list[SearchResult]) -> str:
    snippets: list[str] = []
    seen: set[str] = set()
    for result in results:
        for sentence in best_sentences(result.text, question, limit=2):
            key = sentence.lower()
            if key in seen:
                continue
            seen.add(key)
            snippets.append(_truncate(sentence, 320))
            if len(snippets) >= 3:
                break
        if len(snippets) >= 3:
            break

    if not snippets:
        return WEAK_EVIDENCE_MESSAGE

    bullet_list = "\n".join(f"- {snippet}" for snippet in snippets)
    return f"Based on the strongest retrieved evidence:\n\n{bullet_list}"


def _select_results(results: list[SearchResult], limit: int = 3) -> list[SearchResult]:
    informative = informative_chunks([result.chunk for result in results], limit=limit)
    selected: list[SearchResult] = []
    for chunk in informative:
        for result in results:
            if result.chunk == chunk and result not in selected:
                selected.append(result)
                break
    return selected[:limit] or results[:limit]


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
