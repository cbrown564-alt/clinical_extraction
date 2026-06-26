"""Aggregate-only calibration validation audit for ExECTv2.

The frozen reliability protocol permits full-200 validation only as aggregate
outputs. This module freezes the dev140 scoring rule, applies it once to the
accepted current-code v08-shaped full-200 artifact, and emits no row-level
identifiers, examples, evidence, rationales, or residual ledgers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import cross_model_reliability_analysis as reliability
from . import validation_audit_scaffold as scaffold

REPO_ROOT = scaffold.REPO_ROOT
REPORT_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_calibration_validation_audit_2026-06-25.md"
)

_PROTOCOL_DEV_ECE_BASELINE = 0.1456
_FULL200_ARTIFACT: dict[str, str] = {
    **scaffold.FULL200_ARTIFACT,
    "reason": (
        "Accepted for aggregate-only validation of the frozen dev140 grouped "
        "calibration scoring rule on the current-code v08-shaped rich-schema "
        "holistic assembly surface."
    ),
}


def build_calibration_validation_audit(
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Return the aggregate-only calibration validation package."""

    dev_rows = {
        run.candidate: reliability._load_jsonl(repo_root / run.rows_path)
        for run in reliability.RICH_SCHEMA_RUNS
    }
    dev_cells = list(reliability._iter_reliability_cells(dev_rows))
    dev_proxy = reliability._calibration_proxy(dev_cells)
    artifact = scaffold.artifact_inventory_single(repo_root, _FULL200_ARTIFACT)[0]
    validation = (
        _validation_readout(repo_root, dev_cells, artifact)
        if artifact["eligible"]
        else None
    )
    promotion_gates = _promotion_gates(validation)
    promotion_decision = scaffold.promotion_decision_from_gates(promotion_gates)
    return {
        **scaffold.audit_envelope(
            audit_kind="exectv2_calibration_aggregate_validation",
            repo_root=repo_root,
            scorer="headline_target family-cell correctness",
            row_inspection_boundary=(
                "Aggregate calibration metrics and artifact inventory only; no row "
                "identifiers, note text, gold labels, predictions, evidence spans, "
                "rationales, or selected failure examples are emitted."
            ),
        ),
        "candidate_definition": {
            "model_type": "grouped_logistic_scoring_rule",
            "training_surface": (
                "dev140 rich-schema holistic assembly reliability scorecard"
            ),
            "feature_set": list(reliability._CALIBRATION_FEATURES),
            "dev_cells": len(dev_cells),
            "dev_cross_validated_ece": dev_proxy["expected_calibration_error"],
            "dev_cross_validated_brier": dev_proxy["brier_score"],
            "protocol_dev_ece_baseline": _PROTOCOL_DEV_ECE_BASELINE,
        },
        "artifact_inventory": [artifact],
        "eligible_validation_artifacts": 1 if artifact["eligible"] else 0,
        "validation_readout": validation,
        "stop_rule_outcome": scaffold.stop_rule_outcome(
            validation=validation,
            promotion_decision=promotion_decision,
            promoted_reason=(
                "The frozen dev140 calibration scoring rule passes all "
                "predeclared aggregate validation gates on the accepted "
                "current-code v08-shaped full-200 artifact."
            ),
        ),
        "promotion_gates": promotion_gates,
        "next_action": (
            "Upgrade scorecard calibration coverage above dev-only status while "
            "keeping the claim limited to aggregate full-200 validation, not "
            "deployment-ready probability or holdout calibration."
        )
        if promotion_decision == "promoted"
        else (
            "Keep calibration at dev-only coverage and redesign the scoring rule "
            "on dev140 before any fresh validation attempt."
        ),
    }


