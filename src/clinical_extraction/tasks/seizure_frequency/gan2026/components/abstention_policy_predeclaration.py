"""Predeclare abstention-pressure follow-up policies without changing behavior."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

POLICY_NAME = "gan2026_staged_hybrid_abstention_policy_predeclaration_v0"


def build_predeclaration(
    pressure_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a frozen contract for the next selective-action policy work."""

    lane_counts = Counter(str(row.get("review_lane")) for row in pressure_rows)
    reason_counts = Counter(str(row.get("decision_reason")) for row in pressure_rows)
    return {
        "artifact_kind": "gan2026_staged_hybrid_abstention_policy_predeclaration",
        "policy_name": POLICY_NAME,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "source_pressure_rows": len(pressure_rows),
        "lane_counts": dict(sorted(lane_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "candidate_behavior_change_counts": {
            "direct_trigger_release_candidates": lane_counts[
                "trigger_release_candidate"
            ],
            "last_event_automatic_release_candidates": 0,
        },
        "rules": [_trigger_context_release_rule(), _last_event_date_policy()],
        "non_release_lanes": [
            {
                "lane": "trigger_sentinel_boundary_review",
                "decision": (
                    "Do not release automatically. Review whether an explicit "
                    "unknown-boundary rule should predict unknown or keep abstain."
                ),
            },
            {
                "lane": "anchor_policy_needed",
                "decision": (
                    "Keep abstain until stable denominator and anchor extraction "
                    "are available before routing."
                ),
            },
            {
                "lane": "keep_nonprediction",
                "decision": "Keep non-prediction under the current boundary policy.",
            },
        ],
        "claim_language": (
            "Validation-development predeclaration only. This artifact freezes "
            "the next gold-blinded abstention-pressure policy work and does not "
            "change prediction-bearing behavior, prompts, scorer policy, gold "
            "labels, locked-test behavior, verifier use, or benchmark-comparable "
            "claims."
        ),
        "next_step": (
            "Implement and test the trigger-context release rule against the "
            "pressure lane, then add date instrumentation before any last-event "
            "automatic release."
        ),
    }


def write_summary_json(predeclaration: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(predeclaration, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def write_report(
    predeclaration: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Staged-Hybrid Abstention Policy Predeclaration",
        "",
        str(predeclaration["claim_language"]),
        "",
        "## Pressure Surface",
        "",
        f"Source pressure rows: {predeclaration['source_pressure_rows']}",
        "",
        "| Lane | Rows |",
        "| --- | ---: |",
    ]
    for lane, count in predeclaration["lane_counts"].items():
        lines.append(f"| `{lane}` | {count} |")

    lines.extend(
        [
            "",
            "## Gold-Blinded Release Criteria",
            "",
        ]
    )
    for rule in predeclaration["rules"]:
        lines.extend(
            [
                f"### {rule['name']}",
                "",
                f"Portability: `{rule['portability']}`",
                "",
                f"Decision: {rule['decision']}",
                "",
                "Criteria:",
                "",
            ]
        )
        for criterion in rule["criteria"]:
            lines.append(f"- {criterion}")
        lines.append("")

    lines.extend(
        [
            "## Non-Release Lanes",
            "",
            "| Lane | Decision |",
            "| --- | --- |",
        ]
    )
    for lane in predeclaration["non_release_lanes"]:
        lines.append(f"| `{lane['lane']}` | {lane['decision']} |")

    lines.extend(
        [
            "",
            "## Candidate Behavior Changes",
            "",
            "| Candidate type | Rows |",
            "| --- | ---: |",
        ]
    )
    for key, value in predeclaration["candidate_behavior_change_counts"].items():
        lines.append(f"| {key.replace('_', ' ')} | {value} |")

    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(predeclaration["next_step"]),
            "",
            "## Artifact",
            "",
            f"- Summary JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _trigger_context_release_rule() -> dict[str, Any]:
    return {
        "name": "trigger_context_release_rule_v0",
        "portability": "seizure_frequency",
        "decision": (
            "A trigger-context row may become prediction-bearing only when the "
            "candidate label is non-sentinel and the evidence supports a stable "
            "current seizure-frequency answer without relying on gold labels."
        ),
        "criteria": [
            "Input lane is trigger_release_candidate.",
            "Candidate label is not unknown or no seizure frequency reference.",
            (
                "Selected evidence contains a seizure/event target and an "
                "explicit rate, count, or window."
            ),
            "Trigger wording is contextual, not exclusive trigger-only wording.",
            "Selected evidence and source ids remain exact and auditable.",
            "Development correctness is reported after routing and is never an input.",
        ],
    }


def _last_event_date_policy() -> dict[str, Any]:
    return {
        "name": "last_event_date_policy_v0",
        "portability": "seizure_frequency",
        "decision": (
            "Last-event rows stay human_review until date instrumentation can "
            "derive a stable seizure-free interval from explicit dates and a "
            "known note date without contradictory current events."
        ),
        "criteria": [
            "Input lane is date_policy_needed.",
            "Automatic release requires explicit last-event date or duration.",
            "Automatic release requires a known note or reference date.",
            "The derived interval must be represented as an auditable intermediate field.",
            (
                "Rows with conflicting current events, settled recent events, "
                "or unclear event target stay human_review."
            ),
            "No last-event row becomes prediction-bearing in this predeclaration.",
        ],
    }
