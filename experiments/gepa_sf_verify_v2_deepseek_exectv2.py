"""SF verify v2 — change-class PRECISION refinement, on DeepSeek.

Plan: docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md (focused SF
producer/verify). P2 (gepa_sf_verify_exectv2) recovered change RECALL (0.48) but over-fired
it (0.46 precision) vs the hybrid's 0.85R/1.00P — the one localized residual after Phase 3.
This run targets that cell directly:

* program: ``build_sf_verify_program_v2`` — the recall-additive verify reseeded with an
  explicit change-class boundary rule (preserving the rate+change per-type multiplicity).
* metric: ``build_sf_verify_metric(change_precision_weight=…)`` — penalizes a per-letter
  change over-call and names it in the feedback, so the minority change class is disciplined
  for precision without the aggregate state_profile objective washing it out.
* model: DeepSeek (task ``deepseek-chat``, reflection ``deepseek-reasoner``) — no GPT.

Final eval on full dev140 (NOT test): SF clinical_headline AND state_profile for seed and
optimized. Compare: de-dup 0.592/0.713, P2 0.597/0.741, recall-lanes SF 0.580/0.710,
hybrid 0.926/0.930.

Usage:
    uv run python experiments/gepa_sf_verify_v2_deepseek_exectv2.py --smoke
    uv run python experiments/gepa_sf_verify_v2_deepseek_exectv2.py
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import dotenv
import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import LengthPenaltyConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import approx_tokens
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_sf_verify import (
    EVENT_SCHEMA_JSON,
    build_sf_verify_metric,
    build_sf_verify_program_v2,
    combined_instruction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    score_frequency_state,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
GEPA_LOG_ROOT = EXPERIMENTS / "gepa_overnight_exectv2"


def _examples(letters):
    return [
        dspy.Example(
            letter_text=letter.note_text,
            output_schema=EVENT_SCHEMA_JSON,
            letter_id=letter.letter_id,
            letter=letter,
        ).with_inputs("letter_text", "output_schema")
        for letter in letters
    ]


def _change_pr(gold_list, pred_list):
    """Per-letter change-state presence precision/recall (the targeted cell)."""
    tp = fp = fn = 0
    for g, p in zip(gold_list, pred_list, strict=True):
        gc = "changed" in {frequency_state_faithful(a.attributes) for a in g.entities("SeizureFrequency")}
        pc = "changed" in {frequency_state_faithful(a.attributes) for a in p.entities("SeizureFrequency")}
        tp += gc and pc
        fp += pc and not gc
        fn += gc and not pc
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return rec, prec


def _evaluate(program, letters, num_threads):
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)
    pairs = [(program, {"letter_text": le.note_text, "output_schema": EVENT_SCHEMA_JSON}) for le in letters]
    predictions = evaluator(pairs)
    gold_list, pred_list, rows = [], [], []
    for letter, pred in zip(letters, predictions, strict=True):
        raw = str(getattr(pred, "clinical_facts_json", "") or "") if pred else ""
        record, _errors = parse_dedup_clinical_facts_json(raw) if raw else (None, ["empty_output"])
        if record is None:
            predicted = PredictedLetter(letter_id=letter.letter_id, mentions=())
        else:
            predicted, *_ = to_predicted_letter_from_dedup_facts(letter, record)
        pred_exect = to_exect_letter(predicted)
        gold_list.append(letter)
        pred_list.append(pred_exect)
        rows.append({
            "letter_id": letter.letter_id,
            "predicted_mentions": [
                {"entity": m.entity, "text": m.text, "attributes": dict(m.attributes)}
                for m in predicted.mentions
            ],
        })
    return rows, score_frequency_state(gold_list, pred_list), _change_pr(gold_list, pred_list)


def _fmt(scores, change_pr) -> str:
    ch, sp = scores.clinical_headline, scores.state_profile
    cr, cp = change_pr
    return (
        f"clinical_headline F1={ch.f1:.3f} | state_profile F1={sp.f1:.3f} "
        f"(P={sp.precision:.3f} R={sp.recall:.3f}) | changed {cr:.2f}R/{cp:.2f}P"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="deepseek/deepseek-chat")
    ap.add_argument("--reflection-model", default="deepseek/deepseek-reasoner")
    ap.add_argument("--max-metric-calls", type=int, default=1000)
    ap.add_argument("--minibatch", type=int, default=8)
    ap.add_argument("--change-precision-weight", type=float, default=0.2)
    ap.add_argument("--trainset-size", type=int, default=gepa_data.DEFAULT_TRAINSET_SIZE)
    ap.add_argument("--num-threads", type=int, default=12)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-id", default="exectv2_gepa_sf_verify_v2_deepseekchat_20260629")
    args = ap.parse_args()
    dotenv.load_dotenv(ROOT / ".env")

    if args.smoke:
        args.max_metric_calls, args.trainset_size, args.minibatch, args.num_threads = 20, 10, 3, 4
        args.run_id += "_smoke"

    task_lm = build_dspy_lm(args.model, temperature=0.0, max_tokens=8000, cache=True)
    dspy.configure(lm=task_lm)
    reflection_lm = build_dspy_lm(args.reflection_model, temperature=1.0, max_tokens=12000, cache=False)

    shuffled = gepa_data._shuffled_dev()
    trainset = _examples(shuffled[: args.trainset_size])
    val_letters = shuffled[args.trainset_size :]
    if args.smoke:
        val_letters = val_letters[:8]
    valset = _examples(val_letters)

    metric = build_sf_verify_metric(
        LengthPenaltyConfig(instruction_token_budget=1600),
        change_precision_weight=args.change_precision_weight,
    )
    seed_program = build_sf_verify_program_v2()

    dev = gepa_data.load_dev_letters()
    if args.smoke:
        dev = dev[:12]

    print(f"[sf-verify-v2] evaluating SEED on dev ({len(dev)})...", flush=True)
    _seed_rows, seed_scores, seed_cpr = _evaluate(seed_program, dev, args.num_threads)
    print(f"[sf-verify-v2] SEED   {_fmt(seed_scores, seed_cpr)}", flush=True)

    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    log_dir = GEPA_LOG_ROOT / args.run_id
    log_dir.mkdir(parents=True, exist_ok=True)
    optimizer = dspy.GEPA(
        metric=metric,
        reflection_lm=reflection_lm,
        reflection_minibatch_size=args.minibatch,
        num_threads=args.num_threads,
        track_stats=True,
        track_best_outputs=True,
        log_dir=str(log_dir),
        seed=0,
        add_format_failure_as_feedback=True,
        max_metric_calls=args.max_metric_calls,
        gepa_kwargs={"use_cloudpickle": True},
    )

    started = time.time()
    optimized = optimizer.compile(seed_program, trainset=trainset, valset=valset)
    elapsed = time.time() - started

    print(f"[sf-verify-v2] evaluating OPTIMIZED on dev ({len(dev)})...", flush=True)
    opt_rows, opt_scores, opt_cpr = _evaluate(optimized, dev, args.num_threads)
    print(f"[sf-verify-v2] OPT    {_fmt(opt_scores, opt_cpr)}  ({elapsed/60:.1f} min)", flush=True)
    print("[sf-verify-v2] comparators — de-dup 0.592/0.713 | P2 0.597/0.741 | "
          "recall-lanes SF 0.580/0.710 | hybrid 0.926/0.930 (changed 0.85R/1.00P)")

    instruction = combined_instruction(optimized)
    (EXPERIMENTS / f"{args.run_id}.jsonl").write_text(
        "\n".join(json.dumps(r) for r in opt_rows) + "\n", encoding="utf-8"
    )
    (EXPERIMENTS / f"{args.run_id}.instruction.txt").write_text(instruction + "\n", encoding="utf-8")
    summary = {
        "run_id": args.run_id,
        "model": args.model,
        "reflection_model": args.reflection_model,
        "change_precision_weight": args.change_precision_weight,
        "max_metric_calls": args.max_metric_calls,
        "minibatch": args.minibatch,
        "elapsed_minutes": round(elapsed / 60, 1),
        "instruction_tokens": approx_tokens(instruction),
        "seed": {
            "clinical_headline_f1": round(seed_scores.clinical_headline.f1, 4),
            "state_profile_f1": round(seed_scores.state_profile.f1, 4),
            "changed_recall": round(seed_cpr[0], 4),
            "changed_precision": round(seed_cpr[1], 4),
        },
        "optimized": {
            "clinical_headline_f1": round(opt_scores.clinical_headline.f1, 4),
            "state_profile_f1": round(opt_scores.state_profile.f1, 4),
            "state_profile_precision": round(opt_scores.state_profile.precision, 4),
            "state_profile_recall": round(opt_scores.state_profile.recall, 4),
            "changed_recall": round(opt_cpr[0], 4),
            "changed_precision": round(opt_cpr[1], 4),
        },
        "comparators": {
            "dedup": {"clinical_headline": 0.592, "state_profile": 0.713},
            "p2_sf_verify": {"clinical_headline": 0.597, "state_profile": 0.741,
                             "changed_recall": 0.48, "changed_precision": 0.46},
            "recall_lanes_sf": {"clinical_headline": 0.580, "state_profile": 0.710},
            "v08_hybrid": {"clinical_headline": 0.926, "state_profile": 0.930,
                           "changed_recall": 0.85, "changed_precision": 1.00},
        },
    }
    (EXPERIMENTS / f"{args.run_id}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"[sf-verify-v2] saved -> experiments/{args.run_id}.{{jsonl,instruction.txt,json}}")


if __name__ == "__main__":
    main()
