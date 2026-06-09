import subprocess
import sys
from pathlib import Path

from scripts.run_quality_eval import run_all


ROOT = Path(__file__).resolve().parents[1]


def test_quality_eval_report_passes_all_bundled_fixtures():
    report = run_all()

    assert report.passed is True
    assert report.failure_count == 0
    assert report.check_count > 0
    assert {result.area for result in report.results} >= {
        "study questions",
        "flashcards",
        "source quality",
    }


def test_quality_eval_cli_returns_success_and_summary():
    completed = subprocess.run(
        [sys.executable, "scripts/run_quality_eval.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "QUALITY EVAL PASSED" in completed.stdout
    assert "source quality" in completed.stdout


def test_quality_eval_quiet_cli_hides_passing_area_rows():
    expected_checks = run_all().check_count
    completed = subprocess.run(
        [sys.executable, "scripts/run_quality_eval.py", "--quiet"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stdout.strip() == f"QUALITY EVAL PASSED: {expected_checks} checks"


def test_quality_eval_cli_fails_when_expected_file_is_missing(tmp_path):
    fixtures_dir = tmp_path / "fixtures"
    expected_dir = tmp_path / "expected"
    fixtures_dir.mkdir()
    expected_dir.mkdir()
    (fixtures_dir / "missing_expected.json").write_text(
        """
{
  "schema_version": 1,
  "name": "missing expected",
  "chunks": [{"chunk_index": 1, "text": "Useful technical evidence."}],
  "qa_cases": []
}
""".strip(),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_quality_eval.py",
            "--fixtures-dir",
            str(fixtures_dir),
            "--expected-dir",
            str(expected_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "QUALITY EVAL FAILED" in completed.stdout
    assert "Missing expected file" in completed.stdout
