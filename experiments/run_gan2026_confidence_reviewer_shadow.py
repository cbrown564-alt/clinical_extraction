"""Production-shape shadow run of the variant-D confidence reviewer.

Drives the REAL SE selection pass (`hybrid_structured_events.run_split`) with the
decoupled `ConfidenceReviewer` enabled, so the reviewer fires through the production
hook and stamps `confidence_review` per row. To avoid re-spending on the SE answers,
the saved validation750 SE outputs are reused (0 SE calls); only the reviewer calls
are live. This doubles as the validation750 scale-confirmation of the pilot's 0.755.

Shadow = gates nothing; the SE label/score path is untouched. We then score the
stamped `calibrated_confidence` against the SE pass's own `comparison.purist_correct`.

Resumable: prior reviewer verdicts are reused per source_row_index, so a re-run only
issues the still-pending (or previously errored) reviewer calls.

Usage:
    uv run python experiments/run_gan2026_confidence_reviewer_shadow.py --pilot
    uv run python experiments/run_gan2026_confidence_reviewer_shadow.py --full
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.confidence_reviewer import (
    CONFIDENCE_REVIEWER_VERSION,
    ConfidenceReviewer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.replay_io import (
    load_raw_outputs_by_source_index,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    classify_boundary_families,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    run_split,
)

DATE = "2026-06-17"
MODEL = "openai/gpt-4.1-mini"
SPLIT_MANIFEST = "gan2026_split_v1"
PILOT_N = 160


def is_residual(note_text: str, gold_pm: float | None) -> bool:
    band = boundary_band(gold_pm)
    fams = classify_boundary_families(note_text=note_text, gold_per_month=gold_pm)
    return band == "band_unknown" or "seizure_free_duration" in fams


def load_prior_reviews(path: Path) -> dict[int, dict[str, Any]]:
    """Resume: reuse prior reviewer verdicts that succeeded; retry None/errored ones."""
    if not path.exists():
        return {}
    out: dict[int, dict[str, Any]] = {}
    for row in rc.load_jsonl(path):
        review = row.get("confidence_review") or {}
        if review.get("calibrated_confidence") is not None:
            out[int(row["source_row_index"])] = review
    return out


def analyse(rows: list[dict[str, Any]], records_by_idx, out_json: Path, out_md: Path,
            *, tag: str) -> dict[str, Any]:
    pairs: list[tuple[float, bool]] = []
    risks: list[float] = []
    failures: list[bool] = []
    p_values: list[float] = []
    resid_p, resid_c, nonresid_p, nonresid_c = [], [], [], []
    # intrinsic in-pass baseline (selection.confidence) on the SAME rows
    intrinsic_map = {"high": 1.0, "medium": 0.5, "low": 0.0}
    intr_risks, intr_failures = [], []
    n_review_fail = n_no_comparison = 0

    for row in rows:
        idx = row["source_row_index"]
        comp = row.get("comparison")
        review = row.get("confidence_review") or {}
        if comp is None:
            n_no_comparison += 1
            continue
        correct = bool(comp.get("purist_correct"))
        # intrinsic baseline
        sel = ((row.get("structured_record") or {}).get("selection") or {})
        intr = intrinsic_map.get(sel.get("confidence"))
        if intr is not None:
            intr_risks.append(1.0 - intr)
            intr_failures.append(not correct)
        # variant-D reviewer
        p = review.get("calibrated_confidence")
        if p is None:
            n_review_fail += 1
            continue
        pairs.append((p, correct))
        risks.append(1.0 - p)
        failures.append(not correct)
        p_values.append(p)
        rec = records_by_idx[idx]
        if is_residual(rec.note_text, rec.gold_monthly_frequency):
            resid_p.append(p); resid_c.append(correct)
        else:
            nonresid_p.append(p); nonresid_c.append(correct)

    ece, table = rc.expected_calibration_error(pairs)
    n = len(p_values)
    mean_p = sum(p_values) / n if n else float("nan")
    std_p = (sum((x - mean_p) ** 2 for x in p_values) / n) ** 0.5 if n else float("nan")
    top_bucket = sum(1 for x in p_values if x >= 0.9)

    def _mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")

    result = {
        "artifact_kind": "gan2026_confidence_reviewer_shadow",
        "date": DATE,
        "mode": tag,
        "dimension": "Calibration",
        "model": MODEL,
        "confidence_reviewer_version": CONFIDENCE_REVIEWER_VERSION,
        "host": "hybrid_structured_events.run_split (SE selection pass, reused SE outputs)",
        "shadow": True,
        "n_rows": len(rows),
        "n_scored": n,
        "n_review_parse_fail": n_review_fail,
        "n_no_comparison": n_no_comparison,
        "n_failures": sum(failures),
        "external_signal_comparator_auroc": 0.781,
        "variant_D": {
            "spread": {
                "mean_calibrated_confidence": mean_p,
                "std": std_p,
                "distinct_values": len(set(p_values)),
                "top_bucket_share": top_bucket / n if n else float("nan"),
            },
            "calibration": {"ece": ece, "brier": rc.brier_score(pairs), "reliability_table": table},
            "discrimination": {"failure_prediction_auroc": rc.auroc(risks, failures)},
            "residual_sensitivity": {
                "residual_n": len(resid_p),
                "residual_mean_p": _mean(resid_p),
                "residual_accuracy": _mean([1.0 if c else 0.0 for c in resid_c]),
                "nonresidual_mean_p": _mean(nonresid_p),
                "nonresidual_accuracy": _mean([1.0 if c else 0.0 for c in nonresid_c]),
            },
        },
        "intrinsic_in_pass_baseline": {
            "field": "structured_record.selection.confidence",
            "n": len(intr_failures),
            "failure_prediction_auroc": rc.auroc(intr_risks, intr_failures),
            "top_bucket_share_high": (
                sum(1 for r in intr_risks if r == 0.0) / len(intr_risks) if intr_risks else float("nan")
            ),
            "note": "in-pass joint self-confidence on the SAME rows; the degenerate signal D sits beside.",
        },
        "provenance": {"se_calls": 0, "reviewer_calls": "live (one per scored row)",
                       "production_path_modified": False},
    }
    out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    out_md.write_text(render_md(result), encoding="utf-8")
    return result


def render_md(r: dict[str, Any]) -> str:
    d = r["variant_D"]; sp = d["spread"]; di = d["discrimination"]; rs = d["residual_sensitivity"]
    b = r["intrinsic_in_pass_baseline"]
    L = [
        f"# Confidence-Reviewer Shadow Run ({r['mode']})\n",
        f"Date: {r['date']} · Host: {r['host']} · reviewer `{r['confidence_reviewer_version']}` "
        f"· SE calls 0 (reused), reviewer live · n={r['n_rows']} ({r['n_scored']} scored, "
        f"{r['n_failures']} failures)\n",
        "**Shadow stage — gates nothing; SE label/score path untouched.** "
        "`calibrated_confidence` scored against the SE pass's own `purist_correct`.\n",
        "| Signal | top-bucket | mean p | ECE | Brier | failure AUROC |",
        "|---|---:|---:|---:|---:|---:|",
        f"| **variant D (decoupled reviewer)** | {sp['top_bucket_share']:.1%} | "
        f"{sp['mean_calibrated_confidence']:.3f} | {d['calibration']['ece']:.3f} | "
        f"{d['calibration']['brier']:.3f} | **{di['failure_prediction_auroc']:.3f}** |",
        f"| intrinsic in-pass `selection.confidence` | {b['top_bucket_share_high']:.1%} | — | — | — | "
        f"{b['failure_prediction_auroc']:.3f} |",
        f"\nExternal-corroboration comparator AUROC (P0.3) = {r['external_signal_comparator_auroc']}.\n",
        "## Residual sensitivity\n",
        f"- Residual (n={rs['residual_n']}): mean p {rs['residual_mean_p']:.3f}, acc {rs['residual_accuracy']:.1%}",
        f"- Non-residual: mean p {rs['nonresidual_mean_p']:.3f}, acc {rs['nonresidual_accuracy']:.1%}\n",
        "## Reading\n",
    ]
    auc = di["failure_prediction_auroc"]
    if isinstance(auc, float) and auc == auc and auc >= 0.65:
        L.append(f"In production shape (hosted in the SE pass, scored on SE answers), the decoupled "
                 f"variant-D reviewer ranks errors at AUROC **{auc:.3f}** vs the in-pass joint "
                 f"field's {b['failure_prediction_auroc']:.3f} on the same rows — the discrimination "
                 "survives integration. Still shadow: it complements external corroboration "
                 f"({r['external_signal_comparator_auroc']}) and is not yet a gate.\n")
    else:
        L.append(f"In production shape the reviewer's discrimination is AUROC **{auc:.3f}** "
                 f"(in-pass baseline {b['failure_prediction_auroc']:.3f}). Weaker than the pilot — "
                 "do not gate; investigate the SE-answer vs v0_reference-answer difference.\n")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot", action="store_true", help=f"first {PILOT_N} validation rows")
    ap.add_argument("--full", action="store_true", help="full validation750")
    args = ap.parse_args()
    if not (args.pilot or args.full):
        ap.error("choose --pilot or --full")

    records_all = load_records_for_split("validation")
    records = records_all[:PILOT_N] if args.pilot else records_all
    tag = f"pilot{len(records)}" if args.pilot else "validation750"
    records_by_idx = {r.source_row_index: r for r in records}

    reuse_se = load_raw_outputs_by_source_index(rc.SE_MINI_VALIDATION750)
    have = sum(1 for r in records if r.source_row_index in reuse_se)
    print(f"tag={tag} · {len(records)} rows · {have} SE outputs reused (0 SE calls)")

    rows_path = rc.EXPERIMENTS / f"gan2026_confidence_reviewer_shadow_{tag}_{DATE}.jsonl"
    prior = load_prior_reviews(rows_path)
    print(f"resume: {len(prior)} prior reviewer verdicts cached")

    rows, _meta = run_split(
        records,
        split="validation",
        split_manifest=SPLIT_MANIFEST,
        model=MODEL,
        temperature=0.0,
        max_tokens=1200,
        mode="live",
        dspy_cache=False,
        reuse_raw_outputs=reuse_se,
        reuse_source=str(rc.SE_MINI_VALIDATION750),
        confidence_reviewer=ConfidenceReviewer(),
        reuse_confidence_reviews=prior,
        progress_every=25,
        checkpoint_jsonl_path=rows_path,  # crash-safe: reviewer verdicts persist every 25 rows
    )
    rows_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8"
    )

    out_json = rc.EXPERIMENTS / f"gan2026_confidence_reviewer_shadow_{tag}_{DATE}.json"
    out_md = rc.EXPERIMENTS / f"gan2026_confidence_reviewer_shadow_{tag}_{DATE}.md"
    result = analyse(rows, records_by_idx, out_json, out_md, tag=tag)
    print(f"wrote {out_json}")
    d = result["variant_D"]
    print(f"  variant D: top-bucket {d['spread']['top_bucket_share']:.1%} · "
          f"AUROC {d['discrimination']['failure_prediction_auroc']:.3f} · "
          f"intrinsic baseline AUROC {result['intrinsic_in_pass_baseline']['failure_prediction_auroc']:.3f}")


if __name__ == "__main__":
    main()
