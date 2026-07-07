"""Load extract-phase catalog metadata for Stack A RuleSpec assembly."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from ..rule_metadata import Portability, RuleExample, RuleGroup

_CATALOG_PATH = Path(__file__).resolve().parent / "catalog" / "extract.yaml"


@dataclass(frozen=True)
class ExtractCatalogEntry:
    rule_id: str
    rule_set: str
    order: int
    group: RuleGroup
    portability: Portability
    description: str
    builder: str
    source_stack: str
    examples: tuple[RuleExample, ...]
    provenance: str | None = None
    exclude: tuple[str, ...] = ()
    pattern_id: str | None = None


def _parse_example(entry: dict[str, object]) -> RuleExample:
    attrs = entry.get("expected_attributes")
    return RuleExample(
        text=str(entry["text"]),
        expected_evidence=(
            str(entry["expected_evidence"]) if entry.get("expected_evidence") is not None else None
        ),
        expected_attributes=dict(attrs) if isinstance(attrs, dict) else None,
        anti_example=bool(entry.get("anti_example")),
        note=str(entry["note"]) if entry.get("note") is not None else None,
    )


def _parse_entry(entry: dict[str, object]) -> ExtractCatalogEntry:
    exclude_raw = entry.get("exclude") or []
    return ExtractCatalogEntry(
        rule_id=str(entry["rule_id"]),
        rule_set=str(entry["rule_set"]),
        order=int(entry["order"]),
        group=RuleGroup(str(entry["group"])),
        portability=Portability(str(entry["portability"])),
        description=str(entry["description"]),
        builder=str(entry["builder"]),
        source_stack=str(entry["source_stack"]),
        examples=tuple(_parse_example(ex) for ex in entry.get("examples") or []),
        provenance=str(entry["provenance"]) if entry.get("provenance") is not None else None,
        exclude=tuple(str(name) for name in exclude_raw),
        pattern_id=str(entry["pattern_id"]) if entry.get("pattern_id") is not None else None,
    )


@lru_cache(maxsize=1)
def load_extract_catalog() -> tuple[ExtractCatalogEntry, ...]:
    payload = yaml.safe_load(_CATALOG_PATH.read_text(encoding="utf-8")) or {}
    entries = [_parse_entry(entry) for entry in payload.get("rules") or []]
    return tuple(sorted(entries, key=lambda e: (e.rule_set, e.order)))


def extract_rules_for_set(rule_set: str) -> tuple[ExtractCatalogEntry, ...]:
    return tuple(entry for entry in load_extract_catalog() if entry.rule_set == rule_set)
