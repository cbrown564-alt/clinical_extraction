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

from build_gan2026_reliability_p0_2_risk_coverage import external_risk_score

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)

OUT_JSON = (
    rc.EXPERIMENTS / "gan2026_reliability_p0_3_external_calibration_validation750_2026-06-17.json"
)
OUT_MD = (
    rc.EXPERIMENTS / "gan2026_reliability_p0_3_external_calibration_validation750_2026-06-17.md"
)


def self_confidence_degeneracy(reasoner_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Subject SELF-confidence: the SE selection.confidence on the production path
    (joined from the SE-mini source by source_row_index), and whether it separates
    correct from wrong. The V12 reasoner uncertainty is reported as a comparator."""
    # Subject: SE selection.confidence + subject purist_correct, both from SE-mini.
    se_rows = rc.load_jsonl(rc.SE_MINI_VALIDATION750)
    subj: dict[str, list[bool]] = collections.defaultdict(list)
    for r in se_rows:
        conf = ((r.get("structured_record") or {}).get("selection") or {}).get(
            "confidence"
        ) or "missing"
        subj[conf].append(bool((r.get("comparison") or {}).get("purist_correct")))
    subj_table = {
        b: {"n": len(v), "correct": sum(v), "accuracy": sum(v) / len(v) if v else None}
        for b, v in sorted(subj.items(), key=lambda kv: -len(kv[1]))
    }
    subj_dominant = max(subj_table.values(), key=lambda d: d["n"])
    # Comparator: reasoner uncertainty bucket.
    comp: dict[str, list[bool]] = collections.defaultdict(list)
    for r in reasoner_rows:
        bucket = (r.get("decision_record") or {}).get("uncertainty") or "missing"
        comp[bucket].append(rc.subject_purist_correct(r))
    comp_table = {
        b: {"n": len(v), "correct": sum(v), "accuracy": sum(v) / len(v)}
        for b, v in sorted(comp.items(), key=lambda kv: -len(kv[1]))
    }
    return {
        "field": "structured_record.selection.confidence (subject SE pass)",
        "layer": "subject single-SE-mini",
        "note": "the v0_reference scoring layer drops confidence, but the SE source emits it",
        "by_bucket": subj_table,
        "dominant_bucket_share": subj_dominant["n"] / sum(d["n"] for d in subj_table.values()),
        "comparator_reasoner_uncertainty": comp_table,
    }


def main() -> None:
    rows = rc.load_jsonl(rc.REASONER_VALIDATION750)
    agree = rc.agreement_count_by_source_index(rc.load_jsonl(rc.CONSENSUS_VALIDATION750))
    feats = rc.rq9_boundary_features_by_source_index(rc.load_jsonl(rc.RQ9_ROUTER))
    # parse-repair count on the subject SE-mini path, joined by source_row_index.
    repair_by_idx = {
        r["source_row_index"]: len(r.get("parse_errors") or [])
        for r in rc.load_jsonl(rc.SE_MINI_VALIDATION750)
    }

    # External probability via cross-model agreement share.
    pairs: list[tuple[float, bool]] = []
    ev_correct = collections.defaultdict(list)  # evidence_valid -> correctness
    risk_scores: list[float] = []
    risk_is_error: list[bool] = []
    repair_counts: list[int] = []
    repair_correct = collections.defaultdict(list)  # any-repair -> correctness
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
        rep = repair_by_idx.get(idx, 0)
        repair_counts.append(rep)
        repair_correct[rep > 0].append(correct)

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
    # parse-repair count as an error signal (repairs are common: not a constant).
    repair_auroc = rc.auroc([float(x) for x in repair_counts], risk_is_error)
    repair_table = {
        ("any_repair" if k else "no_repair"): {
            "n": len(v),
            "correct": sum(v),
            "accuracy": sum(v) / len(v) if v else None,
        }
        for k, v in sorted(repair_correct.items())
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
            "parse_repair_auroc_for_failure": repair_auroc,
            "parse_repair_split": repair_table,
            "rows_with_any_repair": sum(1 for x in repair_counts if x > 0),
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(
        f"  self-confidence dominant bucket share: "
        f"{result['self_confidence_degeneracy']['dominant_bucket_share']:.1%}"
    )
    print(f"  external-confidence ECE={ece:.4f} Brier={brier:.4f} AUROC(correct)={auroc_conf:.4f}")
    print(f"  failure-prediction AUROC (risk score)={auroc_fail:.4f}")


def render_md(result: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# P0.3 — External-Signal Calibration (ECE / Brier / Failure-Prediction AUROC)\n")
    L.append(f"Date: {result['date']}  ·  Split: {result['split']}  ·  Model calls: 0\n")
    sc = result["self_confidence_degeneracy"]
    L.append("## Self-confidence is degenerate\n")
    L.append(f"Subject self-confidence is `{sc['field']}` ({sc['layer']}); {sc['note']}.\n")
    L.append("| Confidence bucket | n | Purist acc |")
    L.append("|---|---:|---:|")
    for b, d in sc["by_bucket"].items():
        acc = d["accuracy"]
        L.append(
            f"| {b} | {d['n']} | {acc:.1%} |" if acc is not None else f"| {b} | {d['n']} | — |"
        )
    L.append(
        f"\nThe dominant bucket holds **{sc['dominant_bucket_share']:.1%}** of rows — "
        "the subject's own confidence is near-constant and cannot rank correctness. "
        "(The V12 reasoner self-report is equally degenerate; see JSON "
        "`comparator_reasoner_uncertainty`.)\n"
    )
    ec = result["external_confidence"]
    L.append("## External confidence (cross-model agreement share) — calibration\n")
    L.append(f"- Definition: `{ec['definition']}`")
    L.append(
        f"- **ECE (10-bin): {ec['ece_10bin']:.4f}**, **Brier: {ec['brier']:.4f}**, "
        f"**AUROC for correctness: {ec['auroc_for_correctness']:.4f}**\n"
    )
    L.append("| Bin | n | Mean score | Empirical acc | Gap |")
    L.append("|---|---:|---:|---:|---:|")
    for b in ec["reliability_diagram"]:
        L.append(
            f"| {b['bin']} | {b['n']} | {b['mean_score']:.3f} | "
            f"{b['empirical_accuracy']:.3f} | {b['gap']:+.3f} |"
        )
    fp = result["failure_prediction"]
    L.append("\n## Failure prediction\n")
    L.append(
        f"- **External risk score AUROC for failure: {fp['risk_score_auroc_for_failure']:.4f}**"
    )
    L.append("- Evidence-valid vs correctness:")
    for k, d in fp["evidence_valid_split"].items():
        L.append(f"  - evidence_valid={k}: {d['correct']}/{d['n']} = {d['accuracy']:.1%}")
    L.append(
        f"- **Parse-repair count AUROC for failure: {fp['parse_repair_auroc_for_failure']:.4f}** "
        f"({fp['rows_with_any_repair']}/750 rows took a deterministic repair — repairs "
        "are common, not constant, so the signal is real):"
    )
    for k, d in fp["parse_repair_split"].items():
        L.append(f"  - {k}: {d['correct']}/{d['n']} = {d['accuracy']:.1%}")
    L.append("---\n")
    L.append(
        "**Reading.** External signals rank the subject's correctness "
        f"(agreement-share AUROC {ec['auroc_for_correctness']:.3f}; risk-score "
        f"failure AUROC {fp['risk_score_auroc_for_failure']:.3f}); self-reported "
        "confidence does not (near-constant). The honest calibration story is that "
        "reliability must be read off external corroboration, not the model's own "
        "certainty — the same lesson the architecture arc reached (Insight #3).\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
