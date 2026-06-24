"""Aggregate-only review-routing validation audit for ExECTv2.

The frozen reliability protocol permits full-200 validation only as aggregate
outputs. This module therefore records the validation preflight and stop-rule
outcome without emitting row identifiers, examples, evidence, rationales, or
selected failures from full-200 artifacts.
"""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path
from typing import Any

from . import cross_model_reliability_analysis as reliability

REPO_ROOT = reliability.REPO_ROOT
REPORT_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_review_routing_validation_audit_2026-06-24.md"
)

_FULL200_CANDIDATES: tuple[dict[str, str], ...] = (
    {
        "path": "experiments/exectv2_audit_hybrid_full200_gpt41mini_20260611.jsonl",
        "surface": "historical Phase 7 SF-only hybrid audit",
        "reason": (
            "SF-only audit artifact; not the rich-schema holistic assembly "
            "headline_target surface used by the reliability scorecard."
        ),
    },
    {
        "path": "experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl",
        "surface": "historical all-entity LLM-only audit",
        "reason": (
            "LLM-only all-entity surface; lacks the final-consolidation "
            "rich-schema assembly surface and provenance features that define "
            "the dev review-routing candidate."
        ),
    },
    {
        "path": "experiments/exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611.jsonl",
        "surface": "historical SF-only LLM-only per-entity audit",
        "reason": (
            "SF-only audit artifact; not the all-family rich-schema holistic "
            "assembly reliability surface."
        ),
    },
    {
        "path": "experiments/exectv2_audit_rules_full200_modelindependent_20260611.jsonl",
        "surface": "historical SF-only deterministic-rules audit",
        "reason": (
            "Rules-only SF audit artifact; not the rich-schema holistic "
            "assembly scorecard surface."
        ),
    },
)


