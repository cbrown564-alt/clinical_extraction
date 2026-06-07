from __future__ import annotations

import importlib
import tomllib
from pathlib import Path


def test_project_console_scripts_import() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]

    failures: list[str] = []
    for name, target in scripts.items():
        module_name, _, attr = target.partition(":")
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - assertion reports details
            failures.append(f"{name}: failed to import {module_name}: {exc!r}")
            continue
        if attr and not hasattr(module, attr):
            failures.append(f"{name}: {module_name} has no {attr!r}")

    assert failures == []
