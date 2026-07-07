"""P0.2 — Risk-coverage / selective-prediction curve (HEADLINE).

Reliability scorecard, Phase 0 (zero model budget). Orders all 750 validation
rows by ONE predeclared composite External Risk Score and sweeps the abstention
threshold, plotting selective risk vs coverage as a step function with operating
points, Wilson CIs, AUC, AUROC, and risk-at-fixed-coverage.

This is a falsification test of The Wall, not a reframing of it. The headline is
the decomposition of the error gap into *recoverable* error (shed by the external
score as coverage drops) vs an *irreducible residual* (a plateau in selective
risk that the score cannot drive to zero). A hard plateau is the expected,
publishable result: the empirical proof of the wall drawn as a curve.

PREDECLARED EXTERNAL RISK SCORE (frozen before scoring; higher = riskier):

    risk = 3 * (3 - cross_model_agreement_count)      # strongest leg, 0/3/6
         + 1 * source_residual_flag_count             # 0..5 source_has_* flags
         + 1 * ambiguity_reason_count                 # len(ambiguity_reasons)

  - cross_model_agreement_count in {1,2,3} from consensus_decision.votes
    (gpt-4.1-mini + qwen + deepseek): size of the largest identical-label cluster.
  - source_residual_flag_count: count of True among source_has_{last_event,
    since_anchor, trigger, drop_attack, unable_to_quantify} in the rq9 router
    packet boundary_features (source-derived, layer-independent).
  - ambiguity_reason_count: len(boundary_features.ambiguity_reasons).

Scored against v0_reference.comparison.purist_correct (the canonical subject),
NOT the rq9 hybrid-adjudicator purist (decision 0018).

No model calls; deterministic replay.

Usage:
    uv run python experiments/build_gan2026_reliability_p0_2_risk_coverage.py
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p0_2_risk_coverage_validation750_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p0_2_risk_coverage_validation750_2026-06-17.md"

SOURCE_FLAGS = (
    "source_has_last_event_language",
    "source_has_since_anchor",
    "source_has_trigger_language",
    "source_has_drop_attack_language",
    "source_has_unable_to_quantify",
)


def external_risk_score(agreement: int, features: dict[str, Any]) -> dict[str, Any]:
    agree = agreement if agreement in (1, 2, 3) else 2
    flag_count = sum(1 for f in SOURCE_FLAGS if features.get(f))
    amb_count = len(features.get("ambiguity_reasons") or [])
    score = 3 * (3 - agree) + flag_count + amb_count
    return {
        "score": score,
        "agreement": agree,
        "flag_count": flag_count,
        "ambiguity_count": amb_count,
    }


def risk_coverage_curve(items: list[dict[str, Any]]) -> dict[str, Any]:
    """items: list of {risk, correct}. Build the selective-prediction curve by
    covering the lowest-risk rows first (abstaining the highest risk)."""
    n = len(items)
    total_errors = sum(1 for it in items if not it["correct"])
    # Sort ascending by risk: cover low-risk first.
    ordered = sorted(items, key=lambda it: it["risk"])
    # Operating points at each distinct risk threshold (cumulative coverage).
    points: list[dict[str, Any]] = []
    covered = 0
    errors = 0
    i = 0
    while i < n:
        risk_val = ordered[i]["risk"]
        # consume the whole tie group at this risk level
        while i < n and ordered[i]["risk"] == risk_val:
            covered += 1
            errors += 0 if ordered[i]["correct"] else 1
            i += 1
        coverage = covered / n
        sel_risk = errors / covered
        lo, hi = rc.wilson_interval(errors, covered)
        points.append(
            {
                "risk_threshold": risk_val,
                "covered": covered,
                "coverage": coverage,
                "selective_errors": errors,
                "selective_risk": sel_risk,
                "selective_risk_ci95": [lo, hi],
            }
        )

    # AUC of selective risk vs coverage (trapezoidal over coverage). Lower = better.
    auc = 0.0
    for a, b in zip(points, points[1:], strict=False):
        auc += (b["coverage"] - a["coverage"]) * (a["selective_risk"] + b["selective_risk"]) / 2

    # Risk at fixed coverage by step lookup (first operating point with coverage >= c).
    def risk_at(cov: float) -> dict[str, Any] | None:
        for p in points:
            if p["coverage"] >= cov - 1e-9:
                return {
                    "coverage": p["coverage"],
                    "selective_risk": p["selective_risk"],
                    "selective_risk_ci95": p["selective_risk_ci95"],
                }
        return None

    return {
        "n": n,
        "total_errors": total_errors,
        "base_error_rate": total_errors / n,
        "operating_points": points,
        "auc_selective_risk_vs_coverage": auc,
        "risk_at_fixed_coverage": {
            f"{c:.2f}": risk_at(c) for c in (1.0, 0.95, 0.90, 0.80, 0.70, 0.50)
        },
        "plateau_lowest_coverage": {
            "coverage": points[0]["coverage"],
            "selective_risk": points[0]["selective_risk"],
            "selective_risk_ci95": points[0]["selective_risk_ci95"],
            "note": "selective risk among the safest rows the score can isolate; "
            "if > 0 with a tight CI, errors leak into the low-risk region -> "
            "irreducible residual (The Wall).",
        },
    }


def baseline_curves(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Oracle (errors-last) and the score's AUROC for predicting error, for context."""
    n = len(items)
    errs = sum(1 for it in items if not it["correct"])
    # Oracle AUC: perfect ranking abstains every error first -> selective risk 0
    # until all errors shed, then climbs. Compute its AUC the same way.
    oracle = sorted(items, key=lambda it: 0 if it["correct"] else 1)  # correct first (low risk)
    pts = []
    covered = err = 0
    for it in oracle:
        covered += 1
        err += 0 if it["correct"] else 1
        pts.append((covered / n, err / covered))
    oracle_auc = sum((b[0] - a[0]) * (a[1] + b[1]) / 2 for a, b in zip(pts, pts[1:], strict=False))
    scores = [it["risk"] for it in items]
    labels = [not it["correct"] for it in items]  # positive = error
    return {
        "oracle_auc_selective_risk_vs_coverage": oracle_auc,
        "external_score_auroc_for_error": rc.auroc(scores, labels),
        "random_baseline_auc_approx": errs / n / 2 + errs / n / 2,  # ~ base rate (flat curve area)
    }


