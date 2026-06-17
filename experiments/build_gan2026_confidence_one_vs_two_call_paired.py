"""Paired test: one-call (joint) vs two-call (decoupled) variant-D confidence.

Tests whether variant D's failure-prediction discrimination (validation750 AUROC
0.684 vs 0.497 intrinsic) comes from the **decoupled second call** or simply from
the **changed prompt wording** (the failure-mode priming).

Design (see docs/research/gan2026_confidence_one_vs_two_call_predeclaration_2026-06-17.md):
both confidence signals are scored against the SAME answers / SAME error labels —

  * JOINT arm (1 call/row): a single SE extraction pass whose prompt embeds the
    verbatim variant-D priming and emits `selection.answer_probability_correct`
    in the same JSON as the answer (the model sees its own rationale = no decoupling).
  * DECOUPLED arm (1 extra call/row): the existing ConfidenceReviewer run over the
    JOINT arm's own answers (note + stated answer only, rationale-blind).

The joint answers are the canonical answer set for both arms: the decoupled arm
reuses the joint raw outputs through `run_split` (0 SE calls; only reviewer calls
are live), guaranteeing identical `purist_correct`. Difference in AUROC is then
attributable to one-call-vs-two with the priming wording held constant.

Resumable (core/run_resume.py): the joint pass checkpoints per source_row_index;
the decoupled pass reuses prior reviewer verdicts.

Usage:
    uv run python experiments/build_gan2026_confidence_one_vs_two_call_paired.py --pilot
    uv run python experiments/build_gan2026_confidence_one_vs_two_call_paired.py --full
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.core import run_resume
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.confidence_reviewer import (
    CONFIDENCE_REVIEWER_VERSION,
    ConfidenceReviewer,
    VARIANT_D_INSTRUCTIONS,
    _clamp,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    classify_boundary_families,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events as hse
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

DATE = "2026-06-17"
MODEL = "openai/gpt-4.1-mini"
SPLIT_MANIFEST = "gan2026_split_v1"
PILOT_N = 160
JOINT_PROMPT_VERSION = "gan2026_joint_se_plus_variantD_confidence_v1"

# The joint-arm elicitation instructions: the SAME variant-D priming, re-voiced for
# a self-rating in the same call (the model rates its own chosen answer). The
# failure-mode-priming sentence (VARIANT_D_INSTRUCTIONS[2]) is carried VERBATIM so
# the wording is held constant against the decoupled reviewer.
JOINT_ELICITATION_INSTRUCTIONS: tuple[str, ...] = (
    "After choosing your final answer, also estimate the probability (an integer "
    "0-100) that YOUR final_label is the CORRECT purist seizure-frequency category.",
    VARIANT_D_INSTRUCTIONS[2],  # the verbatim unknown<->rate over-read priming
    "Decide how exposed YOUR answer is to that error, then report the probability "
    "that your final answer is correct.",
    "Put this probability in selection.answer_probability_correct (integer 0-100) "
    "and a one-sentence selection.answer_probability_reason.",
)


class JointExtractorWithConfidenceSignature(dspy.Signature):
    """Extract source-near seizure-frequency events, choose a final answer, AND
    self-rate that answer's probability of being correct — all in one call.

    Return exactly one JSON object with keys events and selection. The selection
    block additionally includes answer_probability_correct (integer 0-100) and a
    one-sentence answer_probability_reason.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical note, task instructions, and output schemas."
    )
    structured_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object with events and selection. selection also carries "
            "answer_probability_correct (0-100) and answer_probability_reason."
        )
    )


def build_joint_prompt_input(record) -> str:
    """Production SE prompt + appended variant-D self-confidence elicitation."""
    payload = json.loads(hse.build_prompt_input(record))
    payload["prompt_version"] = JOINT_PROMPT_VERSION
    payload["instructions"] = list(payload["instructions"]) + list(JOINT_ELICITATION_INSTRUCTIONS)
    payload["selection_schema"]["answer_probability_correct"] = (
        "integer 0-100: probability your final_label is the correct purist category"
    )
    payload["selection_schema"]["answer_probability_reason"] = "one short sentence"
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_joint_probability(raw: str) -> tuple[int | None, str | None]:
    """Pull selection.answer_probability_correct from the joint raw output."""
    if not raw or not raw.strip():
        return None, None
    try:
        obj = json.loads(hse._extract_json_object(raw))
    except json.JSONDecodeError:
        return None, None
    sel = obj.get("selection")
    if not isinstance(sel, dict):
        return None, None
    prob = sel.get("answer_probability_correct")
    try:
        return _clamp(int(round(float(prob)))), sel.get("answer_probability_reason")
    except (TypeError, ValueError):
        return None, sel.get("answer_probability_reason")


