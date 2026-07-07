"""Load clinical-findings extraction prompt corpora from YAML."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

_PACKAGE_DIR = Path(__file__).resolve().parent


def _read_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError("PyYAML is required to load clinical-findings prompt corpora") from exc
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        raise ValueError(f"{path} must not be empty")
    return payload


@lru_cache(maxsize=1)
def _load_extraction_prompt_corpus_cached() -> dict[str, Any]:
    path = _PACKAGE_DIR / "extraction_prompt_corpus.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping")
    return payload


def load_extraction_prompt_corpus() -> dict[str, Any]:
    """Return static stage-1 clinical-findings extraction prompt fields."""
    return _load_extraction_prompt_corpus_cached()
