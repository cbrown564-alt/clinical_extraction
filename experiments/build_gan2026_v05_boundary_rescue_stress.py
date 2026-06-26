"""Build a synthetic boundary-rescue stress panel for selector v0.5.

This is a mechanism probe, not benchmark evidence. The cases are
hand-specified source-near note fragments with synthetic deterministic,
consensus, and fresh-evidence component outputs. Gold labels are used only to
score the predeclared synthetic panel.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    consensus_fresh_agreement_selector as selector,
)
from clinical_extraction.core.registry import (
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
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_monthly_frequency,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_5_"
    "boundary_rescue_synthetic_stress_2026-06-15"
)
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"


@dataclass(frozen=True)
class BoundaryRescueCase:
    case_id: str
    family: str
    note_text: str
    gold_label: str
    deterministic_label: str
    consensus_label: str
    fresh_label: str
    fresh_boundary_profile: tuple[str, ...]
    expected_v05_action: str
    desired_future_action: str
    risk_type: str
    rationale: str


CASES: tuple[BoundaryRescueCase, ...] = (
    BoundaryRescueCase(
        case_id="sf_last_event_only_to_unknown",
        family="seizure_free_to_unknown",
        note_text=(
            "Her last seizure was on 20 Dec. The note does not state that this "
            "was the only seizure in a defined period."
        ),
        gold_label="unknown",
        deterministic_label="seizure free for 8 month",
        consensus_label="seizure free for 8 month",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "last_event_only",
            "not seizure_free: most recent event is not a zero-event interval",
        ),
        expected_v05_action="accept_fresh_boundary_rescue",
        desired_future_action="accept_fresh_boundary_rescue",
        risk_type="intended_positive",
        rationale=(
            "Last-event-only evidence should not be converted into a "
            "seizure-free duration."
        ),
    ),
    BoundaryRescueCase(
        case_id="sf_open_since_diet_to_unknown",
        family="seizure_free_to_unknown",
        note_text=(
            "Several drop attacks have occurred since starting the ketogenic "
            "diet, but the diet start date is not given."
        ),
        gold_label="unknown",
        deterministic_label="seizure free for multiple year",
        consensus_label="seizure free for multiple year",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "unknown/no-reference boundary",
            "denominator/window unclear",
            "no explicit seizure-free duration",
        ),
        expected_v05_action="accept_fresh_boundary_rescue",
        desired_future_action="accept_fresh_boundary_rescue",
        risk_type="intended_positive",
        rationale="Open-ended since-starting evidence lacks a usable denominator.",
    ),
    BoundaryRescueCase(
        case_id="sf_qualitative_events_to_no_reference",
        family="seizure_free_to_no_reference",
        note_text=(
            "The letter describes intermittent events but gives no explicit "
            "count, rate, or seizure-free interval."
        ),
        gold_label="unknown",
        deterministic_label="seizure free for multiple year",
        consensus_label="seizure free for multiple year",
        fresh_label="no seizure frequency reference",
        fresh_boundary_profile=(
            "no explicit numeric or range frequency",
            "no explicit seizure-free duration",
            "qualitative current events",
        ),
        expected_v05_action="accept_fresh_boundary_rescue",
        desired_future_action="accept_fresh_boundary_rescue",
        risk_type="intended_positive",
        rationale=(
            "A deterministic seizure-free answer is overreach when current "
            "event text is qualitative and not a zero-event statement."
        ),
    ),
    BoundaryRescueCase(
        case_id="no_reference_explicit_no_seizures_to_seizure_free",
        family="no_reference_to_seizure_free",
        note_text=(
            "There have been no epileptic seizures for more than a year; the "
            "events discussed elsewhere are non-epileptic."
        ),
        gold_label="seizure free for multiple month",
        deterministic_label="no seizure frequency reference",
        consensus_label="no seizure frequency reference",
        fresh_label="seizure free for multiple year",
        fresh_boundary_profile=(
            "no_reference boundary",
            "explicit non-epileptic event attribution",
            "no current epileptic seizures",
        ),
        expected_v05_action="accept_fresh_boundary_rescue",
        desired_future_action="accept_fresh_boundary_rescue",
        risk_type="intended_positive",
        rationale=(
            "Fresh evidence can rescue a missed seizure-free state when the "
            "absence applies to epileptic seizures."
        ),
    ),
    BoundaryRescueCase(
        case_id="valid_seizure_free_duration_false_unknown",
        family="valid_seizure_free_hard_negative",
        note_text=(
            "She has been seizure free for six months with no breakthrough "
            "events during that interval."
        ),
        gold_label="seizure free for 6 month",
        deterministic_label="seizure free for 6 month",
        consensus_label="seizure free for 6 month",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "explicit seizure-free duration",
            "zero-event interval stated",
        ),
        expected_v05_action="accept_fresh_boundary_rescue",
        desired_future_action="keep_deterministic_baseline",
        risk_type="current_rule_false_positive",
        rationale=(
            "v0.5 has no evidence-profile guard, so a wrong fresh `unknown` "
            "can erase a valid seizure-free duration."
        ),
    ),
    BoundaryRescueCase(
        case_id="valid_seizure_free_duration_false_no_reference",
        family="valid_seizure_free_hard_negative",
        note_text=(
            "The review clearly states no seizures for two years and gives no "
            "contradictory current seizure count."
        ),
        gold_label="seizure free for multiple year",
        deterministic_label="seizure free for multiple year",
        consensus_label="seizure free for multiple year",
        fresh_label="no seizure frequency reference",
        fresh_boundary_profile=(
            "explicit seizure-free duration",
            "no current seizures",
        ),
        expected_v05_action="accept_fresh_boundary_rescue",
        desired_future_action="keep_deterministic_baseline",
        risk_type="current_rule_false_positive",
        rationale=(
            "A valid zero-event interval should not be demoted to no-reference."
        ),
    ),
    BoundaryRescueCase(
        case_id="valid_no_reference_false_seizure_free",
        family="valid_no_reference_hard_negative",
        note_text=(
            "The note reviews medication side effects and schooling but gives no "
            "seizure-frequency, last-event, or seizure-free information."
        ),
        gold_label="no seizure frequency reference",
        deterministic_label="no seizure frequency reference",
        consensus_label="no seizure frequency reference",
        fresh_label="seizure free for multiple year",
        fresh_boundary_profile=("no positive seizure-frequency evidence",),
        expected_v05_action="accept_fresh_boundary_rescue",
        desired_future_action="keep_deterministic_baseline",
        risk_type="current_rule_false_positive",
        rationale=(
            "No-reference text is not equivalent to seizure-free; v0.5 cannot "
            "distinguish a wrong fresh boundary rescue here."
        ),
    ),
    BoundaryRescueCase(
        case_id="sf_to_specific_rate_blocked",
        family="specific_rate_control",
        note_text=(
            "She has remained seizure free for six months; an alternate read "
            "incorrectly extracts one seizure per month."
        ),
        gold_label="seizure free for 6 month",
        deterministic_label="seizure free for 6 month",
        consensus_label="seizure free for 6 month",
        fresh_label="1 per month",
        fresh_boundary_profile=("explicit seizure-free duration",),
        expected_v05_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="v0.5 only rescues to uncertain boundary states, not rates.",
    ),
    BoundaryRescueCase(
        case_id="unknown_explicit_count_window_conservative_cost",
        family="unknown_origin_false_negative",
        note_text=(
            "Topiramate was stopped two months ago; soon afterwards she had two "
            "seizures and none since."
        ),
        gold_label="2 per 2 month",
        deterministic_label="unknown",
        consensus_label="2 per 2 month",
        fresh_label="2 per 2 month",
        fresh_boundary_profile=(
            "explicit count plus usable follow-up period",
            "current/recent frequency",
        ),
        expected_v05_action="keep_deterministic_baseline",
        desired_future_action="accept_consensus_fresh_agreement",
        risk_type="known_conservative_false_negative",
        rationale=(
            "This mirrors the supervisor-approved count-plus-window exception, "
            "but v0.5 still blocks deterministic `unknown` origins."
        ),
    ),
    BoundaryRescueCase(
        case_id="unknown_last_event_specific_rate_blocked",
        family="unknown_origin_safety",
        note_text=(
            "The note gives a last seizure date but does not give a count over "
            "a defined period."
        ),
        gold_label="unknown",
        deterministic_label="unknown",
        consensus_label="1 per month",
        fresh_label="1 per month",
        fresh_boundary_profile=("last_event_only",),
        expected_v05_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Unknown origins should not relax to a rate from last-event-only text.",
    ),
    BoundaryRescueCase(
        case_id="cluster_cadence_demote_still_blocked",
        family="v04_regression_guard",
        note_text=(
            "Diary describes three clusters per month, with multiple seizures "
            "in each cluster."
        ),
        gold_label="3 cluster per month, multiple per cluster",
        deterministic_label="3 cluster per month, multiple per cluster",
        consensus_label="3 per month",
        fresh_label="3 per month",
        fresh_boundary_profile=("cluster cadence demotion",),
        expected_v05_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="The v0.4 cluster-cadence protection must survive v0.5.",
    ),
    BoundaryRescueCase(
        case_id="specific_consensus_correction_still_accepted",
        family="v04_positive_control",
        note_text="The current diary documents five seizures each week.",
        gold_label="5 per week",
        deterministic_label="2 per month",
        consensus_label="5 per week",
        fresh_label="5 per week",
        fresh_boundary_profile=("current/recent frequency",),
        expected_v05_action="accept_consensus_fresh_agreement",
        desired_future_action="accept_consensus_fresh_agreement",
        risk_type="intended_positive",
        rationale="The v0.4 exact consensus plus fresh agreement path should remain active.",
    ),
)


def main() -> None:
    deterministic_rows = []
    consensus_rows = []
    fresh_rows = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 910000 + offset
        gold_monthly = _monthly_frequency(case.gold_label)
        deterministic_rows.append(
            {
                "source_row_index": source_row_index,
                "final_label": case.deterministic_label,
                "comparison": {
                    "purist_correct": _purist_correct(
                        case.deterministic_label,
                        case.gold_label,
                    )
                },
                "reference": {
                    "gold_label": case.gold_label,
                    "gold_monthly_frequency": gold_monthly,
                    "row_ok": True,
                },
            }
        )
        consensus_rows.append(
            {
                "source_row_index": source_row_index,
                "consensus_final_label": case.consensus_label,
                "consensus_comparison": {
                    "purist_correct": _purist_correct(
                        case.consensus_label,
                        case.gold_label,
                    )
                },
                "consensus_decision": {"reason": "synthetic_predeclared_case"},
            }
        )
        fresh_rows.append(
            {
                "source_row_index": source_row_index,
                "fresh_evidence_decision_record": {
                    "action": "synthetic_component_output",
                    "boundary_profile": list(case.fresh_boundary_profile),
                    "uncertainty": "low",
                },
                "decision_record": {"final_label": case.fresh_label},
                "score_layers": {
                    "final": {
                        "comparison": {
                            "purist_correct": _purist_correct(
                                case.fresh_label,
                                case.gold_label,
                            )
                        }
                    }
                },
            }
        )

    rows = selector.build_selector_rows(
        deterministic_rows=deterministic_rows,
        consensus_rows=consensus_rows,
        fresh_evidence_rows=fresh_rows,
        policy="fresh_boundary_rescue_v0_5",
    )
    by_index = {row["source_row_index"]: row for row in rows}
    enriched_rows = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 910000 + offset
        row = dict(by_index[source_row_index])
        row["synthetic_case"] = _case_record(case)
        row["expected_v05_action_match"] = (
            row["selector_action"] == case.expected_v05_action
        )
        row["desired_future_action_match"] = (
            row["selector_action"] == case.desired_future_action
        )
        row["gold_band"] = boundary_band(_monthly_frequency(case.gold_label))
        enriched_rows.append(row)

    summary = _stress_summary(enriched_rows)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Synthetic mechanism probe for consensus+fresh selector v0.5 "
            "boundary rescue; not validation, holdout, benchmark, or "
            "model-performance evidence."
        ),
        "selector_summary": selector.summarize_rows(enriched_rows),
        "stress_summary": summary,
        "cases": [_case_record(case) for case in CASES],
        "rows": enriched_rows,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MD_PATH.write_text(_markdown_report(payload), encoding="utf-8")
    _register(summary)


def _monthly_frequency(label: str) -> float | None:
    try:
        return label_to_monthly_frequency(label)
    except Exception:
        return None


def _purist_correct(prediction: str, gold: str) -> bool:
    try:
        return map_purist(label_to_monthly_frequency(prediction)) == map_purist(
            label_to_monthly_frequency(gold)
        )
    except Exception:
        return False


def _case_record(case: BoundaryRescueCase) -> dict[str, Any]:
    gold_monthly = _monthly_frequency(case.gold_label)
    return {
        "case_id": case.case_id,
        "family": case.family,
        "note_text": case.note_text,
        "gold_label": case.gold_label,
        "gold_monthly_frequency": gold_monthly,
        "gold_band": boundary_band(gold_monthly),
        "deterministic_label": case.deterministic_label,
        "consensus_label": case.consensus_label,
        "fresh_label": case.fresh_label,
        "fresh_boundary_profile": list(case.fresh_boundary_profile),
        "expected_v05_action": case.expected_v05_action,
        "desired_future_action": case.desired_future_action,
        "risk_type": case.risk_type,
        "rationale": case.rationale,
    }


def _stress_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    families: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
    risk_types: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
    gates = Counter(str(row["selector_gate"]) for row in rows)
    actions = Counter(str(row["selector_action"]) for row in rows)
    desired_misses = []
    current_rule_false_positives = []
    conservative_false_negatives = []
    safety_successes = []
    for row in rows:
        case = row["synthetic_case"]
        _accumulate_bucket(families[case["family"]], row)
        _accumulate_bucket(risk_types[case["risk_type"]], row)
        det_correct = _is_layer_correct(row, "deterministic")
        selected_correct = _is_layer_correct(row, "selected")
        fresh_correct = _is_layer_correct(row, "fresh_evidence")
        if row["desired_future_action_match"] is not True:
            desired_misses.append(case["case_id"])
        if det_correct and not fresh_correct and not selected_correct:
            current_rule_false_positives.append(case["case_id"])
        if not det_correct and fresh_correct and not selected_correct:
            conservative_false_negatives.append(case["case_id"])
        if det_correct and not fresh_correct and selected_correct:
            safety_successes.append(case["case_id"])

    return {
        "rows": len(rows),
        "selector_version": rows[0]["selector_version"],
        "actions": dict(actions),
        "gates": dict(gates),
        "deterministic_purist_correct": sum(
            _is_layer_correct(row, "deterministic") for row in rows
        ),
        "consensus_purist_correct": sum(
            _is_layer_correct(row, "consensus") for row in rows
        ),
        "fresh_purist_correct": sum(
            _is_layer_correct(row, "fresh_evidence") for row in rows
        ),
        "selected_purist_correct": sum(
            _is_layer_correct(row, "selected") for row in rows
        ),
        "expected_v05_action_matches": sum(
            row["expected_v05_action_match"] is True for row in rows
        ),
        "desired_future_action_matches": sum(
            row["desired_future_action_match"] is True for row in rows
        ),
        "desired_future_action_miss_case_ids": desired_misses,
        "current_rule_false_positive_case_ids": current_rule_false_positives,
        "conservative_false_negative_case_ids": conservative_false_negatives,
        "safety_success_case_ids": safety_successes,
        "by_family": {key: dict(value) for key, value in sorted(families.items())},
        "by_risk_type": {
            key: dict(value) for key, value in sorted(risk_types.items())
        },
    }


def _accumulate_bucket(bucket: dict[str, Any], row: dict[str, Any]) -> None:
    bucket["rows"] += 1
    bucket["selected_purist_correct"] += int(_is_layer_correct(row, "selected"))
    bucket["deterministic_purist_correct"] += int(
        _is_layer_correct(row, "deterministic")
    )
    bucket["consensus_purist_correct"] += int(_is_layer_correct(row, "consensus"))
    bucket["fresh_purist_correct"] += int(_is_layer_correct(row, "fresh_evidence"))
    bucket["expected_v05_action_matches"] += int(
        row["expected_v05_action_match"] is True
    )
    bucket["desired_future_action_matches"] += int(
        row["desired_future_action_match"] is True
    )


def _is_layer_correct(row: dict[str, Any], layer: str) -> bool:
    return (
        row["score_layers"][layer]["comparison"].get("purist_correct")
        is True
    )


def _markdown_report(payload: dict[str, Any]) -> str:
    stress = payload["stress_summary"]
    selector_summary = payload["selector_summary"]
    lines = [
        "# Gan 2026 Selector v0.5 Boundary-Rescue Synthetic Stress Panel",
        "",
        "Date: 2026-06-15",
        "",
        "This is a predeclared synthetic mechanism probe for the v0.5 "
        "consensus+fresh agreement selector. It uses hand-specified component "
        "outputs and the real selector implementation. It is not validation, "
        "holdout, benchmark, or model-performance evidence.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: synthetic component-stress / selector mechanics.",
        "- Split: `synthetic_boundary_rescue_probe`; no Gan rows are read.",
        "- Scorer: current Gan-compatible Purist mapping for synthetic labels.",
        "- Selector: `fresh_boundary_rescue_v0_5`.",
        "- Stress families: seizure-free to unknown/no-reference, no-reference "
        "to seizure-free, valid boundary-state hard negatives, unknown-origin "
        "controls, and v0.4 regression guards.",
        "- Stop rule: revise if hard negatives expose boundary-rescue "
        "false positives; do not freeze for holdout from this artifact alone.",
        "",
        "## Summary",
        "",
        f"- Rows: {stress['rows']}",
        f"- Deterministic Purist: {stress['deterministic_purist_correct']}/{stress['rows']}",
        f"- Consensus Purist: {stress['consensus_purist_correct']}/{stress['rows']}",
        f"- Fresh Purist: {stress['fresh_purist_correct']}/{stress['rows']}",
        f"- Selected Purist: {stress['selected_purist_correct']}/{stress['rows']}",
        f"- Expected v0.5 action matches: {stress['expected_v05_action_matches']}/{stress['rows']}",
        (
            "- Desired future action matches: "
            f"{stress['desired_future_action_matches']}/{stress['rows']}"
        ),
        (
            "- Current-rule false positives: "
            f"{len(stress['current_rule_false_positive_case_ids'])}"
        ),
        (
            "- Conservative false negatives: "
            f"{len(stress['conservative_false_negative_case_ids'])}"
        ),
        f"- Safety successes: {len(stress['safety_success_case_ids'])}",
        f"- Selector changed labels: {selector_summary['changed_labels']}",
        (
            "- Selector W->C / C->W: "
            f"{selector_summary['wrong_to_correct']} / "
            f"{selector_summary['correct_to_wrong']}"
        ),
        f"- Actions: `{stress['actions']}`",
        "",
        "## Risk-Type Summary",
        "",
        (
            "| Risk Type | Rows | Deterministic | Consensus | Fresh | Selected | "
            "Expected Matches | Desired Matches |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for risk_type, info in stress["by_risk_type"].items():
        lines.append(_summary_row(risk_type, info))
    lines.extend(
        [
            "",
            "## Family Summary",
            "",
            (
                "| Family | Rows | Deterministic | Consensus | Fresh | Selected | "
                "Expected Matches | Desired Matches |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for family, info in stress["by_family"].items():
        lines.append(_summary_row(family, info))
    lines.extend(
        [
            "",
            "## Case Readout",
            "",
            (
                "| Case | Risk | Gold | Deterministic | Consensus | Fresh | "
                "Action | Gate | Selected Correct | Note |"
            ),
            "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in payload["rows"]:
        case = row["synthetic_case"]
        selected_correct = row["score_layers"]["selected"]["comparison"][
            "purist_correct"
        ]
        lines.append(
            f"| `{case['case_id']}` | `{case['risk_type']}` | "
            f"`{case['gold_label']}` | `{case['deterministic_label']}` | "
            f"`{case['consensus_label']}` | `{case['fresh_label']}` | "
            f"`{row['selector_action']}` | `{row['selector_gate']}` | "
            f"{selected_correct} | {case['rationale']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "v0.5 behaves exactly as currently implemented on this stress panel: "
            "it preserves the v0.4 consensus path and blocks unknown-origin "
            "rate relaxation, but it accepts every seizure-free/no-reference "
            "fresh boundary rescue regardless of whether the fresh boundary "
            "profile actually refutes the deterministic boundary state.",
            "",
            "That is the central revision signal. The intended positives support "
            "the validation finding that deterministic seizure-free/no-reference "
            "overreach is real. The hard negatives show that the current label-only "
            "rescue can erase a valid seizure-free duration or turn a true "
            "no-reference row into seizure-free. A safer next design should add "
            "a gold-free evidence/profile guard for fresh boundary rescue rather "
            "than widening the selector.",
            "",
            "Decision: revise, not freeze. This synthetic probe supports the "
            "v0.5 direction but blocks any holdout-facing protocol until the "
            "boundary rescue is evidence/profile-aware.",
            "",
        ]
    )
    return "\n".join(lines)


def _summary_row(name: str, info: dict[str, Any]) -> str:
    return (
        f"| `{name}` | {info['rows']} | "
        f"{info['deterministic_purist_correct']} | "
        f"{info['consensus_purist_correct']} | "
        f"{info['fresh_purist_correct']} | "
        f"{info['selected_purist_correct']} | "
        f"{info['expected_v05_action_matches']} | "
        f"{info['desired_future_action_matches']} |"
    )


def _register(summary: dict[str, Any]) -> None:
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID
    ]
    entry = RunRegistryEntry(
        run_id=RUN_ID,
        artifact_paths=(
            f"experiments/{JSON_PATH.name}",
            f"experiments/{MD_PATH.name}",
        ),
        date="2026-06-15",
        pipeline_family="consensus_fresh_agreement_selector_synthetic_boundary_stress",
        split="synthetic_boundary_rescue_probe",
        row_count=summary["rows"],
        model="none",
        model_role=(
            "Analysis-only synthetic boundary-rescue probe over hand-specified "
            "deterministic, consensus, and V12 fresh-evidence labels; no model "
            "calls and no Gan rows are read."
        ),
        mode="analysis-only",
        replay_status="analysis_only",
        repair_mode="selector_v0_5_fresh_boundary_rescue",
        cache_reuse_source="Synthetic hand-specified component outputs only.",
        primary_metrics={
            "rows": summary["rows"],
            "deterministic_purist_correct": summary[
                "deterministic_purist_correct"
            ],
            "consensus_purist_correct": summary["consensus_purist_correct"],
            "fresh_purist_correct": summary["fresh_purist_correct"],
            "selected_purist_correct": summary["selected_purist_correct"],
            "expected_v05_action_matches": summary[
                "expected_v05_action_matches"
            ],
            "desired_future_action_matches": summary[
                "desired_future_action_matches"
            ],
            "current_rule_false_positive_count": len(
                summary["current_rule_false_positive_case_ids"]
            ),
            "conservative_false_negative_count": len(
                summary["conservative_false_negative_case_ids"]
            ),
            "safety_success_count": len(summary["safety_success_case_ids"]),
        },
        evidence_validity=(
            "Synthetic mechanism evidence only: source-near note fragments and "
            "hand-specified labels are scored through the current Gan Purist "
            "mapping; no validation or holdout records are read."
        ),
        decision="revise",
        supersedes=(
            "gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_audit_2026-06-15",
        ),
        claim_language_notes=(
            "Predeclared synthetic component-stress probe for selector v0.5. "
            "Supports deterministic seizure-free/no-reference overreach rescue "
            "as a direction, but exposes hard-negative false positives from the "
            "label-only rescue rule. Does not authorize a frozen holdout audit."
        ),
    )
    entries.append(entry)
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