def is_residual(note_text: str, gold_pm: float | None) -> bool:
    band = boundary_band(gold_pm)
    fams = classify_boundary_families(note_text=note_text, gold_per_month=gold_pm)
    return band == "band_unknown" or "seizure_free_duration" in fams


# ── Phase 1: joint pass (resumable per source_row_index) ────────────────────────

def run_joint_pass(records, checkpoint: Path) -> dict[int, str]:
    """Live joint SE+confidence pass; returns {source_row_index: raw_output}."""
    done_rows, completed = run_resume.read_completed(checkpoint, key="source_row_index")
    pending = run_resume.pending_items(
        records, completed, key_of=lambda r: str(r.source_row_index)
    )
    print(f"joint pass: {len(records)} rows · {len(completed)} cached · {len(pending)} pending")
    if pending:
        lm = build_dspy_lm(MODEL, temperature=0.0, max_tokens=1200, cache=False, num_retries=2,
                           timeout=120)
        predict = dspy.Predict(JointExtractorWithConfidenceSignature)
        rows = list(done_rows)
        for i, record in enumerate(pending, 1):
            prompt = build_joint_prompt_input(record)
            try:
                with dspy.context(lm=lm):
                    raw = str(predict(prompt_input_json=prompt).structured_json)
                err = None
            except Exception as exc:  # pragma: no cover - live API only
                raw, err = "", f"{type(exc).__name__}: {exc}"
            rows.append({"source_row_index": record.source_row_index, "raw_output": raw,
                         "call_error": err})
            if i % 25 == 0 or i == len(pending):
                ordered = run_resume.merge_rows(
                    rows, [str(r.source_row_index) for r in records], key="source_row_index"
                )
                checkpoint.write_text(
                    "\n".join(json.dumps(r, ensure_ascii=False) for r in ordered) + "\n",
                    encoding="utf-8",
                )
                print(f"  joint {i}/{len(pending)} done")
        done_rows, _ = run_resume.read_completed(checkpoint, key="source_row_index")
    return {int(r["source_row_index"]): r.get("raw_output") or "" for r in done_rows}


# ── Phase 2: decoupled reviewer over the joint answers ──────────────────────────

