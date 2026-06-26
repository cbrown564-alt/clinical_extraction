"""Build the frozen v0.9 Gate 2 robustness/stress panel.

The panel uses hand-specified synthetic/source-near component states and the
real frozen v0.9 selector implementation. It makes no model calls, changes no
selector behavior, and does not read locked test rows.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    consensus_fresh_agreement_selector as selector,
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
RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "frozen_gate2_robustness_stress_2026-06-26"
)
JSON_OUT = EXPERIMENTS / f"{RUN_ID}.json"
MD_OUT = EXPERIMENTS / f"{RUN_ID}.md"

KEEP = "keep_deterministic_baseline"
ACCEPT_CONSENSUS = "accept_consensus_fresh_agreement"
ACCEPT_FRESH_BOUNDARY = "accept_fresh_boundary_rescue"
ACCEPT_PARSEABLE = "accept_parseable_denominator_window_refinement"
ACCEPT_EQUIV = "accept_normalized_equivalent_agreement"
ACCEPT_UNKNOWN = "accept_unknown_uncertainty_rescue"

REQUIRED_FAMILIES = (
    "normalized_equivalent_agreement",
    "unknown_uncertainty",
    "unknown_no_reference_churn",
    "last_event_seizure_free_overinference",
    "cluster_burden_preservation",
    "multiple_semiology_denominator_conflict",
    "non_equivalent_consensus_fresh_disagreement",
    "parseable_denominator_window_refinement",
)


@dataclass(frozen=True)
class Gate2Case:
    case_id: str
    family: str
    control_type: str
    gold_label: str
    deterministic_label: str
    consensus_label: str
    fresh_label: str
    fresh_boundary_profile: tuple[str, ...]
    desired_action: str
    note_text: str
    rationale: str
    spelling_probe: bool = False


CASES: tuple[Gate2Case, ...] = (
    Gate2Case(
        case_id="norm_equiv_positive_month_spelling",
        family="normalized_equivalent_agreement",
        control_type="positive",
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
        desired_action=ACCEPT_EQUIV,
        note_text="The components differ in spelling but point to one seizure per month.",
        rationale="Consensus and fresh normalize to the same rate while baseline does not.",
        spelling_probe=True,
    ),
    Gate2Case(
        case_id="norm_equiv_negative_deterministic_already_same",
        family="normalized_equivalent_agreement",
        control_type="deterministic_correct_negative",
        gold_label="4 per 7 month",
        deterministic_label="4 per 7 month",
        consensus_label="8 per 14 month",
        fresh_label="4 per 7 month",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action=KEEP,
        note_text="The deterministic label already has the same normalized rate.",
        rationale="Equivalent model spelling should not churn a correct baseline.",
        spelling_probe=True,
    ),
    Gate2Case(
        case_id="norm_equiv_paraphrase_week_to_month",
        family="normalized_equivalent_agreement",
        control_type="paraphrase",
        gold_label="1 per week",
        deterministic_label="1 per day",
        consensus_label="2 per 2 week",
        fresh_label="1 per week",
        fresh_boundary_profile=("explicit current frequency", "denominator/window"),
        desired_action=ACCEPT_EQUIV,
        note_text="One per week and two per two weeks are equivalent parser rates.",
        rationale="Minimal wording perturbation should still use normalized equivalence.",
        spelling_probe=True,
    ),
    Gate2Case(
        case_id="unknown_uncertainty_positive_unquantified_logs",
        family="unknown_uncertainty",
        control_type="positive",
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
        desired_action=ACCEPT_UNKNOWN,
        note_text="Device alerts are mentioned but the patient cannot quantify seizures.",
        rationale="Both model components agree the frequency-bearing evidence is unquantified.",
    ),
    Gate2Case(
        case_id="unknown_uncertainty_negative_missing_profile",
        family="unknown_uncertainty",
        control_type="deterministic_correct_negative",
        gold_label="1 per week",
        deterministic_label="1 per week",
        consensus_label="unknown",
        fresh_label="unknown",
        fresh_boundary_profile=("current/recent frequency",),
        desired_action=KEEP,
        note_text="A current weekly rate is present; components are overcautious.",
        rationale="Unknown rescue needs explicit unquantified-frequency markers.",
    ),
    Gate2Case(
        case_id="unknown_uncertainty_paraphrase_patient_unsure",
        family="unknown_uncertainty",
        control_type="paraphrase",
        gold_label="unknown",
        deterministic_label="2 per week",
        consensus_label="unknown",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "unknown frequency",
            "patient unsure",
            "no explicit recurring rate",
        ),
        desired_action=ACCEPT_UNKNOWN,
        note_text="Patient is unsure how often events occur and no recurring rate is stated.",
        rationale="Paraphrased uncertainty markers should trigger the same v0.9 rescue.",
    ),
    Gate2Case(
        case_id="unknown_no_reference_positive_seizure_free_rescue",
        family="unknown_no_reference_churn",
        control_type="positive",
        gold_label="seizure free for multiple year",
        deterministic_label="no seizure frequency reference",
        consensus_label="no seizure frequency reference",
        fresh_label="seizure free for multiple year",
        fresh_boundary_profile=(
            "no_reference boundary",
            "explicit seizure-free interval",
            "no current or recent epileptic seizure frequency evidence",
        ),
        desired_action=ACCEPT_FRESH_BOUNDARY,
        note_text="The note says there have been no epileptic seizures for years.",
        rationale="The older boundary rescue can correct no-reference to seizure-free.",
    ),
    Gate2Case(
        case_id="unknown_no_reference_negative_no_ref_to_unknown",
        family="unknown_no_reference_churn",
        control_type="deterministic_correct_negative",
        gold_label="no seizure frequency reference",
        deterministic_label="no seizure frequency reference",
        consensus_label="unknown",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "unknown_frequency",
            "last_event_only",
            "no explicit recurring rate",
        ),
        desired_action=KEEP,
        note_text="There is no seizure-frequency reference; unknown would be churn.",
        rationale="No-reference origin must not be converted to unknown.",
    ),
    Gate2Case(
        case_id="unknown_no_reference_paraphrase_absence_only",
        family="unknown_no_reference_churn",
        control_type="paraphrase",
        gold_label="no seizure frequency reference",
        deterministic_label="no seizure frequency reference",
        consensus_label="no seizure frequency reference",
        fresh_label="seizure free for multiple year",
        fresh_boundary_profile=("no positive seizure-frequency evidence",),
        desired_action=KEEP,
        note_text="The letter simply omits frequency content.",
        rationale="Absence-only wording should not become a seizure-free claim.",
    ),
    Gate2Case(
        case_id="last_event_positive_seizure_free_overreach",
        family="last_event_seizure_free_overinference",
        control_type="positive",
        gold_label="unknown",
        deterministic_label="seizure free for multiple year",
        consensus_label="seizure free for multiple year",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "last event only",
            "not seizure free",
            "no explicit seizure-free duration",
        ),
        desired_action=ACCEPT_FRESH_BOUNDARY,
        note_text="Only a last event is given; there is no recurring rate or remission duration.",
        rationale="Fresh boundary rescue should undo seizure-free over-inference.",
    ),
    Gate2Case(
        case_id="last_event_negative_affirms_seizure_free",
        family="last_event_seizure_free_overinference",
        control_type="deterministic_correct_negative",
        gold_label="seizure free for 6 month",
        deterministic_label="seizure free for 6 month",
        consensus_label="seizure free for 6 month",
        fresh_label="unknown",
        fresh_boundary_profile=("explicit seizure-free duration", "zero-event interval stated"),
        desired_action=KEEP,
        note_text="A six-month seizure-free interval is explicitly documented.",
        rationale="Profile affirming seizure freedom blocks fresh unknown.",
    ),
    Gate2Case(
        case_id="last_event_paraphrase_no_further_events_but_short",
        family="last_event_seizure_free_overinference",
        control_type="paraphrase",
        gold_label="unknown",
        deterministic_label="seizure free for multiple year",
        consensus_label="seizure free for multiple year",
        fresh_label="no seizure frequency reference",
        fresh_boundary_profile=(
            "last event",
            "no explicit recurring rate",
            "not seizure free",
        ),
        desired_action=ACCEPT_FRESH_BOUNDARY,
        note_text="No further events are mentioned after a date, but no duration is established.",
        rationale="Paraphrased last-event-only wording should stay uncertain/no-reference.",
    ),
    Gate2Case(
        case_id="cluster_positive_same_cadence_events_per_cluster",
        family="cluster_burden_preservation",
        control_type="positive",
        gold_label="2 cluster per month, 3 per cluster",
        deterministic_label="2 cluster per month, multiple per cluster",
        consensus_label="2 cluster per month, 3 per cluster",
        fresh_label="2 cluster per month, 3 per cluster",
        fresh_boundary_profile=("cluster burden", "events per cluster both specified"),
        desired_action=ACCEPT_CONSENSUS,
        note_text="The cadence is unchanged and events per cluster are clarified.",
        rationale="Same-cadence cluster burden refinement is allowed.",
    ),
    Gate2Case(
        case_id="cluster_negative_demote_to_plain_rate",
        family="cluster_burden_preservation",
        control_type="deterministic_correct_negative",
        gold_label="2 cluster per month, multiple per cluster",
        deterministic_label="2 cluster per month, multiple per cluster",
        consensus_label="2 per month",
        fresh_label="2 per month",
        fresh_boundary_profile=(
            "cluster burden present",
            "cluster frequency with explicit cadence",
        ),
        desired_action=KEEP,
        note_text="The model components drop cluster structure.",
        rationale="Cluster labels must not be demoted to ordinary rates.",
    ),
    Gate2Case(
        case_id="cluster_paraphrase_fully_specified_unknown_block",
        family="cluster_burden_preservation",
        control_type="paraphrase",
        gold_label="3 cluster per 6 week, 2 to 4 per cluster",
        deterministic_label="3 cluster per 6 week, 2 to 4 per cluster",
        consensus_label="unknown",
        fresh_label="unknown",
        fresh_boundary_profile=(
            "cluster burden present",
            "cluster frequency and events per cluster both specified",
        ),
        desired_action=KEEP,
        note_text="Both cluster cadence and events per cluster are fully specified.",
        rationale="Unknown demotion is blocked when cluster burden is specified.",
    ),
    Gate2Case(
        case_id="multi_semiology_positive_parseable_refinement",
        family="multiple_semiology_denominator_conflict",
        control_type="positive",
        gold_label="11 per 3 month",
        deterministic_label="1 per 5 to 7 day",
        consensus_label="11 per 3 month",
        fresh_label="11 per 3 month",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action=ACCEPT_PARSEABLE,
        note_text="The current active semiology has 11 events over three months.",
        rationale="A denominator/window refinement is allowed without conflict markers.",
    ),
    Gate2Case(
        case_id="multi_semiology_negative_lower_burden_selected",
        family="multiple_semiology_denominator_conflict",
        control_type="deterministic_correct_negative",
        gold_label="2 per week",
        deterministic_label="2 per week",
        consensus_label="1 per 2 month",
        fresh_label="1 per 2 month",
        fresh_boundary_profile=(
            "explicit numeric frequency for highest-burden seizure type",
            "multiple active semiologies, highest burden selected",
        ),
        desired_action=KEEP,
        note_text="A lower-burden semiology has a cleaner denominator than the active one.",
        rationale="Multi-semiology conflict blocks parseable refinement.",
    ),
    Gate2Case(
        case_id="multi_semiology_paraphrase_highest_active_block",
        family="multiple_semiology_denominator_conflict",
        control_type="paraphrase",
        gold_label="3 to 4 per 15 month",
        deterministic_label="3 to 4 per 15 month",
        consensus_label="2 to 3 per 15 month",
        fresh_label="2 to 3 per 15 month",
        fresh_boundary_profile=("current/recent frequency", "highest active semiology"),
        desired_action=KEEP,
        note_text="The lower rate belongs to a different semiology.",
        rationale="Highest-active-semiology markers remain unsafe for refinement.",
    ),
    Gate2Case(
        case_id="non_equiv_positive_equiv_disagreement",
        family="non_equivalent_consensus_fresh_disagreement",
        control_type="positive",
        gold_label="1 per month",
        deterministic_label="12 per month",
        consensus_label="1 per 1 month",
        fresh_label="1 per month",
        fresh_boundary_profile=("explicit current frequency", "denominator/window"),
        desired_action=ACCEPT_EQUIV,
        note_text="The disagreement is textual only and normalized rates match.",
        rationale="Equivalent disagreement is the only accepted disagreement form.",
        spelling_probe=True,
    ),
    Gate2Case(
        case_id="non_equiv_negative_disagreement_kept",
        family="non_equivalent_consensus_fresh_disagreement",
        control_type="deterministic_correct_negative",
        gold_label="2 per week",
        deterministic_label="2 per week",
        consensus_label="1 per 3 month",
        fresh_label="2 per week",
        fresh_boundary_profile=(
            "highest current clinically active burden",
            "multiple active semiologies",
        ),
        desired_action=KEEP,
        note_text="Consensus and fresh disagree semantically.",
        rationale="Non-equivalent disagreement keeps deterministic baseline.",
    ),
    Gate2Case(
        case_id="non_equiv_paraphrase_near_numeric_disagreement",
        family="non_equivalent_consensus_fresh_disagreement",
        control_type="paraphrase",
        gold_label="11 per 3 month",
        deterministic_label="1 per 5 to 7 day",
        consensus_label="11 per 3 month",
        fresh_label="10 per 3 month",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action=KEEP,
        note_text="The component labels are close but not equivalent.",
        rationale="Near-miss numeric disagreement is blocked.",
        spelling_probe=True,
    ),
    Gate2Case(
        case_id="parseable_positive_current_denominator_window",
        family="parseable_denominator_window_refinement",
        control_type="positive",
        gold_label="11 per 3 month",
        deterministic_label="1 per 5 to 7 day",
        consensus_label="11 per 3 month",
        fresh_label="11 per 3 month",
        fresh_boundary_profile=("current/recent frequency", "denominator/window"),
        desired_action=ACCEPT_PARSEABLE,
        note_text="Eleven seizures over the last three months is current and parseable.",
        rationale="Inherited v0.8 positive control.",
    ),
    Gate2Case(
        case_id="parseable_negative_seizure_free_interval",
        family="parseable_denominator_window_refinement",
        control_type="deterministic_correct_negative",
        gold_label="9 per 3 month",
        deterministic_label="9 per 3 month",
        consensus_label="8 per 2 month",
        fresh_label="8 per 2 month",
        fresh_boundary_profile=(
            "explicit recent seizure counts",
            "no seizure-free interval",
            "current/recent frequency evidence",
        ),
        desired_action=KEEP,
        note_text="A seizure-free interval marker makes the cleaner count unsafe.",
        rationale="Inherited v0.8 negative control.",
    ),
    Gate2Case(
        case_id="parseable_paraphrase_explicit_count_window",
        family="parseable_denominator_window_refinement",
        control_type="paraphrase",
        gold_label="4 per 2 month",
        deterministic_label="3 per week",
        consensus_label="4 per 2 month",
        fresh_label="4 per 2 month",
        fresh_boundary_profile=(
            "explicit count of 4 events over 2 months",
            "no evidence for seizure-free, unknown, or no_reference",
        ),
        desired_action=ACCEPT_PARSEABLE,
        note_text="A count-over-window paraphrase preserves the same mechanism.",
        rationale="Explicit count plus window should support the inherited gate.",
    ),
)


def main() -> None:
    rows = _build_rows()
    summary = _summary(rows)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-26",
        "purpose": (
            "Frozen Gate 2 robustness/stress panel for v0.9 selector gates over "
            "synthetic and source-near validation-only component states."
        ),
        "claim_boundary": (
            "Mechanism evidence only. Hand-specified component states are passed "
            "through the real frozen v0.9 selector. No model calls, scorer changes, "
            "validation tuning, or locked test rows."
        ),
        "selector_version": selector.SELECTOR_V0_9_VERSION,
        "summary": summary,
        "cases": [_case_record(case) for case in CASES],
        "rows": rows,
        "gate_passed": summary["gate_checks"]["gate_passed"],
        "interpretation": _interpretation(summary),
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(_markdown(payload), encoding="utf-8")


def _build_rows() -> list[dict[str, Any]]:
    deterministic_rows = []
    consensus_rows = []
    fresh_rows = []
    for offset, case in enumerate(CASES, start=1):
        source_row_index = 950000 + offset
        deterministic_rows.append(
            {
                "source_row_index": source_row_index,
                "final_label": case.deterministic_label,
                "comparison": _comparison(case.deterministic_label, case.gold_label),
                "reference": {
                    "gold_label": case.gold_label,
                    "gold_monthly_frequency": _monthly(case.gold_label),
                    "row_ok": True,
                },
            }
        )
        consensus_rows.append(
            {
                "source_row_index": source_row_index,
                "consensus_final_label": case.consensus_label,
                "consensus_comparison": _comparison(case.consensus_label, case.gold_label),
                "consensus_decision": {"reason": "gate2_predeclared_case"},
            }
        )
        fresh_rows.append(
            {
                "source_row_index": source_row_index,
                "fresh_evidence_decision_record": {
                    "action": "gate2_synthetic_component_output",
                    "boundary_profile": list(case.fresh_boundary_profile),
                    "uncertainty": "low",
                },
                "decision_record": {"final_label": case.fresh_label},
                "score_layers": {
                    "final": {"comparison": _comparison(case.fresh_label, case.gold_label)}
                },
            }
        )
    selector_rows = selector.build_selector_rows(
        deterministic_rows=deterministic_rows,
        consensus_rows=consensus_rows,
        fresh_evidence_rows=fresh_rows,
        policy="semantic_equiv_unknown_uncertainty_v0_9",
    )
    rows_by_id = {row["source_row_index"]: row for row in selector_rows}
    enriched = []
    for offset, case in enumerate(CASES, start=1):
        row = dict(rows_by_id[950000 + offset])
        row["gate2_case"] = _case_record(case)
        row["desired_action_match"] = row["selector_action"] == case.desired_action
        row["deterministic_correct_control"] = case.control_type == "deterministic_correct_negative"
        row["false_positive_selector_action"] = (
            row["deterministic_correct_control"] and row["selector_action"] != KEEP
        )
        row["cluster_burden_demoted"] = (
            "cluster" in case.deterministic_label.lower()
            and "cluster" not in row["selected_label"].lower()
        )
        row["no_reference_to_unknown_churn"] = (
            case.deterministic_label == "no seizure frequency reference"
            and row["selected_label"] == "unknown"
        )
        enriched.append(row)
    return enriched


def _monthly(label: str) -> float | None:
    try:
        return label_to_monthly_frequency(label)
    except Exception:
        return None


def _comparison(prediction: str, gold: str) -> dict[str, Any]:
    predicted_monthly = _monthly(prediction)
    gold_monthly = _monthly(gold)
    if predicted_monthly is None or gold_monthly is None:
        purist_correct = False
        pragmatic_correct = False
        predicted_purist = None
        gold_purist = None
        predicted_pragmatic = None
        gold_pragmatic = None
    else:
        predicted_purist = str(map_purist(predicted_monthly))
        gold_purist = str(map_purist(gold_monthly))
        predicted_pragmatic = str(map_pragmatic(predicted_monthly))
        gold_pragmatic = str(map_pragmatic(gold_monthly))
        purist_correct = predicted_purist == gold_purist
        pragmatic_correct = predicted_pragmatic == gold_pragmatic
    return {
        "purist_correct": purist_correct,
        "pragmatic_correct": pragmatic_correct,
        "predicted_monthly_frequency": predicted_monthly,
        "gold_monthly_frequency": gold_monthly,
        "predicted_purist_category": predicted_purist,
        "gold_purist_category": gold_purist,
        "predicted_pragmatic_category": predicted_pragmatic,
        "gold_pragmatic_category": gold_pragmatic,
    }


def _correct(row: dict[str, Any], layer: str, metric: str) -> bool:
    return bool(row["score_layers"][layer]["comparison"][f"{metric}_correct"])


def _transition_counts(rows: list[dict[str, Any]], metric: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        baseline = _correct(row, "deterministic", metric)
        selected = _correct(row, "selected", metric)
        if not baseline and selected:
            counts["wrong_to_correct"] += 1
        elif baseline and not selected:
            counts["correct_to_wrong"] += 1
        elif baseline and selected:
            counts["correct_to_correct"] += 1
        else:
            counts["wrong_to_wrong"] += 1
    return counts


def _case_record(case: Gate2Case) -> dict[str, Any]:
    gold_monthly = _monthly(case.gold_label)
    return {
        "case_id": case.case_id,
        "family": case.family,
        "control_type": case.control_type,
        "gold_label": case.gold_label,
        "gold_monthly_frequency": gold_monthly,
        "gold_band": boundary_band(gold_monthly),
        "deterministic_label": case.deterministic_label,
        "consensus_label": case.consensus_label,
        "fresh_label": case.fresh_label,
        "fresh_boundary_profile": list(case.fresh_boundary_profile),
        "desired_action": case.desired_action,
        "note_text": case.note_text,
        "rationale": case.rationale,
        "spelling_probe": case.spelling_probe,
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    purist = _transition_counts(rows, "purist")
    pragmatic = _transition_counts(rows, "pragmatic")
    changed_rows = [row for row in rows if row["transition_vs_deterministic"]["label_changed"]]
    by_family = {}
    for family in REQUIRED_FAMILIES:
        family_rows = [row for row in rows if row["gate2_case"]["family"] == family]
        by_family[family] = _family_summary(family_rows)

    false_positive_rows = [row for row in rows if row["false_positive_selector_action"]]
    spelling_probe_rows = [row for row in rows if row["gate2_case"]["spelling_probe"]]
    spelling_failures = [
        row["gate2_case"]["case_id"]
        for row in spelling_probe_rows
        if not row["desired_action_match"]
    ]
    gate_checks = {
        "desired_action_match_at_least_0_90": _rate(
            sum(row["desired_action_match"] for row in rows), len(rows)
        )
        >= 0.90,
        "no_family_below_0_80": all(
            summary["desired_action_match_rate"] >= 0.80
            for summary in by_family.values()
        ),
        "correct_to_wrong_zero": purist["correct_to_wrong"] == 0,
        "deterministic_correct_negative_false_positives_zero": len(false_positive_rows) == 0,
        "no_cluster_burden_demotion": not any(row["cluster_burden_demoted"] for row in rows),
        "no_forbidden_no_reference_to_unknown_churn": not any(
            row["no_reference_to_unknown_churn"] for row in rows
        ),
    }
    return {
        "rows": len(rows),
        "required_families": list(REQUIRED_FAMILIES),
        "desired_action_matches": sum(row["desired_action_match"] for row in rows),
        "desired_action_match_rate": _rate(
            sum(row["desired_action_match"] for row in rows), len(rows)
        ),
        "desired_action_miss_case_ids": [
            row["gate2_case"]["case_id"] for row in rows if not row["desired_action_match"]
        ],
        "selected_purist_correct": sum(_correct(row, "selected", "purist") for row in rows),
        "selected_pragmatic_correct": sum(
            _correct(row, "selected", "pragmatic") for row in rows
        ),
        "changed_labels": len(changed_rows),
        "changed_label_precision": _rate(purist["wrong_to_correct"], len(changed_rows)),
        "wrong_to_correct": purist["wrong_to_correct"],
        "correct_to_wrong": purist["correct_to_wrong"],
        "wrong_to_wrong": purist["wrong_to_wrong"],
        "correct_to_correct": purist["correct_to_correct"],
        "pragmatic_wrong_to_correct": pragmatic["wrong_to_correct"],
        "pragmatic_correct_to_wrong": pragmatic["correct_to_wrong"],
        "action_distribution": dict(Counter(row["selector_action"] for row in rows)),
        "gate_distribution": dict(Counter(row["selector_gate"] for row in rows)),
        "false_positive_selector_actions_on_deterministic_correct_controls": len(
            false_positive_rows
        ),
        "false_positive_case_ids": [row["gate2_case"]["case_id"] for row in false_positive_rows],
        "cluster_burden_demotion_case_ids": [
            row["gate2_case"]["case_id"] for row in rows if row["cluster_burden_demoted"]
        ],
        "no_reference_to_unknown_churn_case_ids": [
            row["gate2_case"]["case_id"] for row in rows if row["no_reference_to_unknown_churn"]
        ],
        "spelling_probe_rows": len(spelling_probe_rows),
        "spelling_dependency_failure_case_ids": spelling_failures,
        "by_family": by_family,
        "gate_checks": {**gate_checks, "gate_passed": all(gate_checks.values())},
    }


def _family_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    purist = _transition_counts(rows, "purist")
    matches = sum(row["desired_action_match"] for row in rows)
    return {
        "rows": len(rows),
        "desired_action_matches": matches,
        "desired_action_match_rate": _rate(matches, len(rows)),
        "selected_purist_correct": sum(_correct(row, "selected", "purist") for row in rows),
        "selected_pragmatic_correct": sum(_correct(row, "selected", "pragmatic") for row in rows),
        "wrong_to_correct": purist["wrong_to_correct"],
        "correct_to_wrong": purist["correct_to_wrong"],
        "action_distribution": dict(Counter(row["selector_action"] for row in rows)),
        "control_types": dict(Counter(row["gate2_case"]["control_type"] for row in rows)),
        "case_ids": [row["gate2_case"]["case_id"] for row in rows],
    }


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def _interpretation(summary: dict[str, Any]) -> str:
    if summary["gate_checks"]["gate_passed"]:
        return (
            "Gate 2 passes as a mechanism test: desired-action match is "
            f"{summary['desired_action_matches']}/{summary['rows']} "
            f"({summary['desired_action_match_rate']}), no family falls below 0.80, "
            "Purist correct-to-wrong is 0, deterministic-correct controls have 0 "
            "false-positive selector actions, cluster burden is not demoted, and "
            "no forbidden no-reference-to-unknown churn appears. This authorizes "
            "only Gate 3 source-symmetry preflight, not locked test."
        )
    return (
        "Gate 2 fails; keep v0.9 validation-only and return to selector/component "
        "design on validation surfaces."
    )


def _markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gan 2026 Consensus/Fresh v0.9 Frozen Gate 2 Robustness Stress",
        "",
        "Date: 2026-06-26",
        "",
        (
            "This is a synthetic/source-near validation-only mechanism panel over "
            "the frozen v0.9 selector. It makes no model calls and reads no locked "
            "test rows."
        ),
        "",
        "## Experiment Unit",
        "",
        "- Work class: hybrid selector robustness and component-state stress.",
        "- Surface: synthetic/source-near validation-only component states.",
        "- Selector: `gan2026_consensus_fresh_agreement_selector_v0_9`.",
        "- Scorer: Gan-compatible Purist first; Pragmatic sidecar.",
        "- Stop rule: pass authorizes Gate 3 source-symmetry preflight only.",
        "",
        "## Summary",
        "",
        f"- Rows: {summary['rows']}",
        (
            "- Desired-action match: "
            f"{summary['desired_action_matches']}/{summary['rows']} "
            f"({summary['desired_action_match_rate']})"
        ),
        f"- Selected Purist: {summary['selected_purist_correct']}/{summary['rows']}",
        f"- Selected Pragmatic: {summary['selected_pragmatic_correct']}/{summary['rows']}",
        f"- Changed labels: {summary['changed_labels']}",
        f"- Wrong->correct: {summary['wrong_to_correct']}",
        f"- Correct->wrong: {summary['correct_to_wrong']}",
        f"- Changed-label precision: {summary['changed_label_precision']}",
        (
            "- Deterministic-correct negative-control false positives: "
            f"{summary['false_positive_selector_actions_on_deterministic_correct_controls']}"
        ),
        f"- Cluster demotions: {len(summary['cluster_burden_demotion_case_ids'])}",
        (
            "- Forbidden no-reference-to-unknown churn: "
            f"{len(summary['no_reference_to_unknown_churn_case_ids'])}"
        ),
        f"- Actions: `{summary['action_distribution']}`",
        "",
        "## Family Readout",
        "",
        (
            "| Family | Rows | Match Rate | W->C | C->W | Selected Purist | "
            "Selected Pragmatic | Actions |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for family in REQUIRED_FAMILIES:
        item = summary["by_family"][family]
        lines.append(
            f"| `{family}` | {item['rows']} | {item['desired_action_match_rate']} | "
            f"{item['wrong_to_correct']} | {item['correct_to_wrong']} | "
            f"{item['selected_purist_correct']} | {item['selected_pragmatic_correct']} | "
            f"`{item['action_distribution']}` |"
        )
    lines.extend(
        [
            "",
            "## Case Readout",
            "",
            "| Case | Family | Type | Desired | Actual | Gate | Selected Correct | Match |",
            "| --- | --- | --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in payload["rows"]:
        case = row["gate2_case"]
        selected_correct = row["score_layers"]["selected"]["comparison"]["purist_correct"]
        lines.append(
            f"| `{case['case_id']}` | `{case['family']}` | `{case['control_type']}` | "
            f"`{case['desired_action']}` | `{row['selector_action']}` | "
            f"`{row['selector_gate']}` | {selected_correct} | "
            f"{row['desired_action_match']} |"
        )
    lines.extend(["", "## Gate Checks", ""])
    for check, passed in summary["gate_checks"].items():
        lines.append(f"- {check}: `{passed}`")
    lines.extend(
        [
            "",
            "## Spelling/Equivalence Diagnostics",
            "",
            (
                f"- Spelling/equivalence probe rows: {summary['spelling_probe_rows']}; "
                f"failures: `{summary['spelling_dependency_failure_case_ids']}`"
            ),
            (
                "The panel includes equivalent textual variants (`1 per 1 month` "
                "versus `1 per month`, `2 per 2 week` versus `1 per week`) "
                "and near numeric disagreements "
                "(`11 per 3 month` versus `10 per 3 month`)."
            ),
            "",
            "## Interpretation",
            "",
            payload["interpretation"],
            "",
            f"- JSON summary: `{JSON_OUT.relative_to(ROOT)}`.",
            f"- Markdown report: `{MD_OUT.relative_to(ROOT)}`.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
