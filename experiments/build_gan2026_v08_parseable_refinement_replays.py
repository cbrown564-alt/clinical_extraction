"""Build v0.8 parseable denominator/window refinement replay artifacts.

This is a validation-only no-call replay over saved v0.7 selector rows plus a
small source-near synthetic panel for the new v0.8 parseable-refinement gate.
No locked test rows are read and no model calls are made.
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
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_7_"
    "validation750_no_call_replay_2026-06-15.jsonl"
)

VALIDATION_RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_8_"
    "validation750_no_call_replay_2026-06-15"
)
SYNTHETIC_RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_8_"
    "parseable_refinement_synthetic_stress_2026-06-15"
)


@dataclass(frozen=True)
class ParseableRefinementCase:
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


CASES: tuple[ParseableRefinementCase, ...] = (
    ParseableRefinementCase(
        case_id="denominator_window_current_rate_positive",
        family="denominator_window_positive",
        note_text=(
            "The current review documents 11 seizures over the last three "
            "months; the daily estimate in the baseline is too high."
        ),
        gold_label="11 per 3 month",
        deterministic_label="1 per 5 to 7 day",
        consensus_label="11 per 3 month",
        fresh_label="11 per 3 month",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action="accept_parseable_denominator_window_refinement",
        risk_type="intended_positive",
        rationale="Fresh and consensus agree on a parseable count/window label.",
    ),
    ParseableRefinementCase(
        case_id="explicit_current_frequency_range_denominator_positive",
        family="explicit_current_frequency_positive",
        note_text=(
            "The note states the current seizure frequency is one seizure "
            "every six to eight weeks, not daily."
        ),
        gold_label="1 per 6 to 8 week",
        deterministic_label="1 per day",
        consensus_label="1 per 6 to 8 week",
        fresh_label="1 per 6 to 8 week",
        fresh_boundary_profile=(
            "explicit current frequency",
            "no seizure-free or unknown boundary",
            "cluster/seizure frequency clearly stated",
        ),
        desired_action="accept_parseable_denominator_window_refinement",
        risk_type="intended_positive",
        rationale="The denominator range is explicit and current.",
    ),
    ParseableRefinementCase(
        case_id="explicit_count_over_window_cluster_count_positive",
        family="explicit_count_window_positive",
        note_text=(
            "There were five cluster events over approximately six weeks; "
            "no seizure-free or unknown boundary is described."
        ),
        gold_label="3 per month",
        deterministic_label="3 per week",
        consensus_label="4 per 2 month",
        fresh_label="4 per 2 month",
        fresh_boundary_profile=(
            "explicit count of 5 events over approximately 6 weeks",
            "no evidence for seizure-free, unknown, or no_reference",
            "highest current/recent frequency is cluster count",
        ),
        desired_action="accept_parseable_denominator_window_refinement",
        risk_type="intended_positive",
        rationale="The profile identifies an explicit count over a usable window.",
    ),
    ParseableRefinementCase(
        case_id="highest_active_semiology_negative",
        family="highest_semiology_negative",
        note_text=(
            "Several semiologies are discussed; the lower burden semiology has "
            "a cleaner denominator but is not the highest active burden."
        ),
        gold_label="3 to 4 per 15 month",
        deterministic_label="3 to 4 per 15 month",
        consensus_label="2 to 3 per 15 month",
        fresh_label="2 to 3 per 15 month",
        fresh_boundary_profile=("current/recent frequency", "highest active semiology"),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Highest-semiology profiles were unsafe in the v0.7 residual audit.",
    ),
    ParseableRefinementCase(
        case_id="seizure_free_interval_negative",
        family="seizure_free_interval_negative",
        note_text=(
            "The note mixes recent counts with a seizure-free interval; the "
            "baseline label should not be overridden by the cleaner count."
        ),
        gold_label="9 per 3 month",
        deterministic_label="9 per 3 month",
        consensus_label="8 per 2 month",
        fresh_label="8 per 2 month",
        fresh_boundary_profile=(
            "explicit recent seizure counts",
            "no seizure-free interval",
            "current/recent frequency evidence",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Any seizure-free interval marker blocks this refinement family.",
    ),
    ParseableRefinementCase(
        case_id="last_event_only_negative",
        family="last_event_negative",
        note_text=(
            "The last seizure date is stated, but no count over the denominator "
            "is given."
        ),
        gold_label="unknown",
        deterministic_label="unknown",
        consensus_label="1 per 4 month",
        fresh_label="1 per 4 month",
        fresh_boundary_profile=("last event", "current/recent frequency"),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Last-event-only evidence stays unknown.",
    ),
    ParseableRefinementCase(
        case_id="boundary_origin_not_relaxed_negative",
        family="boundary_origin_negative",
        note_text=(
            "A seizure-free baseline and a parseable frequency candidate are "
            "present, but v0.8 is not a boundary-origin relaxation."
        ),
        gold_label="unknown",
        deterministic_label="seizure free for multiple year",
        consensus_label="2 per 6 week",
        fresh_label="2 per 6 week",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Boundary origins remain handled only by the v0.6/v0.7 gates.",
    ),
    ParseableRefinementCase(
        case_id="fresh_consensus_disagreement_negative",
        family="agreement_control",
        note_text="Consensus and fresh evidence disagree about the denominator.",
        gold_label="11 per 3 month",
        deterministic_label="1 per 5 to 7 day",
        consensus_label="11 per 3 month",
        fresh_label="10 per 3 month",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="The parseable refinement still requires exact agreement.",
    ),
    ParseableRefinementCase(
        case_id="unparseable_replacement_negative",
        family="parseability_control",
        note_text="The profile is strong, but the replacement is not parseable.",
        gold_label="3 per month",
        deterministic_label="1 per day",
        consensus_label="several per month",
        fresh_label="several per month",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="v0.8 does not promote parser-incompatible labels.",
    ),
    ParseableRefinementCase(
        case_id="current_recent_only_negative",
        family="missing_profile_negative",
        note_text="The profile says current/recent but gives no denominator/window cue.",
        gold_label="4 per month",
        deterministic_label="4 per month",
        consensus_label="4 per 2 month",
        fresh_label="4 per 2 month",
        fresh_boundary_profile=("current/recent frequency",),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Current/recent alone is too broad for the refinement gate.",
    ),
    ParseableRefinementCase(
        case_id="multiple_active_semiologies_negative",
        family="multi_semiology_negative",
        note_text=(
            "Multiple active semiologies are present; the lower-burden one has "
            "the cleaner denominator."
        ),
        gold_label="2 per week",
        deterministic_label="2 per week",
        consensus_label="1 per 2 month",
        fresh_label="1 per 2 month",
        fresh_boundary_profile=(
            "explicit numeric frequency for highest-burden seizure type",
            "current/recent frequency window",
            "multiple active semiologies, highest burden selected",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Multi-semiology highest-burden cases are blocked.",
    ),
)


def main() -> None:
    source_rows = _load_jsonl(SOURCE_VALIDATION_JSONL)
    validation_rows = _replay_v08(source_rows)
    validation_jsonl = EXPERIMENTS / f"{VALIDATION_RUN_ID}.jsonl"
    validation_md = EXPERIMENTS / f"{VALIDATION_RUN_ID}.md"
    _write_jsonl(validation_rows, validation_jsonl)
    selector.write_report(
        validation_rows,
        validation_md,
        jsonl_path=validation_jsonl,
        source_artifacts={
            "v0.7_selector_rows": str(SOURCE_VALIDATION_JSONL),
            "replay_source": "reconstructed component rows from v0.7 selector rows",
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
            "Synthetic hard-negative probe for v0.8 parseable denominator/window "
            "refinement."
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

    _register_validation(selector.summarize_rows(validation_rows))
    _register_synthetic(synthetic_summary, selector.summarize_rows(synthetic_rows))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _replay_v08(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deterministic_rows, consensus_rows, fresh_rows = _component_rows(source_rows)
    return selector.build_selector_rows(
        deterministic_rows=deterministic_rows,
        consensus_rows=consensus_rows,
        fresh_evidence_rows=fresh_rows,
        policy="parseable_denominator_window_refinement_v0_8",
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
                "consensus_comparison": row["score_layers"]["consensus"][
                    "comparison"
                ],
                "consensus_decision": {"reason": features.get("consensus_reason")},
            }
        )
        fresh_rows.append(
            {
                "source_row_index": source_row_index,
                "fresh_evidence_decision_record": {
                    "action": features.get("fresh_action"),
                    "boundary_profile": features.get("fresh_boundary_profile")
                    or [],
                    "uncertainty": features.get("fresh_uncertainty"),
                },
                "decision_record": {"final_label": row["fresh_evidence_label"]},
                "score_layers": {
                    "final": {
                        "comparison": row["score_layers"]["fresh_evidence"][
                            "comparison"
                        ]
                    }
                },
            }
        )
    return deterministic_rows, consensus_rows, fresh_rows


def _build_synthetic_rows() -> list[dict[str, Any]]:
    deterministic_rows = []
    consensus_rows = []
    fresh_rows = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 930000 + offset
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
        policy="parseable_denominator_window_refinement_v0_8",
    )
    by_index = {row["source_row_index"]: row for row in rows}
    enriched = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 930000 + offset
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


def _case_record(case: ParseableRefinementCase) -> dict[str, Any]:
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
        "consensus_purist_correct": sum(
            _is_layer_correct(row, "consensus") for row in rows
        ),
        "fresh_purist_correct": sum(
            _is_layer_correct(row, "fresh_evidence") for row in rows
        ),
        "selected_purist_correct": sum(
            _is_layer_correct(row, "selected") for row in rows
        ),
        "desired_action_matches": sum(
            row["desired_action_match"] is True for row in rows
        ),
        "desired_action_miss_case_ids": desired_misses,
        "current_rule_false_positive_case_ids": false_positives,
        "conservative_false_negative_case_ids": false_negatives,
        "safety_success_case_ids": safety_successes,
        "by_risk_type": {
            key: dict(value) for key, value in sorted(by_risk_type.items())
        },
    }


def _accumulate_bucket(bucket: dict[str, int], row: dict[str, Any]) -> None:
    bucket["rows"] += 1
    bucket["deterministic_purist_correct"] += int(
        _is_layer_correct(row, "deterministic")
    )
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
        "# Gan 2026 Selector v0.8 Parseable Refinement Synthetic Stress",
        "",
        "Date: 2026-06-15",
        "",
        "This is a predeclared synthetic mechanism probe for v0.8. It uses "
        "hand-specified component outputs and the real selector implementation. "
        "It is not validation, holdout, benchmark, or model-performance evidence.",
        "",
        "## Summary",
        "",
        f"- Rows: {stress['rows']}",
        (
            "- Deterministic Purist: "
            f"{stress['deterministic_purist_correct']}/{stress['rows']}"
        ),
        f"- Consensus Purist: {stress['consensus_purist_correct']}/{stress['rows']}",
        f"- Fresh Purist: {stress['fresh_purist_correct']}/{stress['rows']}",
        f"- Selected Purist: {stress['selected_purist_correct']}/{stress['rows']}",
        (
            "- Desired action matches: "
            f"{stress['desired_action_matches']}/{stress['rows']}"
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
        f"- Changed-label precision: {selector_summary['changed_label_precision']}",
        f"- Actions: `{stress['actions']}`",
        "",
        "## Risk-Type Summary",
        "",
        (
            "| Risk Type | Rows | Deterministic | Consensus | Fresh | Selected | "
            "Desired Matches |"
        ),
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
        selected_correct = row["score_layers"]["selected"]["comparison"][
            "purist_correct"
        ]
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
            "v0.8 accepts parseable consensus+fresh replacements that v0.7 "
            "treated as ambiguous `other` only when the fresh profile supports "
            "a denominator/window refinement or explicit current count/window. "
            "It blocks boundary origins, last-event and seizure-free interval "
            "profiles, highest-semiology traps, disagreement, and unparseable "
            "replacement labels.",
            "",
            "Decision: revise, not freeze. This strengthens the selector on a "
            "small validation-backed family, but it is still saved-output "
            "development evidence rather than a holdout-facing candidate.",
            "",
        ]
    )
    return "\n".join(lines)


def _register_validation(summary: dict[str, Any]) -> None:
    _upsert_entry(
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
                "No-call replay of selector v0.8 over saved v0.7 validation "
                "selector rows reconstructed into component rows."
            ),
            mode="no-call replay",
            replay_status="saved_output_replay",
            repair_mode="selector_v0_8_parseable_denominator_window_refinement",
            cache_reuse_source=str(SOURCE_VALIDATION_JSONL),
            primary_metrics={
                "deterministic_purist_correct": summary[
                    "deterministic_purist_correct"
                ],
                "consensus_purist_correct": summary["consensus_purist_correct"],
                "fresh_evidence_purist_correct": summary[
                    "fresh_evidence_purist_correct"
                ],
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
            supersedes=(VALIDATION_RUN_ID.replace("_v0_8_", "_v0_7_"),),
            claim_language_notes=(
                "v0.8 improves saved validation through a narrow parseable "
                "denominator/window refinement gate. Still validation-only and "
                "not holdout authorization."
            ),
        )
    )


def _register_synthetic(
    stress: dict[str, Any],
    selector_summary: dict[str, Any],
) -> None:
    _upsert_entry(
        RunRegistryEntry(
            run_id=SYNTHETIC_RUN_ID,
            artifact_paths=(
                f"experiments/{SYNTHETIC_RUN_ID}.json",
                f"experiments/{SYNTHETIC_RUN_ID}.md",
            ),
            date="2026-06-15",
            pipeline_family=(
                "consensus_fresh_agreement_selector_synthetic_refinement_stress"
            ),
            split="synthetic_parseable_refinement_probe",
            row_count=stress["rows"],
            model="none",
            model_role=(
                "Analysis-only synthetic probe over hand-specified parseable "
                "refinement stress cases; no model calls and no Gan rows are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="selector_v0_8_parseable_denominator_window_refinement",
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
                "changed_label_precision": selector_summary[
                    "changed_label_precision"
                ],
            },
            evidence_validity=(
                "Synthetic mechanism evidence only; no validation or holdout "
                "records are read."
            ),
            decision="revise",
            supersedes=(
                "gan2026_consensus_fresh_agreement_selector_v0_7_"
                "unknown_count_window_synthetic_stress_2026-06-15",
            ),
            claim_language_notes=(
                "v0.8 passes source-near parseable-refinement hard negatives, "
                "but does not authorize a frozen holdout audit."
            ),
        )
    )


def _upsert_entry(new_entry: RunRegistryEntry) -> None:
    entries = [
        entry
        for entry in load_run_registry(REGISTRY_PATH)
        if entry.run_id != new_entry.run_id
    ]
    entries.append(new_entry)
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
