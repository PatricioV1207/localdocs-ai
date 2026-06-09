#!/usr/bin/env python3
"""Run deterministic LocalDocs AI quality evaluations."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from localdocs.cleaning import is_low_value_text, is_quality_sentence, split_sentences
from localdocs.concepts import is_valid_generated_question
from localdocs.flashcards import generate_flashcards
from localdocs.models import DocumentChunk, SearchResult
from localdocs.qa import answer_question
from localdocs.study import generate_study_questions
from localdocs.summarizer import summarize_documents

SCHEMA_VERSION = 1
DEFAULT_FIXTURES_DIR = ROOT / "evals" / "fixtures"
DEFAULT_EXPECTED_DIR = ROOT / "evals" / "expected"


@dataclass
class AreaResult:
    fixture: str
    area: str
    checks: int = 0
    failures: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures

    def expect(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(message)


@dataclass
class EvaluationReport:
    results: list[AreaResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return bool(self.results) and all(result.passed for result in self.results)

    @property
    def check_count(self) -> int:
        return sum(result.checks for result in self.results)

    @property
    def failure_count(self) -> int:
        return sum(len(result.failures) for result in self.results)


def run_all(
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    expected_dir: Path = DEFAULT_EXPECTED_DIR,
    fixture_names: set[str] | None = None,
) -> EvaluationReport:
    """Run every matching fixture and return a structured report."""

    report = EvaluationReport()
    fixture_paths = sorted(fixtures_dir.glob("*.json"))
    if fixture_names is not None:
        fixture_paths = [path for path in fixture_paths if path.stem in fixture_names]

    if not fixture_paths:
        report.results.append(
            AreaResult(
                fixture="configuration",
                area="fixture discovery",
                checks=1,
                failures=["No matching quality fixtures were found."],
            )
        )
        return report

    discovered = {path.stem for path in fixture_paths}
    if fixture_names is not None:
        missing = sorted(fixture_names - discovered)
        if missing:
            report.results.append(
                AreaResult(
                    fixture="configuration",
                    area="fixture discovery",
                    checks=1,
                    failures=[f"Unknown fixture(s): {', '.join(missing)}"],
                )
            )

    if fixture_names is None:
        expected_names = {path.stem for path in expected_dir.glob("*.json")}
        orphaned_expected = sorted(expected_names - discovered)
        if orphaned_expected:
            report.results.append(
                AreaResult(
                    fixture="configuration",
                    area="fixture discovery",
                    checks=1,
                    failures=[
                        "Expected file(s) have no matching fixture: "
                        f"{', '.join(orphaned_expected)}"
                    ],
                )
            )

    for fixture_path in fixture_paths:
        expected_path = expected_dir / fixture_path.name
        if not expected_path.exists():
            report.results.append(
                AreaResult(
                    fixture=fixture_path.stem,
                    area="schema",
                    checks=1,
                    failures=[f"Missing expected file: {expected_path}"],
                )
            )
            continue

        try:
            fixture = _load_json(fixture_path)
            expected = _load_json(expected_path)
            _validate_schema(fixture, expected, fixture_path.name)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            report.results.append(
                AreaResult(
                    fixture=fixture_path.stem,
                    area="schema",
                    checks=1,
                    failures=[str(exc)],
                )
            )
            continue

        chunks = _build_chunks(fixture_path.stem, fixture["chunks"])
        chunk_by_index = {chunk.chunk_index: chunk for chunk in chunks}

        qa_outputs, qa_results = _evaluate_qa(
            fixture_path.stem,
            fixture.get("qa_cases", []),
            expected.get("qa", []),
            chunk_by_index,
        )
        study_outputs, study_result = _evaluate_study(
            fixture_path.stem,
            chunks,
            expected["study_questions"],
        )
        flashcard_outputs, flashcard_result = _evaluate_flashcards(
            fixture_path.stem,
            chunks,
            expected["flashcards"],
        )
        summary_outputs, summary_result = _evaluate_summaries(
            fixture_path.stem,
            chunks,
            expected.get("summaries"),
        )
        source_result = _evaluate_source_quality(
            fixture_path.stem,
            chunks,
            expected["source_quality"],
            qa_outputs,
            study_outputs,
            flashcard_outputs,
            summary_outputs,
        )

        report.results.extend(qa_results)
        report.results.extend([study_result, flashcard_result])
        if summary_result is not None:
            report.results.append(summary_result)
        report.results.append(source_result)

    return report


def _evaluate_qa(
    fixture_name: str,
    cases: list[dict[str, Any]],
    expectations: list[dict[str, Any]],
    chunk_by_index: dict[int, DocumentChunk],
) -> tuple[list[Any], list[AreaResult]]:
    expected_by_id = {item["id"]: item for item in expectations}
    outputs = []
    results = []

    for case in cases:
        case_id = case["id"]
        result = AreaResult(fixture=fixture_name, area=f"qa:{case_id}")
        expectation = expected_by_id.get(case_id)
        result.expect(expectation is not None, f"No QA expectation exists for case '{case_id}'.")
        if expectation is None:
            results.append(result)
            continue

        search_results = []
        for raw_index, score in case["scores"].items():
            chunk_index = int(raw_index)
            chunk = chunk_by_index.get(chunk_index)
            result.expect(chunk is not None, f"QA score references missing chunk {chunk_index}.")
            if chunk is not None:
                search_results.append(SearchResult(chunk=chunk, score=float(score)))

        answer = answer_question(case["question"], search_results, use_openai=False)
        outputs.append(answer)
        result.expect(
            answer.enough_evidence is expectation["enough_evidence"],
            f"Expected enough_evidence={expectation['enough_evidence']}, got {answer.enough_evidence}.",
        )

        lower_answer = answer.answer.lower()
        _expect_terms(result, lower_answer, expectation.get("must_include", []), present=True)
        _expect_terms(result, lower_answer, expectation.get("must_not_include", []), present=False)

        actual_citations = sorted(citation.chunk_index for citation in answer.citations)
        expected_citations = sorted(expectation.get("citation_chunks", []))
        result.expect(
            actual_citations == expected_citations,
            f"Expected citation chunks {expected_citations}, got {actual_citations}.",
        )

        if expectation.get("require_complete_sentences"):
            sentences = split_sentences(answer.answer)
            result.expect(bool(sentences), "QA answer did not contain a complete sentence.")
            result.expect(
                all(is_quality_sentence(sentence) for sentence in sentences),
                "QA answer contains a low-quality or broken sentence.",
            )
            result.expect(
                all(sentence.endswith((".", "?", "!")) for sentence in sentences),
                "QA answer contains a sentence without terminal punctuation.",
            )

        results.append(result)

    unexpected = sorted(set(expected_by_id) - {case["id"] for case in cases})
    if unexpected:
        results.append(
            AreaResult(
                fixture=fixture_name,
                area="qa:coverage",
                checks=1,
                failures=[f"Expected QA case(s) missing from fixture: {', '.join(unexpected)}"],
            )
        )
    return outputs, results


def _evaluate_study(
    fixture_name: str,
    chunks: list[DocumentChunk],
    expectation: dict[str, Any],
) -> tuple[list[Any], AreaResult]:
    result = AreaResult(fixture=fixture_name, area="study questions")
    questions = generate_study_questions(chunks, max_questions=int(expectation["max_items"]))
    texts = [item.question for item in questions]
    combined = " ".join(texts).lower()

    _expect_count(result, len(questions), expectation)
    _expect_terms(result, combined, expectation.get("must_include", []), present=True)
    _expect_terms(result, combined, expectation.get("must_not_include", []), present=False)
    _expect_citations(result, questions, expectation.get("citation_chunks", []))
    result.expect(
        all(is_valid_generated_question(text) for text in texts),
        "A study question failed grammatical validation.",
    )
    return questions, result


def _evaluate_flashcards(
    fixture_name: str,
    chunks: list[DocumentChunk],
    expectation: dict[str, Any],
) -> tuple[list[Any], AreaResult]:
    result = AreaResult(fixture=fixture_name, area="flashcards")
    cards = generate_flashcards(chunks, max_cards=int(expectation["max_items"]))
    combined = " ".join(f"{item.question} {item.answer}" for item in cards).lower()

    _expect_count(result, len(cards), expectation)
    _expect_terms(result, combined, expectation.get("must_include", []), present=True)
    _expect_terms(result, combined, expectation.get("must_not_include", []), present=False)
    _expect_citations(result, cards, expectation.get("citation_chunks", []))
    result.expect(
        all(is_valid_generated_question(item.question) for item in cards),
        "A flashcard question failed grammatical validation.",
    )
    result.expect(
        all(is_quality_sentence(item.answer) for item in cards),
        "A flashcard answer failed sentence-quality validation.",
    )
    return cards, result


def _evaluate_summaries(
    fixture_name: str,
    chunks: list[DocumentChunk],
    expectation: dict[str, Any] | None,
) -> tuple[list[Any], AreaResult | None]:
    summaries = summarize_documents(chunks, use_openai=False)
    if expectation is None:
        return summaries, None

    result = AreaResult(fixture=fixture_name, area="summaries")
    combined = " ".join(item.summary for item in summaries).lower()
    _expect_count(result, len(summaries), expectation)
    _expect_terms(result, combined, expectation.get("must_include", []), present=True)
    _expect_terms(result, combined, expectation.get("must_not_include", []), present=False)

    actual_citations = sorted(
        {
            citation.chunk_index
            for summary in summaries
            for citation in summary.citations
        }
    )
    expected_citations = sorted(expectation.get("citation_chunks", []))
    result.expect(
        actual_citations == expected_citations,
        f"Expected citation chunks {expected_citations}, got {actual_citations}.",
    )
    result.expect(
        all(not summary.used_llm for summary in summaries),
        "A deterministic summary unexpectedly used an LLM.",
    )
    return summaries, result


def _evaluate_source_quality(
    fixture_name: str,
    chunks: list[DocumentChunk],
    expectation: dict[str, Any],
    qa_outputs: list[Any],
    study_outputs: list[Any],
    flashcard_outputs: list[Any],
    summary_outputs: list[Any],
) -> AreaResult:
    result = AreaResult(fixture=fixture_name, area="source quality")
    chunk_by_index = {chunk.chunk_index: chunk for chunk in chunks}

    for chunk_index in expectation.get("low_value_chunks", []):
        chunk = chunk_by_index.get(chunk_index)
        result.expect(chunk is not None, f"Missing expected low-value chunk {chunk_index}.")
        if chunk is not None:
            result.expect(
                is_low_value_text(chunk.text),
                f"Chunk {chunk_index} should be classified as low-value.",
            )

    for chunk_index in expectation.get("technical_chunks", []):
        chunk = chunk_by_index.get(chunk_index)
        result.expect(chunk is not None, f"Missing expected technical chunk {chunk_index}.")
        if chunk is not None:
            result.expect(
                not is_low_value_text(chunk.text),
                f"Chunk {chunk_index} should remain usable technical evidence.",
            )

    forbidden = set(expectation.get("forbidden_citation_chunks", []))
    cited = set()
    for answer in qa_outputs:
        cited.update(citation.chunk_index for citation in answer.citations)
    cited.update(item.citation.chunk_index for item in study_outputs)
    cited.update(item.citation.chunk_index for item in flashcard_outputs)
    for summary in summary_outputs:
        cited.update(citation.chunk_index for citation in summary.citations)
    result.expect(
        not (cited & forbidden),
        f"Generated outputs cited forbidden chunk(s): {sorted(cited & forbidden)}.",
    )
    return result


def _build_chunks(fixture_name: str, rows: list[dict[str, Any]]) -> list[DocumentChunk]:
    file_name = f"{fixture_name}.pdf"
    return [
        DocumentChunk(
            text=row["text"],
            file_name=file_name,
            file_path=file_name,
            file_type="pdf",
            chunk_index=int(row["chunk_index"]),
            page_number=row.get("page_number"),
        )
        for row in rows
    ]


def _expect_count(result: AreaResult, actual: int, expectation: dict[str, Any]) -> None:
    minimum = int(expectation.get("min_items", 0))
    maximum = int(expectation["max_items"])
    result.expect(actual >= minimum, f"Expected at least {minimum} item(s), got {actual}.")
    result.expect(actual <= maximum, f"Expected at most {maximum} item(s), got {actual}.")


def _expect_terms(
    result: AreaResult,
    text: str,
    terms: list[str],
    *,
    present: bool,
) -> None:
    for term in terms:
        found = term.lower() in text
        if present:
            result.expect(found, f"Required text is missing: {term!r}.")
        else:
            result.expect(not found, f"Forbidden text is present: {term!r}.")


def _expect_citations(
    result: AreaResult,
    items: list[Any],
    expected_chunks: list[int],
) -> None:
    actual = sorted({item.citation.chunk_index for item in items})
    expected = sorted(expected_chunks)
    result.expect(actual == expected, f"Expected citation chunks {expected}, got {actual}.")


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return data


def _validate_schema(
    fixture: dict[str, Any],
    expected: dict[str, Any],
    filename: str,
) -> None:
    if fixture.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"{filename}: unsupported fixture schema version.")
    if expected.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"{filename}: unsupported expected schema version.")
    if not isinstance(fixture.get("chunks"), list) or not fixture["chunks"]:
        raise ValueError(f"{filename}: fixture must contain at least one chunk.")
    if not isinstance(fixture.get("qa_cases", []), list):
        raise ValueError(f"{filename}: qa_cases must be a list.")
    if not isinstance(expected.get("qa", []), list):
        raise ValueError(f"{filename}: expected qa must be a list.")
    for key in ("study_questions", "flashcards", "source_quality"):
        if not isinstance(expected.get(key), dict):
            raise ValueError(f"{filename}: expected file is missing {key!r}.")

    try:
        chunk_indices = [int(row["chunk_index"]) for row in fixture["chunks"]]
        if any(not isinstance(row.get("text"), str) or not row["text"].strip() for row in fixture["chunks"]):
            raise ValueError
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{filename}: every chunk needs a numeric index and non-empty text.") from exc
    if len(chunk_indices) != len(set(chunk_indices)):
        raise ValueError(f"{filename}: chunk indexes must be unique.")


def _print_report(report: EvaluationReport, quiet: bool = False) -> None:
    if quiet and report.passed:
        print(f"QUALITY EVAL PASSED: {report.check_count} checks")
        return

    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.fixture} :: {result.area} ({result.checks} checks)")
        for failure in result.failures:
            print(f"  - {failure}")

    print()
    if report.passed:
        print(f"QUALITY EVAL PASSED: {report.check_count} checks")
    else:
        print(
            f"QUALITY EVAL FAILED: {report.failure_count} failure(s) "
            f"across {report.check_count} checks"
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        help="Run one fixture by filename stem. May be repeated.",
    )
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=DEFAULT_FIXTURES_DIR,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--expected-dir",
        type=Path,
        default=DEFAULT_EXPECTED_DIR,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only the final summary when all checks pass.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    selected = set(args.fixture) if args.fixture else None
    report = run_all(args.fixtures_dir, args.expected_dir, selected)
    _print_report(report, quiet=args.quiet)
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