def build_review_routing_validation_audit(
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Return the aggregate-only validation audit package.

    No full-200 row contents are surfaced. Full-200 JSONL files are read only to
    count rows and decide whether the artifact is eligible for the frozen
    same-surface validation run.
    """

    scorecard = reliability.build_cross_model_reliability_analysis(repo_root=repo_root)
    operating_points = {
        row["id"]: row for row in scorecard["review_routing"]["operating_points"]
    }
    high_recall = operating_points["high_recall_predeclared"]
    balanced = operating_points["balanced_dev_candidate"]
    inventory = _artifact_inventory(repo_root)
    eligible = [item for item in inventory if item["eligible"]]
    stop_status = (
        "ready_for_aggregate_validation"
        if eligible
        else "blocked_no_same_surface_full200_artifact"
    )
    return {
        "audit_kind": "exectv2_review_routing_aggregate_validation",
        "generated_on": date.today().isoformat(),
        "surface": "rich-schema holistic assembly reliability scorecard",
        "scorer": "headline_target family-cell correctness",
        "split": "full-200 aggregate-only validation requested",
        "code_hash": _git_head(repo_root),
        "row_inspection_boundary": (
            "Aggregate metrics and artifact inventory only; no row identifiers, "
            "note text, gold labels, predictions, evidence spans, rationales, "
            "or selected failure examples are emitted."
        ),
        "candidate_operating_points": [
            _candidate_summary(high_recall),
            _candidate_summary(balanced),
        ],
        "artifact_inventory": inventory,
        "eligible_validation_artifacts": len(eligible),
        "stop_rule_outcome": {
            "status": stop_status,
            "validation_run_executed": bool(eligible),
            "promotion_decision": "not_promoted",
            "reason": (
                "No full-200 artifact matches the frozen rich-schema holistic "
                "assembly reliability surface, so applying the dev routing "
                "candidate would blend surfaces."
            )
            if not eligible
            else "Eligible aggregate validation artifact is available.",
        },
        "promotion_gates": _promotion_gates(high_recall, balanced, bool(eligible)),
        "next_action": (
            "Freeze and generate a same-surface full-200 rich-schema holistic "
            "assembly artifact, then run the validation once with this report "
            "template before reading metrics."
        ),
    }


def render_markdown(audit: dict[str, Any]) -> str:
    """Render a paper-facing Markdown audit without row-level details."""

    lines = [
        "# ExECTv2 Review-Routing Validation Audit",
        "",
        f"Date: {audit['generated_on']}",
        "",
        "Status: aggregate-only validation preflight and stop-rule readout. "
        "No promotion claim is made.",
        "",
        "## Preflight",
        "",
        f"- Surface: {audit['surface']}",
        f"- Scorer: `{audit['scorer']}`",
        f"- Split: `{audit['split']}`",
        f"- Code hash: `{audit['code_hash']}`",
        f"- Row-inspection boundary: {audit['row_inspection_boundary']}",
        "",
        "## Frozen Candidate Operating Points",
        "",
        (
            "| Candidate | Dev status | Eligible cells | Reviewed | Burden | "
            "Error cells | Caught | Catch | False alarms | False alarms / caught error |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in audit["candidate_operating_points"]:
        lines.append(
            f"| {row['label']} | {row['validation_status']} | "
            f"{row['eligible_cells']} | {row['reviewed_cells']} | "
            f"{row['review_burden']:.4f} | {row['total_error_cells']} | "
            f"{row['caught_error_cells']} | {row['catch_rate']:.4f} | "
            f"{row['false_alarm_cells']} | {row['false_alarms_per_caught_error']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Validation Artifact Inventory",
            "",
            "| Artifact | Rows | Surface | Eligibility | Reason |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for item in audit["artifact_inventory"]:
        eligibility = "eligible" if item["eligible"] else "ineligible"
        lines.append(
            f"| `{item['path']}` | {item['rows']} | {item['surface']} | "
            f"{eligibility} | {item['reason']} |"
        )

    stop = audit["stop_rule_outcome"]
    lines.extend(
        [
            "",
            "## Stop-Rule Outcome",
            "",
            f"- Status: `{stop['status']}`",
            f"- Validation run executed: `{stop['validation_run_executed']}`",
            f"- Promotion decision: `{stop['promotion_decision']}`",
            f"- Reason: {stop['reason']}",
            "",
            "## Promotion Gates",
            "",
            "| Gate | Outcome | Note |",
            "| --- | --- | --- |",
        ]
    )
    for gate in audit["promotion_gates"]:
        lines.append(f"| {gate['gate']} | {gate['outcome']} | {gate['note']} |")

    lines.extend(
        [
            "",
            "## Result",
            "",
            "The lower-burden review-routing candidate is not promoted. The dev140 "
            "candidate remains useful but unvalidated because the available full-200 "
            "artifacts do not match the frozen rich-schema holistic assembly surface.",
            "",
            f"Next action: {audit['next_action']}",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(
    *,
    repo_root: Path = REPO_ROOT,
    report_path: Path = REPORT_PATH,
) -> Path:
    audit = build_review_routing_validation_audit(repo_root=repo_root)
    out_path = repo_root / report_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_markdown(audit), encoding="utf-8")
    return out_path


def _artifact_inventory(repo_root: Path) -> list[dict[str, Any]]:
    rows = []
    for item in _FULL200_CANDIDATES:
        path = repo_root / item["path"]
        rows.append(
            {
                "path": item["path"],
                "exists": path.exists(),
                "rows": _count_jsonl_rows(path) if path.exists() else 0,
                "surface": item["surface"],
                "eligible": False,
                "reason": item["reason"],
            }
        )
    return rows


def _candidate_summary(point: dict[str, Any]) -> dict[str, Any]:
    caught = int(point["caught_error_cells"])
    false_alarm = int(point["false_alarm_cells"])
    return {
        "id": point["id"],
        "label": point["label"],
        "rules": point["rules"],
        "validation_status": point["validation_status"],
        "eligible_cells": int(point["eligible_cells"]),
        "reviewed_cells": int(point["reviewed_cells"]),
        "review_burden": float(point["review_burden"]),
        "total_error_cells": int(point["total_error_cells"]),
        "caught_error_cells": caught,
        "catch_rate": float(point["catch_rate"]),
        "false_alarm_cells": false_alarm,
        "false_alarms_per_caught_error": round(false_alarm / caught, 4) if caught else 0.0,
        "missed_error_cells": int(point["missed_error_cells"]),
    }


def _promotion_gates(
    high_recall: dict[str, Any],
    balanced: dict[str, Any],
    validation_available: bool,
) -> list[dict[str, str]]:
    if not validation_available:
        blocked = "not_evaluable"
        reason = "No same-surface full-200 aggregate artifact is available."
        return [
            {
                "gate": "Review burden at least 0.15 absolute below high-recall burden",
                "outcome": blocked,
                "note": reason,
            },
            {
                "gate": "Overall error catch at least 0.80",
                "outcome": blocked,
                "note": reason,
            },
            {
                "gate": "Per-family eligible/error/caught/missed/false-alarm metrics",
                "outcome": blocked,
                "note": reason,
            },
            {
                "gate": "No family with at least ten error cells below 0.70 catch",
                "outcome": blocked,
                "note": reason,
            },
            {
                "gate": "False alarms per caught error lower than high-recall policy",
                "outcome": blocked,
                "note": reason,
            },
        ]

    burden_delta = float(high_recall["review_burden"]) - float(balanced["review_burden"])
    high_cost = int(high_recall["false_alarm_cells"]) / int(high_recall["caught_error_cells"])
    balanced_cost = int(balanced["false_alarm_cells"]) / int(balanced["caught_error_cells"])
    return [
        {
            "gate": "Review burden at least 0.15 absolute below high-recall burden",
            "outcome": "pass" if burden_delta >= 0.15 else "fail",
            "note": f"Dev-frozen delta is {burden_delta:.4f}; validation metrics still required.",
        },
        {
            "gate": "Overall error catch at least 0.80",
            "outcome": "pass" if float(balanced["catch_rate"]) >= 0.80 else "fail",
            "note": "Validation aggregate required before promotion.",
        },
        {
            "gate": "False alarms per caught error lower than high-recall policy",
            "outcome": "pass" if balanced_cost < high_cost else "fail",
            "note": (
                f"Dev-frozen high-recall cost {high_cost:.4f}; "
                f"balanced cost {balanced_cost:.4f}."
            ),
        },
    ]


def _count_jsonl_rows(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _git_head(repo_root: Path) -> str:
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = subprocess.run(
            ["git", "diff", "--quiet"],
            cwd=repo_root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode != 0
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    return f"{head}+dirty" if dirty else head


def main() -> None:
    path = write_report()
    print(path.relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
