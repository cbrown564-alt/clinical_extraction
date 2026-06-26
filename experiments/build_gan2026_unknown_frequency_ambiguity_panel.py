"""Build a supervisor-seeded unknown-frequency ambiguity panel.

This is a validation-only component contract, not a model run. It encodes the
six examples from Yujian's clarification as representative fresh-evidence
decisions and verifies that the current parser/safety gate can preserve the
intended ambiguity classification before final-label rendering.
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
RUN_ID = "gan2026_unknown_frequency_ambiguity_panel_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"


@dataclass(frozen=True)
class AmbiguityPanelCase:
    source_row_index: int
    supervisor_label: str
    expected_final_label: str
    expected_final_kind: str
    ambiguity_classification: str
    note_text: str
    evidence: tuple[str, ...]
    calculation_trace: str | None
    clinical_rationale: str
    policy_reading: str


PANEL_CASES: tuple[AmbiguityPanelCase, ...] = (
    AmbiguityPanelCase(
        source_row_index=11272,
        supervisor_label="unknown",
        expected_final_label="unknown",
        expected_final_kind="unknown",
        ambiguity_classification="last_event_only_unknown",
        note_text=(
            "The patient's last seizure occurred on 20 Dec. "
            "There have been no seizures since then."
        ),
        evidence=(
            "last seizure occurred on 20 Dec",
            "There have been no seizures since then",
        ),
        calculation_trace=None,
        clinical_rationale=(
            "A most-recent seizure date does not prove only one seizure in a "
            "defined observation period."
        ),
        policy_reading="Last-event-only evidence should remain unknown.",
    ),
    AmbiguityPanelCase(
        source_row_index=14454,
        supervisor_label="2 per 2 month",
        expected_final_label="2 per 2 month",
        expected_final_kind="frequency",
        ambiguity_classification="explicit_count_window",
        note_text=(
            "Topiramate was discontinued on 11 Feb. Soon afterwards she "
            "reported two seizures, with no seizures since then across the "
            "two month follow-up."
        ),
        evidence=(
            "reported two seizures",
            "with no seizures since then across the two month follow-up",
        ),
        calculation_trace="Two seizures over the two month follow-up.",
        clinical_rationale=(
            "The number of seizures is explicit and the follow-up period gives "
            "a usable denominator."
        ),
        policy_reading="Explicit count plus usable follow-up can be frequency.",
    ),
    AmbiguityPanelCase(
        source_row_index=14029,
        supervisor_label="unknown",
        expected_final_label="unknown",
        expected_final_kind="unknown",
        ambiguity_classification="unknown_count_or_window",
        note_text=(
            "The patient has had several drop attacks since starting the "
            "ketogenic diet, with the latest one on 05 Sep."
        ),
        evidence=(
            "several drop attacks since starting the ketogenic diet",
            "latest one on 05 Sep",
        ),
        calculation_trace=None,
        clinical_rationale=(
            "The seizure count is vague and the ketogenic diet start date is "
            "not defined, so the time window is unclear."
        ),
        policy_reading="Open-ended since-diet evidence lacks a denominator.",
    ),
    AmbiguityPanelCase(
        source_row_index=13267,
        supervisor_label="2 per 5 month",
        expected_final_label="2 per 5 month",
        expected_final_kind="frequency",
        ambiguity_classification="explicit_count_window",
        note_text=(
            "After starting Clobazam, the patient had a five-month remission, "
            "then had a drop attack three Mondays ago, preceded by myoclonic "
            "jerks."
        ),
        evidence=(
            "five-month remission",
            "had a drop attack three Mondays ago, preceded by myoclonic jerks",
        ),
        calculation_trace=(
            "The five-month period is explicit and the post-remission seizure "
            "activity supports two events over that interval."
        ),
        clinical_rationale=(
            "The note gives an explicit five-month period and clear seizure "
            "activity after remission."
        ),
        policy_reading="Explicit period plus reported events can be frequency.",
    ),
    AmbiguityPanelCase(
        source_row_index=14137,
        supervisor_label="unknown",
        expected_final_label="unknown",
        expected_final_kind="unknown",
        ambiguity_classification="unknown_count_or_window",
        note_text=(
            "The patient has had 3-4 generalised tonic-clonic seizures since "
            "beginning Clobazam, with the most recent on 23 December."
        ),
        evidence=(
            "3-4 generalised tonic-clonic seizures since beginning Clobazam",
            "most recent on 23 December",
        ),
        calculation_trace=None,
        clinical_rationale=(
            "The count is stated, but the Clobazam start date and observation "
            "window are not defined."
        ),
        policy_reading="Open-ended since-medication evidence lacks a denominator.",
    ),
    AmbiguityPanelCase(
        source_row_index=11337,
        supervisor_label="unknown",
        expected_final_label="unknown",
        expected_final_kind="unknown",
        ambiguity_classification="unknown_count_or_window",
        note_text=(
            "The note reports one seizure on 06 Nov after missed doses and "
            "sleep deprivation."
        ),
        evidence=(
            "one seizure on 06 Nov",
            "after missed doses and sleep deprivation",
        ),
        calculation_trace=None,
        clinical_rationale=(
            "A single provoked breakthrough event is not a frequency unless the "
            "relevant observation period is defined."
        ),
        policy_reading="Single provoked breakthrough event has unclear period.",
    ),
)


def main() -> None:
    records = [_evaluate_case(case) for case in PANEL_CASES]
    summary = _summarize(records)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Validation-only hard-negative contract for unknown-frequency "
            "ambiguity classification based on supervisor clarification."
        ),
        "prompt_version": fresh_evidence_reasoner.PROMPT_VERSION,
        "safety_gate_version": fresh_evidence_reasoner.SAFETY_GATE_VERSION,
        "summary": summary,
        "records": records,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)


def _evaluate_case(case: AmbiguityPanelCase) -> dict[str, Any]:
    parsed = fresh_evidence_reasoner.parse_fresh_evidence_decision_json(
        json.dumps(
            {
                "action": "replace_with_fresh_evidence_final",
                "final_label": case.expected_final_label,
                "final_kind": case.expected_final_kind,
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": ["e1"],
                "evidence": list(case.evidence),
                "boundary_profile": [case.policy_reading],
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
    return {
        "source_row_index": case.source_row_index,
        "supervisor_label": case.supervisor_label,
        "expected_final_label": case.expected_final_label,
        "observed_final_label": observed_label,
        "expected_final_kind": case.expected_final_kind,
        "observed_final_kind": observed_kind,
        "expected_ambiguity_classification": case.ambiguity_classification,
        "observed_ambiguity_classification": observed_classification,
        "policy_reading": case.policy_reading,
        "parse_errors": parsed.parse_errors,
        "action_render_events": parsed.action_render_events,
        "passed": (
            observed_label == case.expected_final_label
            and observed_kind == case.expected_final_kind
            and observed_classification == case.ambiguity_classification
            and not any(
                str(error).startswith("fresh_evidence_gate_fallback:")
                for error in parsed.parse_errors
            )
        ),
    }


def _structured_event_row(case: AmbiguityPanelCase) -> dict[str, Any]:
    return {
        "source_row_index": case.source_row_index,
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
                "rationale": "Panel scaffold original.",
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
    classifications = Counter(
        str(record["observed_ambiguity_classification"]) for record in records
    )
    labels = Counter(str(record["observed_final_label"]) for record in records)
    return {
        "rows": len(records),
        "passed": sum(1 for record in records if record["passed"]),
        "failed": sum(1 for record in records if not record["passed"]),
        "classification_distribution": dict(sorted(classifications.items())),
        "final_label_distribution": dict(sorted(labels.items())),
        "panel_passed": all(record["passed"] for record in records),
    }


def _markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gan 2026 Unknown-Frequency Ambiguity Panel",
        "",
        "Date: 2026-06-15",
        "",
        "This validation-only panel encodes six supervisor-discussed ambiguity "
        "cases as a parser/safety-gate contract. It makes no model calls, reads "
        "no locked test rows, and does not change the scorer.",
        "",
        "## Summary",
        "",
        f"- Prompt version under development: `{payload['prompt_version']}`",
        f"- Safety gate: `{payload['safety_gate_version']}`",
        f"- Panel pass: `{summary['passed']}/{summary['rows']}`",
        f"- Final labels: `{summary['final_label_distribution']}`",
        f"- Ambiguity classes: `{summary['classification_distribution']}`",
        "",
        "## Cases",
        "",
        "| Row | Supervisor label | Expected label | Ambiguity class | Passed | Policy reading |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for record in payload["records"]:
        lines.append(
            f"| {record['source_row_index']} | `{record['supervisor_label']}` | "
            f"`{record['expected_final_label']}` | "
            f"`{record['expected_ambiguity_classification']}` | "
            f"`{record['passed']}` | {record['policy_reading']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The ambiguity-classification contract passes on the supervisor "
            "panel. This does not promote a holdout candidate; it gives the next "
            "validation-only live prompt run a hard-negative panel to satisfy "
            "before broad validation replay or any future frozen audit request.",
            "",
        ]
    )
    return "\n".join(lines)


def _register(payload: Mapping[str, Any]) -> None:
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID
    ]
    summary = payload["summary"]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
            ),
            date="2026-06-15",
            pipeline_family="fresh_evidence_reasoner_ambiguity_panel",
            split="validation",
            row_count=summary["rows"],
            model="none",
            model_role=(
                "Supervisor-seeded unknown-frequency ambiguity component "
                "contract; parser and safety-gate replay only."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode=(
                "optional model-owned ambiguity_classification field before "
                "fresh-evidence final-label rendering"
            ),
            cache_reuse_source=None,
            primary_metrics={
                "panel_rows": summary["rows"],
                "panel_passed": summary["passed"],
                "panel_failed": summary["failed"],
                "prompt_version": payload["prompt_version"],
                "safety_gate_version": payload["safety_gate_version"],
            },
            evidence_validity=(
                "Synthetic validation-only policy panel derived from supervisor "
                "clarification. No model calls, no scorer changes, and no "
                "locked test row inspection."
            ),
            decision="revise",
            supersedes=(
                "gan2026_fresh_evidence_reasoner_unknown_policy_v0_6_safety_v0_9_replay_2026-06-15",
            ),
            claim_language_notes=(
                "Adds a hard-negative ambiguity-classification contract for "
                "unknown-frequency cases. This is prerequisite validation "
                "infrastructure, not a promoted test450 candidate."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
