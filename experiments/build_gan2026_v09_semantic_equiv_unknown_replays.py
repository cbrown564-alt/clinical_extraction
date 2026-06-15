"""Build v0.9 semantic-equivalence and unknown-uncertainty replay artifacts.

This is a validation-only no-call replay over saved v0.8 selector rows plus a
small synthetic hard-negative panel. No locked test rows are read and no model
calls are made.
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
    / "gan2026_consensus_fresh_agreement_selector_v0_8_"
    "validation750_no_call_replay_2026-06-15.jsonl"
)
VALIDATION_RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "validation750_no_call_replay_2026-06-15"
)
SYNTHETIC_RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "semantic_equiv_unknown_synthetic_stress_2026-06-15"
)


@dataclass(frozen=True)
class V09Case:
    case_id: str
    gold_label: str
    deterministic_label: str
    consensus_label: str
    fresh_label: str
    fresh_boundary_profile: tuple[str, ...]
    desired_action: str
    risk_type: str
    rationale: str


CASES: tuple[V09Case, ...] = (
    V09Case(
        case_id="normalized_equivalent_month_positive",
        gold_label="1 per month",
        deterministic_label="12 per month",
        consensus_label="1 per 1 month",
        fresh_label="1 per month",
        fresh_boundary_profile=(
            "explicit last event date",
            "explicit seizure-free interval",
            "duration since last event is just over 4 weeks",
            "no conflicting current/recent frequency evidence",
        ),
        desired_action="accept_normalized_equivalent_agreement",
        risk_type="intended_positive",
        rationale="Consensus and fresh differ in text but normalize to the same rate.",
    ),
    V09Case(
        case_id="unknown_uncertainty_positive",
        gold_label="unknown",
        deterministic_label="1 per 5 day",
        consensus_label="unknown",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "unknown_frequency",
            "no explicit count or rate",
            "device logs suggest clusters but no counts",
            "patient unsure if episodes correspond to device alerts",
        ),
        desired_action="accept_unknown_uncertainty_rescue",
        risk_type="intended_positive",
        rationale="Both model sources identify unquantified uncertainty.",
    ),
    V09Case(
        case_id="non_equivalent_disagreement_negative",
        gold_label="2 per week",
        deterministic_label="2 per week",
        consensus_label="1 per 3 month",
        fresh_label="2 per week",
        fresh_boundary_profile=(
            "highest current clinically active burden",
            "explicit numeric frequency for absence seizures",
            "multiple active semiologies",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Disagreement is not accepted unless normalized rates match.",
    ),
    V09Case(
        case_id="already_equivalent_deterministic_negative",
        gold_label="4 per 7 month",
        deterministic_label="4 per 7 month",
        consensus_label="8 per 14 month",
        fresh_label="4 per 7 month",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="No churn when the deterministic label already normalizes the same way.",
    ),
    V09Case(
        case_id="cluster_burden_specified_unknown_negative",
        gold_label="3 cluster per 6 week, 2 to 4 per cluster",
        deterministic_label="3 cluster per 6 week, 2 to 4 per cluster",
        consensus_label="unknown",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "cluster burden present",
            "cluster frequency and events per cluster both specified",
            "no explicit recurring rate for clusters or events",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Fully specified cluster burden must not be demoted to unknown.",
    ),
    V09Case(
        case_id="unknown_no_reference_origin_negative",
        gold_label="unknown",
        deterministic_label="no seizure frequency reference",
        consensus_label="unknown",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "unknown_frequency",
            "last_event_only",
            "cluster frequency uncertain",
            "no explicit recurring rate",
        ),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="v0.9 avoids no-reference to unknown churn.",
    ),
    V09Case(
        case_id="unknown_missing_profile_negative",
        gold_label="unknown",
        deterministic_label="1 per week",
        consensus_label="unknown",
        fresh_label="unknown",
        fresh_boundary_profile=("current/recent frequency",),
        desired_action="keep_deterministic_baseline",
        risk_type="intended_negative",
        rationale="Unknown rescue requires explicit uncertainty and missing-count markers.",
    ),
)


def main() -> None:
    source_rows = _load_jsonl(SOURCE_VALIDATION_JSONL)
    validation_rows = _replay(source_rows)
    validation_jsonl = EXPERIMENTS / f"{VALIDATION_RUN_ID}.jsonl"
    validation_md = EXPERIMENTS / f"{VALIDATION_RUN_ID}.md"
    _write_jsonl(validation_rows, validation_jsonl)
    selector.write_report(
        validation_rows,
        validation_md,
        jsonl_path=validation_jsonl,
        source_artifacts={
            "v0.8_selector_rows": str(SOURCE_VALIDATION_JSONL),
            "replay_source": "reconstructed component rows from v0.8 selector rows",
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
            "Synthetic hard-negative probe for v0.9 normalized-equivalent "
            "agreement and unknown-uncertainty rescue."
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


def _replay(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deterministic_rows, consensus_rows, fresh_rows = _component_rows(source_rows)
    return selector.build_selector_rows(
        deterministic_rows=deterministic_rows,
        consensus_rows=consensus_rows,
        fresh_evidence_rows=fresh_rows,
        policy="semantic_equiv_unknown_uncertainty_v0_9",
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
        source_row_index = 940000 + offset
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
        policy="semantic_equiv_unknown_uncertainty_v0_9",
    )
    by_index = {row["source_row_index"]: row for row in rows}
    enriched = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 940000 + offset
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


def _case_record(case: V09Case) -> dict[str, Any]:
    gold_monthly = _monthly_frequency(case.gold_label)
    return {
        "case_id": case.case_id,
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
        "# Gan 2026 Selector v0.9 Semantic-Equiv/Unknown Synthetic Stress",
        "",
        "Date: 2026-06-15",
        "",
        "This is a predeclared synthetic mechanism probe for v0.9. It uses "
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
        "## Case Readout",
        "",
        "| Case | Risk | Action | Gate | Selected Correct | Desired Match |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
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
            "v0.9 accepts two small selector-only openings: consensus/fresh "
            "disagreement when the labels normalize to the same rate, and "
            "specific-rate to unknown when both model sources agree on unknown "
            "and the fresh profile explicitly says the evidence is unquantified. "
            "It blocks non-equivalent disagreement, no-reference churn, missing "
            "unknown profiles, and fully specified cluster-burden demotion.",
            "",
            "Decision: revise, not freeze. This is useful residual-headroom "
            "cleanup, but the gain is too small and validation-local for a "
            "holdout-facing candidate.",
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
                "No-call replay of selector v0.9 over saved v0.8 validation "
                "selector rows reconstructed into component rows."
            ),
            mode="no-call replay",
            replay_status="saved_output_replay",
            repair_mode="selector_v0_9_semantic_equiv_unknown_uncertainty",
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
            supersedes=(VALIDATION_RUN_ID.replace("_v0_9_", "_v0_8_"),),
            claim_language_notes=(
                "v0.9 improves saved validation through two narrow residual "
                "selector gates. Still validation-only and not holdout authorization."
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
            pipeline_family="consensus_fresh_agreement_selector_synthetic_v09_stress",
            split="synthetic_semantic_equiv_unknown_probe",
            row_count=stress["rows"],
            model="none",
            model_role=(
                "Analysis-only synthetic probe over hand-specified v0.9 stress "
                "cases; no model calls and no Gan rows are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="selector_v0_9_semantic_equiv_unknown_uncertainty",
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
                "gan2026_consensus_fresh_agreement_selector_v0_8_"
                "parseable_refinement_synthetic_stress_2026-06-15",
            ),
            claim_language_notes=(
                "v0.9 passes source-near hard negatives for two narrow residual "
                "selector gates, but does not authorize a frozen holdout audit."
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
