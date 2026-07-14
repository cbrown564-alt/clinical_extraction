"""Load the retained Diagnosis decomposer prompt corpus from YAML."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

_PACKAGE_DIR = Path(__file__).resolve().parent


def _read_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "PyYAML is required to load diagnosis-verification prompt corpora"
        ) from exc
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        raise ValueError(f"{path} must not be empty")
    return payload


@lru_cache(maxsize=1)
def _load_corpus_cached() -> dict[str, Any]:
    path = _PACKAGE_DIR / "corpus.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping")
    return payload


def load_clinical_rules() -> list[str]:
    """Return clinical rules for the Diagnosis decomposer prompt."""
    rules = _load_corpus_cached().get("clinical_rules")
    if not isinstance(rules, list):
        raise ValueError("corpus.yaml must contain clinical_rules list")
    return rules


def load_resolution_candidate_rules() -> list[str]:
    """Return the opt-in dev140 Diagnosis resolution candidate rules."""

    path = _PACKAGE_DIR / "resolution_candidate_rules.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping")
    rules = payload.get("clinical_rules")
    if not isinstance(rules, list):
        raise ValueError("resolution_candidate_rules.yaml must contain clinical_rules list")
    return rules


def load_worked_examples() -> list[dict[str, Any]]:
    """Return worked examples for the Diagnosis decomposer prompt."""
    examples = _load_corpus_cached().get("worked_examples")
    if not isinstance(examples, list):
        raise ValueError("corpus.yaml must contain worked_examples list")
    return examples
