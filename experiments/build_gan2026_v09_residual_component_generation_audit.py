"""Audit component-generation needs in selector v0.9 residual errors.

This is a validation-only analysis over saved selector rows. It asks whether the
remaining v0.9 selected errors are still selector-addressable, or whether the
component set itself lacks a Purist-correct answer. No holdout rows are read and
no model calls are made.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import boundary_band

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

SOURCE_JSONL = (
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "validation750_no_call_replay_2026-06-15.jsonl"
)
RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "residual_component_generation_audit_2026-06-15"
)
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"


def main() -> None:
    rows = _load_jsonl(SOURCE_JSONL)
    summary = _audit(rows)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Validation-only residual audit for selector v0.9, focused on "
            "component-generation failures after unknown-frequency policy work."
        ),
        "source_artifact": str(SOURCE_JSONL),
        "summary": summary,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(summary)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected_wrong = [
        row
        for row in rows
        if row["score_layers"]["selected"]["comparison"].get("purist_correct")
        is not True
    ]
    availability_counter: Counter[str] = Counter()
    band_counter: Counter[str] = Counter()
    action_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()
    no_correct_category_counter: Counter[str] = Counter()
    records = []

    for row in selected_wrong:
        correct_components = _correct_components(row)
        availability_key = _component_key(correct_components)
        categories = _categories(row, correct_components)
        availability_counter[availability_key] += 1
        band_counter[boundary_band(row["reference"]["gold_monthly_frequency"])] += 1
        action_counter[str(row["selector_action"])] += 1
        category_counter.update(categories)
        if not correct_components:
            no_correct_category_counter.update(categories)
        records.append(_selected_wrong_record(row, correct_components, categories))

    correct_available = sum(
        count for key, count in availability_counter.items() if key != "none"
    )
    no_correct = availability_counter["none"]
    selected_correct = len(rows) - len(selected_wrong)
    return {
        "rows": len(rows),
        "selected_correct": selected_correct,
        "selected_wrong": len(selected_wrong),
        "selected_wrong_by_component_availability": dict(availability_counter),
        "selected_wrong_by_band": dict(sorted(band_counter.items())),
        "selected_wrong_by_action": dict(action_counter),
        "selected_wrong_by_category": dict(sorted(category_counter.items())),
        "no_correct_component_by_category": dict(
            sorted(no_correct_category_counter.items())
        ),
        "correct_component_available": correct_available,
        "no_correct_component": no_correct,
        "selector_only_oracle_correct": selected_correct + correct_available,
        "residual_selector_only_headroom": correct_available,
        "residual_component_generation_required": no_correct,
        "selected_wrong_records": records,
    }


def _correct_components(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        component
        for component in ("deterministic", "consensus", "fresh_evidence")
        if row["score_layers"][component]["comparison"].get("purist_correct")
        is True
    )


def _categories(
    row: dict[str, Any],
    correct_components: tuple[str, ...],
) -> list[str]:
    gold = _lower(row["reference"]["gold_label"])
    selected = _lower(row["selected_label"])
    deterministic = _lower(row["deterministic_label"])
    consensus = _lower(row["consensus_label"])
    fresh = _lower(row["fresh_evidence_label"])
    profile = " ".join(
        _lower(item)
        for item in row["decision_features"].get("fresh_boundary_profile", [])
    )
    gold_band = boundary_band(row["reference"]["gold_monthly_frequency"])
    labels = " ".join((selected, deterministic, consensus, fresh, profile))

    categories: list[str] = []
    if gold_band == "band_unknown" and "seizure free" in labels:
        categories.append("last_event_or_seizure_free_overinfer_unknown")
    if gold_band == "band_unknown" and "unknown" not in selected and " per " in labels:
        categories.append("unknown_over_quantified_rate")
    if "cluster" in gold and ("cluster" not in selected or "cluster" not in fresh):
        categories.append("cluster_burden_component_failure")
    if correct_components == ("fresh_evidence",):
        categories.append("fresh_only_correct_candidate")
    if correct_components == ("consensus", "fresh_evidence"):
        categories.append("consensus_fresh_correct_but_blocked")
    if (
        gold_band != "band_unknown"
        and ("highest active" in profile or "denominator/window" in profile)
    ):
        categories.append("highest_semiology_or_denominator_conflict")
    if not correct_components and not categories:
        categories.append("other_component_generation_failure")
    if correct_components and not categories:
        categories.append("other_selector_headroom")
    return categories


def _selected_wrong_record(
    row: dict[str, Any],
    correct_components: tuple[str, ...],
    categories: list[str],
) -> dict[str, Any]:
    return {
        "source_row_index": row["source_row_index"],
        "gold_label": row["reference"]["gold_label"],
        "gold_band": boundary_band(row["reference"]["gold_monthly_frequency"]),
        "deterministic_label": row["deterministic_label"],
        "consensus_label": row["consensus_label"],
        "fresh_evidence_label": row["fresh_evidence_label"],
        "selected_label": row["selected_label"],
        "selector_action": row["selector_action"],
        "selector_gate": row["selector_gate"],
        "correct_components": list(correct_components),
        "audit_categories": categories,
        "fresh_boundary_profile": row["decision_features"].get(
            "fresh_boundary_profile",
            [],
        ),
    }


def _component_key(components: tuple[str, ...]) -> str:
    return "+".join(components) if components else "none"


def _lower(value: Any) -> str:
    return str(value or "").lower()


def _markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gan 2026 Selector v0.9 Residual Component-Generation Audit",
        "",
        "Date: 2026-06-15",
        "",
        "This is a validation-only audit over saved v0.9 selector rows. It "
        "does not read locked test rows and does not make model calls.",
        "",
        "## Summary",
        "",
        f"- Rows: {summary['rows']}",
        f"- Selected correct: {summary['selected_correct']}/{summary['rows']}",
        f"- Selected wrong: {summary['selected_wrong']}",
        (
            "- Selected-wrong rows with a correct unselected component: "
            f"{summary['correct_component_available']}"
        ),
        (
            "- Selected-wrong rows with no correct component available: "
            f"{summary['no_correct_component']}"
        ),
        (
            "- Selector-only oracle ceiling with current components: "
            f"{summary['selector_only_oracle_correct']}/{summary['rows']}"
        ),
        (
            "- Residual selector-only headroom: "
            f"{summary['residual_selector_only_headroom']} rows"
        ),
        (
            "- Residual component-generation required: "
            f"{summary['residual_component_generation_required']} rows"
        ),
        f"- Selected wrong by band: `{summary['selected_wrong_by_band']}`",
        (
            "- Selected wrong by component availability: "
            f"`{summary['selected_wrong_by_component_availability']}`"
        ),
        f"- Selected wrong by category: `{summary['selected_wrong_by_category']}`",
        "",
        "## Component Availability",
        "",
        "| Components correct but not selected | Rows |",
        "| --- | ---: |",
    ]
    for key, count in summary["selected_wrong_by_component_availability"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Unknown-Frequency Residual",
            "",
            "Yujian's clarification says unknown is usually safer when either "
            "the seizure count or the relevant time period is unclear. The "
            "v0.9 residual shows this is no longer mainly a selector problem: "
            "several unknown-boundary rows still have no Purist-correct "
            "available component because all sources over-infer from last-event, "
            "seizure-free, or underspecified recent-rate evidence.",
            "",
            "The largest no-correct residual categories are:",
            "",
            "| Category | Rows |",
            "| --- | ---: |",
        ]
    )
    for key, count in summary["no_correct_component_by_category"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "v0.9 leaves 17 validation rows wrong. Only 6 are still "
            "selector-addressable with the current deterministic, consensus, "
            "and fresh-evidence outputs. Even an oracle selector over these "
            "three components would top out at 739/750.",
            "",
            "The remaining 11 rows require better component generation. The "
            "highest-value next design should teach the component layer to "
            "preserve unknown when count/window is underspecified, avoid "
            "converting last-event-only evidence into seizure-free durations, "
            "and represent cluster burden when the gold label carries a "
            "cluster axis.",
            "",
            "Decision: revise, not freeze. Continue development on validation "
            "component generation rather than adding selector micro-gates.",
            "",
        ]
    )
    return "\n".join(lines)


def _register(summary: dict[str, Any]) -> None:
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID
    ]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
            ),
            date="2026-06-15",
            pipeline_family="consensus_fresh_agreement_selector_residual_audit",
            split="validation",
            row_count=summary["rows"],
            model="none",
            model_role=(
                "Validation-only residual analysis over saved v0.9 selector "
                "rows; no model calls and no holdout rows are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="selector_v0_9_residual_component_generation_audit",
            cache_reuse_source=str(SOURCE_JSONL),
            primary_metrics={
                "selected_correct": summary["selected_correct"],
                "selected_wrong": summary["selected_wrong"],
                "correct_component_available": summary[
                    "correct_component_available"
                ],
                "no_correct_component": summary["no_correct_component"],
                "selector_only_oracle_correct": summary[
                    "selector_only_oracle_correct"
                ],
                "residual_selector_only_headroom": summary[
                    "residual_selector_only_headroom"
                ],
                "residual_component_generation_required": summary[
                    "residual_component_generation_required"
                ],
            },
            evidence_validity=(
                "Validation-only saved-output audit. Gold labels are used only "
                "for post-hoc component availability and residual taxonomy; no "
                "holdout rows are read."
            ),
            decision="revise",
            supersedes=(
                "gan2026_consensus_fresh_agreement_selector_v0_9_"
                "validation750_no_call_replay_2026-06-15",
            ),
            claim_language_notes=(
                "Identifies component-generation bottlenecks in the v0.9 "
                "validation residual, especially unknown-frequency over-"
                "inference. Not a holdout-facing candidate."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
