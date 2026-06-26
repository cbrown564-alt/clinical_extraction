"""Aggregate-only review-routing validation audit for ExECTv2.

The frozen reliability protocol permits full-200 validation only as aggregate
outputs. This module therefore records the validation preflight and stop-rule
outcome without emitting row identifiers, examples, evidence, rationales, or
selected failures from full-200 artifacts.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from . import cross_model_reliability_analysis as reliability
from . import validation_audit_scaffold as scaffold

REPO_ROOT = scaffold.REPO_ROOT
REPORT_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_review_routing_validation_audit_2026-06-24.md"
)

_FULL200_CANDIDATES: tuple[dict[str, str], ...] = (
    {
        **scaffold.FULL200_ARTIFACT,
        "reason": (
            "Accepted for a one-shot aggregate validation of the current-code "
            "v08-shaped rich-schema holistic assembly surface. This is not "
            "byte-identical archived dev140 prompt/module replay, so promotion "
            "claims remain limited to the current-code validation surface."
        ),
    },
    {
        "path": "experiments/exectv2_audit_hybrid_full200_gpt41mini_20260611.jsonl",
        "surface": "historical Phase 7 SF-only hybrid audit",
        "eligibility": "ineligible",
        "reason": (
            "SF-only audit artifact; not the rich-schema holistic assembly "
            "headline_target surface used by the reliability scorecard."
        ),
    },
    {
        "path": "experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl",
        "surface": "historical all-entity LLM-only audit",
        "eligibility": "ineligible",
        "reason": (
            "LLM-only all-entity surface; lacks the final-consolidation "
            "rich-schema assembly surface and provenance features that define "
            "the dev review-routing candidate."
        ),
    },
    {
        "path": "experiments/exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611.jsonl",
        "surface": "historical SF-only LLM-only per-entity audit",
        "eligibility": "ineligible",
        "reason": (
            "SF-only audit artifact; not the all-family rich-schema holistic "
            "assembly reliability surface."
        ),
    },
    {
        "path": "experiments/exectv2_audit_rules_full200_modelindependent_20260611.jsonl",
        "surface": "historical SF-only deterministic-rules audit",
        "eligibility": "ineligible",
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
    inventory = scaffold.artifact_inventory_multi(repo_root, _FULL200_CANDIDATES)
    eligible = [item for item in inventory if item["eligible"]]
    validation = _validation_readout(repo_root, eligible[0]) if eligible else None
    promotion_gates = _promotion_gates(high_recall, balanced, validation)
    promotion_decision = scaffold.promotion_decision_from_gates(promotion_gates)
    blocked_reason = (
        "No full-200 artifact matches the frozen rich-schema holistic "
        "assembly reliability surface, so applying the dev routing "
        "candidate would blend surfaces."
        if validation is None
        else (
            "The current-code v08-shaped full-200 artifact was accepted as "
            "an aggregate-only validation surface, but the lower-burden dev "
            "candidate did not preserve a lower review burden on validation."
        )
    )
    return {
        **scaffold.audit_envelope(
            audit_kind="exectv2_review_routing_aggregate_validation",
            repo_root=repo_root,
            scorer="headline_target family-cell correctness",
            row_inspection_boundary=(
                "Aggregate metrics and artifact inventory only; no row identifiers, "
                "note text, gold labels, predictions, evidence spans, rationales, "
                "or selected failure examples are emitted."
            ),
        ),
        "candidate_operating_points": [
            _candidate_summary(high_recall),
            _candidate_summary(balanced),
        ],
        "artifact_inventory": inventory,
        "eligible_validation_artifacts": len(eligible),
        "validation_readout": validation,
        "stop_rule_outcome": scaffold.stop_rule_outcome(
            validation=validation,
            promotion_decision=promotion_decision,
            promoted_reason=(
                "The lower-burden review-routing candidate passes all predeclared "
                "aggregate validation gates on the accepted current-code surface."
            ),
            blocked_reason=blocked_reason,
        ),
        "promotion_gates": promotion_gates,
        "next_action": (
            "Freeze and generate a same-surface full-200 rich-schema holistic "
            "assembly artifact, then run the validation once with this report "
            "template before reading metrics."
        )
        if validation is None
        else (
            "Do not promote the lower-burden review-routing candidate. Move "
            "review-routing work back to dev140 risk-feature redesign or a "
            "fresh predeclared calibration/routing model before another "
            "validation attempt."
        ),
    }


def render_markdown(audit: Mapping[str, Any]) -> str:
    """Render a paper-facing Markdown audit without row-level details."""

    lines = scaffold.render_preflight_section(
        audit,
        title="# ExECTv2 Review-Routing Validation Audit",
        status_line=(
            "Status: aggregate-only validation preflight and stop-rule readout. "
            "No promotion claim is made."
        ),
    )
    lines.extend(
        [
            "",
            "## Frozen Candidate Operating Points",
            "",
            (
                "| Candidate | Dev status | Eligible cells | Reviewed | Burden | "
                "Error cells | Caught | Catch | False alarms | False alarms / caught error |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in audit["candidate_operating_points"]:
        lines.append(
            f"| {row['label']} | {row['validation_status']} | "
            f"{row['eligible_cells']} | {row['reviewed_cells']} | "
            f"{row['review_burden']:.4f} | {row['total_error_cells']} | "
            f"{row['caught_error_cells']} | {row['catch_rate']:.4f} | "
            f"{row['false_alarm_cells']} | {row['false_alarms_per_caught_error']:.4f} |"
        )

    lines.extend(scaffold.render_artifact_inventory_section(audit["artifact_inventory"]))

    validation = audit.get("validation_readout")
    if validation:
        lines.extend(
            [
                "",
                "## Aggregate Validation Readout",
                "",
                f"- Artifact: `{validation['artifact_path']}`",
                f"- Rows: {validation['rows']}",
                f"- Eligible family cells: {validation['eligible_cells']}",
                "",
                (
                    "| Operating point | Reviewed | Burden | Error cells | Caught | "
                    "Catch | False alarms | False alarms / caught error |"
                ),
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in validation["operating_points"]:
            lines.append(
                f"| {row['label']} | {row['reviewed_cells']} | "
                f"{row['review_burden']:.4f} | {row['total_error_cells']} | "
                f"{row['caught_error_cells']} | {row['catch_rate']:.4f} | "
                f"{row['false_alarm_cells']} | "
                f"{row['false_alarms_per_caught_error']:.4f} |"
            )
        lines.extend(
            [
                "",
                "### Per-Family Validation Metrics",
                "",
                (
                    "| Operating point | Family | Eligible | Errors | Reviewed | "
                    "Caught | Missed | False alarms | Burden | Catch |"
                ),
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in validation["by_family"]:
            lines.append(
                f"| {row['operating_point']} | {row['family']} | "
                f"{row['eligible_cells']} | {row['total_error_cells']} | "
                f"{row['reviewed_cells']} | {row['caught_error_cells']} | "
                f"{row['missed_error_cells']} | {row['false_alarm_cells']} | "
                f"{row['review_burden']:.4f} | {row['catch_rate']:.4f} |"
            )

    lines.extend(scaffold.render_stop_rule_outcome_section(audit))
    lines.extend(scaffold.render_promotion_gates_section(audit))
    lines.extend(scaffold.render_report_footer(audit, _result_paragraph(audit)))
    return "\n".join(lines)


def write_report(
    *,
    repo_root: Path = REPO_ROOT,
    report_path: Path = REPORT_PATH,
) -> Path:
    return scaffold.write_validation_report(
        build_audit=build_review_routing_validation_audit,
        render_markdown=render_markdown,
        repo_root=repo_root,
        report_path=report_path,
    )


def _validation_readout(
    repo_root: Path,
    artifact: Mapping[str, Any],
) -> dict[str, Any]:
    rows = reliability._load_jsonl(repo_root / artifact["path"])
    cells = _validation_cells(rows)
    high_recall = _aggregate_operating_point(
        cells,
        point_id="high_recall_predeclared",
        label="High-recall predeclared trigger net",
        review_fn=lambda cell: bool(reliability._review_triggers(cell)),
    )
    balanced = _aggregate_operating_point(
        cells,
        point_id="balanced_dev_candidate",
        label="Balanced dev candidate",
        review_fn=_balanced_review_decision,
    )
    return {
        "artifact_path": artifact["path"],
        "rows": len(rows),
        "eligible_cells": len(cells),
        "operating_points": [high_recall, balanced],
        "by_family": [
            *high_recall.pop("by_family"),
            *balanced.pop("by_family"),
        ],
    }


def _validation_cells(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for row in rows:
        for family in reliability.FAMILIES:
            score = reliability._row_family_score(row, family)
            if score.pred_count == 0 and score.gold_count == 0:
                continue
            features = reliability._risk_features(row, family)
            cells.append(
                {
                    "family": family,
                    "correct": score.fp == 0 and score.fn == 0,
                    "risk_score": reliability._risk_score(family, features),
                    "features": features,
                }
            )
    return cells


def _balanced_review_decision(cell: dict[str, Any]) -> bool:
    features = cell["features"]
    return (
        float(cell["risk_score"]) >= 0.35
        or bool(features["source_final_delta"])
        or bool(features["low_confidence"])
        or bool(features["result_state"])
    )


def _aggregate_operating_point(
    cells: list[dict[str, Any]],
    *,
    point_id: str,
    label: str,
    review_fn: Any,
) -> dict[str, Any]:
    by_family: dict[str, dict[str, int]] = {}
    reviewed = caught = false_alarm = total_errors = 0
    for cell in cells:
        family = str(cell["family"])
        counts = by_family.setdefault(
            family,
            {
                "eligible_cells": 0,
                "total_error_cells": 0,
                "reviewed_cells": 0,
                "caught_error_cells": 0,
                "missed_error_cells": 0,
                "false_alarm_cells": 0,
            },
        )
        is_error = not bool(cell["correct"])
        is_reviewed = bool(review_fn(cell))
        counts["eligible_cells"] += 1
        if is_error:
            total_errors += 1
            counts["total_error_cells"] += 1
        if is_reviewed:
            reviewed += 1
            counts["reviewed_cells"] += 1
            if is_error:
                caught += 1
                counts["caught_error_cells"] += 1
            else:
                false_alarm += 1
                counts["false_alarm_cells"] += 1
        elif is_error:
            counts["missed_error_cells"] += 1

    by_family_rows = []
    for family, counts in sorted(by_family.items()):
        by_family_rows.append(
            {
                "operating_point": label,
                "family": family,
                **counts,
                "review_burden": scaffold.round_rate(
                    counts["reviewed_cells"], counts["eligible_cells"]
                ),
                "catch_rate": scaffold.round_rate(
                    counts["caught_error_cells"], counts["total_error_cells"]
                ),
            }
        )

    return {
        "id": point_id,
        "label": label,
        "eligible_cells": len(cells),
        "reviewed_cells": reviewed,
        "review_burden": scaffold.round_rate(reviewed, len(cells)),
        "total_error_cells": total_errors,
        "caught_error_cells": caught,
        "catch_rate": scaffold.round_rate(caught, total_errors),
        "false_alarm_cells": false_alarm,
        "missed_error_cells": total_errors - caught,
        "false_alarms_per_caught_error": round(false_alarm / caught, 4)
        if caught
        else 0.0,
        "by_family": by_family_rows,
    }


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
    validation: dict[str, Any] | None,
) -> list[dict[str, str]]:
    blocked_note = "No same-surface full-200 aggregate artifact is available."
    if validation is None:
        return [
            scaffold.gate(
                "Review burden at least 0.15 absolute below high-recall burden",
                "not_evaluable",
                blocked_note,
            ),
            scaffold.gate(
                "Overall error catch at least 0.80",
                "not_evaluable",
                blocked_note,
            ),
            scaffold.gate(
                "Per-family eligible/error/caught/missed/false-alarm metrics",
                "not_evaluable",
                blocked_note,
            ),
            scaffold.gate(
                "No family with at least ten error cells below 0.70 catch",
                "not_evaluable",
                blocked_note,
            ),
            scaffold.gate(
                "False alarms per caught error lower than high-recall policy",
                "not_evaluable",
                blocked_note,
            ),
        ]

    validation_points = {row["id"]: row for row in validation["operating_points"]}
    validation_high = validation_points["high_recall_predeclared"]
    validation_balanced = validation_points["balanced_dev_candidate"]
    burden_delta = float(validation_high["review_burden"]) - float(
        validation_balanced["review_burden"]
    )
    high_cost = int(validation_high["false_alarm_cells"]) / int(
        validation_high["caught_error_cells"]
    )
    balanced_cost = int(validation_balanced["false_alarm_cells"]) / int(
        validation_balanced["caught_error_cells"]
    )
    family_floor_pass = _family_catch_floor_pass(validation, "Balanced dev candidate")
    return [
        scaffold.gate(
            "Review burden at least 0.15 absolute below high-recall burden",
            "pass" if burden_delta >= 0.15 else "fail",
            f"Validation burden delta is {burden_delta:.4f}.",
        ),
        scaffold.gate(
            "Overall error catch at least 0.80",
            "pass"
            if float(validation_balanced["catch_rate"]) >= 0.80
            else "fail",
            f"Validation catch is {validation_balanced['catch_rate']:.4f}.",
        ),
        scaffold.gate(
            "Per-family eligible/error/caught/missed/false-alarm metrics",
            "pass",
            "Per-family aggregate metrics are reported without row-level details.",
        ),
        scaffold.gate(
            "No family with at least ten error cells below 0.70 catch",
            "pass" if family_floor_pass else "fail",
            "Balanced candidate family catch floor evaluated on aggregate counts.",
        ),
        scaffold.gate(
            "False alarms per caught error lower than high-recall policy",
            "pass" if balanced_cost < high_cost else "fail",
            (
                f"Validation high-recall cost {high_cost:.4f}; "
                f"balanced cost {balanced_cost:.4f}."
            ),
        ),
    ]


def _family_catch_floor_pass(validation: dict[str, Any], operating_point: str) -> bool:
    rows = [
        row
        for row in validation["by_family"]
        if row["operating_point"] == operating_point
        and int(row["total_error_cells"]) >= 10
    ]
    return all(float(row["catch_rate"]) >= 0.70 for row in rows)


def _result_paragraph(audit: Mapping[str, Any]) -> str:
    if not audit.get("validation_readout"):
        return (
            "The lower-burden review-routing candidate is not promoted. The dev140 "
            "candidate remains useful but unvalidated because the available full-200 "
            "artifacts do not match the frozen rich-schema holistic assembly surface."
        )
    return (
        "The current-code v08-shaped full-200 artifact was accepted for this "
        "aggregate-only validation readout, but the lower-burden review-routing "
        "candidate is not promoted. It preserved high catch, but review burden "
        "rose to the high-recall policy level instead of meeting the predeclared "
        "lower-burden gate."
    )


def main() -> None:
    path = write_report()
    print(path.relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