def render_markdown(audit: dict[str, Any]) -> str:
    """Render a paper-facing Markdown audit without row-level details."""

    candidate = audit["candidate_definition"]
    lines = scaffold.render_preflight_section(
        audit,
        title="# ExECTv2 Calibration Validation Audit",
        status_line=(
            "Status: aggregate-only calibration validation and stop-rule readout."
        ),
    )
    lines.extend(
        [
            "",
            "## Frozen Calibration Candidate",
            "",
            f"- Model type: `{candidate['model_type']}`",
            f"- Training surface: {candidate['training_surface']}",
            f"- Development cells: {candidate['dev_cells']}",
            f"- Dev cross-validated ECE: {candidate['dev_cross_validated_ece']:.4f}",
            f"- Dev cross-validated Brier: {candidate['dev_cross_validated_brier']:.4f}",
            (
                "- Protocol ECE baseline for promotion: "
                f"{candidate['protocol_dev_ece_baseline']:.4f}"
            ),
            f"- Feature set: `{', '.join(candidate['feature_set'])}`",
        ]
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
                f"- Overall accuracy: {validation['overall_accuracy']:.4f}",
                f"- Mean calibrated confidence: {validation['mean_calibrated_confidence']:.4f}",
                f"- ECE: {validation['expected_calibration_error']:.4f}",
                f"- Brier: {validation['brier_score']:.4f}",
                (
                    "- Constant base-rate Brier: "
                    f"{validation['constant_base_rate_brier_score']:.4f}"
                ),
                (
                    "- Brier improvement vs constant base rate: "
                    f"{validation['brier_improvement_vs_base_rate']:.4f}"
                ),
                (
                    "- Maximum adjacent-bin reversal: "
                    f"{validation['max_adjacent_bin_reversal']:.4f}"
                ),
                "",
                "### Reliability Bins",
                "",
                (
                    "| Bin | Cells | Confidence range | Mean confidence | Accuracy | "
                    "Gap | ECE contribution | Mean cell F1 |"
                ),
                "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in validation["bins"]:
            conf_range = (
                f"{row['confidence_range'][0]:.4f}-"
                f"{row['confidence_range'][1]:.4f}"
            )
            lines.append(
                f"| {row['bin']} | {row['cells']} | {conf_range} | "
                f"{row['avg_calibrated_confidence']:.4f} | "
                f"{row['accuracy']:.4f} | {row['calibration_gap']:.4f} | "
                f"{row['ece_contribution']:.4f} | {row['mean_cell_f1']:.4f} |"
            )
        lines.extend(
            [
                "",
                "### Per-Family Calibration",
                "",
                (
                    "| Family | Cells | Accuracy | Mean confidence | ECE | Brier | "
                    "Constant Brier | Bins |"
                ),
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in validation["per_family"]:
            lines.append(
                f"| {row['family']} | {row['cells']} | {row['accuracy']:.4f} | "
                f"{row['mean_calibrated_confidence']:.4f} | "
                f"{row['expected_calibration_error']:.4f} | "
                f"{row['brier_score']:.4f} | "
                f"{row['constant_base_rate_brier_score']:.4f} | "
                f"{row['bin_count']} |"
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
        build_audit=build_calibration_validation_audit,
        render_markdown=render_markdown,
        repo_root=repo_root,
        report_path=report_path,
    )


def _validation_readout(
    repo_root: Path,
    dev_cells: list[dict[str, Any]],
    artifact: dict[str, Any],
) -> dict[str, Any]:
    weights = reliability._fit_logistic_scoring_rule(dev_cells)
    dev_base_rate = (
        sum(1 for cell in dev_cells if bool(cell["correct"])) / len(dev_cells)
        if dev_cells
        else 0.5
    )
    rows = reliability._load_jsonl(repo_root / artifact["path"])
    scored = _validation_cells(rows, weights, dev_base_rate)
    pairs = [
        (float(row["calibrated_confidence"]), bool(row["correct"]))
        for row in scored
    ]
    baseline_pairs = [
        (float(row["training_base_rate"]), bool(row["correct"]))
        for row in scored
    ]
    bins = reliability._reliability_bins(scored, bin_count=5)
    ece = reliability._expected_calibration_error(pairs, bins)
    brier = reliability._brier_score(pairs)
    baseline_brier = reliability._brier_score(baseline_pairs)
    return {
        "artifact_path": artifact["path"],
        "rows": len(rows),
        "eligible_cells": len(scored),
        "overall_accuracy": scaffold.round_rate(
            sum(1 for row in scored if bool(row["correct"])),
            len(scored),
        ),
        "mean_calibrated_confidence": round(
            sum(float(row["calibrated_confidence"]) for row in scored)
            / len(scored),
            4,
        )
        if scored
        else 0.0,
        "expected_calibration_error": round(ece, 4),
        "brier_score": round(brier, 4),
        "constant_base_rate_brier_score": round(baseline_brier, 4),
        "brier_improvement_vs_base_rate": round(baseline_brier - brier, 4),
        "max_adjacent_bin_reversal": reliability._max_adjacent_bin_reversal(bins),
        "bins": bins,
        "per_family": [
            reliability._calibration_summary_for_family(
                family,
                [row for row in scored if str(row["family"]) == family],
                baseline_pairs=[
                    (float(row["training_base_rate"]), bool(row["correct"]))
                    for row in scored
                    if str(row["family"]) == family
                ],
            )
            for family in reliability.FAMILIES
        ],
    }


def _validation_cells(
    rows: list[dict[str, Any]],
    weights: list[float],
    training_base_rate: float,
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for row in rows:
        for family in reliability.FAMILIES:
            score = reliability._row_family_score(row, family)
            if score.pred_count == 0 and score.gold_count == 0:
                continue
            features = reliability._risk_features(row, family)
            cell = {
                "family": family,
                "correct": score.fp == 0 and score.fn == 0,
                "f1": score.f1,
                "features": features,
                "risk_score": reliability._risk_score(family, features),
            }
            cells.append(
                {
                    **cell,
                    "calibrated_confidence": round(
                        reliability._predict_logistic_probability(weights, cell),
                        6,
                    ),
                    "training_base_rate": round(training_base_rate, 6),
                }
            )
    return cells


def _promotion_gates(validation: dict[str, Any] | None) -> list[dict[str, str]]:
    blocked_note = "No same-surface full-200 aggregate artifact is available."
    if validation is None:
        return [
            scaffold.gate(
                "ECE improves over protocol dev-only proxy baseline",
                "not_evaluable",
                blocked_note,
            ),
            scaffold.gate(
                "Brier improves over constant base-rate comparator",
                "not_evaluable",
                blocked_note,
            ),
            scaffold.gate(
                "At least four populated reliability bins",
                "not_evaluable",
                blocked_note,
            ),
            scaffold.gate(
                "No adjacent-bin reversal larger than 0.10",
                "not_evaluable",
                blocked_note,
            ),
            scaffold.gate(
                "Per-family ECE reported for all four families",
                "not_evaluable",
                blocked_note,
            ),
        ]

    families = {row["family"] for row in validation["per_family"]}
    return [
        scaffold.gate(
            "ECE improves over protocol dev-only proxy baseline",
            "pass"
            if float(validation["expected_calibration_error"])
            < _PROTOCOL_DEV_ECE_BASELINE
            else "fail",
            (
                f"Validation ECE {validation['expected_calibration_error']:.4f}; "
                f"baseline {_PROTOCOL_DEV_ECE_BASELINE:.4f}."
            ),
        ),
        scaffold.gate(
            "Brier improves over constant base-rate comparator",
            "pass"
            if float(validation["brier_score"])
            < float(validation["constant_base_rate_brier_score"])
            else "fail",
            (
                f"Validation Brier {validation['brier_score']:.4f}; constant "
                f"base-rate {validation['constant_base_rate_brier_score']:.4f}."
            ),
        ),
        scaffold.gate(
            "At least four populated reliability bins",
            "pass" if len(validation["bins"]) >= 4 else "fail",
            f"Populated bins: {len(validation['bins'])}.",
        ),
        scaffold.gate(
            "No adjacent-bin reversal larger than 0.10",
            "pass"
            if float(validation["max_adjacent_bin_reversal"]) <= 0.10
            else "fail",
            (
                "Maximum adjacent-bin reversal is "
                f"{validation['max_adjacent_bin_reversal']:.4f}."
            ),
        ),
        scaffold.gate(
            "Per-family ECE reported for all four families",
            "pass" if families == set(reliability.FAMILIES) else "fail",
            f"Families reported: {', '.join(sorted(families))}.",
        ),
    ]


def _result_paragraph(audit: dict[str, Any]) -> str:
    if audit["stop_rule_outcome"]["promotion_decision"] != "promoted":
        return (
            "The calibration candidate is not promoted. Keep the scorecard claim "
            "at dev-only calibration coverage until a fresh predeclared candidate "
            "passes aggregate validation."
        )
    validation = audit["validation_readout"]
    return (
        "The frozen dev140 calibration scoring rule is promoted as aggregate "
        "full-200 validation evidence. The claim is limited to improved "
        "calibration evidence on this surface: "
        f"ECE {validation['expected_calibration_error']:.4f}, "
        f"Brier {validation['brier_score']:.4f}, five populated bins, and "
        "per-family ECE reported for every scored family."
    )


def main() -> None:
    path = write_report()
    print(path.relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
