"""Load and validate SF surface catalog YAML tables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from .types import SurfacePhase, SurfaceRule

_CATALOG_DIR = Path(__file__).resolve().parent / "catalog"


def catalog_dir() -> Path:
    return _CATALOG_DIR


@lru_cache(maxsize=1)
def load_all_catalog_rules() -> tuple[SurfaceRule, ...]:
    rules: list[SurfaceRule] = []
    for path in sorted(_CATALOG_DIR.glob("*.yaml")):
        rules.extend(_load_catalog_file(path))
    return tuple(rules)


def _load_catalog_file(path: Path) -> list[SurfaceRule]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = payload.get("rules") or []
    loaded: list[SurfaceRule] = []
    for entry in entries:
        phases = frozenset(SurfacePhase(value) for value in entry.get("phases") or [])
        loaded.append(
            SurfaceRule(
                rule_id=str(entry["rule_id"]),
                phases=phases,
                pattern_id=entry.get("pattern_id"),
                builder=entry.get("builder"),
                quarantine_family=entry.get("quarantine_family"),
                source_stack=entry.get("source_stack"),
            )
        )
    return loaded


def validate_unique_rule_ids(rules: tuple[SurfaceRule, ...] | None = None) -> None:
    seen: set[str] = set()
    duplicates: list[str] = []
    for rule in rules if rules is not None else load_all_catalog_rules():
        if rule.rule_id in seen:
            duplicates.append(rule.rule_id)
        seen.add(rule.rule_id)
    if duplicates:
        raise ValueError(f"Duplicate rule_id values in catalog: {sorted(set(duplicates))}")


def rules_for_phase(phase: SurfacePhase) -> tuple[SurfaceRule, ...]:
    return tuple(rule for rule in load_all_catalog_rules() if phase in rule.phases)


@lru_cache(maxsize=1)
def quarantined_projection_families() -> frozenset[str]:
    """Return quarantine_family values from the projection catalog (single source)."""

    families: set[str] = set()
    for rule in load_all_catalog_rules():
        if rule.quarantine_family:
            families.add(rule.quarantine_family)
    return frozenset(families)


def projection_sf_rule_ids() -> frozenset[str]:
    """Rule IDs registered under catalog/projection_sf.yaml."""

    path = _CATALOG_DIR / "projection_sf.yaml"
    return frozenset(rule.rule_id for rule in _load_catalog_file(path))
