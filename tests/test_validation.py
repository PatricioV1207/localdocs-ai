import sys

import pytest

from scripts.validate import AREA_FIXTURES, FAST_TESTS, build_plan


def test_fast_plan_uses_small_smoke_suite_without_quality_evals():
    steps = build_plan("fast")

    assert len(steps) == 2
    assert steps[0].command[:4] == (sys.executable, "-m", "compileall", "-q")
    assert set(FAST_TESTS).issubset(steps[1].command)
    assert all("run_quality_eval.py" not in step.command for step in steps)


def test_focused_plan_deduplicates_tests_and_selects_relevant_fixtures():
    steps = build_plan("focused", ("qa", "study"))

    pytest_command = steps[1].command
    assert pytest_command.count("tests/test_golden_spanish.py") == 1
    assert pytest_command.count("tests/test_quality_v034.py") == 1

    quality_command = steps[2].command
    assert "--quiet" in quality_command
    for fixture in set(AREA_FIXTURES["qa"]) | set(AREA_FIXTURES["study"]):
        assert fixture in quality_command


def test_focused_non_quality_area_skips_fixture_runner():
    steps = build_plan("focused", ("parsing",))

    assert len(steps) == 2
    assert "tests/test_parser.py" in steps[1].command
    assert "tests/test_chunker.py" in steps[1].command


def test_full_plan_preserves_all_three_release_gates():
    steps = build_plan("full")

    assert [step.label for step in steps] == [
        "Run full pytest suite",
        "Compile all Python modules",
        "Run all quality fixtures",
    ]
    assert steps[0].command == (sys.executable, "-m", "pytest", "-q")
    assert steps[2].command[-1] == "--quiet"


def test_focused_plan_rejects_missing_or_unknown_areas():
    with pytest.raises(ValueError, match="requires at least one area"):
        build_plan("focused")
    with pytest.raises(ValueError, match="Unknown focused area"):
        build_plan("focused", ("unknown",))
