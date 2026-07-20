"""Load structured key-entity prompt corpora from YAML."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

_PACKAGE_DIR = Path(__file__).resolve().parent


def _read_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError("PyYAML is required to load key-entity prompt corpora") from exc
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        raise ValueError(f"{path} must not be empty")
    return payload


@lru_cache(maxsize=1)
def _load_structured_worked_examples_cached() -> list[dict[str, Any]]:
    path = _PACKAGE_DIR / "structured_worked_examples.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a list of worked examples")
    return payload


@lru_cache(maxsize=1)
def _load_dedup_fact_decision_tables_cached() -> dict[str, list[dict[str, str]]]:
    path = _PACKAGE_DIR / "dedup_fact_decision_tables.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping of family decision tables")
    return payload


@lru_cache(maxsize=1)
def _load_dedup_fact_worked_examples_cached() -> list[dict[str, Any]]:
    path = _PACKAGE_DIR / "dedup_fact_worked_examples.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a list of worked examples")
    return payload


@lru_cache(maxsize=1)
def _load_dedup_fact_guidance_cached() -> list[str]:
    path = _PACKAGE_DIR / "dedup_fact_guidance.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping with fact_guidance")
    guidance = payload.get("fact_guidance")
    if not isinstance(guidance, list):
        raise ValueError(f"{path} must contain fact_guidance list")
    return guidance


@lru_cache(maxsize=1)
def _load_qwen_compact_worked_examples_cached() -> list[dict[str, Any]]:
    path = _PACKAGE_DIR / "qwen_compact_worked_examples.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a list of worked examples")
    return payload


def load_worked_examples() -> list[dict[str, Any]]:
    """Return the structured key-entity worked examples prompt corpus."""
    return _load_structured_worked_examples_cached()


def load_dedup_fact_decision_tables() -> dict[str, list[dict[str, str]]]:
    """Return de-duplicated clinical-fact decision tables keyed by family."""
    return _load_dedup_fact_decision_tables_cached()


def load_dedup_fact_worked_examples() -> list[dict[str, Any]]:
    """Return worked examples for the de-duplicated clinical-facts route."""
    return _load_dedup_fact_worked_examples_cached()


def load_dedup_fact_guidance() -> list[str]:
    """Return family-agnostic clinical-fact guidance for dedup prompts."""
    return _load_dedup_fact_guidance_cached()


def load_qwen_compact_worked_examples() -> list[dict[str, Any]]:
    """Return worked examples for the qwen_compact structured prompt profile."""
    return _load_qwen_compact_worked_examples_cached()
