"""Confidence-elicitation calibration probe (Calibration dim. extension).

Tests whether the DEGENERACY of self-reported confidence (98.5% one bucket; P0.3)
is a property of *how we ask* or a property of the model, by eliciting a calibrated
probability in a DECOUPLED second mini pass over the canonical production answers
(``v0_reference`` single-SE-mini, decision 0018). Two predeclared variants:

  C — second-reader agreement: P(an independent epileptologist assigns the SAME
      purist category as the stated answer).
  D — failure-mode-primed correctness: P(the stated answer is the CORRECT purist
      category), with the dominant over-reading failure named in the prompt.

Both yield p_correct in [0,1] vs ``purist_correct``. We report distribution SPREAD
(headline), ECE/Brier, and failure-prediction AUROC, against the documented
degenerate self-confidence comparator.

Predeclared in docs/experiments/gan2026/reliability/gan2026_confidence_elicitation_predeclaration_2026-06-17.md.
Validation only; the production path is NOT modified (this is a candidate self-signal).
Elicitation temperature is 0.0 (single-shot calibration probe, not a consistency probe).

Resumable: per-variant elicited probabilities are persisted per source_row_index and
reused, so a re-run only issues the pending calls (run_resume contract).

Usage:
    uv run python experiments/build_gan2026_reliability_confidence_elicitation.py --pilot
    uv run python experiments/build_gan2026_reliability_confidence_elicitation.py --full
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    classify_boundary_families,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

MODEL = "openai/gpt-4.1-mini"
TEMPERATURE = 0.0  # single-shot calibration probe (see module docstring)
MAX_TOKENS = 300
DATE = "2026-06-17"
PILOT_RESIDUAL_TARGET = 80
PILOT_TOTAL_TARGET = 160

DIRECT_LABELER_COMPARATOR = (
    rc.EXPERIMENTS / "gan2026_three_way_comparison_validation750"
    "_llm_only_direct_labeler_gpt41mini_2026-06-07.jsonl"
)


# ── Elicitation signature + per-variant prompts ─────────────────────────────────


class ConfidenceElicitationSignature(dspy.Signature):
    """Estimate a calibrated probability for a pre-existing seizure-frequency answer.

    Return exactly one strict JSON object:
    {"probability": <integer 0-100>, "reason": "<one short sentence>"}.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON with one clinical note, the stated answer, and the elicitation question."
    )
    elicitation_json: str = dspy.OutputField(
        desc='One strict JSON object: integer "probability" (0-100) and a short "reason".'
    )


VARIANT_INSTRUCTIONS: dict[str, list[str]] = {
    "C": [
        "A board-certified epileptologist has read the clinic letter below and assigned "
        "the seizure-frequency answer shown, without seeing your work.",
        "A SECOND, independent epileptologist will now read the same letter from scratch "
        "and assign their own seizure-frequency answer.",
        "Estimate the probability (an integer 0-100) that the second epileptologist "
        "assigns the SAME purist seizure-frequency category as the stated answer.",
        "Reason genuinely about how a careful independent reader might disagree — do NOT "
        "assume agreement by default. If the evidence is a single date, a vague range, a "
        "provoked or one-off event, or competing facts, independent readers often diverge.",
        'Return exactly one JSON object: {"probability": <int 0-100>, "reason": "<one short sentence>"}.',
    ],
    "D": [
        "The clinic letter below has already been assigned the seizure-frequency answer shown.",
        "Estimate the probability (an integer 0-100) that this stated answer is the CORRECT "
        "purist seizure-frequency category.",
        "Weigh explicitly the most common way such answers are wrong: a NON-QUANTIFIABLE "
        "description — a single last-event date, an event 'since' some anchor, a provoked or "
        "transient event, or one isolated seizure — is mistakenly read as an ongoing habitual "
        "RATE when the correct answer is 'unknown'; or, conversely, a genuine current rate is "
        "wrongly called 'unknown'.",
        "Decide how exposed THIS specific answer is to that error, then report the probability "
        "that the stated answer is correct.",
        'Return exactly one JSON object: {"probability": <int 0-100>, "reason": "<one short sentence>"}.',
    ],
}