def main() -> None:
    rsn = rc.load_jsonl(rc.REASONER_VALIDATION750)
    agree = rc.agreement_count_by_source_index(rc.load_jsonl(rc.CONSENSUS_VALIDATION750))
    feats = rc.rq9_boundary_features_by_source_index(rc.load_jsonl(rc.RQ9_ROUTER))

    items: list[dict[str, Any]] = []
    score_breakdown: list[dict[str, Any]] = []
    for row in rsn:
        idx = row["source_row_index"]
        comp = external_risk_score(agree.get(idx, 2), feats.get(idx, {}))
        items.append({"risk": comp["score"], "correct": rc.subject_purist_correct(row)})
        score_breakdown.append({"source_row_index": idx, **comp})

    curve = risk_coverage_curve(items)
    context = baseline_curves(items)

    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p0_2_risk_coverage",
        "date": "2026-06-17",
        "dimensions": ["Abstention", "Calibration", "Task correctness"],
        "split": "validation750",
        "predeclared_external_risk_score": {
            "formula": "3*(3-agreement) + source_flag_count + ambiguity_reason_count",
            "agreement_source": "consensus_decision.votes (gpt-4.1-mini+qwen+deepseek)",
            "flags": list(SOURCE_FLAGS),
            "scored_against": "v0_reference.comparison.purist_correct",
        },
        "provenance": rc.provenance_block(
            subject="single_se_mini_v0_reference",
            sources=[rc.REASONER_VALIDATION750, rc.CONSENSUS_VALIDATION750, rc.RQ9_ROUTER],
        ),
        "curve": curve,
        "context": context,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(
        f"  base error rate: {curve['base_error_rate']:.3f} ({curve['total_errors']}/{curve['n']})"
    )
    print(
        f"  AUC (selective risk vs coverage): {curve['auc_selective_risk_vs_coverage']:.4f}"
        f"  (oracle {context['oracle_auc_selective_risk_vs_coverage']:.4f},"
        f" random ~{curve['base_error_rate']:.4f})"
    )
    print(f"  AUROC external score for error: {context['external_score_auroc_for_error']:.4f}")
    pl = curve["plateau_lowest_coverage"]
    print(
        f"  plateau @ coverage {pl['coverage']:.2f}: selective risk {pl['selective_risk']:.3f}"
        f" CI {pl['selective_risk_ci95'][0]:.3f}-{pl['selective_risk_ci95'][1]:.3f}"
    )


