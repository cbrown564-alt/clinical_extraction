#!/usr/bin/env python3
"""Generate SF surface rule index and Phase-0 convention catalog from live stacks."""

from __future__ import annotations

import re
from importlib import import_module
from pathlib import Path

import yaml

sf_rules = import_module(
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic."
    "sf_surface_registry.adapters.extraction"
)

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "docs" / "plans" / "sf_surface_rule_index.yaml"
CATALOG_DIR = (
    REPO_ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "deterministic"
    / "sf_surface_registry"
    / "catalog"
)
_CONVENTION_PATH = (
    REPO_ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "deterministic"
    / "conventions"
    / "seizure_frequency.py"
)
_PROJECTION_PATH = (
    REPO_ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "reports"
    / "projection_rule_attribution.py"
)
_REWRITE_RULE_ID = re.compile(r'"(rewrite_[a-z0-9_]+|drop_[a-z0-9_]+|collapse_[a-z0-9_]+)"')
_PROJECTION_RULE_ID = re.compile(r'_(?:spec|quarantined_spec)\(\s*"([^"]+)"\s*,\s*([A-Z_]+)\.name')
_ENTITY_NAME = {
    "DIAGNOSIS": "Diagnosis",
    "SEIZURE_FREQUENCY": "SeizureFrequency",
    "PRESCRIPTION": "Prescription",
    "INVESTIGATIONS": "Investigations",
}
_EXTRACT_RULE_SETS = (
    sf_rules.ANCHOR_RULES,
    sf_rules.RATE_RULES,
    sf_rules.SEIZURE_FREE_RULES,
    sf_rules.CHANGE_RULES,
    sf_rules.TEMPORAL_RULES,
)


def _collect_extract_rule_ids() -> list[str]:
    ids: list[str] = []
    for rule_set in _EXTRACT_RULE_SETS:
        for spec in rule_set:
            ids.append(spec.rule_id)
    return sorted(set(ids))


def _collect_convention_rewrite_rule_ids() -> list[str]:
    text = _CONVENTION_PATH.read_text(encoding="utf-8")
    return sorted(set(_REWRITE_RULE_ID.findall(text)))


def _collect_projection_rule_ids(*, entity: str | None = None) -> list[str]:
    text = _PROJECTION_PATH.read_text(encoding="utf-8")
    ids: list[str] = []
    for rule_id, entity_symbol in _PROJECTION_RULE_ID.findall(text):
        mapped_entity = _ENTITY_NAME.get(entity_symbol, entity_symbol)
        if entity is None or mapped_entity == entity:
            ids.append(rule_id)
    return sorted(set(ids))


def _build_rule_index() -> dict[str, object]:
    extract = _collect_extract_rule_ids()
    convention = _collect_convention_rewrite_rule_ids()
    projection_sf = _collect_projection_rule_ids(entity="SeizureFrequency")
    projection_all = _collect_projection_rule_ids()
    return {
        "generated_from": "scripts/generate_sf_surface_rule_index.py",
        "stacks": {
            "extract": {
                "path": "deterministic/rules/",
                "phase": "extract",
                "rule_count": len(extract),
                "rule_ids": extract,
            },
            "convention_rewrite": {
                "path": "deterministic/conventions/seizure_frequency.py",
                "phase": "rewrite",
                "rule_count": len(convention),
                "rule_ids": convention,
            },
            "projection": {
                "path": "reports/projection_rule_attribution.py",
                "phase": "project",
                "rule_count": len(projection_all),
                "rule_ids": projection_all,
                "seizure_frequency_rule_count": len(projection_sf),
                "seizure_frequency_rule_ids": projection_sf,
            },
        },
        "total_unique_rule_ids": len(set(extract) | set(convention) | set(projection_all)),
    }


def _catalog_payload(rules: list[dict[str, object]]) -> str:
    return yaml.safe_dump(
        {"rules": rules},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )


def main() -> None:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        yaml.safe_dump(_build_rule_index(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    rewrite_entries = [
        {
            "rule_id": rule_id,
            "phases": ["rewrite"],
            "source_stack": "conventions/seizure_frequency.py",
        }
        for rule_id in _collect_convention_rewrite_rule_ids()
    ]
    (CATALOG_DIR / "convention_rewrite.yaml").write_text(
        _catalog_payload(rewrite_entries),
        encoding="utf-8",
    )
    from generate_extract_catalog import build_extract_catalog

    (CATALOG_DIR / "extract.yaml").write_text(
        yaml.safe_dump(build_extract_catalog(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"wrote {INDEX_PATH}")
    print(f"wrote {CATALOG_DIR / 'convention_rewrite.yaml'}")
    print(f"wrote {CATALOG_DIR / 'extract.yaml'}")


if __name__ == "__main__":
    main()
