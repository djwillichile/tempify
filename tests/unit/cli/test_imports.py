"""Architectural test: CLI must only import from tempify.pipeline."""

from __future__ import annotations

import ast
from pathlib import Path

CLI_SRC_DIR = Path(__file__).resolve().parents[3] / "src" / "tempify" / "cli"

FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "tempify.detection",
    "tempify.io",
    "tempify.interpolation",
    "tempify.validation",
)


def _iter_imports(src: str) -> set[str]:
    tree = ast.parse(src)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                names.add(node.module)
    return names


def test_cli_imports_only_pipeline() -> None:
    """No CLI source file may import from forbidden layers directly."""
    offenders: dict[str, set[str]] = {}
    for py_file in CLI_SRC_DIR.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        imports = _iter_imports(text)
        bad = {
            imp for imp in imports if any(imp.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
        }
        if bad:
            offenders[str(py_file)] = bad
    assert not offenders, f"CLI files import forbidden tempify layers directly: {offenders}"
