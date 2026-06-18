"""One-call vs two-call confidence paired test on frozen test450 — aggregate-only.

Confirms the validation750 finding (the variant-D gain is a prompt-WORDING effect,
not a decoupling effect) on the locked holdout. Freeze-warden gated, run once.

Predeclared: docs/experiments/gan2026/reliability/gan2026_confidence_one_vs_two_call_test450_predeclaration_2026-06-17.md

The joint-arm transform is imported BYTE-IDENTICAL from the validation driver
(`build_gan2026_confidence_one_vs_two_call_paired`) and hash-frozen before touching
test450. Both confidence signals are scored on the SAME (fresh joint) answers / SAME
error labels, so the only difference is one call vs two. Per-row data lives only in
resumable checkpoints; the readout (OUT_JSON/OUT_MD) is aggregate-only.

Usage:
    uv run python experiments/build_gan2026_confidence_one_vs_two_call_test450.py --run
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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events as hse

# The validation driver owns the joint-arm transform; import it byte-identical.
import experiments.build_gan2026_confidence_one_vs_two_call_paired as vmod

DATE = "2026-06-17"
JOINT_CKPT = rc.EXPERIMENTS / f"gan2026_confidence_one_vs_two_joint_test450_{DATE}.jsonl"
DEC_CKPT = rc.EXPERIMENTS / f"gan2026_confidence_one_vs_two_decoupled_test450_{DATE}.jsonl"
OUT_JSON = rc.EXPERIMENTS / f"gan2026_confidence_one_vs_two_call_test450_{DATE}.json"
OUT_MD = rc.EXPERIMENTS / f"gan2026_confidence_one_vs_two_call_test450_{DATE}.md"


def frozen_transform_hashes() -> dict[str, str]:
    """SHA-256 of the predeclared deterministic transforms (frozen by hash)."""
    joint_src = (
        inspect.getsource(vmod.build_joint_prompt_input)
        + inspect.getsource(vmod.parse_joint_probability)
        + inspect.getsource(vmod.arm_metrics)
        + inspect.getsource(vmod.bootstrap_auroc_diff)
        + repr(vmod.JOINT_ELICITATION_INSTRUCTIONS)
        + vmod.JOINT_PROMPT_VERSION
    )
    return {
        "joint_transform_sha256": hashlib.sha256(joint_src.encode()).hexdigest(),
        "confidence_reviewer_module_sha256": hashlib.sha256(
            inspect.getsource(cr).encode()
        ).hexdigest(),
        "readout_sha256": hashlib.sha256(
            (inspect.getsource(aggregate) + inspect.getsource(render_md)).encode()
        ).hexdigest(),
    }


def load_decoupled_done(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[int, dict[str, Any]] = {}
    for row in rc.load_jsonl(path):
        if (row.get("review") or {}).get("calibrated_confidence") is not None:
            out[int(row["source_row_index"])] = row["review"]
    return out


def checkpoint_decoupled(done: dict[int, dict[str, Any]]) -> None:
    rows = [{"source_row_index": i, "review": r} for i, r in sorted(done.items())]
    DEC_CKPT.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8"
    )


def aggregate(
    joint_pairs: list[tuple[float, bool]],
    dec_pairs: list[tuple[float, bool]],
    joint_p: list[float],
    dec_p: list[float],
    correct: list[bool],
    resid_flags: list[bool],
    *,
    n_purist_correct: int,
    n_with_comparison: int,
) -> dict[str, Any]:
    joint_m = vmod.arm_metrics(joint_pairs)
    dec_m = vmod.arm_metrics(dec_pairs)
    boot = vmod.bootstrap_auroc_diff(joint_p, dec_p, correct)

    def _resid(pvals, corr, flags, want):
        sp = [p for p, f in zip(pvals, flags) if f == want]
        sc = [c for c, f in zip(corr, flags) if f == want]
        return {
            "n": len(sp),
            "mean_p": (sum(sp) / len(sp)) if sp else float("nan"),
            "accuracy": (sum(1 for c in sc if c) / len(sc)) if sc else float("nan"),
        }

    return {
        "n_scored_paired": len(correct),
        "n_failures": sum(1 for c in correct if not c),
        "joint_arm_purist_accuracy": (n_purist_correct / n_with_comparison)
        if n_with_comparison else float("nan"),
        "joint_arm_one_call": {
            **joint_m,
            "residual": _resid(joint_p, correct, resid_flags, True),
            "nonresidual": _resid(joint_p, correct, resid_flags, False),
        },
        "decoupled_arm_two_call": {
            **dec_m,
            "residual": _resid(dec_p, correct, resid_flags, True),
            "nonresidual": _resid(dec_p, correct, resid_flags, False),
        },
        "paired_auroc_difference": boot,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", action="store_true",
                    help="REQUIRED to issue live test450 calls (freeze-warden gate).")
    args = ap.parse_args()
    if not args.run:
        ap.error("refusing to touch test450 without --run (freeze-warden gated).")

    preflight = run_single_model_preflight(SingleModelPreflightConfig(
        split="test",
        subject_artifact_path=rc.REASONER_TEST450,
        outputs_must_be_absent=(OUT_JSON, OUT_MD),
    ))
    if not preflight.ok:
        for f in preflight.failures:
            print(f"PREFLIGHT FAIL: {f}")
        ap.error("single-model preflight failed; refusing to touch test450.")
    print(f"single-model preflight OK ({len(preflight.checks)} checks passed)")

    frozen = frozen_transform_hashes()
    print(f"frozen transforms: joint {frozen['joint_transform_sha256'][:16]}… "
          f"reviewer {frozen['confidence_reviewer_module_sha256'][:16]}… "
          f"readout {frozen['readout_sha256'][:16]}…")

    records = load_records_for_split("test")
    records_by_idx = {r.source_row_index: r for r in records}

    # Phase 1 — fresh joint SE+confidence pass (resumable, 450 calls).
    raw_by_idx = vmod.run_joint_pass(records, JOINT_CKPT)

    # Phase 2 — decoupled reviewer over the joint answers (resumable, 450 calls).
    dec_done = load_decoupled_done(DEC_CKPT)
    reviewer = ConfidenceReviewer()
    print(f"decoupled pass: {len(dec_done)} cached")

    joint_pairs: list[tuple[float, bool]] = []
    dec_pairs: list[tuple[float, bool]] = []
    paired_joint_p: list[float] = []
    paired_dec_p: list[float] = []
    paired_correct: list[bool] = []
    resid_flags: list[bool] = []
    n_purist_correct = n_with_comparison = 0
    n_joint_prob_fail = n_dec_fail = n_no_comparison = 0
    n_processed = 0

    for idx, rec in records_by_idx.items():
        raw = raw_by_idx.get(idx, "")
        extraction, _norm, _errs = (
            hse.parse_structured_json(raw, note_text=rec.note_text)
            if raw else (None, [], ["not_run"])
        )
        comparison = hse._compare_to_gold(rec, extraction) if extraction else None
        if not comparison:
            n_no_comparison += 1
            continue
        correct = bool(comparison.get("purist_correct"))
        n_with_comparison += 1
        n_purist_correct += int(correct)

        final_label = extraction.selection.final_label
        final_kind = str(extraction.selection.final_kind)
        review = dec_done.get(idx)
        if review is None:
            review = reviewer.review(
                note_text=rec.note_text, final_label=final_label, final_kind=final_kind
            ).to_dict()
            dec_done[idx] = review
            n_processed += 1
            if n_processed % 25 == 0:
                checkpoint_decoupled(dec_done)
                print(f"  {n_processed} reviewer calls")

        jp, _ = vmod.parse_joint_probability(raw)
        dp = review.get("calibrated_confidence")
        if jp is None:
            n_joint_prob_fail += 1
        if dp is None:
            n_dec_fail += 1
        if jp is None or dp is None:
            continue
        jpf = jp / 100.0
        joint_pairs.append((jpf, correct))
        dec_pairs.append((float(dp), correct))
        paired_joint_p.append(jpf)
        paired_dec_p.append(float(dp))
        paired_correct.append(correct)
        resid_flags.append(vmod.is_residual(rec.note_text, rec.gold_monthly_frequency))
    checkpoint_decoupled(dec_done)

    agg = aggregate(
        joint_pairs, dec_pairs, paired_joint_p, paired_dec_p, paired_correct, resid_flags,
        n_purist_correct=n_purist_correct, n_with_comparison=n_with_comparison,
    )
    result = {
        "artifact_kind": "gan2026_confidence_one_vs_two_call_test450",
        "date": DATE,
        "dimension": "Calibration",
        "split": "test450 (frozen holdout)",
        "architecture": "fresh joint gpt-4.1-mini SE+confidence pass (paired with decoupled reviewer)",
        "claim_boundary": "frozen aggregate-only holdout readout; no row-level test inspection",
        "predeclaration": "docs/experiments/gan2026/reliability/gan2026_confidence_one_vs_two_call_test450_predeclaration_2026-06-17.md",
        "frozen_transforms": frozen,
        "model": "openai/gpt-4.1-mini",
        "n_joint_prob_parse_fail": n_joint_prob_fail,
        "n_decoupled_parse_fail": n_dec_fail,
        "n_no_comparison": n_no_comparison,
        "comparators": {
            "validation750_joint_auroc": 0.609,
            "validation750_decoupled_auroc": 0.641,
            "validation750_paired_diff_ci": [-0.032, 0.098],
            "decoupled_on_frozen_SE_validation": 0.684,
            "intrinsic_in_pass": 0.497,
            "external_corroboration": 0.781,
            "se_test450_baseline_purist_accuracy": 0.809,
        },
        "provenance": rc.provenance_block(
            subject="fresh_joint_se_mini_paired", sources=[rc.REASONER_TEST450],
        ) | {"model_calls": f"{len(raw_by_idx)} joint + {n_processed} reviewer live calls (temp 0)",
             "reviewer_version": cr.CONFIDENCE_REVIEWER_VERSION,
             "answers_shared_across_arms": True},
        "aggregate_results": agg,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    j = agg["joint_arm_one_call"]; d = agg["decoupled_arm_two_call"]; b = agg["paired_auroc_difference"]
    print(f"  joint(1-call) AUROC {j['failure_prediction_auroc']:.3f} · "
          f"decoupled(2-call) AUROC {d['failure_prediction_auroc']:.3f}")
    print(f"  paired diff (dec - joint) {b['point_diff_decoupled_minus_joint']:+.3f} "
          f"CI [{b['ci95_lo']:+.3f}, {b['ci95_hi']:+.3f}]")


def render_md(r: dict[str, Any]) -> str:
    agg = r["aggregate_results"]
    j = agg["joint_arm_one_call"]; d = agg["decoupled_arm_two_call"]
    b = agg["paired_auroc_difference"]; c = r["comparators"]; ft = r["frozen_transforms"]
    ci_excludes_zero = b["ci95_lo"] > 0 or b["ci95_hi"] < 0
    aj = j["failure_prediction_auroc"]
    L = [
        "# Confidence Elicitation — One Call vs Two on Frozen test450\n",
        "## Aggregate-Only Holdout Readout\n",
        f"Date: {r['date']} · Split: {r['split']} · arch: {r['architecture']}\n",
        f"_{r['claim_boundary']}._\n",
        f"n={agg['n_scored_paired']} paired ({agg['n_failures']} failures) · temp 0.0 · "
        f"joint-arm Purist accuracy {agg['joint_arm_purist_accuracy']:.3f} "
        f"(SE test baseline {c['se_test450_baseline_purist_accuracy']}).\n",
        f"Frozen transforms (predeclared, hashed before touching test450): joint "
        f"`{ft['joint_transform_sha256'][:16]}…`, reviewer "
        f"`{ft['confidence_reviewer_module_sha256'][:16]}…`, readout "
        f"`{ft['readout_sha256'][:16]}…`.\n",
        "**Both confidence signals scored on the SAME answers / SAME error labels "
        "(the fresh joint answers) — the only difference is one call vs two.**\n",
        "| Arm | calls | top-bucket | mean p | ECE | Brier | failure AUROC |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| **Joint (1 call, wording embedded)** | 1 | {j['top_bucket_share']:.1%} | {j['mean_p']:.3f} | "
        f"{j['ece']:.3f} | {j['brier']:.3f} | **{aj:.3f}** |",
        f"| **Decoupled reviewer (2 calls)** | 2 | {d['top_bucket_share']:.1%} | {d['mean_p']:.3f} | "
        f"{d['ece']:.3f} | {d['brier']:.3f} | **{d['failure_prediction_auroc']:.3f}** |",
        f"\n**Paired AUROC difference (decoupled − joint): "
        f"{b['point_diff_decoupled_minus_joint']:+.3f}, 95% CI "
        f"[{b['ci95_lo']:+.3f}, {b['ci95_hi']:+.3f}]** ({b['reps_used']} bootstrap reps).\n",
        f"Comparators — validation750: joint {c['validation750_joint_auroc']}, decoupled "
        f"{c['validation750_decoupled_auroc']}, paired-diff CI {c['validation750_paired_diff_ci']}; "
        f"intrinsic in-pass {c['intrinsic_in_pass']}; external corroboration "
        f"{c['external_corroboration']}.\n",
        "## Verdict\n",
    ]
    if ci_excludes_zero and b["point_diff_decoupled_minus_joint"] > 0:
        L.append(
            f"**Does not replicate.** On the holdout the paired difference CI excludes 0 in "
            f"favour of the decoupled reviewer (joint {aj:.3f} vs decoupled "
            f"{d['failure_prediction_auroc']:.3f}); the extra call earns its cost on test.\n"
        )
    elif aj > 0.5:
        L.append(
            f"**Replicates (H_wording).** The joint one-call self-confidence ranks holdout "
            f"errors at AUROC {aj:.3f}, within the bootstrap CI of the decoupled reviewer "
            "(paired-difference CI includes 0). As on validation, the discrimination is a "
            "wording effect, not a decoupling effect — the second call is removable.\n"
        )
    else:
        L.append(
            f"**Neither.** Both arms collapse toward chance on the holdout (joint {aj:.3f}); "
            "the self-signal does not transfer to test at this scale.\n"
        )
    return "\n".join(L)


if __name__ == "__main__":
    main()
