"""SF verify Phase 5 — per-(type, state) feedback, configurable per-stage models + demos.

Plan: docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md §5 (Phase 5).

Phase 5 pushes the GEPA route on SeizureFrequency WITHOUT the deterministic SF projection
fallback. The lever is **feedback precision**: ``build_sf_verify_metric`` now builds the diff
at per-(seizure_type, state) granularity with the reason attached for each of the four error
classes the SF verify error analysis named (multiplicity / FC=Same / confirmed-dx gate /
historical-vs-current). Scoring is unchanged so any lift is attributable to feedback.

This launcher parametrizes the model matrix the user is teeing up:

* ``--extraction-model`` — the generate (S0) LM. Default ``deepseek/deepseek-reasoner``
  (chain-of-thought helps the per-type enumeration / temporal / empty-output classes).
* ``--verify-model`` — the verify (S1) LM, set independently. ``deepseek/deepseek-reasoner``
  (reasoner-both) or ``openai/gpt-4.1-mini`` (mini verifier on the reasoner draft — better
  instruction-following for the confirmed-diagnosis gate).
* ``--with-examples`` — attach the hand-curated H-examples demos (``sf_verify_demos``) to
  BOTH stages, teaching the four conventions by demonstration.

The four overnight runs:

    # A1  reasoner extraction + reasoner verify, feedback-only
    uv run python experiments/gepa_sf_verify_phase5_exectv2.py \
        --extraction-model deepseek/deepseek-reasoner --verify-model deepseek/deepseek-reasoner
    # A2  reasoner extraction + gpt-4.1-mini verify, feedback-only
    uv run python experiments/gepa_sf_verify_phase5_exectv2.py \
        --extraction-model deepseek/deepseek-reasoner --verify-model openai/gpt-4.1-mini
    # A1+examples / A2+examples — add --with-examples to each

Gate (plan §5): LLM-only SF state_profile >= 0.80 AND clinical_headline SF >= 0.65 on dev140;
the feedback lever is judged on beating the best non-deterministic SF run (P2 mini 0.741
state_profile) by >= +0.03. Phase 3b's 0.779/0.650 (WITH deterministic projection) is the
comparison line, not the gate. Final eval is full dev140 (NOT the frozen test split).
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
    SfVerifyExtractor,
    build_sf_verify_metric,
    combined_instruction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.sf_verify_demos import (
    build_sf_verify_demos,
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

_MODEL_TAGS = {
    "deepseek/deepseek-reasoner": "reasoner",
    "deepseek/deepseek-chat": "chat",
    "openai/gpt-4.1-mini": "mini",
}


def _tag(model: str) -> str:
    return _MODEL_TAGS.get(model, model.split("/")[-1].replace(".", "").replace("-", ""))


def _max_tokens_for(model: str) -> int:
    """Reasoner models need headroom for the reasoning trace; chat/mini do not."""

    return 12000 if "reasoner" in model else 8000


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
        gc = "changed" in {
            frequency_state_faithful(a.attributes) for a in g.entities("SeizureFrequency")
        }
        pc = "changed" in {
            frequency_state_faithful(a.attributes) for a in p.entities("SeizureFrequency")
        }
        tp += gc and pc
        fp += pc and not gc
        fn += gc and not pc
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return rec, prec


def _evaluate(program, letters, num_threads):
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)
    pairs = [
        (program, {"letter_text": le.note_text, "output_schema": EVENT_SCHEMA_JSON})
        for le in letters
    ]
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
        rows.append(
            {
                "letter_id": letter.letter_id,
                "predicted_mentions": [
                    {"entity": m.entity, "text": m.text, "attributes": dict(m.attributes)}
                    for m in predicted.mentions
                ],
            }
        )
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
    ap.add_argument("--extraction-model", default="deepseek/deepseek-reasoner")
    ap.add_argument("--verify-model", default="deepseek/deepseek-reasoner")
    ap.add_argument("--reflection-model", default="deepseek/deepseek-reasoner")
    ap.add_argument(
        "--with-examples", action="store_true", help="attach hand-curated H-examples demos"
    )
    ap.add_argument(
        "--change-precision-weight",
        type=float,
        default=0.0,
        help="0.0 = feedback-only (scoring identical, lift attributable to feedback)",
    )
    ap.add_argument("--max-metric-calls", type=int, default=1000)
    ap.add_argument("--minibatch", type=int, default=8)
    ap.add_argument("--trainset-size", type=int, default=gepa_data.DEFAULT_TRAINSET_SIZE)
    ap.add_argument("--num-threads", type=int, default=12)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    dotenv.load_dotenv(ROOT / ".env")

    if args.run_id is None:
        suffix = "ex" if args.with_examples else "fb"
        args.run_id = (
            f"exectv2_gepa_sf_verify_p5_{_tag(args.extraction_model)}_"
            f"{_tag(args.verify_model)}_{suffix}_20260629"
        )
    if args.smoke:
        args.max_metric_calls, args.trainset_size, args.minibatch, args.num_threads = 20, 10, 3, 4
        args.run_id += "_smoke"

    task_lm = build_dspy_lm(
        args.extraction_model,
        temperature=0.0,
        max_tokens=_max_tokens_for(args.extraction_model),
        cache=True,
    )
    verify_lm = build_dspy_lm(
        args.verify_model,
        temperature=0.0,
        max_tokens=_max_tokens_for(args.verify_model),
        cache=True,
    )
    dspy.configure(lm=task_lm)
    reflection_lm = build_dspy_lm(
        args.reflection_model, temperature=1.0, max_tokens=12000, cache=False
    )

    gen_demos, ver_demos = build_sf_verify_demos() if args.with_examples else (None, None)
    demo_budget = 2400 if args.with_examples else LengthPenaltyConfig().demo_token_budget
    metric = build_sf_verify_metric(
        LengthPenaltyConfig(instruction_token_budget=1600, demo_token_budget=demo_budget),
        change_precision_weight=args.change_precision_weight,
    )

    def _seed() -> SfVerifyExtractor:
        return SfVerifyExtractor(
            generate_lm=task_lm,
            verify_lm=verify_lm,
            generate_demos=gen_demos,
            verify_demos=ver_demos,
        )

    shuffled = gepa_data._shuffled_dev()
    trainset = _examples(shuffled[: args.trainset_size])
    val_letters = shuffled[args.trainset_size :]
    if args.smoke:
        val_letters = val_letters[:8]
    valset = _examples(val_letters)

    dev = gepa_data.load_dev_letters()
    if args.smoke:
        dev = dev[:12]

    print(
        f"[p5 {args.run_id}] extract={args.extraction_model} verify={args.verify_model} "
        f"reflect={args.reflection_model} examples={args.with_examples} "
        f"cpw={args.change_precision_weight} calls={args.max_metric_calls} mb={args.minibatch}",
        flush=True,
    )
    seed_program = _seed()
    print(f"[p5 {args.run_id}] evaluating SEED on dev ({len(dev)})...", flush=True)
    _seed_rows, seed_scores, seed_cpr = _evaluate(seed_program, dev, args.num_threads)
    print(f"[p5 {args.run_id}] SEED  {_fmt(seed_scores, seed_cpr)}", flush=True)

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
    optimized = optimizer.compile(_seed(), trainset=trainset, valset=valset)
    elapsed = time.time() - started

    print(f"[p5 {args.run_id}] evaluating OPTIMIZED on dev ({len(dev)})...", flush=True)
    opt_rows, opt_scores, opt_cpr = _evaluate(optimized, dev, args.num_threads)
    print(
        f"[p5 {args.run_id}] OPT   {_fmt(opt_scores, opt_cpr)}  ({elapsed / 60:.1f} min)",
        flush=True,
    )
    print(
        "[p5] comparators — P2 mini 0.597/0.741 | recall-lanes SF 0.580/0.710 | "
        "Phase3b+proj 0.650/0.779 | hybrid 0.926/0.930 (changed 0.85R/1.00P)"
    )
    print("[p5] gate — state_profile >= 0.80 AND clinical_headline SF >= 0.65 (LLM-only)")

    instruction = combined_instruction(optimized)
    (EXPERIMENTS / f"{args.run_id}.jsonl").write_text(
        "\n".join(json.dumps(r) for r in opt_rows) + "\n", encoding="utf-8"
    )
    (EXPERIMENTS / f"{args.run_id}.instruction.txt").write_text(
        instruction + "\n", encoding="utf-8"
    )
    summary = {
        "run_id": args.run_id,
        "extraction_model": args.extraction_model,
        "verify_model": args.verify_model,
        "reflection_model": args.reflection_model,
        "with_examples": args.with_examples,
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
            "p2_sf_verify_mini": {"clinical_headline": 0.597, "state_profile": 0.741},
            "recall_lanes_sf": {"clinical_headline": 0.580, "state_profile": 0.710},
            "phase3b_with_projection": {"clinical_headline": 0.650, "state_profile": 0.779},
            "v08_hybrid": {
                "clinical_headline": 0.926,
                "state_profile": 0.930,
                "changed_recall": 0.85,
                "changed_precision": 1.00,
            },
        },
        "gate": {
            "state_profile": 0.80,
            "clinical_headline_sf": 0.65,
            "feedback_lever_min_state_profile": 0.771,
        },
    }
    (EXPERIMENTS / f"{args.run_id}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"[p5 {args.run_id}] saved -> experiments/{args.run_id}.{{jsonl,instruction.txt,json}}")


if __name__ == "__main__":
    main()
