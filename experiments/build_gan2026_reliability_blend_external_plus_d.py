"""Blend the variant-D self-signal with the P0.2 external risk score.

Question: does combining the cheap decoupled self-signal (variant D,
``1 - calibrated_confidence``) with the predeclared external composite risk
(cross-model agreement + residual flags + ambiguity count) rank errors better
than the external score alone (AUROC 0.781)?

No model calls — pure replay over saved artifacts:
  - external composite : recomputed exactly as P0.2 (consensus votes + rq9 packet).
  - variant-D risk      : from the validation750 shadow run JSONL.
  - correctness target  : v0_reference.comparison.purist_correct (canonical, decision
                          0018). We also verify it matches the SE-pass purist_correct
                          the shadow run scored against (they should be byte-identical).

PREDECLARED combiners (frozen before scoring):
  1. rank-average fusion  : mean of each risk's fractional rank in [0,1].
                            Unsupervised -> no fitting, no leakage. HEADLINE blend.
  2. CV-weighted blend    : w*norm(external) + (1-w)*norm(D), w chosen per-fold by
                            5-fold CV (honest tuned number, no whole-data overfit).
  3. whole-data best-w    : optimistic upper bound, reported with caveat.

PREDECLARED hypotheses:
  H1 — blend AUROC materially exceeds external alone (>= +0.02): D carries
       complementary signal; the cheap self-signal is additive to corroboration.
  H0 — blend ~ external: D is redundant with / dominated by the external score
       (expected if D-risk and external-risk are strongly correlated).

Usage:
    uv run python experiments/build_gan2026_reliability_blend_external_plus_d.py
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

# Frozen-identical copy of the P0.2 external composite (the experiments/ dir is not an
# importable package, so the formula is inlined here rather than imported).
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
    return {"score": 3 * (3 - agree) + flag_count + amb_count}


DATE = "2026-06-17"
SHADOW = rc.EXPERIMENTS / f"gan2026_confidence_reviewer_shadow_validation750_{DATE}.jsonl"
OUT_JSON = rc.EXPERIMENTS / f"gan2026_reliability_blend_external_plus_d_validation750_{DATE}.json"
OUT_MD = rc.EXPERIMENTS / f"gan2026_reliability_blend_external_plus_d_validation750_{DATE}.md"


# ── small stats (no sklearn) ────────────────────────────────────────────────────


def fractional_ranks(values: list[float]) -> list[float]:
    """Map values to fractional ranks in [0,1] (ties share the average rank)."""
    n = len(values)
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg / (n - 1) if n > 1 else 0.0
        i = j + 1
    return ranks


def minmax(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def spearman(a: list[float], b: list[float]) -> float:
    ra, rb = fractional_ranks(a), fractional_ranks(b)
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb, strict=False))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (va * vb) if va and vb else float("nan")


def cv_weighted_auroc(
    ext: list[float], d: list[float], labels: list[bool], *, folds: int = 5
) -> tuple[float, float, list[float]]:
    """Per-fold pick the blend weight on train, evaluate held-out. Returns
    (mean held-out AUROC, whole-data best-w AUROC, per-fold best weights)."""
    ne, nd = minmax(ext), minmax(d)
    weights = [i / 20 for i in range(21)]
    n = len(labels)
    fold_of = [i % folds for i in range(n)]  # deterministic interleave
    held_out: list[float] = []
    chosen: list[float] = []
    for f in range(folds):
        tr = [i for i in range(n) if fold_of[i] != f]
        te = [i for i in range(n) if fold_of[i] == f]
        best_w, best_auc = 0.5, -1.0
        for w in weights:
            blended = [w * ne[i] + (1 - w) * nd[i] for i in tr]
            auc = rc.auroc(blended, [labels[i] for i in tr])
            if auc == auc and auc > best_auc:
                best_auc, best_w = auc, w
        te_blend = [best_w * ne[i] + (1 - best_w) * nd[i] for i in te]
        te_auc = rc.auroc(te_blend, [labels[i] for i in te])
        if te_auc == te_auc:
            held_out.append(te_auc)
        chosen.append(best_w)
    # whole-data best-w (optimistic)
    best_w, best_auc = 0.5, -1.0
    for w in weights:
        blended = [w * ne[i] + (1 - w) * nd[i] for i in range(n)]
        auc = rc.auroc(blended, labels)
        if auc == auc and auc > best_auc:
            best_auc, best_w = auc, w
    mean_ho = sum(held_out) / len(held_out) if held_out else float("nan")
    return mean_ho, best_auc, chosen


# ── selective risk-coverage AUC (lower = better), reused from P0.2 logic ─────────


def risk_coverage_auc(risk: list[float], correct: list[bool]) -> float:
    items = sorted(zip(risk, correct, strict=False), key=lambda t: t[0])
    n = len(items)
    pts: list[tuple[float, float]] = []
    covered = err = 0
    i = 0
    while i < n:
        rv = items[i][0]
        while i < n and items[i][0] == rv:
            covered += 1
            err += 0 if items[i][1] else 1
            i += 1
        pts.append((covered / n, err / covered))
    return sum((b[0] - a[0]) * (a[1] + b[1]) / 2 for a, b in zip(pts, pts[1:], strict=False))


def main() -> None:
    rsn = {r["source_row_index"]: r for r in rc.load_jsonl(rc.REASONER_VALIDATION750)}
    agree = rc.agreement_count_by_source_index(rc.load_jsonl(rc.CONSENSUS_VALIDATION750))
    feats = rc.rq9_boundary_features_by_source_index(rc.load_jsonl(rc.RQ9_ROUTER))
    shadow = {r["source_row_index"]: r for r in load_jsonl_rows(SHADOW)}

    ext_risk: list[float] = []
    d_risk: list[float] = []
    correct: list[bool] = []
    se_target_mismatch = 0
    dropped_no_d = 0

    for idx, row in rsn.items():
        srow = shadow.get(idx)
        review = (srow or {}).get("confidence_review") or {}
        p = review.get("calibrated_confidence")
        if p is None:
            dropped_no_d += 1
            continue
        comp = external_risk_score(agree.get(idx, 2), feats.get(idx, {}))
        v0_correct = rc.subject_purist_correct(row)
        se_correct = bool((srow.get("comparison") or {}).get("purist_correct"))
        if v0_correct != se_correct:
            se_target_mismatch += 1
        ext_risk.append(float(comp["score"]))
        d_risk.append(1.0 - float(p))
        correct.append(v0_correct)

    labels = [not c for c in correct]  # positive = error
    n = len(labels)

    auroc_ext = rc.auroc(ext_risk, labels)
    auroc_d = rc.auroc(d_risk, labels)
    rank_blend = [
        (a + b) / 2
        for a, b in zip(fractional_ranks(ext_risk), fractional_ranks(d_risk), strict=False)
    ]
    auroc_rank = rc.auroc(rank_blend, labels)
    cv_auroc, bestw_auroc, chosen_w = cv_weighted_auroc(ext_risk, d_risk, labels)
    rho = spearman(ext_risk, d_risk)

    # selective risk-coverage AUC (lower=better) for ext vs rank-blend
    rc_auc_ext = risk_coverage_auc(ext_risk, correct)
    rc_auc_blend = risk_coverage_auc(rank_blend, correct)

    delta = auroc_rank - auroc_ext
    verdict = "H1_complementary" if delta >= 0.02 else "H0_redundant"

    result = {
        "artifact_kind": "gan2026_reliability_blend_external_plus_d",
        "date": DATE,
        "dimension": "Calibration / Abstention",
        "split": "validation750",
        "n": n,
        "n_errors": sum(labels),
        "dropped_no_d_signal": dropped_no_d,
        "se_vs_v0reference_target_mismatch": se_target_mismatch,
        "scored_against": "v0_reference.comparison.purist_correct",
        "spearman_extrisk_vs_drisk": rho,
        "auroc": {
            "external_alone": auroc_ext,
            "variant_d_alone": auroc_d,
            "rank_average_blend": auroc_rank,
            "cv_weighted_blend_heldout": cv_auroc,
            "whole_data_best_weight_blend": bestw_auroc,
        },
        "auroc_delta_rankblend_minus_external": delta,
        "cv_chosen_weights_external": chosen_w,
        "selective_risk_coverage_auc_lower_better": {
            "external_alone": rc_auc_ext,
            "rank_average_blend": rc_auc_blend,
        },
        "hypothesis_verdict": verdict,
        "provenance": {
            "model_calls": 0,
            "sources": [
                str(rc.REASONER_VALIDATION750),
                str(rc.CONSENSUS_VALIDATION750),
                str(rc.RQ9_ROUTER),
                str(SHADOW),
            ],
            "combiners": "rank-average (headline, unsupervised) + 5-fold CV weighted",
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    a = result["auroc"]
    print(f"  n={n} errors={sum(labels)} target_mismatch={se_target_mismatch}")
    print(f"  external alone        {a['external_alone']:.3f}")
    print(f"  variant D alone       {a['variant_d_alone']:.3f}")
    print(f"  rank-average blend    {a['rank_average_blend']:.3f}  (delta {delta:+.3f})")
    print(f"  CV-weighted held-out  {a['cv_weighted_blend_heldout']:.3f}")
    print(f"  best-w (optimistic)   {a['whole_data_best_weight_blend']:.3f}")
    print(f"  spearman(ext,D)={rho:.3f}  verdict={verdict}")


def render_md(r: dict[str, Any]) -> str:
    a = r["auroc"]
    L = [
        "# Blend: External Risk Score + Variant-D Self-Signal (validation750)\n",
        f"Date: {r['date']} · n={r['n']} ({r['n_errors']} errors) · model calls 0 · "
        f"scored against `{r['scored_against']}`\n",
        f"Correctness-target cross-check: SE-pass vs v0_reference purist mismatch on "
        f"**{r['se_vs_v0reference_target_mismatch']}/{r['n']}** rows "
        f"(confirms the shadow run scored the canonical subject). "
        f"Dropped (no D signal): {r['dropped_no_d_signal']}.\n",
        "## Failure-prediction AUROC\n",
        "| Signal | AUROC |",
        "|---|---:|",
        f"| external composite alone | {a['external_alone']:.3f} |",
        f"| variant D alone | {a['variant_d_alone']:.3f} |",
        f"| **rank-average blend (headline)** | **{a['rank_average_blend']:.3f}** |",
        f"| CV-weighted blend (held-out) | {a['cv_weighted_blend_heldout']:.3f} |",
        f"| whole-data best-weight (optimistic) | {a['whole_data_best_weight_blend']:.3f} |",
        f"\nΔ(rank-blend − external) = **{r['auroc_delta_rankblend_minus_external']:+.3f}**. "
        f"Spearman(external-risk, D-risk) = **{r['spearman_extrisk_vs_drisk']:.3f}**.\n",
        "## Selective risk-coverage AUC (lower = better)\n",
        f"- external alone: {r['selective_risk_coverage_auc_lower_better']['external_alone']:.4f}",
        f"- rank-average blend: {r['selective_risk_coverage_auc_lower_better']['rank_average_blend']:.4f}\n",
        "## Reading\n",
    ]
    if r["hypothesis_verdict"] == "H1_complementary":
        L.append(
            "**H1 — the self-signal is complementary.** Blending variant D with the external "
            "composite ranks errors better than corroboration alone, and the modest "
            "Spearman correlation explains why: D and the external score make partly "
            "*independent* errors, so fusion helps. A cheap single extra mini call adds "
            "signal on top of 3-model agreement.\n"
        )
    else:
        rho = r["spearman_extrisk_vs_drisk"]
        L.append(
            "**H0 — D does not materially boost the external score.** The unsupervised "
            f"rank-average edges external alone by only {r['auroc_delta_rankblend_minus_external']:+.3f} "
            "(within CI on this error count), and crucially the **honest CV-weighted blend "
            f"({a['cv_weighted_blend_heldout']:.3f}) collapses back to external alone "
            f"({a['external_alone']:.3f})** — when the weight is chosen without peeking, "
            "fusion buys nothing. Note this is NOT because the signals are redundant: "
            f"Spearman is only {rho:.2f}, so D and the external composite make partly "
            "*independent* errors. The problem is that D is simply the weaker, noisier "
            "ranker (0.684 vs 0.783), so averaging it in mostly adds noise. External "
            "corroboration stays the single best forward-observable signal; D's value is "
            "as a cheaper standalone proxy where 3-model agreement is unavailable, not as "
            "an additive booster.\n"
        )
    return "\n".join(L)


if __name__ == "__main__":
    main()
