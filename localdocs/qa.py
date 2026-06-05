"""Question answering over retrieved document chunks."""

from __future__ import annotations

import os
import re

from localdocs.models import Answer, Citation, SearchResult

MIN_EVIDENCE_SCORE = 0.02


def answer_question(
    question: str,
    search_results: list[SearchResult],
    openai_api_key: str | None = None,
    model: str = "gpt-4o-mini",
    min_score: float = MIN_EVIDENCE_SCORE,
) -> Answer:
    """Answer a question using only retrieved document context."""

    strong_results = [result for result in search_results if result.score >= min_score]
    if not question.strip() or not strong_results:
        return Answer(
            question=question,
            answer="There is not enough evidence in the indexed documents to answer this question.",
            citations=[],
            context=search_results,
            used_llm=False,
            enough_evidence=False,
        )

    selected_results = strong_results[:3]
    citations = _unique_citations(selected_results)
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    if api_key:
        llm_answer = _try_openai_answer(question, selected_results, api_key, model)
        if llm_answer:
            return Answer(
                question=question,
                answer=llm_answer,
                citations=citations,
                context=selected_results,
                used_llm=True,
                enough_evidence=True,
            )

    return Answer(
        question=question,
        answer=_extractive_answer(question, selected_results),
        citations=citations,
        context=selected_results,
        used_llm=False,
        enough_evidence=True,
    )


def _try_openai_answer(
    question: str,
    results: list[SearchResult],
    api_key: str,
    model: str,
) -> str | None:
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
        return answer.strip() or None
    except Exception:
        return None


def _extractive_answer(question: str, results: list[SearchResult]) -> str:
    snippets = [_best_snippet(result.text, question) for result in results]
    snippets = [snippet for snippet in snippets if snippet]

    if not snippets:
        return "There is not enough evidence in the indexed documents to answer this question."

    bullet_list = "\n".join(f"- {snippet}" for snippet in snippets)
    return f"I found relevant context in the indexed documents:\n\n{bullet_list}"


def _best_snippet(text: str, question: str, max_chars: int = 700) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return _truncate(text, max_chars)

    query_terms = {term.lower() for term in re.findall(r"[A-Za-z0-9]+", question) if len(term) > 2}
    if not query_terms:
        return _truncate(sentences[0], max_chars)

    def score(sentence: str) -> int:
        terms = {term.lower() for term in re.findall(r"[A-Za-z0-9]+", sentence)}
        return len(query_terms & terms)

    best_sentence = max(sentences, key=score)
    return _truncate(best_sentence, max_chars)


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


def _split_sentences(text: str) -> list[str]:
    compact = " ".join(text.split())
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", compact) if sentence.strip()]


def _truncate(text: str, max_chars: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."
