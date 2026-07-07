"""Load entity-verifier prompt corpora from YAML."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

_PACKAGE_DIR = Path(__file__).resolve().parent


def _read_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError("PyYAML is required to load entity-verifier prompt corpora") from exc
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        raise ValueError(f"{path} must not be empty")
    return payload


@lru_cache(maxsize=1)
def _load_sf_corpus_cached() -> dict[str, Any]:
    path = _PACKAGE_DIR / "sf_corpus.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping")
    return payload


@lru_cache(maxsize=1)
def _load_med_inv_corpus_cached() -> dict[str, Any]:
    path = _PACKAGE_DIR / "med_inv_corpus.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping")
    return payload


def load_sf_clinical_rules() -> list[str]:
    """Return clinical rules for the SeizureFrequency verifier prompt."""
    rules = _load_sf_corpus_cached().get("clinical_rules")
    if not isinstance(rules, list):
        raise ValueError("sf_corpus.yaml must contain clinical_rules list")
    return rules


def load_sf_worked_examples() -> list[dict[str, Any]]:
    """Return worked examples for the SeizureFrequency verifier prompt."""
    examples = _load_sf_corpus_cached().get("worked_examples")
    if not isinstance(examples, list):
        raise ValueError("sf_corpus.yaml must contain worked_examples list")
    return examples


def load_med_inv_clinical_rules() -> list[str]:
    """Return clinical rules for the Prescription/Investigations verifier prompt."""
    rules = _load_med_inv_corpus_cached().get("clinical_rules")
    if not isinstance(rules, list):
        raise ValueError("med_inv_corpus.yaml must contain clinical_rules list")
    return rules


def load_med_inv_worked_examples() -> list[dict[str, Any]]:
    """Return worked examples for the Prescription/Investigations verifier prompt."""
    examples = _load_med_inv_corpus_cached().get("worked_examples")
    if not isinstance(examples, list):
        raise ValueError("med_inv_corpus.yaml must contain worked_examples list")
    return examples
