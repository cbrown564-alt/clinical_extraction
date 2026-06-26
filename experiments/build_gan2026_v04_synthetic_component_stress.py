"""Build a synthetic component-stress panel for selector v0.4.

This is a mechanism probe, not benchmark evidence. The cases are hand-specified
source-near note fragments with synthetic deterministic, consensus, and
fresh-evidence component outputs. Gold labels are used only to score the
predeclared synthetic panel.
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
    "gan2026_consensus_fresh_agreement_selector_v0_4_"
    "synthetic_component_stress_2026-06-15"
)
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"


@dataclass(frozen=True)
class StressCase:
    case_id: str
    family: str
    note_text: str
    gold_label: str
    deterministic_label: str
    consensus_label: str
    fresh_label: str
    expected_v04_action: str
    desired_future_action: str
    rationale: str


CASES: tuple[StressCase, ...] = (
    StressCase(
        case_id="cluster_demote_plain_rate",
        family="cluster_cadence",
        note_text=(
            "Diary describes 3 clusters per month, with multiple seizures in "
            "each cluster; no separate plain monthly rate is stated."
        ),
        gold_label="3 cluster per month, multiple per cluster",
        deterministic_label="3 cluster per month, multiple per cluster",
        consensus_label="3 per month",
        fresh_label="3 per month",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="A cluster cadence should not be demoted to a plain rate.",
    ),
    StressCase(
        case_id="cluster_cadence_change",
        family="cluster_cadence",
        note_text=(
            "Current diary reports 5 clusters per month, multiple seizures per "
            "cluster; an alternate read collapses this to one cluster monthly."
        ),
        gold_label="5 cluster per month, multiple per cluster",
        deterministic_label="5 cluster per month, multiple per cluster",
        consensus_label="1 cluster per month, multiple per cluster",
        fresh_label="1 cluster per month, multiple per cluster",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="The selector should preserve the deterministic cluster cadence.",
    ),
    StressCase(
        case_id="same_cadence_burden_refinement",
        family="cluster_cadence",
        note_text=(
            "There are 2 to 3 clusters per month and each cluster contains about "
            "5 seizures."
        ),
        gold_label="2 to 3 cluster per month, 5 per cluster",
        deterministic_label="2 to 3 cluster per month, multiple per cluster",
        consensus_label="2 to 3 cluster per month, 5 per cluster",
        fresh_label="2 to 3 cluster per month, 5 per cluster",
        expected_v04_action="accept_consensus_fresh_agreement",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale="Same-cadence burden refinement is allowed.",
    ),
    StressCase(
        case_id="plain_monthly_to_cluster_weekly",
        family="cluster_cadence",
        note_text=(
            "Mother reports one cluster each week, usually 2 to 3 seizures in "
            "the cluster."
        ),
        gold_label="1 cluster per week, 2 to 3 per cluster",
        deterministic_label="2 per month",
        consensus_label="1 cluster per week, 2 to 3 per cluster",
        fresh_label="1 cluster per week, 2 to 3 per cluster",
        expected_v04_action="accept_consensus_fresh_agreement",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale=(
            "Consensus can add a cluster label when the deterministic label has "
            "no cluster cadence to protect."
        ),
    ),
    StressCase(
        case_id="last_event_only_unknown",
        family="unknown_boundary",
        note_text=(
            "Her last seizure was on 20 Dec. The note gives no count and no "
            "defined observation period."
        ),
        gold_label="unknown",
        deterministic_label="unknown",
        consensus_label="1 per month",
        fresh_label="1 per month",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="Last-event date alone should not become a frequency.",
    ),
    StressCase(
        case_id="open_ended_since_diet_unknown",
        family="unknown_boundary",
        note_text=(
            "Several drop attacks have occurred since starting the ketogenic "
            "diet; the diet start date is not stated."
        ),
        gold_label="unknown",
        deterministic_label="unknown",
        consensus_label="3 per month",
        fresh_label="3 per month",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="Open-ended since-starting evidence lacks a usable denominator.",
    ),
    StressCase(
        case_id="explicit_count_window_from_unknown",
        family="unknown_boundary",
        note_text=(
            "Topiramate was stopped two months ago; soon afterwards she had two "
            "seizures and none since."
        ),
        gold_label="2 per 2 month",
        deterministic_label="unknown",
        consensus_label="2 per 2 month",
        fresh_label="2 per 2 month",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale=(
            "Current v0.4 is conservative out of unknown origins; this is a "
            "known false-negative cost."
        ),
    ),
    StressCase(
        case_id="no_reference_origin_suppressed",
        family="unknown_boundary",
        note_text=(
            "Epilepsy clinic review discusses medication tolerance but no "
            "seizure frequency information."
        ),
        gold_label="no seizure frequency reference",
        deterministic_label="no seizure frequency reference",
        consensus_label="2 per week",
        fresh_label="2 per week",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="No-reference origins should not be overwritten by a specific rate.",
    ),
    StressCase(
        case_id="unknown_replacement_suppressed",
        family="unknown_boundary",
        note_text="The diary records two seizures per month over the current review period.",
        gold_label="2 per month",
        deterministic_label="2 per month",
        consensus_label="unknown",
        fresh_label="unknown",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="Specific deterministic rates should not be replaced by unknown.",
    ),
    StressCase(
        case_id="seizure_free_replacement_suppressed",
        family="seizure_free_boundary",
        note_text=(
            "She averages two seizures per month; the older seizure-free period "
            "has resolved."
        ),
        gold_label="2 per month",
        deterministic_label="2 per month",
        consensus_label="seizure free",
        fresh_label="seizure free",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="A current frequency should not be replaced by historical seizure-free wording.",
    ),
    StressCase(
        case_id="ambiguous_plural_other_suppressed",
        family="denominator_window",
        note_text="The note says two seizures across a five-month interval.",
        gold_label="2 per month",
        deterministic_label="2 per month",
        consensus_label="2 per 5 months",
        fresh_label="2 per 5 months",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="Parser-ambiguous replacements are suppressed by v0.4.",
    ),
    StressCase(
        case_id="daily_correction_accepted",
        family="denominator_window",
        note_text="Current burden is one seizure each day, not one in the last year.",
        gold_label="1 per day",
        deterministic_label="1 per year",
        consensus_label="1 per day",
        fresh_label="1 per day",
        expected_v04_action="accept_consensus_fresh_agreement",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale="A specific non-boundary correction with fresh agreement is accepted.",
    ),
    StressCase(
        case_id="weekly_denominator_accepted",
        family="denominator_window",
        note_text="The current diary documents five seizures each week.",
        gold_label="5 per week",
        deterministic_label="2 per month",
        consensus_label="5 per week",
        fresh_label="5 per week",
        expected_v04_action="accept_consensus_fresh_agreement",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale="Weekly denominator corrections are allowed when specific and agreed.",
    ),
    StressCase(
        case_id="multi_semiology_highest_current",
        family="multi_semiology",
        note_text=(
            "Focal seizures occur once per month, while tonic-clonic seizures "
            "occur three times per week."
        ),
        gold_label="3 per week",
        deterministic_label="1 per month",
        consensus_label="3 per week",
        fresh_label="3 per week",
        expected_v04_action="accept_consensus_fresh_agreement",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale=(
            "The selected current burden should follow the highest current "
            "seizure frequency."
        ),
    ),
    StressCase(
        case_id="fresh_disagrees_keep",
        family="agreement_control",
        note_text="The diary records five seizures each week.",
        gold_label="5 per week",
        deterministic_label="5 per week",
        consensus_label="1 per day",
        fresh_label="5 per week",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="Consensus without fresh-evidence agreement is not enough to switch.",
    ),
    StressCase(
        case_id="consensus_same_unchanged",
        family="agreement_control",
        note_text="The current report remains two seizures per month.",
        gold_label="2 per month",
        deterministic_label="2 per month",
        consensus_label="2 per month",
        fresh_label="2 per month",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="No selector action is needed when consensus matches deterministic.",
    ),
    StressCase(
        case_id="same_day_cluster_demotion_category_neutral",
        family="cluster_cadence",
        note_text=(
            "Every five days she has a cluster with 2 to 4 seizures in that "
            "cluster."
        ),
        gold_label="1 cluster per 5 day, 2 to 4 per cluster",
        deterministic_label="1 cluster per 5 day, 2 to 4 per cluster",
        consensus_label="1 per 5 day",
        fresh_label="1 per 5 day",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="keep_deterministic_baseline",
        rationale="Even when Purist category is unchanged, cluster semantics should be preserved.",
    ),
    StressCase(
        case_id="explicit_followup_from_unknown",
        family="unknown_boundary",
        note_text=(
            "Since the medication change three months ago, exactly three "
            "seizures are documented."
        ),
        gold_label="3 per month",
        deterministic_label="unknown",
        consensus_label="3 per month",
        fresh_label="3 per month",
        expected_v04_action="keep_deterministic_baseline",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale=(
            "Another explicit count-window case exposes the conservative "
            "unknown-origin cost."
        ),
    ),
    StressCase(
        case_id="plain_to_cluster_monthly_refinement",
        family="cluster_cadence",
        note_text="She has one monthly cluster, with multiple seizures in the cluster.",
        gold_label="1 cluster per month, multiple per cluster",
        deterministic_label="2 per month",
        consensus_label="1 cluster per month, multiple per cluster",
        fresh_label="1 cluster per month, multiple per cluster",
        expected_v04_action="accept_consensus_fresh_agreement",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale="Adding cluster semantics is allowed when deterministic had no cluster cadence.",
    ),
    StressCase(
        case_id="monthly_within_band_churn",
        family="denominator_window",
        note_text="The note gives two seizures per month in the current interval.",
        gold_label="2 per month",
        deterministic_label="1 per month",
        consensus_label="2 per month",
        fresh_label="2 per month",
        expected_v04_action="accept_consensus_fresh_agreement",
        desired_future_action="accept_consensus_fresh_agreement",
        rationale="Specific same-band refinements may be accepted, but they do not improve Purist.",
    ),
)


def main() -> None:
    deterministic_rows = []
    consensus_rows = []
    fresh_rows = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 900000 + offset
        gold_monthly = _monthly_frequency(case.gold_label)
        deterministic_rows.append(
            {
                "source_row_index": source_row_index,
                "final_label": case.deterministic_label,
                "comparison": {
                    "purist_correct": _purist_correct(
                        case.deterministic_label, case.gold_label
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
                        case.consensus_label, case.gold_label
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
                    "boundary_profile": [case.family],
                    "uncertainty": "synthetic",
                },
                "decision_record": {"final_label": case.fresh_label},
                "score_layers": {
                    "final": {
                        "comparison": {
                            "purist_correct": _purist_correct(
                                case.fresh_label, case.gold_label
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
        policy="cluster_cadence_precision_v0_4",
    )
    by_index = {row["source_row_index"]: row for row in rows}
    enriched_rows = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 900000 + offset
        row = dict(by_index[source_row_index])
        row["synthetic_case"] = _case_record(case)
        row["expected_v04_action_match"] = (
            row["selector_action"] == case.expected_v04_action
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
            "Synthetic mechanism probe for consensus+fresh selector v0.4; "
            "not validation, holdout, benchmark, or model-performance evidence."
        ),
        "selector_summary": selector.summarize_rows(enriched_rows),
        "stress_summary": summary,
        "cases": [_case_record(case) for case in CASES],
        "rows": enriched_rows,
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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


def _case_record(case: StressCase) -> dict[str, Any]:
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
        "expected_v04_action": case.expected_v04_action,
        "desired_future_action": case.desired_future_action,
        "rationale": case.rationale,
    }


def _stress_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    families: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
    gates = Counter(str(row["selector_gate"]) for row in rows)
    actions = Counter(str(row["selector_action"]) for row in rows)
    false_negatives = []
    safety_successes = []
    desired_misses = []
    for row in rows:
        case = row["synthetic_case"]
        family = case["family"]
        families[family]["rows"] += 1
        families[family]["selected_purist_correct"] += int(
            row["score_layers"]["selected"]["comparison"]["purist_correct"] is True
        )
        families[family]["deterministic_purist_correct"] += int(
            row["score_layers"]["deterministic"]["comparison"]["purist_correct"] is True
        )
        families[family]["consensus_purist_correct"] += int(
            row["score_layers"]["consensus"]["comparison"]["purist_correct"] is True
        )
        families[family]["fresh_purist_correct"] += int(
            row["score_layers"]["fresh_evidence"]["comparison"]["purist_correct"]
            is True
        )
        families[family]["expected_v04_action_matches"] += int(
            row["expected_v04_action_match"] is True
        )
        families[family]["desired_future_action_matches"] += int(
            row["desired_future_action_match"] is True
        )
        det_correct = row["score_layers"]["deterministic"]["comparison"][
            "purist_correct"
        ] is True
        consensus_correct = row["score_layers"]["consensus"]["comparison"][
            "purist_correct"
        ] is True
        selected_correct = row["score_layers"]["selected"]["comparison"][
            "purist_correct"
        ] is True
        if not det_correct and consensus_correct and not selected_correct:
            false_negatives.append(case["case_id"])
        if det_correct and not consensus_correct and selected_correct:
            safety_successes.append(case["case_id"])
        if row["desired_future_action_match"] is not True:
            desired_misses.append(case["case_id"])

    return {
        "rows": len(rows),
        "selector_version": rows[0]["selector_version"],
        "actions": dict(actions),
        "gates": dict(gates),
        "deterministic_purist_correct": sum(
            row["score_layers"]["deterministic"]["comparison"]["purist_correct"] is True
            for row in rows
        ),
        "consensus_purist_correct": sum(
            row["score_layers"]["consensus"]["comparison"]["purist_correct"] is True
            for row in rows
        ),
        "fresh_purist_correct": sum(
            row["score_layers"]["fresh_evidence"]["comparison"]["purist_correct"] is True
            for row in rows
        ),
        "selected_purist_correct": sum(
            row["score_layers"]["selected"]["comparison"]["purist_correct"] is True
            for row in rows
        ),
        "expected_v04_action_matches": sum(
            row["expected_v04_action_match"] is True for row in rows
        ),
        "desired_future_action_matches": sum(
            row["desired_future_action_match"] is True for row in rows
        ),
        "false_negative_case_ids": false_negatives,
        "safety_success_case_ids": safety_successes,
        "desired_future_action_miss_case_ids": desired_misses,
        "by_family": {key: dict(value) for key, value in sorted(families.items())},
    }


def _markdown_report(payload: dict[str, Any]) -> str:
    stress = payload["stress_summary"]
    selector_summary = payload["selector_summary"]
    lines = [
        "# Gan 2026 Selector v0.4 Synthetic Component-Stress Panel",
        "",
        "Date: 2026-06-15",
        "",
        "This is a predeclared synthetic mechanism probe for the v0.4 "
        "consensus+fresh agreement selector. It uses hand-specified component "
        "outputs and the real selector implementation. It is not validation, "
        "holdout, benchmark, or model-performance evidence.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: synthetic component-stress / selector mechanics.",
        "- Split: `synthetic_validation_probe`; no Gan rows are read.",
        "- Scorer: current Gan-compatible Purist mapping for synthetic labels.",
        "- Selector: `cluster_cadence_precision_v0_4`.",
        (
            "- Stress families: cluster cadence, unknown boundary, "
            "denominator/window, multi-semiology, seizure-free boundary, and "
            "agreement controls."
        ),
        (
            "- Stop rule: record safety behavior and known conservative costs; "
            "do not freeze for holdout from this artifact alone."
        ),
        "",
        "## Summary",
        "",
        f"- Rows: {stress['rows']}",
        f"- Deterministic Purist: {stress['deterministic_purist_correct']}/{stress['rows']}",
        f"- Consensus Purist: {stress['consensus_purist_correct']}/{stress['rows']}",
        f"- Fresh Purist: {stress['fresh_purist_correct']}/{stress['rows']}",
        f"- Selected Purist: {stress['selected_purist_correct']}/{stress['rows']}",
        f"- Expected v0.4 action matches: {stress['expected_v04_action_matches']}/{stress['rows']}",
        (
            "- Desired future action matches: "
            f"{stress['desired_future_action_matches']}/{stress['rows']}"
        ),
        (
            "- False negatives from conservative unknown-origin gate: "
            f"{len(stress['false_negative_case_ids'])}"
        ),
        (
            "- Safety successes where v0.4 blocks a wrong agreed switch: "
            f"{len(stress['safety_success_case_ids'])}"
        ),
        f"- Selector changed labels: {selector_summary['changed_labels']}",
        (
            "- Selector W->C / C->W: "
            f"{selector_summary['wrong_to_correct']} / "
            f"{selector_summary['correct_to_wrong']}"
        ),
        f"- Actions: `{stress['actions']}`",
        "",
        "## Family Summary",
        "",
        (
            "| Family | Rows | Deterministic | Consensus | Fresh | Selected | "
            "Expected Action Matches | Desired Matches |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for family, info in stress["by_family"].items():
        lines.append(
            f"| `{family}` | {info['rows']} | "
            f"{info['deterministic_purist_correct']} | "
            f"{info['consensus_purist_correct']} | "
            f"{info['fresh_purist_correct']} | "
            f"{info['selected_purist_correct']} | "
            f"{info['expected_v04_action_matches']} | "
            f"{info['desired_future_action_matches']} |"
        )
    lines.extend(
        [
            "",
            "## Case Readout",
            "",
            (
                "| Case | Family | Gold | Deterministic | Consensus | Fresh | "
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
            f"| `{case['case_id']}` | `{case['family']}` | "
            f"`{case['gold_label']}` | `{case['deterministic_label']}` | "
            f"`{case['consensus_label']}` | `{case['fresh_label']}` | "
            f"`{row['selector_action']}` | "
            f"`{row['selector_gate']}` | {selected_correct} | "
            f"{case['rationale']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "v0.4 behaves as designed on the stress panel: it protects cluster "
            "cadence, suppresses last-event-only and open-ended unknown-boundary "
            "over-inference, blocks seizure-free/unknown replacements of specific "
            "rates, and requires fresh-evidence agreement before switching.",
            "",
            "The panel also exposes the main conservative cost: explicit "
            "count-plus-window cases that start from deterministic `unknown` are "
            "kept as unknown by the current selector. That is safer under "
            "Yujian's guidance, but it likely leaves recoverable rows on the "
            "table. A future v0.5 should only relax this with a narrow evidence "
            "feature for explicit count plus usable follow-up period, and should "
            "be tested on a separate predeclared panel before any holdout-facing "
            "protocol.",
            "",
            "Decision: revise, not freeze. This synthetic probe supports the "
            "v0.4 mechanism but does not establish validation/test generalization "
            "or authorize a `test450` audit.",
            "",
        ]
    )
    return "\n".join(lines)


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
        pipeline_family="consensus_fresh_agreement_selector_synthetic_component_stress",
        split="synthetic_validation_probe",
        row_count=summary["rows"],
        model="none",
        model_role=(
            "Analysis-only synthetic component-stress probe over hand-specified "
            "deterministic, consensus, and V12 fresh-evidence labels; no model "
            "calls and no Gan rows are read."
        ),
        mode="analysis-only",
        replay_status="analysis_only",
        repair_mode="selector_v0_4_cluster_cadence_precision",
        cache_reuse_source="Synthetic hand-specified component outputs only.",
        primary_metrics={
            "rows": summary["rows"],
            "deterministic_purist_correct": summary[
                "deterministic_purist_correct"
            ],
            "consensus_purist_correct": summary[
                "consensus_purist_correct"
            ],
            "fresh_purist_correct": summary["fresh_purist_correct"],
            "selected_purist_correct": summary["selected_purist_correct"],
            "expected_v04_action_matches": summary[
                "expected_v04_action_matches"
            ],
            "desired_future_action_matches": summary[
                "desired_future_action_matches"
            ],
            "false_negative_count": len(summary["false_negative_case_ids"]),
            "safety_success_count": len(summary["safety_success_case_ids"]),
        },
        evidence_validity=(
            "Synthetic mechanism evidence only: source-near note fragments and "
            "hand-specified labels are scored through the current Gan Purist "
            "mapping; no validation or holdout records are read."
        ),
        decision="revise",
        supersedes=(
            "gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15",
        ),
        claim_language_notes=(
            "Predeclared synthetic component-stress probe for selector v0.4. "
            "Supports the cluster-cadence and unknown-boundary mechanics, exposes "
            "the conservative unknown-origin false-negative cost, and does not "
            "authorize a frozen holdout audit."
        ),
    )
    entries.append(entry)
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
