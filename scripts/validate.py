#!/usr/bin/env python3
"""Run LocalDocs AI validation with fast, focused, or full coverage."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ValidationStep:
    label: str
    command: tuple[str, ...]


FAST_TESTS = (
    "tests/test_app.py",
    "tests/test_parser.py",
    "tests/test_chunker.py",
    "tests/test_search.py",
    "tests/test_export.py",
)

AREA_TESTS = {
    "core": (
        "tests/test_app.py",
        "tests/test_config.py",
        "tests/test_document_types.py",
    ),
    "parsing": (
        "tests/test_parser.py",
        "tests/test_chunker.py",
        "tests/test_cleaning.py",
    ),
    "search": ("tests/test_search.py", "tests/test_semantic_search.py"),
    "qa": (
        "tests/test_qa.py",
        "tests/test_golden_spanish.py",
        "tests/test_quality_v034.py",
    ),
    "summaries": (
        "tests/test_summarizer.py",
        "tests/test_quality_v034.py",
    ),
    "study": (
        "tests/test_study.py",
        "tests/test_concepts.py",
        "tests/test_document_types.py",
        "tests/test_golden_spanish.py",
        "tests/test_quality_v034.py",
    ),
    "flashcards": (
        "tests/test_flashcards.py",
        "tests/test_concepts.py",
        "tests/test_document_types.py",
        "tests/test_golden_spanish.py",
        "tests/test_quality_v034.py",
    ),
    "exports": (
        "tests/test_export.py",
        "tests/test_obsidian.py",
    ),
    "ui": ("tests/test_app.py",),
    "quality": ("tests/test_quality_eval_runner.py",),
    "validation": ("tests/test_validation.py",),
}

AREA_FIXTURES = {
    "qa": (
        "long_technical_sentence",
        "mixed_technical_with_noise",
        "noisy_pressure_monitoring",
        "spanish_pneumatic_safety",
        "unsupported_cross_chunk_relation",
    ),
    "summaries": (
        "long_technical_sentence",
        "low_value_only_document",
        "mixed_technical_with_noise",
    ),
    "study": (
        "long_technical_sentence",
        "mixed_technical_with_noise",
        "noisy_pressure_monitoring",
        "spanish_pneumatic_safety",
        "general_document_types",
    ),
    "flashcards": (
        "long_technical_sentence",
        "mixed_technical_with_noise",
        "noisy_pressure_monitoring",
        "spanish_pneumatic_safety",
        "general_document_types",
    ),
    "quality": (
        "long_technical_sentence",
        "low_value_only_document",
        "mixed_technical_with_noise",
        "noisy_pressure_monitoring",
        "spanish_pneumatic_safety",
        "unsupported_cross_chunk_relation",
        "general_document_types",
    ),
    "search": ("mixed_technical_with_noise",),
    "core": ("general_document_types",),
}


def build_plan(profile: str, areas: tuple[str, ...] = ()) -> list[ValidationStep]:
    """Build a deterministic validation plan without executing it."""

    python = sys.executable
    compile_targets = ("app.py", "localdocs", "tests", "scripts")

    if profile == "fast":
        return [
            ValidationStep(
                "Compile application modules",
                (python, "-m", "compileall", "-q", "app.py", "localdocs", "scripts"),
            ),
            ValidationStep(
                "Run fast smoke tests",
                (
                    python,
                    "-m",
                    "pytest",
                    "-q",
                    "--disable-warnings",
                    "--maxfail=1",
                    *FAST_TESTS,
                ),
            ),
        ]

    if profile == "focused":
        if not areas:
            raise ValueError("Focused validation requires at least one area.")
        unknown = sorted(set(areas) - set(AREA_TESTS))
        if unknown:
            raise ValueError(f"Unknown focused area(s): {', '.join(unknown)}")

        tests = _ordered_unique(
            test
            for area in areas
            for test in AREA_TESTS[area]
        )
        fixtures = _ordered_unique(
            fixture
            for area in areas
            for fixture in AREA_FIXTURES.get(area, ())
        )
        steps = [
            ValidationStep(
                "Compile touched-area dependencies",
                (python, "-m", "compileall", "-q", *compile_targets),
            ),
            ValidationStep(
                f"Run focused tests ({', '.join(areas)})",
                (
                    python,
                    "-m",
                    "pytest",
                    "-q",
                    "--disable-warnings",
                    "--maxfail=1",
                    *tests,
                ),
            ),
        ]
        if fixtures:
            fixture_args = tuple(
                argument
                for fixture in fixtures
                for argument in ("--fixture", fixture)
            )
            steps.append(
                ValidationStep(
                    "Run focused quality fixtures",
                    (
                        python,
                        "scripts/run_quality_eval.py",
                        "--quiet",
                        *fixture_args,
                    ),
                )
            )
        return steps

    if profile == "full":
        return [
            ValidationStep(
                "Run full pytest suite",
                (python, "-m", "pytest", "-q"),
            ),
            ValidationStep(
                "Compile all Python modules",
                (python, "-m", "compileall", "-q", *compile_targets),
            ),
            ValidationStep(
                "Run all quality fixtures",
                (python, "scripts/run_quality_eval.py", "--quiet"),
            ),
        ]

    raise ValueError(f"Unknown validation profile: {profile}")


def run_plan(steps: list[ValidationStep], dry_run: bool = False) -> int:
    """Run validation steps in order and stop at the first failure."""

    environment = os.environ.copy()
    environment["OPENAI_API_KEY"] = ""

    for number, step in enumerate(steps, start=1):
        command_text = " ".join(_display_argument(part) for part in step.command)
        print(f"[{number}/{len(steps)}] {step.label}", flush=True)
        if dry_run:
            print(f"  {command_text}")
            continue
        completed = subprocess.run(
            step.command,
            cwd=ROOT,
            env=environment,
            check=False,
        )
        if completed.returncode:
            print(f"FAILED: {step.label}")
            return completed.returncode

    if dry_run:
        print("Validation plan only; no commands were run.")
    else:
        print(f"VALIDATION PASSED: {len(steps)} step(s)")
    return 0


def _ordered_unique(values) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _display_argument(value: str) -> str:
    return f'"{value}"' if " " in value else value


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the selected commands without running them.",
    )
    subparsers = parser.add_subparsers(dest="profile", required=True)
    subparsers.add_parser("fast", help="Compile and run a small smoke-test set.")
    focused = subparsers.add_parser(
        "focused",
        help="Validate one or more touched areas.",
    )
    focused.add_argument(
        "areas",
        nargs="+",
        choices=sorted(AREA_TESTS),
        help="Touched areas to validate.",
    )
    subparsers.add_parser(
        "full",
        help="Run pytest, compileall, and every deterministic quality fixture.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    areas = tuple(getattr(args, "areas", ()))
    try:
        steps = build_plan(args.profile, areas)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return run_plan(steps, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
