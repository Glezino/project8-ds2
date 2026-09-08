import ast
from pathlib import Path

ML_DIR = Path(__file__).resolve().parents[1] / "ml"


def _iter_ml_modules() -> list[Path]:
    return sorted(p for p in ML_DIR.rglob("*.py") if p.name != "__init__.py" or p.parent != ML_DIR)


def test_ml_has_no_fastapi_or_api_imports() -> None:
    forbidden = ("fastapi", "app.api", "app.main")

    for module in _iter_ml_modules():
        tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in forbidden, (
                        f"{module} imports forbidden module {alias.name}"
                    )
                    assert not alias.name.startswith("app.api"), (
                        f"{module} imports forbidden module {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                assert node.module.split(".")[0] not in forbidden, (
                    f"{module} imports forbidden module {node.module}"
                )
                assert not node.module.startswith("app.api"), (
                    f"{module} imports forbidden module {node.module}"
                )
