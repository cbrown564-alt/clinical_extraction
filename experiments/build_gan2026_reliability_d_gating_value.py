"""Is variant-D confidence practically useful as a GATE on the single-model arch?

The primary architecture is the single gpt-4.1-mini SE pass. D adds a confidence per
row (one extra mini call). That only *improves* the architecture if the confidence is
usable to abstain/route the riskiest rows for a worthwhile selective-accuracy lift.

This is a no-budget validation750 simulation that answers "is gating worth it?" BEFORE
spending the frozen test450 holdout. For each coverage level we abstain the highest
D-risk rows and report:
  - selective accuracy on covered rows (vs the no-gate base accuracy),
  - abstention precision = error rate among ABSTAINED rows (vs base error = the
    precision RANDOM abstention would get; beating it is the whole point),
  - lift over random abstention.

External composite is shown for context only — it needs 3 models, so it is NOT
available to the single-model architecture; D is the only forward-observable signal
that architecture actually has.

Usage:
    uv run python experiments/build_gan2026_reliability_d_gating_value.py
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.replay_io import (
    load_jsonl_rows,
)

DATE = "2026-06-17"
SHADOW = rc.EXPERIMENTS / f"gan2026_confidence_reviewer_shadow_validation750_{DATE}.jsonl"
OUT_JSON = rc.EXPERIMENTS / f"gan2026_reliability_d_gating_value_validation750_{DATE}.json"
OUT_MD = rc.EXPERIMENTS / f"gan2026_reliability_d_gating_value_validation750_{DATE}.md"

SOURCE_FLAGS = (
    "source_has_last_event_language",
    "source_has_since_anchor",
    "source_has_trigger_language",
    "source_has_drop_attack_language",
    "source_has_unable_to_quantify",
)
COVERAGES = (1.0, 0.95, 0.90, 0.80, 0.70, 0.50)


def external_score(agreement: int, features: dict[str, Any]) -> float:
    agree = agreement if agreement in (1, 2, 3) else 2
    flag_count = sum(1 for f in SOURCE_FLAGS if features.get(f))
    amb_count = len(features.get("ambiguity_reasons") or [])
    return float(3 * (3 - agree) + flag_count + amb_count)


def gating_table(risk: list[float], correct: list[bool]) -> list[dict[str, Any]]:
    """Abstain the highest-risk rows; report selective accuracy + abstention quality."""
    n = len(risk)
    base_err = sum(1 for c in correct if not c) / n
    order = sorted(range(n), key=lambda i: risk[i])  # ascending risk = cover first
    rows: list[dict[str, Any]] = []
    for cov in COVERAGES:
        k = max(1, round(cov * n))
        covered = order[:k]
        abstained = order[k:]
        cov_correct = sum(1 for i in covered if correct[i])
        sel_acc = cov_correct / len(covered)
        abst_err = sum(1 for i in abstained if not correct[i])
        abst_prec = (abst_err / len(abstained)) if abstained else float("nan")
        errors_shed = abst_err
        total_errors = sum(1 for c in correct if not c)
        lo, hi = rc.wilson_interval(cov_correct, len(covered))
        rows.append({
            "coverage": len(covered) / n,
            "covered": len(covered),
            "abstained": len(abstained),
            "selective_accuracy": sel_acc,
            "selective_accuracy_ci95": [lo, hi],
            "abstention_precision": abst_prec,         # errors among abstained
            "random_abstention_precision": base_err,    # what random would get
            "abstention_lift_over_random": (abst_prec - base_err) if abstained else float("nan"),
            "errors_shed": errors_shed,
            "errors_shed_frac_of_total": (errors_shed / total_errors) if total_errors else float("nan"),
            "errors_shed_frac_if_random": (1 - cov),    # random sheds proportional to abstain frac
        })
    return rows


def main() -> None:
    rsn = {r["source_row_index"]: r for r in rc.load_jsonl(rc.REASONER_VALIDATION750)}
    agree = rc.agreement_count_by_source_index(rc.load_jsonl(rc.CONSENSUS_VALIDATION750))
    feats = rc.rq9_boundary_features_by_source_index(rc.load_jsonl(rc.RQ9_ROUTER))
    shadow = {r["source_row_index"]: r for r in load_jsonl_rows(SHADOW)}

    d_risk: list[float] = []
    ext_risk: list[float] = []
    correct: list[bool] = []
    for idx, row in rsn.items():
        review = (shadow.get(idx) or {}).get("confidence_review") or {}
        p = review.get("calibrated_confidence")
        if p is None:
            continue
        d_risk.append(1.0 - float(p))
        ext_risk.append(external_score(agree.get(idx, 2), feats.get(idx, {})))
        correct.append(rc.subject_purist_correct(row))

    n = len(correct)
    base_acc = sum(1 for c in correct if c) / n
    d_table = gating_table(d_risk, correct)
    ext_table = gating_table(ext_risk, correct)
    d_auroc = rc.auroc(d_risk, [not c for c in correct])

    result = {
        "artifact_kind": "gan2026_reliability_d_gating_value",
        "date": DATE,
        "split": "validation750",
        "architecture": "single gpt-4.1-mini SE pass (primary)",
        "n": n,
        "base_accuracy": base_acc,
        "base_error_rate": 1 - base_acc,
        "d_failure_auroc": d_auroc,
        "d_gating": d_table,
        "external_gating_context_only": ext_table,
        "note": (
            "External composite needs 3 models and is NOT available to the single-model "
            "architecture; shown only as the ceiling a multi-model gate would reach."
        ),
        "provenance": {"model_calls": 0, "sources": [str(SHADOW), str(rc.REASONER_VALIDATION750)]},
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"  base accuracy {base_acc:.3f} (error {1-base_acc:.3f}), D AUROC {d_auroc:.3f}")
    for r in d_table:
        print(f"  cov {r['coverage']:.0%}: sel acc {r['selective_accuracy']:.3f} "
              f"| abst prec {r['abstention_precision']:.3f} vs random {r['random_abstention_precision']:.3f} "
              f"(lift {r['abstention_lift_over_random']:+.3f})")


def render_md(r: dict[str, Any]) -> str:
    L = [
        "# Variant-D as a Gate on the Single-Model Architecture (validation750)\n",
        f"Date: {r['date']} · arch: {r['architecture']} · n={r['n']} · model calls 0\n",
        f"Base accuracy (no gate): **{r['base_accuracy']:.1%}** (error {r['base_error_rate']:.1%}). "
        f"D failure-prediction AUROC: **{r['d_failure_auroc']:.3f}**.\n",
        "**The bar:** random abstention sheds errors in proportion to the abstained fraction "
        "and leaves selective accuracy unchanged in expectation. A gate is useful only if it "
        "beats that — higher selective accuracy and abstention precision above the base error rate.\n",
        "## D gate (the signal the single-model arch actually has)\n",
        "| Coverage | Selective acc | 95% CI | Abstention precision | vs random | Errors shed | vs random shed |",
        "|---:|---:|:--|---:|---:|---:|---:|",
    ]
    for x in r["d_gating"]:
        L.append(
            f"| {x['coverage']:.0%} | {x['selective_accuracy']:.1%} | "
            f"{x['selective_accuracy_ci95'][0]:.1%}–{x['selective_accuracy_ci95'][1]:.1%} | "
            f"{x['abstention_precision']:.1%} | {x['abstention_lift_over_random']:+.1%} | "
            f"{x['errors_shed']} | {x['errors_shed_frac_of_total']:.0%} vs {x['errors_shed_frac_if_random']:.0%} |"
        )
    L.append("\n## External composite gate (context only — needs 3 models, unavailable single-model)\n")
    L.append("| Coverage | Selective acc | Abstention precision | vs random |")
    L.append("|---:|---:|---:|---:|")
    for x in r["external_gating_context_only"]:
        L.append(
            f"| {x['coverage']:.0%} | {x['selective_accuracy']:.1%} | "
            f"{x['abstention_precision']:.1%} | {x['abstention_lift_over_random']:+.1%} |"
        )
    L.append(f"\n_{r['note']}_\n")
    L.append("## Reading\n")
    g90 = next(x for x in r["d_gating"] if abs(x["coverage"] - 0.90) < 0.02)
    L.append(
        f"At 90% coverage the D gate lifts accuracy from {r['base_accuracy']:.1%} to "
        f"{g90['selective_accuracy']:.1%} and its abstention precision is {g90['abstention_precision']:.1%} "
        f"vs the random bar {g90['random_abstention_precision']:.1%} ({g90['abstention_lift_over_random']:+.1%}). "
        "Judge practical usefulness by how far selective accuracy and abstention precision sit "
        "above the random bar, and whether the lift justifies one extra mini call per row plus "
        "the discarded coverage.\n")
    return "\n".join(L)


if __name__ == "__main__":
    main()
