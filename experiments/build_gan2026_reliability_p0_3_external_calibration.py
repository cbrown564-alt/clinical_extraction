"""P0.3 — External-signal calibration (ECE / Brier / failure-prediction AUROC).

Reliability scorecard, Phase 0 (zero model budget). The subject path emits no
self-confidence field, and the nearest logged self-confidence (the V12 reasoner's
`decision_record.uncertainty`, a comparator layer) is degenerate. So the
calibration score is defined from EXTERNAL features over existing per-row logs and
assessed with a real reliability diagram + numeric ECE/Brier/failure-prediction
AUROC.

External probability of correctness (predeclared, NOT fitted): the cross-model
agreement share = (size of the largest identical-label vote cluster among
gpt-4.1-mini + qwen + deepseek) / 3, taking values {1/3, 2/3, 1}. Measuring its
ECE asks an honest, non-circular question: is cross-model agreement a *calibrated*
probability of the subject's correctness?

Scored against v0_reference.comparison.purist_correct (canonical subject,
decision 0018). No model calls.

Usage:
    uv run python experiments/build_gan2026_reliability_p0_3_external_calibration.py
"""

from __future__ import annotations

import collections
import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)
from build_gan2026_reliability_p0_2_risk_coverage import SOURCE_FLAGS, external_risk_score

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p0_3_external_calibration_validation750_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p0_3_external_calibration_validation750_2026-06-17.md"


