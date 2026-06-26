"""Paired source-near contrast panel for ambiguity-class generation.

Instrumentation step 3.3 of the unknown-frequency agentic pathways doc. The
supervisor policy is not "demote to unknown"; it is a set of *distinctions*
between surface-similar evidence with opposite correct decisions. The live run
showed that feeding the class in masks the hard part (the static supervisor
panel passed 6/6 while live generation collapsed the explicit `2 per 5 month`
row): the model's weak point is choosing the class when the surface cues are
nearly identical.

This panel encodes those distinctions as *pairs* sharing surface cues but
requiring opposite calls:

1. last seizure date only -> unknown  vs  last seizure date + independently
   stated seizure-free duration -> seizure-free duration;
2. open-ended "since starting X" count -> unknown  vs  explicit count plus a
   defined follow-up period -> frequency;
3. cluster cadence without events-per-cluster -> unknown (incomplete)  vs
   cluster cadence with events-per-cluster -> cluster-burden frequency.

It is a validation-only parser/safety-gate contract: it feeds each intended
decision and verifies the gate preserves it, exactly like the supervisor panel.
Passing it statically is *necessary but not sufficient* — the live run must be
scored against the same pairs, because (per the 13267 lesson) the static contract
cannot exercise the model's generation-time class choice. Cluster burden is a
separate generation problem (Insight 3); the cluster pair is included here only
to predeclare the contrast, not to claim the renderer solves it.

No model calls, no locked test rows, no scorer change.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    fresh_evidence_reasoner,
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

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"
RUN_ID = "gan2026_source_near_contrast_panel_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"


@dataclass(frozen=True)
class ContrastCase:
    case_id: str
    pair_id: str
    direction: str  # "ambiguous" or "determinate"
    distinction: str
    expected_final_label: str
    expected_final_kind: str
    ambiguity_classification: str
    note_text: str
    evidence: tuple[str, ...]
    calculation_trace: str | None
    clinical_rationale: str


# Each pair shares surface cues (a last-event date, a since-treatment count, a
# cluster cadence) but the determinate member adds the one fact that licenses a
# concrete label. The ambiguous member must stay unknown.
PAIR_CASES: tuple[ContrastCase, ...] = (
    # Pair 1: last-event date.
    ContrastCase(
        case_id="last_event_only",
        pair_id="last_event",
        direction="ambiguous",
        distinction="last seizure date only",
        expected_final_label="unknown",
        expected_final_kind="unknown",
        ambiguity_classification="last_event_only_unknown",
        note_text=(
            "The patient's last seizure was on 14 March. There have been no "
            "seizures since then, but the notes do not state how long she has "
            "been followed."
        ),
        evidence=(
            "last seizure was on 14 March",
            "no seizures since then",
        ),
        calculation_trace=None,
        clinical_rationale=(
            "A most-recent seizure date with no stated observation period does "
            "not define a frequency or a seizure-free duration."
        ),
    ),
    ContrastCase(
        case_id="last_event_plus_duration",
        pair_id="last_event",
        direction="determinate",
        distinction="last seizure date plus independently stated duration",
        expected_final_label="seizure free for 6 month",
        expected_final_kind="seizure_free",
        ambiguity_classification="explicit_seizure_free_duration",
        note_text=(
            "The patient's last seizure was on 14 March. She has now been "
            "seizure free for 6 months on the current regimen, confirmed at "
            "today's review."
        ),
        evidence=(
            "last seizure was on 14 March",
            "seizure free for 6 months on the current regimen",
        ),
        calculation_trace="An explicit 6-month seizure-free duration is stated.",
        clinical_rationale=(
            "The note independently states a current seizure-free duration, not "
            "just a last-event date, so a seizure-free label is supported."
        ),
    ),
    # Pair 2: since-treatment count.
    ContrastCase(
        case_id="open_ended_since_treatment",
        pair_id="since_treatment_count",
        direction="ambiguous",
        distinction="open-ended since-medication count",
        expected_final_label="unknown",
        expected_final_kind="unknown",
        ambiguity_classification="unknown_count_or_window",
        note_text=(
            "She has had about four tonic-clonic seizures since starting "
            "Clobazam, but the start date is not recorded and no follow-up "
            "period is given."
        ),
        evidence=(
            "about four tonic-clonic seizures since starting Clobazam",
            "start date is not recorded",
        ),
        calculation_trace=None,
        clinical_rationale=(
            "An open-ended since-treatment count with no defined start date or "
            "follow-up period has no usable denominator."
        ),
    ),
    ContrastCase(
        case_id="explicit_count_plus_window",
        pair_id="since_treatment_count",
        direction="determinate",
        distinction="explicit count plus defined follow-up period",
        expected_final_label="3 per 6 month",
        expected_final_kind="frequency",
        ambiguity_classification="explicit_count_window",
        note_text=(
            "Over the documented 6 month follow-up period she had 3 seizures, "
            "with no further events recorded after the last of them."
        ),
        evidence=(
            "documented 6 month follow-up period she had 3 seizures",
            "no further events recorded",
        ),
        calculation_trace="3 seizures over a defined 6 month follow-up period.",
        clinical_rationale=(
            "The count is explicit and the follow-up period gives a usable "
            "denominator, so a frequency label is supported."
        ),
    ),
    # Pair 3: cluster cadence.
    ContrastCase(
        case_id="cluster_cadence_no_per_cluster",
        pair_id="cluster_cadence",
        direction="ambiguous",
        distinction="cluster cadence without events-per-cluster",
        expected_final_label="unknown",
        expected_final_kind="unknown",
        ambiguity_classification="cluster_axis_incomplete",
        note_text=(
            "He has clusters of seizures roughly once a month, but the notes do "
            "not record how many seizures occur within each cluster."
        ),
        evidence=(
            "clusters of seizures roughly once a month",
            "do not record how many seizures occur within each cluster",
        ),
        calculation_trace=None,
        clinical_rationale=(
            "A cluster cadence without an events-per-cluster count leaves the "
            "cluster burden axis incomplete."
        ),
    ),
    ContrastCase(
        case_id="cluster_cadence_with_per_cluster",
        pair_id="cluster_cadence",
        direction="determinate",
        distinction="cluster cadence plus events-per-cluster",
        expected_final_label="1 cluster per month, multiple per cluster",
        expected_final_kind="frequency",
        ambiguity_classification="cluster_axis_complete",
        note_text=(
            "He has 1 cluster of seizures per month, with multiple seizures "
            "within each cluster on every occasion."
        ),
        evidence=(
            "1 cluster of seizures per month",
            "multiple seizures within each cluster",
        ),
        calculation_trace="One cluster per month with multiple seizures per cluster.",
        clinical_rationale=(
            "Both the cluster cadence and the events-per-cluster are stated, so "
            "the cluster burden is complete."
        ),
    ),
)


def main() -> None:
    records = [_evaluate_case(case) for case in PAIR_CASES]
    summary = _summarize(records)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Validation-only paired source-near hard-negative contract for "
            "ambiguity-class generation. Each pair shares surface cues but "
            "requires opposite calls; the gate must preserve both directions."
        ),
        "prompt_version": fresh_evidence_reasoner.PROMPT_VERSION,
        "safety_gate_version": fresh_evidence_reasoner.SAFETY_GATE_VERSION,
        "summary": summary,
        "records": records,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)
    print(json.dumps(summary, indent=2, sort_keys=True))


def _evaluate_case(case: ContrastCase) -> dict[str, Any]:
    parsed = fresh_evidence_reasoner.parse_fresh_evidence_decision_json(
        json.dumps(
            {
                "action": "replace_with_fresh_evidence_final",
                "final_label": case.expected_final_label,
                "final_kind": case.expected_final_kind,
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": ["e1"],
                "evidence": list(case.evidence),
                "boundary_profile": [case.distinction],
                "ambiguity_classification": case.ambiguity_classification,
                "calculation_trace": case.calculation_trace,
                "clinical_rationale": case.clinical_rationale,
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        note_text=case.note_text,
        structured_event_row=_structured_event_row(case),
    )
    raw = parsed.raw_fresh_decision
    final = parsed.final_decision
    observed_label = final.final_label if final else None
    observed_kind = final.final_kind if final else None
    observed_classification = raw.ambiguity_classification if raw else None
    gate_fallback = any(
        str(error).startswith("fresh_evidence_gate_fallback:")
        for error in parsed.parse_errors
    )
    passed = (
        observed_label == case.expected_final_label
        and observed_kind == case.expected_final_kind
        and observed_classification == case.ambiguity_classification
        and not gate_fallback
    )
    return {
        "case_id": case.case_id,
        "pair_id": case.pair_id,
        "direction": case.direction,
        "distinction": case.distinction,
        "expected_final_label": case.expected_final_label,
        "observed_final_label": observed_label,
        "expected_final_kind": case.expected_final_kind,
        "observed_final_kind": observed_kind,
        "expected_ambiguity_classification": case.ambiguity_classification,
        "observed_ambiguity_classification": observed_classification,
        "gate_fallback": gate_fallback,
        "parse_errors": parsed.parse_errors,
        "action_render_events": parsed.action_render_events,
        "passed": passed,
    }


def _structured_event_row(case: ContrastCase) -> dict[str, Any]:
    return {
        "source_row_index": -1,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "no seizure frequency reference",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "no seizure frequency reference",
                    "time_window": "current",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "no_reference",
                "final_label": "no seizure frequency reference",
                "evidence": "no seizure frequency reference",
                "confidence": "medium",
                "rationale": "Contrast scaffold original.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": "no seizure frequency reference",
                "semantic_kind": "no_reference",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {"purist_correct": False, "pragmatic_correct": False},
        "evidence_valid": True,
    }


def _summarize(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    pairs: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        pairs.setdefault(record["pair_id"], []).append(record)
    pair_pass = {
        pair_id: all(member["passed"] for member in members)
        for pair_id, members in pairs.items()
    }
    return {
        "cases": len(records),
        "passed": sum(1 for record in records if record["passed"]),
        "failed": sum(1 for record in records if not record["passed"]),
        "pairs": len(pairs),
        "pairs_both_directions_pass": sum(1 for ok in pair_pass.values() if ok),
        "pair_pass": dict(sorted(pair_pass.items())),
        "class_distribution": dict(
            sorted(
                Counter(
                    str(record["observed_ambiguity_classification"])
                    for record in records
                ).items()
            )
        ),
        "panel_passed": all(record["passed"] for record in records),
        "failed_cases": sorted(
            record["case_id"] for record in records if not record["passed"]
        ),
    }


def _markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gan 2026 Source-Near Contrast Panel",
        "",
        "Date: 2026-06-15",
        "",
        "Validation-only paired hard-negative contract (step 3.3 of the "
        "unknown-frequency agentic pathways doc). Each pair shares surface cues "
        "but requires opposite calls, so generation is stressed on the "
        "*distinction*, not just the easy demote-to-unknown direction. It makes "
        "no model calls, reads no locked test rows, and does not change the "
        "scorer.",
        "",
        "## Necessary, not sufficient",
        "",
        "This is a parser/safety-gate contract: it feeds each intended decision "
        "and checks the gate preserves it. The live run showed that feeding the "
        "class in masks the hard part — the static supervisor panel passed "
        "`6/6` while live generation collapsed an explicit `2 per 5 month` "
        "(`13267`) to `unknown`. So passing this panel statically is required "
        "before, but does not substitute for, scoring live generation against "
        "the same pairs. Cluster burden is a separate generation problem "
        "(Insight 3); the cluster pair predeclares the contrast, it does not "
        "claim the renderer solves it.",
        "",
        "## Summary",
        "",
        f"- Prompt version under development: `{payload['prompt_version']}`",
        f"- Safety gate: `{payload['safety_gate_version']}`",
        f"- Cases passed: `{summary['passed']}/{summary['cases']}`",
        f"- Pairs passing both directions: "
        f"`{summary['pairs_both_directions_pass']}/{summary['pairs']}`",
        f"- Failed cases: `{summary['failed_cases'] or 'none'}`",
        f"- Observed ambiguity classes: `{summary['class_distribution']}`",
        "",
        "## Pairs",
        "",
        "| Pair | Direction | Distinction | Expected label | Observed label | Expected class | Observed class | Passed |",
        "| --- | --- | --- | --- | --- | --- | --- | :---: |",
    ]
    for record in payload["records"]:
        lines.append(
            f"| {record['pair_id']} "
            f"| {record['direction']} "
            f"| {record['distinction']} "
            f"| `{record['expected_final_label']}` "
            f"| `{record['observed_final_label']}` "
            f"| `{record['expected_ambiguity_classification']}` "
            f"| `{record['observed_ambiguity_classification']}` "
            f"| {'yes' if record['passed'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            _decision(summary),
            "",
        ]
    )
    return "\n".join(lines)


def _decision(summary: Mapping[str, Any]) -> str:
    if summary["panel_passed"]:
        return (
            "The gate preserves both directions of every contrast pair, so the "
            "panel is a clean predeclared hard-negative set for the next live "
            "run. The live run must reproduce these distinctions from raw "
            "evidence without the class fed in; only then is the "
            "ambiguity-class decision trustworthy enough to treat as a feature."
        )
    return (
        "The gate does not preserve every intended decision: failed cases "
        f"{summary['failed_cases']}. This is itself a finding — the safety gate "
        "is over- or under-applying on a source-near contrast — and must be "
        "resolved before the live run is scored against this panel."
    )


def _register(payload: Mapping[str, Any]) -> None:
    summary = payload["summary"]
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
            pipeline_family="fresh_evidence_reasoner_source_near_contrast_panel",
            split="validation",
            row_count=summary["cases"],
            model="none",
            model_role=(
                "Paired source-near hard-negative ambiguity contract; parser and "
                "safety-gate replay only, no model calls."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode=(
                "optional model-owned ambiguity_classification field before "
                "fresh-evidence final-label rendering"
            ),
            cache_reuse_source=None,
            primary_metrics={
                "cases": summary["cases"],
                "passed": summary["passed"],
                "failed": summary["failed"],
                "pairs_both_directions_pass": summary["pairs_both_directions_pass"],
                "prompt_version": payload["prompt_version"],
                "safety_gate_version": payload["safety_gate_version"],
            },
            evidence_validity=(
                "Synthetic validation-only contrast panel derived from the "
                "supervisor distinctions. No model calls, no scorer changes, no "
                "locked test row inspection. Static passing is necessary but not "
                "sufficient for the live run."
            ),
            decision="revise",
            supersedes=(),
            claim_language_notes=(
                "Adds paired source-near hard negatives stressing the "
                "ambiguous-vs-determinate distinction. Prerequisite validation "
                "infrastructure for the live ambiguity run, not a promoted "
                "test450 candidate."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
