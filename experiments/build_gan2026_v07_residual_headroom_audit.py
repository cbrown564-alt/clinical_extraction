"""Audit residual validation headroom for selector v0.7.

This is a validation-only analysis over saved selector rows. It asks which
selected-wrong rows already have a correct component output available, and
whether the tempting parseable-``other`` relaxation is safe. No holdout rows are
read, and no model calls are made.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
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
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_monthly_frequency,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

SOURCE_JSONL = (
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_7_"
    "validation750_no_call_replay_2026-06-15.jsonl"
)
RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_7_"
    "residual_headroom_audit_2026-06-15"
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
            "Validation-only residual headroom audit for selector v0.7; no "
            "holdout rows and no model calls."
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
    oracle_counter: Counter[str] = Counter()
    band_counter: Counter[str] = Counter()
    action_counter: Counter[str] = Counter()
    selected_wrong_records = []
    for row in selected_wrong:
        correct_components = tuple(
            component
            for component in ("deterministic", "consensus", "fresh_evidence")
            if row["score_layers"][component]["comparison"].get("purist_correct")
            is True
        )
        oracle_counter[_component_key(correct_components)] += 1
        band_counter[boundary_band(row["reference"]["gold_monthly_frequency"])] += 1
        action_counter[str(row["selector_action"])] += 1
        selected_wrong_records.append(_selected_wrong_record(row, correct_components))

    parseable_probe = _parseable_other_probe(rows)
    return {
        "rows": len(rows),
        "selected_correct": len(rows) - len(selected_wrong),
        "selected_wrong": len(selected_wrong),
        "selected_wrong_by_component_availability": dict(oracle_counter),
        "selected_wrong_by_band": dict(sorted(band_counter.items())),
        "selected_wrong_by_action": dict(action_counter),
        "oracle_correct_available": sum(
            count for key, count in oracle_counter.items() if key != "none"
        ),
        "oracle_correct_unavailable": oracle_counter["none"],
        "parseable_other_relaxation_probe": parseable_probe,
        "selected_wrong_records": selected_wrong_records,
    }


def _selected_wrong_record(
    row: dict[str, Any],
    correct_components: tuple[str, ...],
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
        "fresh_boundary_profile": row["decision_features"].get(
            "fresh_boundary_profile",
            [],
        ),
    }


def _parseable_other_probe(rows: list[dict[str, Any]]) -> dict[str, Any]:
    transitions: Counter[str] = Counter()
    bands: dict[str, Counter[str]] = defaultdict(Counter)
    examples = []
    for row in rows:
        if "uncertain_or_ambiguous_replacement:other" not in row["selector_gate"]:
            continue
        if row["fresh_evidence_label"] != row["consensus_label"]:
            continue
        if not _parseable_specific(row["fresh_evidence_label"]):
            continue
        transition = _transition_if_fresh_selected(row)
        transitions[transition] += 1
        band = boundary_band(row["reference"]["gold_monthly_frequency"])
        bands[band][transition] += 1
        examples.append(
            {
                "source_row_index": row["source_row_index"],
                "transition_if_accepted": transition,
                "gold_label": row["reference"]["gold_label"],
                "deterministic_label": row["deterministic_label"],
                "fresh_evidence_label": row["fresh_evidence_label"],
                "gold_band": band,
                "fresh_boundary_profile": row["decision_features"].get(
                    "fresh_boundary_profile",
                    [],
                ),
            }
        )
    return {
        "candidate_actions": sum(transitions.values()),
        "wrong_to_correct": transitions["wrong_to_correct"],
        "correct_to_wrong": transitions["correct_to_wrong"],
        "correct_to_correct": transitions["correct_to_correct"],
        "wrong_to_wrong": transitions["wrong_to_wrong"],
        "net_purist_gain": transitions["wrong_to_correct"]
        - transitions["correct_to_wrong"],
        "by_band": {key: dict(value) for key, value in sorted(bands.items())},
        "examples": examples,
        "decision": "reject_broad_parseable_other_relaxation",
    }


def _parseable_specific(label: str) -> bool:
    try:
        monthly = label_to_monthly_frequency(label)
    except Exception:
        return False
    return monthly not in (0.0, 1000.0)


def _transition_if_fresh_selected(row: dict[str, Any]) -> str:
    deterministic_correct = (
        row["score_layers"]["deterministic"]["comparison"].get("purist_correct")
        is True
    )
    fresh_correct = (
        row["score_layers"]["fresh_evidence"]["comparison"].get("purist_correct")
        is True
    )
    if not deterministic_correct and fresh_correct:
        return "wrong_to_correct"
    if deterministic_correct and not fresh_correct:
        return "correct_to_wrong"
    if deterministic_correct and fresh_correct:
        return "correct_to_correct"
    return "wrong_to_wrong"


def _component_key(components: tuple[str, ...]) -> str:
    return "+".join(components) if components else "none"


def _markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    probe = summary["parseable_other_relaxation_probe"]
    lines = [
        "# Gan 2026 Selector v0.7 Residual Headroom Audit",
        "",
        "Date: 2026-06-15",
        "",
        "This is a validation-only audit over saved v0.7 selector rows. It "
        "does not read locked test rows and does not make model calls.",
        "",
        "## Summary",
        "",
        f"- Rows: {summary['rows']}",
        f"- Selected correct: {summary['selected_correct']}/{summary['rows']}",
        f"- Selected wrong: {summary['selected_wrong']}",
        (
            "- Selected-wrong rows with a correct unselected component: "
            f"{summary['oracle_correct_available']}"
        ),
        (
            "- Selected-wrong rows with no correct component available: "
            f"{summary['oracle_correct_unavailable']}"
        ),
        f"- Selected wrong by band: `{summary['selected_wrong_by_band']}`",
        (
            "- Selected wrong by component availability: "
            f"`{summary['selected_wrong_by_component_availability']}`"
        ),
        "",
        "## Parseable Other Probe",
        "",
        "A tempting next relaxation is to accept all consensus+fresh-agreed "
        "replacement labels currently gated as parser-ambiguous `other` when "
        "they are actually parseable by the Gan label parser. This probe rejects "
        "that broad rule.",
        "",
        f"- Candidate actions: {probe['candidate_actions']}",
        f"- Wrong->correct: {probe['wrong_to_correct']}",
        f"- Correct->wrong: {probe['correct_to_wrong']}",
        f"- Correct->correct churn: {probe['correct_to_correct']}",
        f"- Wrong->wrong churn: {probe['wrong_to_wrong']}",
        f"- Net Purist gain: {probe['net_purist_gain']}",
        f"- By band: `{probe['by_band']}`",
        "",
        "## Selected-Wrong Component Availability",
        "",
        "| Components correct but not selected | Rows |",
        "| --- | ---: |",
    ]
    for key, count in summary["selected_wrong_by_component_availability"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "v0.7 leaves 22 validation rows wrong. Eleven have no correct "
            "component among deterministic, consensus, and fresh evidence, so "
            "selector changes alone cannot recover them. Eleven do have a "
            "correct unselected component: six where consensus and fresh are "
            "both correct, and five where only fresh is correct.",
            "",
            "The broad parseable-`other` relaxation is rejected: it would take "
            "27 actions but net -1 Purist (4 W->C, 5 C->W). The next selector "
            "must use a narrower, clinically meaningful profile feature, not "
            "parser compatibility alone.",
            "",
            "Decision: revise, not freeze. This audit identifies remaining "
            "selector headroom but does not produce a holdout-facing candidate.",
            "",
        ]
    )
    return "\n".join(lines)


def _register(summary: dict[str, Any]) -> None:
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID
    ]
    probe = summary["parseable_other_relaxation_probe"]
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
                "Validation-only residual analysis over saved v0.7 selector "
                "rows; no model calls and no holdout rows are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="selector_v0_7_residual_headroom_audit",
            cache_reuse_source=str(SOURCE_JSONL),
            primary_metrics={
                "selected_correct": summary["selected_correct"],
                "selected_wrong": summary["selected_wrong"],
                "oracle_correct_available": summary["oracle_correct_available"],
                "oracle_correct_unavailable": summary[
                    "oracle_correct_unavailable"
                ],
                "parseable_other_candidate_actions": probe["candidate_actions"],
                "parseable_other_wrong_to_correct": probe["wrong_to_correct"],
                "parseable_other_correct_to_wrong": probe["correct_to_wrong"],
                "parseable_other_net_purist_gain": probe["net_purist_gain"],
            },
            evidence_validity=(
                "Validation-only saved-output audit. Gold labels are used only "
                "for post-hoc scoring and transition accounting; no holdout rows "
                "are read."
            ),
            decision="revise",
            supersedes=(
                RUN_ID.replace(
                    "_residual_headroom_audit_",
                    "_validation750_no_call_replay_",
                ),
            ),
            claim_language_notes=(
                "Identifies residual selector headroom and rejects broad "
                "parseable-other relaxation as validation-negative. Not a "
                "holdout-facing candidate."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
