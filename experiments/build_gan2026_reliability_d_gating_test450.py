"""Variant-D gating on frozen test450 — aggregate-only, freeze-warden gated.

Answers: is the variant-D calibrated confidence practically useful as an abstention
gate on the primary single gpt-4.1-mini architecture, on the LOCKED holdout?

Predeclared in docs/experiments/gan2026/reliability/gan2026_d_gating_test450_predeclaration_2026-06-17.md.

This is a LIVE holdout model run (one reviewer call per test450 row), so it is
freeze-warden gated. It reads the canonical single-SE-mini answers from the
`v0_reference` layer of the test450 reasoner artifact (decision 0018) — no new SE call.
Per-row correctness is read INTERNALLY only to form aggregates; nothing per-row leaves
the readout (no source_row_index / transition_vs_v0 / score_layers markers).

Resumable: reviewer verdicts are checkpointed per source_row_index and reused.

Usage:
    # default refuses to touch test450 unless explicitly authorised:
    uv run python experiments/build_gan2026_reliability_d_gating_test450.py --run
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import confidence_reviewer as cr
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.confidence_reviewer import (
    ConfidenceReviewer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_preflight_single_model import (
    SingleModelPreflightConfig,
    run_single_model_preflight,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split

DATE = "2026-06-17"
COVERAGES = (0.95, 0.90, 0.80, 0.70, 0.50)
SAMPLES = rc.EXPERIMENTS / f"gan2026_reliability_d_gating_test450_samples_{DATE}.jsonl"
OUT_JSON = rc.EXPERIMENTS / f"gan2026_reliability_d_gating_test450_{DATE}.json"
OUT_MD = rc.EXPERIMENTS / f"gan2026_reliability_d_gating_test450_{DATE}.md"


def frozen_transform_hashes() -> dict[str, str]:
    """SHA-256 of the predeclared deterministic transforms (frozen by hash)."""
    reviewer_src = inspect.getsource(cr)
    gating_src = (
        inspect.getsource(gating_table) + inspect.getsource(failure_auroc) + repr(COVERAGES)
    )
    return {
        "confidence_reviewer_module_sha256": hashlib.sha256(reviewer_src.encode()).hexdigest(),
        "gating_readout_sha256": hashlib.sha256(gating_src.encode()).hexdigest(),
    }


def gating_table(risk: list[float], correct: list[bool]) -> list[dict[str, Any]]:
    n = len(risk)
    base_err = sum(1 for c in correct if not c) / n
    total_errors = sum(1 for c in correct if not c)
    order = sorted(range(n), key=lambda i: risk[i])  # cover low-risk first
    out: list[dict[str, Any]] = []
    for cov in COVERAGES:
        k = max(1, round(cov * n))
        covered, abstained = order[:k], order[k:]
        cov_correct = sum(1 for i in covered if correct[i])
        abst_err = sum(1 for i in abstained if not correct[i])
        lo, hi = rc.wilson_interval(cov_correct, len(covered))
        plo, phi = (
            rc.wilson_interval(abst_err, len(abstained))
            if abstained
            else (float("nan"), float("nan"))
        )
        out.append(
            {
                "coverage": len(covered) / n,
                "covered": len(covered),
                "abstained": len(abstained),
                "selective_accuracy": cov_correct / len(covered),
                "selective_accuracy_ci95": [lo, hi],
                "abstention_precision": (abst_err / len(abstained)) if abstained else float("nan"),
                "abstention_precision_ci95": [plo, phi],
                "random_abstention_precision": base_err,
                "abstention_lift_over_random": (abst_err / len(abstained) - base_err)
                if abstained
                else float("nan"),
                "errors_shed": abst_err,
                "errors_shed_frac_of_total": (abst_err / total_errors)
                if total_errors
                else float("nan"),
            }
        )
    return out


def failure_auroc(risk: list[float], correct: list[bool]) -> float:
    return rc.auroc(risk, [not c for c in correct])


def load_done(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[int, dict[str, Any]] = {}
    for row in rc.load_jsonl(path):
        if (row.get("review") or {}).get("calibrated_confidence") is not None:
            out[int(row["source_row_index"])] = row["review"]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--run",
        action="store_true",
        help="REQUIRED to issue live test450 reviewer calls (freeze-warden gate).",
    )
    args = ap.parse_args()
    if not args.run:
        ap.error("refusing to touch test450 without --run (freeze-warden gated).")

    # First-class single-model integrity preflight (fail-closed gate). The final
    # aggregate outputs must be absent (a completed prior run); the resumable per-row
    # samples checkpoint is allowed to exist so resume works.
    preflight = run_single_model_preflight(
        SingleModelPreflightConfig(
            split="test",
            subject_artifact_path=rc.REASONER_TEST450,
            outputs_must_be_absent=(OUT_JSON, OUT_MD),
        )
    )
    if not preflight.ok:
        for f in preflight.failures:
            print(f"PREFLIGHT FAIL: {f}")
        ap.error("single-model preflight failed; refusing to touch test450.")
    print(f"single-model preflight OK ({len(preflight.checks)} checks passed)")

    # Canonical test450 SE answers (v0_reference) + notes joined by source_row_index.
    rsn = {r["source_row_index"]: r for r in rc.load_jsonl(rc.REASONER_TEST450)}
    records = {r.source_row_index: r for r in load_records_for_split("test")}

    done = load_done(SAMPLES)
    reviewer = ConfidenceReviewer()
    risk: list[float] = []
    correct: list[bool] = []
    pending = [idx for idx in rsn if idx not in done]
    print(f"test450: {len(rsn)} rows · {len(done)} cached · {len(pending)} pending reviewer calls")

    n_processed = 0
    for idx, row in rsn.items():
        rec = records.get(idx)
        if rec is None:
            continue
        review = done.get(idx)
        if review is None:
            final_label = rc.subject_final_label(row)
            final_kind = rc.subject_final_kind(row)
            review = reviewer.review(
                note_text=rec.note_text, final_label=final_label, final_kind=str(final_kind)
            ).to_dict()
            done[idx] = review
            n_processed += 1
            if n_processed % 25 == 0:
                _checkpoint(done)
                print(f"  {n_processed}/{len(pending)} reviewer calls")
        p = review.get("calibrated_confidence")
        if p is None:
            continue
        risk.append(1.0 - float(p))
        correct.append(rc.subject_purist_correct(row))
    _checkpoint(done)

    n = len(correct)
    base_correct = sum(1 for c in correct if c)
    lo_b, hi_b = rc.wilson_interval(base_correct, n)
    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_d_gating_test450",
        "date": DATE,
        "dimensions": ["Calibration", "Abstention"],
        "split": "test450 (frozen holdout)",
        "architecture": "single gpt-4.1-mini SE pass (primary)",
        "claim_boundary": "frozen aggregate-only holdout readout; no row-level test inspection",
        "predeclaration": "docs/experiments/gan2026/reliability/gan2026_d_gating_test450_predeclaration_2026-06-17.md",
        "frozen_transforms": frozen_transform_hashes(),
        "asymmetry_note": (
            "Single-model self-signal computed live identically on both splits — NO "
            "degradation (unlike P1.1's external score). Apples-to-apples holdout test."
        ),
        "provenance": rc.provenance_block(
            subject="single_se_mini_v0_reference",
            sources=[rc.REASONER_TEST450],
        )
        | {
            "model_calls": f"{n_processed} live gpt-4.1-mini reviewer calls (temp 0)",
            "reviewer_version": cr.CONFIDENCE_REVIEWER_VERSION,
        },
        "aggregate_results": {
            "rows_scored": n,
            "base_accuracy": base_correct / n,
            "base_accuracy_ci95": [lo_b, hi_b],
            "base_error_rate": 1 - base_correct / n,
            "d_failure_auroc": failure_auroc(risk, correct),
            "gating_operating_points": gating_table(risk, correct),
        },
        "validation_comparator": {
            "note": "[comparator: validation750] base acc 0.884, AUROC 0.684; "
            "90% cov selective acc 0.905, abstention precision 0.307 vs random 0.116.",
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    ar = result["aggregate_results"]
    print(f"  base acc {ar['base_accuracy']:.3f} · D AUROC {ar['d_failure_auroc']:.3f}")
    for x in ar["gating_operating_points"]:
        print(
            f"  cov {x['coverage']:.0%}: sel acc {x['selective_accuracy']:.3f} · "
            f"abst prec {x['abstention_precision']:.3f} vs random {x['random_abstention_precision']:.3f}"
        )


def _checkpoint(done: dict[int, dict[str, Any]]) -> None:
    rows = [{"source_row_index": idx, "review": rev} for idx, rev in sorted(done.items())]
    SAMPLES.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8"
    )


def render_md(result: dict[str, Any]) -> str:
    ar = result["aggregate_results"]
    ft = result["frozen_transforms"]
    L = [
        "# Variant-D Gating on Frozen test450\n",
        "## Aggregate-Only Holdout Readout\n",
        f"Date: {result['date']} · Split: {result['split']} · arch: {result['architecture']}\n",
        f"_{result['claim_boundary']}._\n",
        f"**Asymmetry.** {result['asymmetry_note']}\n",
        f"Frozen transforms (predeclared, hashed before touching test450): reviewer "
        f"`{ft['confidence_reviewer_module_sha256'][:16]}…`, readout "
        f"`{ft['gating_readout_sha256'][:16]}…`.\n",
        f"- Base accuracy (no gate): **{ar['base_accuracy']:.1%}** "
        f"(CI {ar['base_accuracy_ci95'][0]:.1%}–{ar['base_accuracy_ci95'][1]:.1%}), "
        f"error {ar['base_error_rate']:.1%}.",
        f"- D failure-prediction AUROC: **{ar['d_failure_auroc']:.3f}**.\n",
        "## Gating operating points\n",
        "| Coverage | Selective acc | 95% CI | Abstention precision | 95% CI | vs random | Errors shed |",
        "|---:|---:|:--|---:|:--|---:|---:|",
    ]
    for x in ar["gating_operating_points"]:
        L.append(
            f"| {x['coverage']:.0%} | {x['selective_accuracy']:.1%} | "
            f"{x['selective_accuracy_ci95'][0]:.1%}–{x['selective_accuracy_ci95'][1]:.1%} | "
            f"{x['abstention_precision']:.1%} | "
            f"{x['abstention_precision_ci95'][0]:.1%}–{x['abstention_precision_ci95'][1]:.1%} | "
            f"{x['abstention_lift_over_random']:+.1%} | {x['errors_shed']} |"
        )
    L.append(f"\n{result['validation_comparator']['note']}\n")
    L.append("---\n")
    auc = ar["d_failure_auroc"]
    L.append(
        f"**Reading.** On the locked holdout the single-model variant-D gate ranks errors at "
        f"AUROC {auc:.3f}. Judge practical usefulness against the predeclared criterion: "
        "AUROC CI above chance, abstention precision at 90% coverage above the random bar "
        "(base error rate), and a positive monotone selective-accuracy lift. The val→test "
        "movement is itself the finding.\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
