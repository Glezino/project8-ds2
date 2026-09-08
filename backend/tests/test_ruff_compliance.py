import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _run_ruff(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ruff", *args],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )


def test_ruff_check_passes() -> None:
    result = _run_ruff("check", ".")
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_ruff_format_check_passes() -> None:
    result = _run_ruff("format", "--check", ".")
    assert result.returncode == 0, f"ruff format --check failed:\n{result.stdout}\n{result.stderr}"