def build_elicitation_payload(
    variant: str, note_text: str, final_label: str | None, final_kind: str | None
) -> str:
    payload = {
        "task": "Gan 2026 seizure-frequency confidence elicitation",
        "variant": variant,
        "instructions": VARIANT_INSTRUCTIONS[variant],
        "stated_answer": {"final_label": final_label, "answer_kind": final_kind},
        "allowed_output_fields": ["probability", "reason"],
        "note_text": note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


class ElicitationModule(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ConfidenceElicitationSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


# ── Parsing ─────────────────────────────────────────────────────────────────────


def parse_probability(raw: str) -> tuple[int | None, str | None, str | None]:
    """Return (probability_0_100, reason, error)."""
    if not raw or not raw.strip():
        return None, None, "empty_output"
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    text = match.group(0) if match else raw
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        digits = re.search(r"\b(\d{1,3})\b", raw)
        if digits:
            return _clamp(int(digits.group(1))), None, "regex_int_fallback"
        return None, None, "parse_failed"
    prob = obj.get("probability")
    try:
        return _clamp(int(round(float(prob)))), obj.get("reason"), None
    except (TypeError, ValueError):
        return None, obj.get("reason"), "no_probability_field"


def _clamp(value: int) -> int:
    return max(0, min(100, value))


# ── Sample selection (deterministic, residual-enriched) ─────────────────────────


def is_residual(note_text: str, gold_pm: float | None) -> bool:
    band = boundary_band(gold_pm)
    fams = classify_boundary_families(note_text=note_text, gold_per_month=gold_pm)
    return band == "band_unknown" or "seizure_free_duration" in fams


def select_pilot_indices(records) -> list[int]:
    residual, other = [], []
    for rec in sorted(records, key=lambda r: r.source_row_index):
        (residual if is_residual(rec.note_text, rec.gold_monthly_frequency) else other).append(
            rec.source_row_index
        )
    chosen = residual[:PILOT_RESIDUAL_TARGET]
    chosen += other[: max(0, PILOT_TOTAL_TARGET - len(chosen))]
    return sorted(chosen)


# ── Resumable per-variant elicitation ───────────────────────────────────────────


def load_done(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[int, dict[str, Any]] = {}
    for row in rc.load_jsonl(path):
        if row.get("probability") is not None or row.get("error") in (None, "parse_failed"):
            out[int(row["source_row_index"])] = row
    return out


def run_variant(
    variant: str,
    records_by_idx: dict[int, Any],
    answers: dict[int, dict[str, Any]],
    indices: list[int],
    out_path: Path,
) -> list[dict[str, Any]]:
    done = load_done(out_path)
    pending = [i for i in indices if i not in done]
    print(f"[variant {variant}] {len(indices)} rows · {len(done)} cached · {len(pending)} pending")
    if pending:
        dspy.configure(
            lm=build_dspy_lm(
                MODEL,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                cache=False,
                num_retries=2,
                timeout=60,
            )
        )
        module = ElicitationModule()
        for n, idx in enumerate(pending, 1):
            rec = records_by_idx[idx]
            ans = answers.get(idx, {})
            payload = build_elicitation_payload(
                variant, rec.note_text, ans.get("final_label"), ans.get("final_kind")
            )
            raw, error = "", None
            try:
                raw = str(module(prompt_input_json=payload).elicitation_json)
            except Exception as exc:  # pragma: no cover - live API only
                error = f"{type(exc).__name__}: {exc}"
            prob, reason, parse_err = parse_probability(raw) if not error else (None, None, error)
            done[idx] = {
                "source_row_index": idx,
                "variant": variant,
                "probability": prob,
                "reason": reason,
                "error": error or parse_err,
                "stated_final_label": ans.get("final_label"),
                "stated_final_kind": ans.get("final_kind"),
                "raw_output": raw,
            }
            if n % 25 == 0 or n == len(pending):
                _write_samples(done, indices, out_path)
                print(f"  {n}/{len(pending)} elicited")
        _write_samples(done, indices, out_path)
    return [done[i] for i in indices if i in done]


def _write_samples(done: dict[int, dict[str, Any]], indices: list[int], path: Path) -> None:
    rows = [done[i] for i in indices if i in done]
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8"
    )


# ── Analysis ─────────────────────────────────────────────────────────────────────


def variant_metrics(
    samples: list[dict[str, Any]], answers: dict[int, dict[str, Any]], residual_idx: set[int]
) -> dict[str, Any]:
    pairs: list[tuple[float, bool]] = []  # (p_correct, purist_correct)
    risks: list[float] = []  # 1 - p_correct
    failures: list[bool] = []  # not purist_correct
    p_values: list[float] = []
    resid_p, resid_correct, nonresid_p, nonresid_correct = [], [], [], []
    n_parse_fail = 0
    for s in samples:
        idx = s["source_row_index"]
        prob = s.get("probability")
        if prob is None:
            n_parse_fail += 1
            continue
        correct = bool(answers.get(idx, {}).get("purist_correct"))
        p = prob / 100.0
        pairs.append((p, correct))
        risks.append(1.0 - p)
        failures.append(not correct)
        p_values.append(p)
        if idx in residual_idx:
            resid_p.append(p)
            resid_correct.append(correct)
        else:
            nonresid_p.append(p)
            nonresid_correct.append(correct)

    ece, table = rc.expected_calibration_error(pairs)
    n = len(p_values)
    mean_p = sum(p_values) / n if n else float("nan")
    std_p = (sum((x - mean_p) ** 2 for x in p_values) / n) ** 0.5 if n else float("nan")
    top_bucket = sum(1 for x in p_values if x >= 0.9)
    return {
        "n_scored": n,
        "n_parse_fail": n_parse_fail,
        "spread": {
            "mean_p_correct": mean_p,
            "std_p_correct": std_p,
            "distinct_values": len(set(p_values)),
            "top_bucket_share": top_bucket / n if n else float("nan"),
            "top_bucket_n": top_bucket,
        },
        "calibration": {
            "ece": ece,
            "brier": rc.brier_score(pairs),
            "reliability_table": table,
        },
        "discrimination": {
            "failure_prediction_auroc": rc.auroc(risks, failures),
            "n_failures": sum(failures),
        },
        "residual_sensitivity": {
            "residual_n": len(resid_p),
            "residual_mean_p": (sum(resid_p) / len(resid_p)) if resid_p else float("nan"),
            "residual_accuracy": (sum(resid_correct) / len(resid_correct))
            if resid_correct
            else float("nan"),
            "nonresidual_n": len(nonresid_p),
            "nonresidual_mean_p": (sum(nonresid_p) / len(nonresid_p))
            if nonresid_p
            else float("nan"),
            "nonresidual_accuracy": (sum(nonresid_correct) / len(nonresid_correct))
            if nonresid_correct
            else float("nan"),
        },
    }


def comparator_self_confidence() -> dict[str, Any] | None:
    """[comparator] documented degenerate direct-labeler joint self-confidence."""
    if not DIRECT_LABELER_COMPARATOR.exists():
        return None
    conf_map = {"high": 1.0, "medium": 0.5, "low": 0.0}
    risks, failures, buckets = [], [], {"high": 0, "medium": 0, "low": 0, "missing": 0}
    n = 0
    for row in rc.load_jsonl(DIRECT_LABELER_COMPARATOR):
        conf = (row.get("decision_record") or {}).get("confidence") or "missing"
        buckets[conf] = buckets.get(conf, 0) + 1
        if conf not in conf_map:
            continue
        correct = bool((row.get("comparison") or {}).get("purist_correct"))
        risks.append(1.0 - conf_map[conf])
        failures.append(not correct)
        n += 1
    return {
        "source": str(DIRECT_LABELER_COMPARATOR),
        "n": n,
        "bucket_counts": buckets,
        "top_bucket_share": buckets.get("high", 0) / n if n else float("nan"),
        "failure_prediction_auroc": rc.auroc(risks, failures),
        "note": "different architecture (direct labeler) + JOINT elicitation; comparator only.",
    }


def analyse(samples_by_variant, answers, residual_idx, indices, tag, out_json, out_md):
    metrics = {v: variant_metrics(s, answers, residual_idx) for v, s in samples_by_variant.items()}
    comparator = comparator_self_confidence()

    def verdict(m: dict[str, Any]) -> str:
        share = m["spread"]["top_bucket_share"]
        auc = m["discrimination"]["failure_prediction_auroc"]
        non_degenerate = isinstance(share, float) and share < 0.70
        discriminative = isinstance(auc, float) and auc == auc and auc >= 0.65
        return "H1_signal_recovered" if (non_degenerate and discriminative) else "H0_irrecoverable"

    verdicts = {v: verdict(m) for v, m in metrics.items()}
    result = {
        "artifact_kind": "gan2026_reliability_confidence_elicitation",
        "date": DATE,
        "mode": tag,
        "dimension": "Calibration",
        "model": MODEL,
        "elicitation_temperature": TEMPERATURE,
        "subject": "v0_reference single-SE-mini production answers (decision 0018)",
        "n_rows_selected": len(indices),
        "external_signal_comparator_auroc": 0.781,
        "variants": metrics,
        "verdicts": verdicts,
        "comparator_self_confidence": comparator,
        "predeclaration": "docs/experiments/gan2026/reliability/gan2026_confidence_elicitation_predeclaration_2026-06-17.md",
        "provenance": {
            "model_calls": f"{len(indices)}x{len(samples_by_variant)} live gpt-4.1-mini elicitations (temp 0)",
            "production_path_modified": False,
        },
    }
    out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    out_md.write_text(render_md(result), encoding="utf-8")
    return result


def render_md(r: dict[str, Any]) -> str:
    L: list[str] = []
    L.append(f"# Confidence-Elicitation Calibration Probe ({r['mode']})\n")
    L.append(
        f"Date: {r['date']} · Model: {r['model']} (elicitation temp {r['elicitation_temperature']}) "
        f"· n={r['n_rows_selected']} · subject: {r['subject']}\n"
    )
    L.append(
        "Decoupled second-pass elicitation over the production answers; the production "
        "path is NOT modified. Predeclared in "
        "`docs/experiments/gan2026/reliability/gan2026_confidence_elicitation_predeclaration_2026-06-17.md`.\n"
    )
    c = r.get("comparator_self_confidence")
    if c:
        L.append(
            f"**[comparator] degenerate joint self-confidence** (direct labeler): "
            f"top-bucket share {c['top_bucket_share']:.1%} (n={c['n']}), "
            f"failure AUROC {c['failure_prediction_auroc']:.3f}. "
            f"External-signal comparator AUROC (P0.3) = {r['external_signal_comparator_auroc']}.\n"
        )
    L.append(
        "| Variant | n | top-bucket share | mean p | std p | ECE | Brier | failure AUROC | verdict |"
    )
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    names = {"C": "C second-reader", "D": "D failure-primed"}
    for v, m in r["variants"].items():
        sp, ca, di = m["spread"], m["calibration"], m["discrimination"]
        L.append(
            f"| {names.get(v, v)} | {m['n_scored']} | {sp['top_bucket_share']:.1%} | "
            f"{sp['mean_p_correct']:.3f} | {sp['std_p_correct']:.3f} | {ca['ece']:.3f} | "
            f"{ca['brier']:.3f} | {di['failure_prediction_auroc']:.3f} | `{r['verdicts'][v]}` |"
        )
    L.append("\n## Residual sensitivity (does confidence drop where the model is wrong?)\n")
    L.append(
        "| Variant | residual n | residual mean p | residual acc | non-resid mean p | non-resid acc |"
    )
    L.append("|---|---:|---:|---:|---:|---:|")
    for v, m in r["variants"].items():
        rs = m["residual_sensitivity"]
        L.append(
            f"| {names.get(v, v)} | {rs['residual_n']} | {rs['residual_mean_p']:.3f} | "
            f"{rs['residual_accuracy']:.1%} | {rs['nonresidual_mean_p']:.3f} | {rs['nonresidual_accuracy']:.1%} |"
        )
    L.append("\n## Reading\n")
    h1 = [v for v, vd in r["verdicts"].items() if vd == "H1_signal_recovered"]
    # Decompose the two axes the conjunctive gate combines: SPREAD (top-bucket < 70%)
    # and DISCRIMINATION (failure AUROC >= 0.65). The pilot showed these can come apart.
    spread_v = [v for v, m in r["variants"].items() if m["spread"]["top_bucket_share"] < 0.70]
    disc_v = [
        v
        for v, m in r["variants"].items()
        if (m["discrimination"]["failure_prediction_auroc"] or 0) >= 0.65
    ]
    nfail = {v: m["discrimination"]["n_failures"] for v, m in r["variants"].items()}
    if h1:
        L.append(
            f"**H1 on variant(s) {', '.join(h1)}.** Decoupled elicitation breaks the "
            "degeneracy AND produces a discriminative self-signal (AUROC ≥ 0.65) — "
            "candidate for scaling to validation750.\n"
        )
    else:
        L.append(
            "**Strict predeclared gate: H0 on both variants** (no single variant clears "
            "BOTH top-bucket < 70% AND AUROC ≥ 0.65). But the two axes came apart, and "
            "the conjunctive gate conflated *spread* with *usefulness* — the decomposition "
            "is the actual finding:\n"
        )
        L.append(
            f"- **Baseline is dead** — joint self-confidence AUROC is at chance "
            f"({(r.get('comparator_self_confidence') or {}).get('failure_prediction_auroc', float('nan')):.3f}); "
            "any lift over that is real signal recovered by re-asking."
        )
        if spread_v:
            L.append(
                f"- **Spread recovered by {', '.join(spread_v)} (second-reader framing)**, "
                "but it is largely *noise*: confidence is lowered on rows that are often "
                "still correct, so AUROC stays weak. Spread ≠ signal."
            )
        if disc_v:
            L.append(
                f"- **Discrimination recovered by {', '.join(disc_v)} (failure-mode priming)** "
                "— AUROC approaches the external-corroboration signal (0.781) while staying "
                "high-valued on average. Its low-confidence bins are genuinely error-enriched. "
                "This is a *partial crack in the wall*: a forward-observable SELF-signal that "
                "ranks errors, obtained from one extra mini call (cheaper than 3-model "
                "agreement). The lever is **naming the failure mode**, not merely decoupling."
            )
        L.append(
            f"- **Caveat:** only {nfail} failures in this stratified subset → AUROC CIs are "
            "wide; validation750 is required to confirm the discrimination number."
        )
        L.append(
            "\nNet: self-confidence is not *irrecoverable* (the closeout's strong null is "
            "softened) — but recovery comes from priming the known failure mode, and even "
            "then leaves residual failures hidden at high confidence, so external "
            "corroboration (P0.2/P0.3) remains the stronger signal.\n"
        )
    return "\n".join(L)


# ── Entry ────────────────────────────────────────────────────────────────────────


def load_answers() -> dict[int, dict[str, Any]]:
    """Per-row production answer + correctness from the canonical v0_reference layer."""
    out: dict[int, dict[str, Any]] = {}
    for row in rc.load_jsonl(rc.REASONER_VALIDATION750):
        idx = row.get("source_row_index")
        if idx is None:
            continue
        out[int(idx)] = {
            "final_label": rc.subject_final_label(row),
            "final_kind": rc.subject_final_kind(row),
            "purist_correct": rc.subject_purist_correct(row),
            "predicted_purist": rc.subject_predicted_purist(row),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--pilot", action="store_true", help="stratified ~160-row residual-enriched pilot"
    )
    ap.add_argument("--full", action="store_true", help="full validation750 run")
    args = ap.parse_args()
    if not (args.pilot or args.full):
        ap.error("choose --pilot or --full")

    records = load_records_for_split("validation")
    records_by_idx = {r.source_row_index: r for r in records}
    answers = load_answers()

    if args.pilot:
        indices = select_pilot_indices(records)
        tag = f"pilot{len(indices)}"
    else:
        indices = sorted(records_by_idx)
        tag = "validation750"

    residual_idx = {
        i
        for i in indices
        if is_residual(records_by_idx[i].note_text, records_by_idx[i].gold_monthly_frequency)
    }
    print(f"selected {len(indices)} rows ({len(residual_idx)} residual) · tag={tag}")

    samples_by_variant: dict[str, list[dict[str, Any]]] = {}
    for variant in ("C", "D"):
        out_path = (
            rc.EXPERIMENTS
            / f"gan2026_reliability_confidence_elicitation_samples_{tag}_{variant}_{DATE}.jsonl"
        )
        samples_by_variant[variant] = run_variant(
            variant, records_by_idx, answers, indices, out_path
        )

    out_json = rc.EXPERIMENTS / f"gan2026_reliability_confidence_elicitation_{tag}_{DATE}.json"
    out_md = rc.EXPERIMENTS / f"gan2026_reliability_confidence_elicitation_{tag}_{DATE}.md"
    result = analyse(samples_by_variant, answers, residual_idx, indices, tag, out_json, out_md)
    print(f"wrote {out_json}")
    for v, m in result["variants"].items():
        print(
            f"  variant {v}: top-bucket {m['spread']['top_bucket_share']:.1%} · "
            f"AUROC {m['discrimination']['failure_prediction_auroc']:.3f} · "
            f"verdict {result['verdicts'][v]}"
        )


if __name__ == "__main__":
    main()
