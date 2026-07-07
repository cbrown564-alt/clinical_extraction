"""Build v0.7 unknown-origin count-window selector replay artifacts.

The script replays selector v0.7 over the saved validation750 selector rows and
over a synthetic source-near panel for deterministic ``unknown`` origins with
explicit count plus usable window evidence. No Gan holdout rows are read, and no
model calls are made.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    consensus_fresh_agreement_selector as selector,
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
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

SOURCE_VALIDATION_JSONL = (
    EXPERIMENTS / "gan2026_consensus_fresh_agreement_selector_v0_6_"
    "validation750_no_call_replay_2026-06-15.jsonl"
)

VALIDATION_RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15"
)
SYNTHETIC_RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_7_"
    "unknown_count_window_synthetic_stress_2026-06-15"
)


@dataclass(frozen=True)
class CountWindowCase:
    case_id: str
    family: str
    note_text: str
    gold_label: str
    deterministic_label: str
    consensus_label: str
    fresh_label: str
    fresh_boundary_profile: tuple[str, ...]
    desired_action: str
    risk_type: str
    rationale: str


CASES: tuple[CountWindowCase, ...] = (
    CountWindowCase(
        case_id="topiramate_two_seizures_two_months",
        family="explicit_count_window_positive",
        note_text=(
            "Topiramate was discontinued two months ago; soon afterwards she "
            "reported two seizures and no further seizures since."
        ),
        gold_label="2 per 2 month",
        deterministic_label="unknown",
        consensus_label="2 per 2 month",
        fresh_label="2 per 2 month",
        fresh_boundary_profile=(
            "explicit count plus usable follow-up period",
            "defined observation period",
        ),
        desired_action="accept_unknown_count_window_rescue",
        risk_type="intended_positive",
        rationale="Count and follow-up period are both explicit enough to score a rate.",
    ),
    CountWindowCase(
        case_id="three_events_three_month_review",
        family="explicit_count_window_positive",
        note_text=(
            "Since the medication review three months ago, exactly three "
            "seizures have been documented."
        ),
        gold_label="3 per 3 month",
        deterministic_label="unknown",
        consensus_label="3 per 3 month",
        fresh_label="3 per 3 month",
        fresh_boundary_profile=(
            "explicit numeric count",
            "usable observation period",
            "defined period",
        ),
        desired_action="accept_unknown_count_window_rescue",
        risk_type="intended_positive",
        rationale="An exact count over a defined review interval is a rate.",
    ),
    CountWindowCase(
        case_id="two_events_five_month_followup",
        family="explicit_count_window_positive",
        note_text=(
            "During the five-month follow-up after clobazam adjustment, two "
            "drop attacks were recorded."
        ),
        gold_label="2 per 5 month",
        deterministic_label="unknown",
        consensus_label="2 per 5 month",
        fresh_label="2 per 5 month",
        fresh_boundary_profile=(
            "number of seizures explicitly given",
            "usable follow-up period",
        ),
        desired_action="accept_unknown_count_window_rescue",
        risk_type="intended_positive",
        rationale="The count and denominator are explicit even though the rate is submonthly.",
    ),
    CountWindowCase(
        case_id="four_events_four_month_interval",
        family="explicit_count_window_positive",
        note_text=(
            "Across the last four months there have been four focal seizures, "
            "with no additional events reported."
        ),
        gold_label="4 per 4 month",
        deterministic_label="unknown",
        consensus_label="4 per 4 month",
        fresh_label="4 per 4 month",
        fresh_boundary_profile=(
            "count-plus-window",
            "usable window",
            "defined observation period",
        ),
        desired_action="accept_unknown_count_window_rescue",
        risk_type="intended_positive",
        rationale="This is the same count/window feature in a different wording.",
    ),
    CountWindowCase(
        case_id="last_event_only_none_since",
        family="last_event_only_negative",
        note_text=(
            "Her last seizure was on 05 August and there have been none since; "
            "the note gives no total count before that date."
        ),
        gold_label="unknown",
        deterministic_label="unknown",
        consensus_label="1 per 4 month",
        fresh_label="1 per 4 month",
        fresh_boundary_profile=(
            "explicit last event date",
            "none since",
            "duration since last event is approximately 4 months",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Last-event date plus none-since is not a count over a period.",
    ),
    CountWindowCase(
        case_id="open_ended_since_diet",
        family="open_ended_since_negative",
        note_text=(
            "Several drop attacks have occurred since starting the ketogenic "
            "diet, but the diet start date is not stated."
        ),
        gold_label="unknown",
        deterministic_label="unknown",
        consensus_label="3 per month",
        fresh_label="3 per month",
        fresh_boundary_profile=(
            "explicit count plus window attempted",
            "since starting ketogenic diet",
            "start date unclear",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="The start of the period is unclear.",
    ),
    CountWindowCase(
        case_id="vague_several_with_period",
        family="vague_count_negative",
        note_text="Over the last two months she has had several brief seizures.",
        gold_label="unknown",
        deterministic_label="unknown",
        consensus_label="multiple per month",
        fresh_label="multiple per month",
        fresh_boundary_profile=(
            "usable observation period",
            "vague count several seizures",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="The denominator is present but the seizure count is vague.",
    ),
    CountWindowCase(
        case_id="fresh_consensus_disagreement",
        family="agreement_control",
        note_text=("Since the review two months ago, two seizures were recorded and none since."),
        gold_label="2 per 2 month",
        deterministic_label="unknown",
        consensus_label="2 per 2 month",
        fresh_label="3 per 3 month",
        fresh_boundary_profile=(
            "explicit count plus usable follow-up period",
            "defined observation period",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Unknown-origin rescue still requires consensus and fresh agreement.",
    ),
    CountWindowCase(
        case_id="no_reference_origin_not_relaxed",
        family="origin_control",
        note_text="The count/window evidence is present but the origin is no-reference.",
        gold_label="2 per 2 month",
        deterministic_label="no seizure frequency reference",
        consensus_label="2 per 2 month",
        fresh_label="2 per 2 month",
        fresh_boundary_profile=(
            "explicit count plus usable follow-up period",
            "defined observation period",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="known_conservative_false_negative",
        rationale="v0.7 only relaxes deterministic unknown origins.",
    ),
    CountWindowCase(
        case_id="unknown_to_seizure_free_not_count_window",
        family="unsupported_replacement_control",
        note_text="The note only states seizure-free for six months.",
        gold_label="unknown",
        deterministic_label="unknown",
        consensus_label="seizure free for 6 month",
        fresh_label="seizure free for 6 month",
        fresh_boundary_profile=(
            "explicit seizure-free duration",
            "no conflicting current/recent frequency",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="The v0.7 count-window gate does not relax unknown to seizure-free.",
    ),
    CountWindowCase(
        case_id="v06_boundary_positive_control",
        family="v06_boundary_control",
        note_text="Her last seizure date is given, but no count or rate is stated.",
        gold_label="unknown",
        deterministic_label="seizure free for 8 month",
        consensus_label="seizure free for 8 month",
        fresh_label="unknown",
        fresh_boundary_profile=("last_event_only", "not seizure_free"),
        desired_action="accept_fresh_boundary_rescue",
        risk_type="intended_positive",
        rationale="v0.7 should preserve v0.6 seizure-free boundary rescue.",
    ),
    CountWindowCase(
        case_id="cluster_cadence_guard_control",
        family="v04_cluster_control",
        note_text="Diary documents three clusters per month, with multiple seizures per cluster.",
        gold_label="3 cluster per month, multiple per cluster",
        deterministic_label="3 cluster per month, multiple per cluster",
        consensus_label="3 per month",
        fresh_label="3 per month",
        fresh_boundary_profile=("cluster cadence demotion",),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="v0.7 must preserve the v0.4 cluster-cadence guard.",
    ),
)


def main() -> None:
    validation_rows = _load_jsonl(SOURCE_VALIDATION_JSONL)
    v07_validation_rows = _replay_v07(validation_rows)
    validation_jsonl = EXPERIMENTS / f"{VALIDATION_RUN_ID}.jsonl"
    validation_md = EXPERIMENTS / f"{VALIDATION_RUN_ID}.md"
    _write_jsonl(v07_validation_rows, validation_jsonl)
    selector.write_report(
        v07_validation_rows,
        validation_md,
        jsonl_path=validation_jsonl,
        source_artifacts={
            "v0.6_selector_rows": str(SOURCE_VALIDATION_JSONL),
            "replay_source": "reconstructed component rows from v0.6 selector rows",
        },
    )

    synthetic_rows = _build_synthetic_rows()
    synthetic_summary = _synthetic_summary(synthetic_rows)
    synthetic_json = EXPERIMENTS / f"{SYNTHETIC_RUN_ID}.json"
    synthetic_md = EXPERIMENTS / f"{SYNTHETIC_RUN_ID}.md"
    synthetic_payload = {
        "run_id": SYNTHETIC_RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Synthetic mechanism probe for v0.7 deterministic-unknown explicit "
            "count plus usable window rescue."
        ),
        "selector_summary": selector.summarize_rows(synthetic_rows),
        "stress_summary": synthetic_summary,
        "cases": [_case_record(case) for case in CASES],
        "rows": synthetic_rows,
    }
    synthetic_json.write_text(
        json.dumps(synthetic_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    synthetic_md.write_text(_synthetic_markdown(synthetic_payload), encoding="utf-8")

    _register_validation(selector.summarize_rows(v07_validation_rows))
    _register_synthetic(synthetic_summary, selector.summarize_rows(synthetic_rows))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _replay_v07(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deterministic_rows, consensus_rows, fresh_rows = _component_rows(source_rows)
    return selector.build_selector_rows(
        deterministic_rows=deterministic_rows,
        consensus_rows=consensus_rows,
        fresh_evidence_rows=fresh_rows,
        policy="unknown_count_window_rescue_v0_7",
    )


def _component_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    deterministic_rows = []
    consensus_rows = []
    fresh_rows = []
    for row in rows:
        source_row_index = row["source_row_index"]
        features = row.get("decision_features", {})
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
                "consensus_comparison": row["score_layers"]["consensus"]["comparison"],
                "consensus_decision": {"reason": features.get("consensus_reason")},
            }
        )
        fresh_rows.append(
            {
                "source_row_index": source_row_index,
                "fresh_evidence_decision_record": {
                    "action": features.get("fresh_action"),
                    "boundary_profile": features.get("fresh_boundary_profile") or [],
                    "uncertainty": features.get("fresh_uncertainty"),
                },
                "decision_record": {"final_label": row["fresh_evidence_label"]},
                "score_layers": {
                    "final": {"comparison": row["score_layers"]["fresh_evidence"]["comparison"]}
                },
            }
        )
    return deterministic_rows, consensus_rows, fresh_rows


def _build_synthetic_rows() -> list[dict[str, Any]]:
    deterministic_rows = []
    consensus_rows = []
    fresh_rows = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 920000 + offset
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
        policy="unknown_count_window_rescue_v0_7",
    )
    by_index = {row["source_row_index"]: row for row in rows}
    enriched = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 920000 + offset
        row = dict(by_index[source_row_index])
        row["synthetic_case"] = _case_record(case)
        row["desired_action_match"] = row["selector_action"] == case.desired_action
        enriched.append(row)
    return enriched


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


def _case_record(case: CountWindowCase) -> dict[str, Any]:
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
        "desired_action": case.desired_action,
        "risk_type": case.risk_type,
        "rationale": case.rationale,
    }


def _synthetic_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_risk_type: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    desired_misses = []
    false_positives = []
    false_negatives = []
    safety_successes = []
    for row in rows:
        risk_type = row["synthetic_case"]["risk_type"]
        _accumulate_bucket(by_risk_type[risk_type], row)
        det_correct = _is_layer_correct(row, "deterministic")
        fresh_correct = _is_layer_correct(row, "fresh_evidence")
        selected_correct = _is_layer_correct(row, "selected")
        if row["desired_action_match"] is not True:
            desired_misses.append(row["synthetic_case"]["case_id"])
        if det_correct and not fresh_correct and not selected_correct:
            false_positives.append(row["synthetic_case"]["case_id"])
        if not det_correct and fresh_correct and not selected_correct:
            false_negatives.append(row["synthetic_case"]["case_id"])
        if det_correct and not fresh_correct and selected_correct:
            safety_successes.append(row["synthetic_case"]["case_id"])
    return {
        "rows": len(rows),
        "selector_version": rows[0]["selector_version"],
        "actions": dict(Counter(str(row["selector_action"]) for row in rows)),
        "gates": dict(Counter(str(row["selector_gate"]) for row in rows)),
        "deterministic_purist_correct": sum(
            _is_layer_correct(row, "deterministic") for row in rows
        ),
        "consensus_purist_correct": sum(_is_layer_correct(row, "consensus") for row in rows),
        "fresh_purist_correct": sum(_is_layer_correct(row, "fresh_evidence") for row in rows),
        "selected_purist_correct": sum(_is_layer_correct(row, "selected") for row in rows),
        "desired_action_matches": sum(row["desired_action_match"] is True for row in rows),
        "desired_action_miss_case_ids": desired_misses,
        "current_rule_false_positive_case_ids": false_positives,
        "conservative_false_negative_case_ids": false_negatives,
        "safety_success_case_ids": safety_successes,
        "by_risk_type": {key: dict(value) for key, value in sorted(by_risk_type.items())},
    }


def _accumulate_bucket(bucket: dict[str, int], row: dict[str, Any]) -> None:
    bucket["rows"] += 1
    bucket["deterministic_purist_correct"] += int(_is_layer_correct(row, "deterministic"))
    bucket["consensus_purist_correct"] += int(_is_layer_correct(row, "consensus"))
    bucket["fresh_purist_correct"] += int(_is_layer_correct(row, "fresh_evidence"))
    bucket["selected_purist_correct"] += int(_is_layer_correct(row, "selected"))
    bucket["desired_action_matches"] += int(row["desired_action_match"] is True)


def _is_layer_correct(row: dict[str, Any], layer: str) -> bool:
    return row["score_layers"][layer]["comparison"].get("purist_correct") is True


def _synthetic_markdown(payload: dict[str, Any]) -> str:
    stress = payload["stress_summary"]
    selector_summary = payload["selector_summary"]
    lines = [
        "# Gan 2026 Selector v0.7 Unknown Count-Window Synthetic Stress",
        "",
        "Date: 2026-06-15",
        "",
        "This is a predeclared synthetic mechanism probe for v0.7. It uses "
        "hand-specified component outputs and the real selector implementation. "
        "It is not validation, holdout, benchmark, or model-performance evidence.",
        "",
        "## Summary",
        "",
        f"- Rows: {stress['rows']}",
        f"- Deterministic Purist: {stress['deterministic_purist_correct']}/{stress['rows']}",
        f"- Consensus Purist: {stress['consensus_purist_correct']}/{stress['rows']}",
        f"- Fresh Purist: {stress['fresh_purist_correct']}/{stress['rows']}",
        f"- Selected Purist: {stress['selected_purist_correct']}/{stress['rows']}",
        f"- Desired action matches: {stress['desired_action_matches']}/{stress['rows']}",
        (f"- Current-rule false positives: {len(stress['current_rule_false_positive_case_ids'])}"),
        (f"- Conservative false negatives: {len(stress['conservative_false_negative_case_ids'])}"),
        f"- Safety successes: {len(stress['safety_success_case_ids'])}",
        f"- Selector changed labels: {selector_summary['changed_labels']}",
        (
            "- Selector W->C / C->W: "
            f"{selector_summary['wrong_to_correct']} / "
            f"{selector_summary['correct_to_wrong']}"
        ),
        f"- Changed-label precision: {selector_summary['changed_label_precision']}",
        f"- Actions: `{stress['actions']}`",
        "",
        "## Risk-Type Summary",
        "",
        ("| Risk Type | Rows | Deterministic | Consensus | Fresh | Selected | Desired Matches |"),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for risk_type, info in stress["by_risk_type"].items():
        lines.append(
            f"| `{risk_type}` | {info['rows']} | "
            f"{info['deterministic_purist_correct']} | "
            f"{info['consensus_purist_correct']} | "
            f"{info['fresh_purist_correct']} | "
            f"{info['selected_purist_correct']} | "
            f"{info['desired_action_matches']} |"
        )
    lines.extend(
        [
            "",
            "## Case Readout",
            "",
            "| Case | Risk | Action | Gate | Selected Correct | Desired Match |",
            "| --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in payload["rows"]:
        case = row["synthetic_case"]
        selected_correct = row["score_layers"]["selected"]["comparison"]["purist_correct"]
        lines.append(
            f"| `{case['case_id']}` | `{case['risk_type']}` | "
            f"`{row['selector_action']}` | `{row['selector_gate']}` | "
            f"{selected_correct} | {row['desired_action_match']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "v0.7 accepts only explicit count-plus-window unknown-origin "
            "rescues and blocks last-event-only, open-ended treatment-start, "
            "vague-count, unsupported replacement, and disagreement controls. "
            "It preserves the v0.6 boundary-rescue and v0.4 cluster-cadence "
            "controls.",
            "",
            "Decision: revise, not freeze. The synthetic mechanism works, but "
            "the saved validation replay has no qualifying unknown-origin "
            "W->C rows, so this is robustness/preparation evidence rather than "
            "a new holdout-facing candidate.",
            "",
        ]
    )
    return "\n".join(lines)


def _register_validation(summary: dict[str, Any]) -> None:
    _upsert_entries(
        RunRegistryEntry(
            run_id=VALIDATION_RUN_ID,
            artifact_paths=(
                f"experiments/{VALIDATION_RUN_ID}.jsonl",
                f"experiments/{VALIDATION_RUN_ID}.md",
            ),
            date="2026-06-15",
            pipeline_family="consensus_fresh_agreement_selector",
            split="validation",
            row_count=summary["rows"],
            model="none",
            model_role=(
                "No-call replay of selector v0.7 over saved v0.6 validation "
                "selector rows reconstructed into component rows."
            ),
            mode="no-call replay",
            replay_status="saved_output_replay",
            repair_mode="selector_v0_7_unknown_count_window_rescue",
            cache_reuse_source=str(SOURCE_VALIDATION_JSONL),
            primary_metrics={
                "deterministic_purist_correct": summary["deterministic_purist_correct"],
                "consensus_purist_correct": summary["consensus_purist_correct"],
                "fresh_evidence_purist_correct": summary["fresh_evidence_purist_correct"],
                "selected_purist_correct": summary["selected_purist_correct"],
                "changed_labels": summary["changed_labels"],
                "wrong_to_correct": summary["wrong_to_correct"],
                "correct_to_wrong": summary["correct_to_wrong"],
                "changed_label_precision": summary["changed_label_precision"],
            },
            evidence_validity=(
                "Saved-output validation replay; gold labels are used only for "
                "post-hoc scoring. No holdout rows are read."
            ),
            decision="revise",
            supersedes=(VALIDATION_RUN_ID.replace("_v0_7_", "_v0_6_"),),
            claim_language_notes=(
                "v0.7 preserves the v0.6 validation score and adds a guarded "
                "unknown-origin count-window mechanism. Still validation-only "
                "and not holdout authorization."
            ),
        )
    )


def _register_synthetic(
    stress: dict[str, Any],
    selector_summary: dict[str, Any],
) -> None:
    _upsert_entries(
        RunRegistryEntry(
            run_id=SYNTHETIC_RUN_ID,
            artifact_paths=(
                f"experiments/{SYNTHETIC_RUN_ID}.json",
                f"experiments/{SYNTHETIC_RUN_ID}.md",
            ),
            date="2026-06-15",
            pipeline_family="consensus_fresh_agreement_selector_synthetic_boundary_stress",
            split="synthetic_unknown_count_window_probe",
            row_count=stress["rows"],
            model="none",
            model_role=(
                "Analysis-only synthetic probe over hand-specified unknown "
                "count-window stress cases; no model calls and no Gan rows are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="selector_v0_7_unknown_count_window_rescue",
            cache_reuse_source="Synthetic hand-specified component outputs only.",
            primary_metrics={
                "selected_purist_correct": stress["selected_purist_correct"],
                "desired_action_matches": stress["desired_action_matches"],
                "current_rule_false_positive_count": len(
                    stress["current_rule_false_positive_case_ids"]
                ),
                "conservative_false_negative_count": len(
                    stress["conservative_false_negative_case_ids"]
                ),
                "wrong_to_correct": selector_summary["wrong_to_correct"],
                "correct_to_wrong": selector_summary["correct_to_wrong"],
                "changed_label_precision": selector_summary["changed_label_precision"],
            },
            evidence_validity=(
                "Synthetic mechanism evidence only; no validation or holdout records are read."
            ),
            decision="revise",
            supersedes=(
                "gan2026_consensus_fresh_agreement_selector_v0_6_"
                "boundary_rescue_synthetic_stress_2026-06-15",
            ),
            claim_language_notes=(
                "v0.7 passes a source-near unknown count-window synthetic "
                "mechanism probe, but it does not improve saved validation and "
                "does not authorize a frozen holdout audit."
            ),
        )
    )


def _upsert_entries(new_entry: RunRegistryEntry) -> None:
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != new_entry.run_id
    ]
    entries.append(new_entry)
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