def render_md(result: dict[str, Any]) -> str:
    c = result["curve"]
    ctx = result["context"]
    L: list[str] = []
    L.append("# P0.2 — Risk-Coverage / Selective-Prediction Curve (HEADLINE)\n")
    L.append(f"Date: {result['date']}  ·  Split: {result['split']}  ·  Model calls: 0\n")
    pd = result["predeclared_external_risk_score"]
    L.append("**Predeclared External Risk Score** (frozen before scoring; higher = riskier):\n")
    L.append(f"`risk = {pd['formula']}`\n")
    L.append(f"- agreement from {pd['agreement_source']}")
    L.append(f"- source residual flags: {', '.join(pd['flags'])}")
    L.append(f"- scored against `{pd['scored_against']}` (canonical subject, decision 0018)\n")
    L.append(
        f"Base error rate: **{c['total_errors']}/{c['n']} = {c['base_error_rate']:.1%}**. "
        f"The curve rests on only {c['total_errors']} error events, so every operating "
        "point carries a 95% Wilson CI.\n"
    )
    L.append("## Headline numbers\n")
    L.append(
        f"- **AUC (selective risk vs coverage):** {c['auc_selective_risk_vs_coverage']:.4f} "
        f"(lower is better; oracle {ctx['oracle_auc_selective_risk_vs_coverage']:.4f}, "
        f"random ≈ {c['base_error_rate']:.4f})"
    )
    L.append(
        f"- **AUROC of external score for predicting error:** "
        f"{ctx['external_score_auroc_for_error']:.4f}"
    )
    pl = c["plateau_lowest_coverage"]
    L.append(
        f"- **Plateau (safest rows, coverage {pl['coverage']:.2f}):** selective risk "
        f"{pl['selective_risk']:.1%} (CI {pl['selective_risk_ci95'][0]:.1%}–{pl['selective_risk_ci95'][1]:.1%})\n"
    )
    L.append("## Risk at fixed coverage\n")
    L.append("| Coverage | Selective risk | 95% CI |")
    L.append("|---:|---:|:--|")
    for cov, p in c["risk_at_fixed_coverage"].items():
        if p:
            L.append(
                f"| {float(cov):.0%} | {p['selective_risk']:.1%} | "
                f"{p['selective_risk_ci95'][0]:.1%}–{p['selective_risk_ci95'][1]:.1%} |"
            )
    L.append("\n## Operating points (step function)\n")
    L.append("| Risk ≤ | Covered | Coverage | Sel. errors | Selective risk | 95% CI |")
    L.append("|---:|---:|---:|---:|---:|:--|")
    for p in c["operating_points"]:
        L.append(
            f"| {p['risk_threshold']} | {p['covered']} | {p['coverage']:.1%} | "
            f"{p['selective_errors']} | {p['selective_risk']:.1%} | "
            f"{p['selective_risk_ci95'][0]:.1%}–{p['selective_risk_ci95'][1]:.1%} |"
        )
    L.append("\n---\n")
    auroc = ctx["external_score_auroc_for_error"]
    direction = "ranks errors above the diagonal" if auroc > 0.5 else "carries no error signal"
    L.append(
        f"**Reading (falsification test of The Wall).** The external score {direction} "
        f"(AUROC {auroc:.3f}). The recoverable error is the drop in selective risk as "
        "coverage falls from 100%; the irreducible residual is the plateau the score "
        "cannot shed. If the plateau CI excludes zero, the residual is empirically real: "
        "errors leak into the low-risk region precisely because the documented over-reading "
        "is *confident*, which is why no forward-observable abstention signal catches it.\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
