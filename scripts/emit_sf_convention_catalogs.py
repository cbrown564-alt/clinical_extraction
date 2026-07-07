#!/usr/bin/env python3
"""Emit Phase-2 convention catalog YAML tables with builder metadata."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CATALOG = (
    REPO
    / "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic"
    / "sf_surface_registry/catalog"
)
LEGACY = (
    REPO
    / "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic"
    / "sf_surface_registry/builders/_legacy_impl.py"
)


def _dump(path: Path, rules: list[dict[str, object]]) -> None:
    path.write_text(
        yaml.safe_dump({"rules": rules}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _rewrite_catalog() -> None:
    rewrite_path = CATALOG / "convention_rewrite.yaml"
    payload = yaml.safe_load(rewrite_path.read_text(encoding="utf-8"))
    rules: list[dict[str, object]] = []
    for entry in payload["rules"]:
        rule_id = entry["rule_id"]
        builder = rule_id
        if rule_id.startswith(("collapse_", "drop_", "rewrite_exact_")):
            builder = "operand_format_rewrite"
        rules.append(
            {
                "rule_id": rule_id,
                "phases": ["rewrite"],
                "builder": builder,
                "source_stack": "sf_surface_registry/builders/rewrite_builders.py",
            }
        )
    _dump(rewrite_path, rules)
    print(f"updated {rewrite_path} ({len(rules)} rules)")


def _noise_catalog() -> None:
    rules = [
        {
            "rule_id": "noise_vague_episode_phrase",
            "phases": ["noise"],
            "builder": "noise_branch_01",
        },
        {
            "rule_id": "noise_prompt_selection_phrase_set",
            "phases": ["noise"],
            "builder": "noise_branch_02",
        },
        {
            "rule_id": "noise_one_seizure_risk_counselling",
            "phases": ["noise"],
            "builder": "noise_branch_03",
        },
        {
            "rule_id": "noise_further_seizures_risk_counselling",
            "phases": ["noise"],
            "builder": "noise_branch_04",
        },
        {
            "rule_id": "noise_previous_seizures_phrase",
            "phases": ["noise"],
            "builder": "noise_branch_05",
        },
        {
            "rule_id": "noise_absence_contextual_history",
            "phases": ["noise"],
            "builder": "noise_branch_06",
        },
        {
            "rule_id": "noise_generic_around_three_per_month",
            "phases": ["noise"],
            "builder": "noise_branch_07",
        },
        {
            "rule_id": "noise_ftb_dated_or_asleep_context",
            "phases": ["noise"],
            "builder": "noise_branch_08",
        },
        {
            "rule_id": "noise_canonical_seizure_free_contextual_rate",
            "phases": ["noise"],
            "builder": "noise_branch_09",
        },
        {
            "rule_id": "noise_keep_canonical_seizure_free",
            "phases": ["noise"],
            "builder": "noise_keep_canonical_seizure_free",
        },
        {
            "rule_id": "noise_generic_contextual_rate",
            "phases": ["noise"],
            "builder": "noise_branch_11",
        },
        {
            "rule_id": "noise_contextual_seizure_free_phrase",
            "phases": ["noise"],
            "builder": "noise_branch_12",
        },
        {
            "rule_id": "noise_historical_comparator_seizure",
            "phases": ["noise"],
            "builder": "noise_branch_13",
        },
    ]
    path = CATALOG / "convention_noise.yaml"
    _dump(path, rules)
    print(f"wrote {path} ({len(rules)} rules)")


def _residual_catalog() -> None:
    rules = [
        {
            "rule_id": "residual_all_patterns",
            "phases": ["residual_add"],
            "builder": "residual_all_patterns",
            "source_stack": "sf_surface_registry/builders/_legacy_impl.py",
        }
    ]
    path = CATALOG / "convention_residual.yaml"
    _dump(path, rules)
    print(f"wrote {path} ({len(rules)} rules)")


def main() -> None:
    _rewrite_catalog()
    _noise_catalog()
    _residual_catalog()


if __name__ == "__main__":
    main()
