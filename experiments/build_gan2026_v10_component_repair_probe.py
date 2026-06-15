"""Probe deterministic component repairs after selector v0.9.

This validation-only no-call replay tests whether the v0.9 residual can be
improved by rewriting fresh-evidence last-event/seizure-free outputs to
``unknown`` before the existing selector sees them. It is intentionally a probe:
the residual audit suggested a tempting repair, but the same pattern may damage
valid seizure-free rows.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    consensus_fresh_agreement_selector as selector,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_monthly_frequency,
)

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
    "gan2026_consensus_fresh_agreement_selector_v0_10_"
    "component_repair_probe_2026-06-15"
)
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"


@dataclass(frozen=True)
class RepairRule:
    rule_id: str
    description: str
    repair: Callable[[Mapping[str, Any]], str | None]


REPAIR_RULES: tuple[RepairRule, ...] = (
    RepairRule(
        rule_id="seizure_free_last_event_to_unknown",
        description=(
            "Rewrite fresh seizure-free labels to unknown when the fresh profile "
            "mentions last-event/no-events-since evidence."
        ),
        repair=lambda row: _repair_last_event_to_unknown(
            row,
            include_frequency=False,
            require_unclear_marker=False,
        ),
    ),
    RepairRule(
        rule_id="last_event_unclear_count_to_unknown",
        description=(
            "Rewrite fresh seizure-free or frequency labels to unknown only when "
            "last-event evidence is paired with no-explicit-count/no-recurring-"
            "rate markers."
        ),
        repair=lambda row: _repair_last_event_to_unknown(
            row,
            include_frequency=True,
            require_unclear_marker=True,
        ),
    ),
    RepairRule(
        rule_id="any_last_event_to_unknown",
        description=(
            "Broad stress rule: rewrite any fresh seizure-free or frequency "
            "label to unknown when the profile mentions last-event/no-events-"
            "since evidence."
        ),
        repair=lambda row: _repair_last_event_to_unknown(
            row,
            include_frequency=True,
            require_unclear_marker=False,
        ),
    ),
)


def main() -> None:
    source_rows = _load_jsonl(SOURCE_JSONL)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Validation-only component-generation probe after selector v0.9. "
            "Tests whether deterministic last-event-to-unknown repair is safe "
            "before changing component generation."
        ),
        "source_artifact": str(SOURCE_JSONL),
        "baseline_summary": selector.summarize_rows(source_rows),
        "rule_results": [_evaluate_rule(source_rows, rule) for rule in REPAIR_RULES],
    }
    payload["decision"] = _decision(payload["rule_results"])
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _evaluate_rule(
    source_rows: Sequence[dict[str, Any]],
    rule: RepairRule,
) -> dict[str, Any]:
    repaired_rows, repair_records = _replay_with_repair(source_rows, rule)
    summary = selector.summarize_rows(repaired_rows)
    baseline_summary = selector.summarize_rows(source_rows)
    selected_changes = _selected_changes(source_rows, repaired_rows)
    fresh_repair_transitions = Counter(
        _repair_transition(record) for record in repair_records
    )
    selected_change_transitions = Counter(
        change["transition"] for change in selected_changes
    )
    return {
        "rule_id": rule.rule_id,
        "description": rule.description,
        "selector_summary": summary,
        "delta_selected_purist_correct": (
            summary["selected_purist_correct"]
            - baseline_summary["selected_purist_correct"]
        ),
        "repair_count": len(repair_records),
        "fresh_repair_transitions": dict(fresh_repair_transitions),
        "selected_change_count": len(selected_changes),
        "selected_change_transitions": dict(selected_change_transitions),
        "selected_changes": selected_changes,
        "repair_records": repair_records,
        "decision": _rule_decision(summary, baseline_summary, selected_changes),
    }


def _replay_with_repair(
    source_rows: Sequence[dict[str, Any]],
    rule: RepairRule,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    deterministic_rows: list[dict[str, Any]] = []
    consensus_rows: list[dict[str, Any]] = []
    fresh_rows: list[dict[str, Any]] = []
    repair_records: list[dict[str, Any]] = []

    for row in source_rows:
        source_row_index = row["source_row_index"]
        gold_monthly = row["reference"]["gold_monthly_frequency"]
        original_fresh = row["fresh_evidence_label"]
        repaired_fresh = rule.repair(row) or original_fresh
        if repaired_fresh != original_fresh:
            repair_records.append(
                {
                    "source_row_index": source_row_index,
                    "gold_label": row["reference"]["gold_label"],
                    "gold_band": boundary_band(gold_monthly),
                    "deterministic_label": row["deterministic_label"],
                    "consensus_label": row["consensus_label"],
                    "fresh_label_before": original_fresh,
                    "fresh_label_after": repaired_fresh,
                    "fresh_correct_before": _purist_correct(
                        original_fresh,
                        gold_monthly,
                    ),
                    "fresh_correct_after": _purist_correct(
                        repaired_fresh,
                        gold_monthly,
                    ),
                    "fresh_boundary_profile": row["decision_features"].get(
                        "fresh_boundary_profile",
                        [],
                    ),
                }
            )
        deterministic_rows.append(
            {
                "source_row_index": source_row_index,
                "final_label": row["deterministic_label"],
                "comparison": row["score_layers"]["deterministic"]["comparison"],
                "reference": row["reference"],
            }
        )
        consensus_rows.append(
            {
                "source_row_index": source_row_index,
                "consensus_final_label": row["consensus_label"],
                "consensus_comparison": row["score_layers"]["consensus"][
                    "comparison"
                ],
                "consensus_decision": {
                    "reason": row["decision_features"].get("consensus_reason")
                },
            }
        )
        fresh_rows.append(
            {
                "source_row_index": source_row_index,
                "fresh_evidence_decision_record": {
                    "action": row["decision_features"].get("fresh_action"),
                    "boundary_profile": row["decision_features"].get(
                        "fresh_boundary_profile",
                    )
                    or [],
                    "uncertainty": row["decision_features"].get(
                        "fresh_uncertainty"
                    ),
                },
                "decision_record": {"final_label": repaired_fresh},
                "score_layers": {
                    "final": {
                        "comparison": _comparison(repaired_fresh, gold_monthly)
                    }
                },
            }
        )

    return (
        selector.build_selector_rows(
            deterministic_rows=deterministic_rows,
            consensus_rows=consensus_rows,
            fresh_evidence_rows=fresh_rows,
            policy="semantic_equiv_unknown_uncertainty_v0_9",
        ),
        repair_records,
    )


def _repair_last_event_to_unknown(
    row: Mapping[str, Any],
    *,
    include_frequency: bool,
    require_unclear_marker: bool,
) -> str | None:
    label = str(row.get("fresh_evidence_label") or "").strip().lower()
    profile_text = _profile_text(row)
    label_is_candidate = label.startswith("seizure free") or (
        include_frequency and " per " in label
    )
    if not label_is_candidate:
        return None
    if not _profile_has_last_event_boundary(profile_text):
        return None
    if _profile_has_count_window_exception(profile_text):
        return None
    if require_unclear_marker and not _profile_has_unclear_count_window(profile_text):
        return None
    return "unknown"


def _profile_text(row: Mapping[str, Any]) -> str:
    return " | ".join(
        str(item).lower()
        for item in row.get("decision_features", {}).get(
            "fresh_boundary_profile",
            [],
        )
    )


def _profile_has_last_event_boundary(profile_text: str) -> bool:
    return any(
        marker in profile_text
        for marker in (
            "last event",
            "last seizure date",
            "last-event",
            "no seizures since last event",
            "no further events reported",
            "no further events since",
        )
    )


def _profile_has_count_window_exception(profile_text: str) -> bool:
    return any(
        marker in profile_text
        for marker in (
            "explicit count plus window",
            "count-plus-window",
            "usable follow-up",
            "usable observation",
            "number of seizures explicitly given",
        )
    )


def _profile_has_unclear_count_window(profile_text: str) -> bool:
    return any(
        marker in profile_text
        for marker in (
            "no explicit count",
            "no evidence for ongoing or recurring frequency",
            "no evidence for recurring rate",
            "no current recurring frequency",
            "no explicit seizure-free",
            "not seizure free",
        )
    )


def _comparison(label: str, gold_monthly: float) -> dict[str, Any]:
    predicted_monthly = _monthly(label)
    return {
        "final_label": label,
        "gold_monthly_frequency": gold_monthly,
        "predicted_monthly_frequency": predicted_monthly,
        "purist_correct": False
        if predicted_monthly is None
        else map_purist(predicted_monthly) == map_purist(gold_monthly),
        "pragmatic_correct": False
        if predicted_monthly is None
        else map_pragmatic(predicted_monthly) == map_pragmatic(gold_monthly),
    }


def _monthly(label: str) -> float | None:
    try:
        return label_to_monthly_frequency(label)
    except Exception:
        return None


def _purist_correct(label: str, gold_monthly: float) -> bool:
    predicted_monthly = _monthly(label)
    if predicted_monthly is None:
        return False
    return map_purist(predicted_monthly) == map_purist(gold_monthly)


def _repair_transition(record: Mapping[str, Any]) -> str:
    before = record["fresh_correct_before"] is True
    after = record["fresh_correct_after"] is True
    if not before and after:
        return "fresh_wrong_to_correct"
    if before and not after:
        return "fresh_correct_to_wrong"
    if before and after:
        return "fresh_correct_to_correct"
    return "fresh_wrong_to_wrong"


def _selected_changes(
    baseline_rows: Sequence[Mapping[str, Any]],
    repaired_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    changes = []
    for before, after in zip(baseline_rows, repaired_rows, strict=True):
        if before["selected_label"] == after["selected_label"]:
            continue
        before_correct = (
            before["score_layers"]["selected"]["comparison"].get("purist_correct")
            is True
        )
        after_correct = (
            after["score_layers"]["selected"]["comparison"].get("purist_correct")
            is True
        )
        changes.append(
            {
                "source_row_index": before["source_row_index"],
                "gold_label": before["reference"]["gold_label"],
                "gold_band": boundary_band(
                    before["reference"]["gold_monthly_frequency"]
                ),
                "selected_label_before": before["selected_label"],
                "selected_label_after": after["selected_label"],
                "selected_correct_before": before_correct,
                "selected_correct_after": after_correct,
                "selector_action_after": after["selector_action"],
                "selector_gate_after": after["selector_gate"],
                "transition": _transition(before_correct, after_correct),
            }
        )
    return changes


def _transition(before_correct: bool, after_correct: bool) -> str:
    if not before_correct and after_correct:
        return "selected_wrong_to_correct"
    if before_correct and not after_correct:
        return "selected_correct_to_wrong"
    if before_correct and after_correct:
        return "selected_correct_to_correct"
    return "selected_wrong_to_wrong"


def _rule_decision(
    summary: Mapping[str, Any],
    baseline_summary: Mapping[str, Any],
    selected_changes: Sequence[Mapping[str, Any]],
) -> str:
    if summary["selected_purist_correct"] < baseline_summary["selected_purist_correct"]:
        return "reject_validation_negative"
    if any(
        change["transition"] == "selected_correct_to_wrong"
        for change in selected_changes
    ):
        return "reject_regresses_selected_rows"
    if summary["selected_purist_correct"] == baseline_summary["selected_purist_correct"]:
        return "diagnostic_no_selected_gain"
    return "revise_requires_hard_negative_panel"


def _decision(rule_results: Sequence[Mapping[str, Any]]) -> str:
    if any(result["decision"].startswith("revise") for result in rule_results):
        return "revise"
    return "reject"


def _markdown(payload: Mapping[str, Any]) -> str:
    baseline = payload["baseline_summary"]
    lines = [
        "# Gan 2026 v0.10 Component Repair Probe",
        "",
        "Date: 2026-06-15",
        "",
        "This validation-only no-call probe tests deterministic fresh-component "
        "repairs after selector v0.9. It does not read locked test rows and does "
        "not make model calls.",
        "",
        "## Experiment Unit",
        "",
        "- Hypothesis: broad last-event/seizure-free to unknown repair may recover "
        "the unknown-boundary residual.",
        "- Comparator: selector v0.9 saved validation replay.",
        "- Surface: full validation750 saved-output replay, because the candidate "
        "component repair could affect many seizure-free rows and needs a "
        "regression count before any narrower design.",
        "- Scorer: unchanged Gan-compatible Purist.",
        "- Inspection policy: aggregate transitions and validation row records only.",
        "- Stop rule: reject any repair with selected C->W regressions or lower "
        "selected Purist; revise only for zero-C->W selected gain.",
        "",
        "## Baseline",
        "",
        f"- v0.9 selected Purist: {baseline['selected_purist_correct']}/"
        f"{baseline['rows']}",
        f"- v0.9 W->C / C->W: {baseline['wrong_to_correct']} / "
        f"{baseline['correct_to_wrong']}",
        "",
        "## Rule Results",
        "",
        "| Rule | Repairs | Selected Purist | Delta | Selected changes | "
        "Selected W->C | Selected C->W | Decision |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in payload["rule_results"]:
        transitions = result["selected_change_transitions"]
        summary = result["selector_summary"]
        lines.append(
            f"| `{result['rule_id']}` | {result['repair_count']} | "
            f"{summary['selected_purist_correct']}/{summary['rows']} | "
            f"{result['delta_selected_purist_correct']} | "
            f"{result['selected_change_count']} | "
            f"{transitions.get('selected_wrong_to_correct', 0)} | "
            f"{transitions.get('selected_correct_to_wrong', 0)} | "
            f"`{result['decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The tempting deterministic repair is not safe. The broad rules recover "
            "some supervisor-style unknown-boundary rows, but they also rewrite "
            "many validation rows where seizure-free is Purist-correct. The "
            "narrow unclear-count version makes no selected-label gains and still "
            "turns two correct fresh components into wrong fresh components.",
            "",
            "Decision: reject broad deterministic last-event-to-unknown component "
            "repair. The next component-generation design should make the model "
            "emit an explicit ambiguity classification before rendering the final "
            "label, rather than relying on a profile-string rewrite.",
            "",
        ]
    )
    return "\n".join(lines)


def _register(payload: Mapping[str, Any]) -> None:
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID
    ]
    best = max(
        payload["rule_results"],
        key=lambda result: result["selector_summary"]["selected_purist_correct"],
    )
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
            ),
            date="2026-06-15",
            pipeline_family="consensus_fresh_agreement_selector_component_repair_probe",
            split="validation",
            row_count=payload["baseline_summary"]["rows"],
            model="none",
            model_role=(
                "Validation-only no-call component-repair probe over saved v0.9 "
                "selector rows; no model calls and no holdout rows are read."
            ),
            mode="no-call replay",
            replay_status="saved_output_replay",
            repair_mode="deterministic_last_event_to_unknown_component_probe",
            cache_reuse_source=str(SOURCE_JSONL),
            primary_metrics={
                "baseline_selected_purist_correct": payload["baseline_summary"][
                    "selected_purist_correct"
                ],
                "best_probe_selected_purist_correct": best["selector_summary"][
                    "selected_purist_correct"
                ],
                "best_probe_delta_selected_purist_correct": best[
                    "delta_selected_purist_correct"
                ],
                "rules_tested": len(payload["rule_results"]),
            },
            evidence_validity=(
                "Validation-only saved-output replay. Gold labels are used only "
                "for post-hoc scoring and transition accounting; no holdout rows "
                "are read."
            ),
            decision=payload["decision"],
            supersedes=(
                "gan2026_consensus_fresh_agreement_selector_v0_9_"
                "residual_component_generation_audit_2026-06-15",
            ),
            claim_language_notes=(
                "Rejects broad deterministic last-event-to-unknown component "
                "repair as validation-negative or non-improving. Supports a "
                "model-owned ambiguity-classification redesign instead."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
