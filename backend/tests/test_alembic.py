import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_alembic_offline_upgrade_loads_env() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"alembic offline upgrade failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "CREATE TABLE alembic_version" in result.stdout
