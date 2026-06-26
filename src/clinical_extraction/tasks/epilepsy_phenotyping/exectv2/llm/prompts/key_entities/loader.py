"""Load structured key-entity worked examples from YAML."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

_YAML_PATH = Path(__file__).resolve().parent / "structured_worked_examples.yaml"


@lru_cache(maxsize=1)
def _load_cached() -> list[dict[str, Any]]:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "PyYAML is required to load structured worked examples"
        ) from exc
    text = _YAML_PATH.read_text(encoding="utf-8")
    payload = yaml.safe_load(text)
    if not isinstance(payload, list):
        raise ValueError(f"{_YAML_PATH} must contain a list of worked examples")
    return payload


def load_worked_examples() -> list[dict[str, Any]]:
    """Return the structured key-entity worked examples prompt corpus."""
    return _load_cached()
