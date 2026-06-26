#!/usr/bin/env python3
"""Generate catalog/extract.yaml from live Stack A RuleSpec objects."""

from __future__ import annotations

from pathlib import Path

import yaml

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    RuleExample,
    RuleSpec,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.anchor import (
    ANCHOR_RULES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import (
    CHANGE_RULES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.rate import (
    RATE_RULES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.seizure_free import (
    SEIZURE_FREE_RULES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.temporal import (
    TEMPORAL_RULES,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = (
    REPO_ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "deterministic"
    / "sf_surface_registry"
    / "catalog"
    / "extract.yaml"
)

_RULE_SETS: dict[str, list[RuleSpec]] = {
    "anchor": ANCHOR_RULES,
    "rate": RATE_RULES,
    "seizure_free": SEIZURE_FREE_RULES,
    "change": CHANGE_RULES,
    "temporal": TEMPORAL_RULES,
}

_SOURCE_STACK = {
    "anchor": "rules/anchor.py",
    "rate": "rules/rate_builders.py",
    "seizure_free": "rules/seizure_free.py",
    "change": "rules/change.py",
    "temporal": "rules/temporal.py",
}


def _example_to_dict(example: RuleExample) -> dict[str, object]:
    entry: dict[str, object] = {"text": example.text}
    if example.expected_evidence is not None:
        entry["expected_evidence"] = example.expected_evidence
    if example.expected_attributes is not None:
        entry["expected_attributes"] = dict(example.expected_attributes)
    if example.anti_example:
        entry["anti_example"] = True
    if example.note is not None:
        entry["note"] = example.note
    return entry


def _spec_to_entry(spec: RuleSpec, *, rule_set: str, order: int) -> dict[str, object]:
    entry: dict[str, object] = {
        "rule_id": spec.rule_id,
        "phases": ["extract"],
        "rule_set": rule_set,
        "order": order,
        "group": spec.group.value,
        "portability": spec.portability.value,
        "description": spec.description,
        "builder": spec.build.__name__,
        "source_stack": _SOURCE_STACK[rule_set],
        "examples": [_example_to_dict(ex) for ex in spec.examples],
    }
    if spec.provenance is not None:
        entry["provenance"] = spec.provenance
    if spec.exclude:
        entry["exclude"] = [fn.__name__ for fn in spec.exclude]
    return entry


def build_extract_catalog() -> dict[str, object]:
    rules: list[dict[str, object]] = []
    for rule_set, specs in _RULE_SETS.items():
        for order, spec in enumerate(specs):
            rules.append(_spec_to_entry(spec, rule_set=rule_set, order=order))
    return {"rules": rules}


def main() -> None:
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(
        yaml.safe_dump(build_extract_catalog(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"wrote {CATALOG_PATH} ({len(build_extract_catalog()['rules'])} rules)")


if __name__ == "__main__":
    main()