def self_confidence_degeneracy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Comparator-layer self-confidence: the V12 reasoner uncertainty bucket and
    whether it separates correct from wrong. (The subject SE layer has none.)"""
    by_bucket: dict[str, list[bool]] = collections.defaultdict(list)
    for r in rows:
        bucket = (r.get("decision_record") or {}).get("uncertainty") or "missing"
        by_bucket[bucket].append(rc.subject_purist_correct(r))
    table = {
        b: {"n": len(v), "correct": sum(v), "accuracy": sum(v) / len(v)}
        for b, v in sorted(by_bucket.items(), key=lambda kv: -len(kv[1]))
    }
    dominant = max(table.values(), key=lambda d: d["n"])
    return {
        "field": "decision_record.uncertainty",
        "layer": "[comparator: V12-full-gpt4.1] reasoner self-report",
        "note": "subject single-SE-mini layer emits NO self-confidence field",
        "by_bucket": table,
        "dominant_bucket_share": dominant["n"] / sum(d["n"] for d in table.values()),
    }


def main() -> None:
    rows = rc.load_jsonl(rc.REASONER_VALIDATION750)
    agree = rc.agreement_count_by_source_index(rc.load_jsonl(rc.CONSENSUS_VALIDATION750))
    feats = rc.rq9_boundary_features_by_source_index(rc.load_jsonl(rc.RQ9_ROUTER))

    # External probability via cross-model agreement share.
    pairs: list[tuple[float, bool]] = []
    ev_correct = collections.defaultdict(list)  # evidence_valid -> correctness
    risk_scores: list[float] = []
    risk_is_error: list[bool] = []
    for r in rows:
        idx = r["source_row_index"]
        a = agree.get(idx, 2)
        a = a if a in (1, 2, 3) else 2
        prob = a / 3.0
        correct = rc.subject_purist_correct(r)
        pairs.append((prob, correct))
        ev_correct[bool(rc.subject_evidence_valid(r))].append(correct)
        comp = external_risk_score(a, feats.get(idx, {}))
        risk_scores.append(comp["score"])
        risk_is_error.append(not correct)

    ece, bins = rc.expected_calibration_error(pairs, n_bins=10)
    brier = rc.brier_score(pairs)
    # AUROC of external confidence (=prob) for CORRECTNESS.
    auroc_conf = rc.auroc([p for p, _ in pairs], [o for _, o in pairs])
    # AUROC of risk score for FAILURE (the failure-prediction number the plan names).
    auroc_fail = rc.auroc(risk_scores, risk_is_error)

    ev_table = {
        str(k): {"n": len(v), "correct": sum(v), "accuracy": sum(v) / len(v) if v else None}
        for k, v in sorted(ev_correct.items())
    }

    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p0_3_external_calibration",
        "date": "2026-06-17",
        "dimensions": ["Calibration"],
        "split": "validation750",
        "provenance": rc.provenance_block(
            subject="single_se_mini_v0_reference",
            sources=[rc.REASONER_VALIDATION750, rc.CONSENSUS_VALIDATION750, rc.RQ9_ROUTER],
        ),
        "self_confidence_degeneracy": self_confidence_degeneracy(rows),
        "external_confidence": {
            "definition": "cross_model_agreement_count / 3  (predeclared, not fitted)",
            "ece_10bin": ece,
            "brier": brier,
            "auroc_for_correctness": auroc_conf,
            "reliability_diagram": bins,
        },
        "failure_prediction": {
            "risk_score_auroc_for_failure": auroc_fail,
            "evidence_valid_split": ev_table,
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"  self-confidence dominant bucket share: "
          f"{result['self_confidence_degeneracy']['dominant_bucket_share']:.1%}")
    print(f"  external-confidence ECE={ece:.4f} Brier={brier:.4f} "
          f"AUROC(correct)={auroc_conf:.4f}")
    print(f"  failure-prediction AUROC (risk score)={auroc_fail:.4f}")


def render_md(result: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# P0.3 — External-Signal Calibration (ECE / Brier / Failure-Prediction AUROC)\n")
    L.append(f"Date: {result['date']}  ·  Split: {result['split']}  ·  Model calls: 0\n")
    sc = result["self_confidence_degeneracy"]
    L.append("## Self-confidence is degenerate (and the subject has none)\n")
    L.append(f"Nearest logged self-confidence is `{sc['field']}` "
             f"({sc['layer']}); the subject single-SE-mini layer emits none.\n")
    L.append("| Uncertainty bucket | n | Purist acc |")
    L.append("|---|---:|---:|")
    for b, d in sc["by_bucket"].items():
        L.append(f"| {b} | {d['n']} | {d['accuracy']:.1%} |")
    L.append(f"\nThe dominant bucket holds **{sc['dominant_bucket_share']:.1%}** of rows — "
             "self-report is near-constant and cannot rank correctness.\n")
    ec = result["external_confidence"]
    L.append("## External confidence (cross-model agreement share) — calibration\n")
    L.append(f"- Definition: `{ec['definition']}`")
    L.append(f"- **ECE (10-bin): {ec['ece_10bin']:.4f}**, **Brier: {ec['brier']:.4f}**, "
             f"**AUROC for correctness: {ec['auroc_for_correctness']:.4f}**\n")
    L.append("| Bin | n | Mean score | Empirical acc | Gap |")
    L.append("|---|---:|---:|---:|---:|")
    for b in ec["reliability_diagram"]:
        L.append(f"| {b['bin']} | {b['n']} | {b['mean_score']:.3f} | "
                 f"{b['empirical_accuracy']:.3f} | {b['gap']:+.3f} |")
    fp = result["failure_prediction"]
    L.append("\n## Failure prediction\n")
    L.append(f"- **External risk score AUROC for failure: {fp['risk_score_auroc_for_failure']:.4f}**")
    L.append("- Evidence-valid vs correctness:")
    for k, d in fp["evidence_valid_split"].items():
        L.append(f"  - evidence_valid={k}: {d['correct']}/{d['n']} = {d['accuracy']:.1%}")
    L.append("\n- Parse-repair count is a non-signal here: the production path logs "
             "0 parse failures / 0 evidence loss across 2,295 rows (RQ5/RQ8), so it has "
             "no variance to calibrate against.\n")
    L.append("---\n")
    L.append("**Reading.** External signals rank the subject's correctness "
             f"(agreement-share AUROC {ec['auroc_for_correctness']:.3f}; risk-score "
             f"failure AUROC {fp['risk_score_auroc_for_failure']:.3f}); self-reported "
             "confidence does not (near-constant). The honest calibration story is that "
             "reliability must be read off external corroboration, not the model's own "
             "certainty — the same lesson the architecture arc reached (Insight #3).\n")
    return "\n".join(L)


if __name__ == "__main__":
    main()