def load_prior_reviews(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[int, dict[str, Any]] = {}
    for row in rc.load_jsonl(path):
        review = row.get("confidence_review") or {}
        if review.get("calibrated_confidence") is not None:
            out[int(row["source_row_index"])] = review
    return out


# ── Statistics ──────────────────────────────────────────────────────────────────

def arm_metrics(pairs: list[tuple[float, bool]]) -> dict[str, Any]:
    """pairs = (p_correct, is_correct). Risk = 1-p; failure = not correct."""
    risks = [1.0 - p for p, _ in pairs]
    failures = [not c for _, c in pairs]
    ps = [p for p, _ in pairs]
    n = len(ps)
    mean_p = sum(ps) / n if n else float("nan")
    std_p = (sum((x - mean_p) ** 2 for x in ps) / n) ** 0.5 if n else float("nan")
    ece, table = rc.expected_calibration_error(pairs)
    return {
        "n": n,
        "failure_prediction_auroc": rc.auroc(risks, failures),
        "ece": ece,
        "brier": rc.brier_score(pairs),
        "mean_p": mean_p,
        "std_p": std_p,
        "distinct_values": len(set(ps)),
        "top_bucket_share": (sum(1 for x in ps if x >= 0.9) / n) if n else float("nan"),
        "reliability_table": table,
    }


def bootstrap_auroc_diff(
    joint_p: list[float], dec_p: list[float], correct: list[bool], *, reps: int = 1000, seed: int = 7
) -> dict[str, float]:
    """Paired row-bootstrap of (AUROC_decoupled - AUROC_joint). Same resampled rows
    for both arms each rep, so the difference CI is paired."""
    rng = random.Random(seed)
    n = len(correct)
    j_risk = [1.0 - p for p in joint_p]
    d_risk = [1.0 - p for p in dec_p]
    fail = [not c for c in correct]
    diffs: list[float] = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        jr = [j_risk[i] for i in idx]
        dr = [d_risk[i] for i in idx]
        fl = [fail[i] for i in idx]
        a_j = rc.auroc(jr, fl)
        a_d = rc.auroc(dr, fl)
        if a_j == a_j and a_d == a_d:  # skip degenerate (single-class) resamples
            diffs.append(a_d - a_j)
    diffs.sort()
    lo = diffs[int(0.025 * len(diffs))]
    hi = diffs[int(0.975 * len(diffs))]
    point = rc.auroc(d_risk, fail) - rc.auroc(j_risk, fail)
    return {"point_diff_decoupled_minus_joint": point, "ci95_lo": lo, "ci95_hi": hi,
            "reps_used": len(diffs)}


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

    joint_ckpt = rc.EXPERIMENTS / f"gan2026_confidence_one_vs_two_joint_{tag}_{DATE}.jsonl"
    raw_by_idx = run_joint_pass(records, joint_ckpt)

    # Phase 2: decoupled reviewer over the joint answers (reuse joint raw => 0 SE calls).
    dec_ckpt = rc.EXPERIMENTS / f"gan2026_confidence_one_vs_two_decoupled_{tag}_{DATE}.jsonl"
    prior = load_prior_reviews(dec_ckpt)
    print(f"decoupled pass: {len(prior)} prior reviewer verdicts cached")
    rows, _meta = hse.run_split(
        records,
        split="validation",
        split_manifest=SPLIT_MANIFEST,
        model=MODEL,
        temperature=0.0,
        max_tokens=1200,
        mode="live",
        dspy_cache=False,
        reuse_raw_outputs=raw_by_idx,
        reuse_source=str(joint_ckpt),
        confidence_reviewer=ConfidenceReviewer(),
        reuse_confidence_reviews=prior,
        progress_every=25,
        checkpoint_jsonl_path=dec_ckpt,
    )
    dec_ckpt.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8"
    )

    # Join the two confidence signals on the same answers / same error labels.
    joint_pairs: list[tuple[float, bool]] = []
    dec_pairs: list[tuple[float, bool]] = []
    paired_joint_p: list[float] = []
    paired_dec_p: list[float] = []
    paired_correct: list[bool] = []
    resid_flags: list[bool] = []
    n_joint_prob_fail = n_dec_fail = n_no_comparison = 0
    n_purist_correct = 0

    for row in rows:
        idx = row["source_row_index"]
        comp = row.get("comparison")
        if comp is None:
            n_no_comparison += 1
            continue
        correct = bool(comp.get("purist_correct"))
        n_purist_correct += int(correct)
        jp, _ = parse_joint_probability(raw_by_idx.get(idx, ""))
        review = row.get("confidence_review") or {}
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
        rec = records_by_idx[idx]
        resid_flags.append(is_residual(rec.note_text, rec.gold_monthly_frequency))

    joint_m = arm_metrics(joint_pairs)
    dec_m = arm_metrics(dec_pairs)
    boot = bootstrap_auroc_diff(paired_joint_p, paired_dec_p, paired_correct)

    def _resid(pvals, corr, flags, want):
        sel_p = [p for p, f in zip(pvals, flags) if f == want]
        sel_c = [c for c, f in zip(corr, flags) if f == want]
        mp = sum(sel_p) / len(sel_p) if sel_p else float("nan")
        acc = sum(1 for c in sel_c if c) / len(sel_c) if sel_c else float("nan")
        return {"n": len(sel_p), "mean_p": mp, "accuracy": acc}

    n_scored = len(paired_correct)
    result = {
        "artifact_kind": "gan2026_confidence_one_vs_two_call_paired",
        "date": DATE,
        "mode": tag,
        "dimension": "Calibration",
        "model": MODEL,
        "question": "Does variant-D's discrimination come from the decoupled call or the prompt wording?",
        "joint_prompt_version": JOINT_PROMPT_VERSION,
        "confidence_reviewer_version": CONFIDENCE_REVIEWER_VERSION,
        "n_rows": len(rows),
        "n_scored_paired": n_scored,
        "n_joint_prob_parse_fail": n_joint_prob_fail,
        "n_decoupled_parse_fail": n_dec_fail,
        "n_no_comparison": n_no_comparison,
        "n_failures": sum(1 for c in paired_correct if not c),
        "joint_arm_purist_accuracy": (n_purist_correct / (len(rows) - n_no_comparison))
        if (len(rows) - n_no_comparison) else float("nan"),
        "se_baseline_purist_accuracy_comparator": 0.881,
        "external_signal_comparator_auroc": 0.781,
        "decoupled_on_frozen_SE_comparator_auroc": 0.684,
        "intrinsic_in_pass_comparator_auroc": 0.497,
        "joint_arm_one_call": {
            **joint_m,
            "residual": _resid(paired_joint_p, paired_correct, resid_flags, True),
            "nonresidual": _resid(paired_joint_p, paired_correct, resid_flags, False),
        },
        "decoupled_arm_two_call": {
            **dec_m,
            "residual": _resid(paired_dec_p, paired_correct, resid_flags, True),
            "nonresidual": _resid(paired_dec_p, paired_correct, resid_flags, False),
        },
        "paired_auroc_difference": boot,
        "provenance": {
            "se_calls": "live joint pass (1/row)",
            "reviewer_calls": "live (1/row over joint answers)",
            "answers_shared_across_arms": True,
            "predeclaration": "docs/research/gan2026_confidence_one_vs_two_call_predeclaration_2026-06-17.md",
        },
    }
    out_json = rc.EXPERIMENTS / f"gan2026_confidence_one_vs_two_call_{tag}_{DATE}.json"
    out_md = rc.EXPERIMENTS / f"gan2026_confidence_one_vs_two_call_{tag}_{DATE}.md"
    out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    out_md.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {out_json}")
    print(f"  joint(1-call) AUROC {joint_m['failure_prediction_auroc']:.3f} · "
          f"decoupled(2-call) AUROC {dec_m['failure_prediction_auroc']:.3f}")
    print(f"  paired diff (dec - joint) {boot['point_diff_decoupled_minus_joint']:+.3f} "
          f"CI [{boot['ci95_lo']:+.3f}, {boot['ci95_hi']:+.3f}]")


def render_md(r: dict[str, Any]) -> str:
    j = r["joint_arm_one_call"]
    d = r["decoupled_arm_two_call"]
    b = r["paired_auroc_difference"]
    ci_excludes_zero = b["ci95_lo"] > 0 or b["ci95_hi"] < 0
    L = [
        f"# Confidence Elicitation — One Call vs Two ({r['mode']})\n",
        f"Date: {r['date']} · Model {r['model']} · n={r['n_scored_paired']} paired "
        f"({r['n_failures']} failures) · temp 0.0\n",
        "**Question.** Does variant-D's failure-prediction discrimination come from the "
        "**decoupled second call** or simply from the **changed prompt wording**? Both "
        "signals are scored on the SAME answers / SAME error labels (the joint arm's "
        "answers), so the only difference is one call vs two.\n",
        f"Joint-arm Purist accuracy {r['joint_arm_purist_accuracy']:.3f} "
        f"(SE baseline {r['se_baseline_purist_accuracy_comparator']}; embedding the priming "
        "moves the answer if these differ).\n",
        "| Arm | calls | top-bucket | mean p | ECE | Brier | failure AUROC |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| **Joint (1 call, wording only)** | 1 | {j['top_bucket_share']:.1%} | {j['mean_p']:.3f} | "
        f"{j['ece']:.3f} | {j['brier']:.3f} | **{j['failure_prediction_auroc']:.3f}** |",
        f"| **Decoupled reviewer (2 calls)** | 2 | {d['top_bucket_share']:.1%} | {d['mean_p']:.3f} | "
        f"{d['ece']:.3f} | {d['brier']:.3f} | **{d['failure_prediction_auroc']:.3f}** |",
        f"\nComparators: decoupled-on-frozen-SE AUROC {r['decoupled_on_frozen_SE_comparator_auroc']}; "
        f"intrinsic in-pass {r['intrinsic_in_pass_comparator_auroc']}; external corroboration "
        f"{r['external_signal_comparator_auroc']}.\n",
        f"**Paired AUROC difference (decoupled − joint): "
        f"{b['point_diff_decoupled_minus_joint']:+.3f}, 95% CI "
        f"[{b['ci95_lo']:+.3f}, {b['ci95_hi']:+.3f}]** ({b['reps_used']} bootstrap reps).\n",
        "## Residual sensitivity\n",
        f"- Joint: residual (n={j['residual']['n']}) mean p {j['residual']['mean_p']:.3f}, "
        f"acc {j['residual']['accuracy']:.1%}; non-residual mean p {j['nonresidual']['mean_p']:.3f}, "
        f"acc {j['nonresidual']['accuracy']:.1%}",
        f"- Decoupled: residual (n={d['residual']['n']}) mean p {d['residual']['mean_p']:.3f}, "
        f"acc {d['residual']['accuracy']:.1%}; non-residual mean p {d['nonresidual']['mean_p']:.3f}, "
        f"acc {d['nonresidual']['accuracy']:.1%}\n",
        "## Verdict\n",
    ]
    aj = j["failure_prediction_auroc"]
    if ci_excludes_zero and b["point_diff_decoupled_minus_joint"] > 0:
        L.append(
            f"**H_decoupling.** The paired difference CI excludes 0 in favour of the decoupled "
            f"reviewer — folding the same priming into one call degrades discrimination "
            f"(joint {aj:.3f} vs decoupled {d['failure_prediction_auroc']:.3f}). The extra call "
            "does real work; the wording alone is not sufficient. Keep the two-call decoupled stage.\n"
        )
    elif aj > 0.5:
        L.append(
            f"**H_wording.** The joint one-call self-confidence ranks errors at AUROC {aj:.3f}, "
            f"within the bootstrap CI of the decoupled reviewer (difference CI includes 0). The "
            "discrimination comes from the changed wording, not the decoupling — the second call "
            "is removable and the priming can ride along in the extraction pass for free.\n"
        )
    else:
        L.append(
            f"**Neither.** Both arms collapse toward chance at this scale (joint {aj:.3f}); the "
            "paired test cannot separate them.\n"
        )
    return "\n".join(L)


if __name__ == "__main__":
    main()
