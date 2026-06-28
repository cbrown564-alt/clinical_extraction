"""Recall-oriented GEPA over the per-family ExECTv2 program (resumable).

The investigation localized the ~0.16 gap to the v08 hybrid (0.9155) to GENUINE
recall: the model consolidates where the gold tags every co-present concept
(generic epilepsy + specific syndrome + each named seizure type, incl. in frequency
lines) and under-detects SF seizure-free/changed states. Prior F1-balanced GEPA
settled on a PARSIMONIOUS optimum; the deterministic exhaustiveness probe recovered
0.000 (the scorer collapses parent/child), so the only lever is genuine LLM recall.

This re-runs the per-family program (the 0.731 architecture) under a RECALL-WEIGHTED
metric (F-beta, beta>1) so selection rewards emitting the missed co-present concepts /
states. The reported headline stays F1 (comparable to 0.731); only the optimization
objective is recall-weighted. Test: can LLM-only recall tuning close the gap, or does
it confirm the hybrid's edge is its hand-curated rule/example corpus (clean negative)?

Usage:
    uv run python experiments/gepa_recall_exectv2.py
    uv run python experiments/gepa_recall_exectv2.py --beta 1.5
    uv run python experiments/gepa_recall_exectv2.py --smoke
"""

from __future__ import annotations

import argparse
import json
import traceback
from datetime import UTC, datetime
from pathlib import Path

import dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import LengthPenaltyConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multifamily import (
    build_per_family_program,
    combined_instruction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import (
    EXPERIMENTS,
    GEPA_LOG_ROOT,
    GepaExperimentConfig,
    run_experiment,
)

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = GEPA_LOG_ROOT / "recall_status.json"
DATE = "2026-06-28"
SUFFIX = DATE.replace("-", "")
MINI = "openai/gpt-4.1-mini"
DEEPSEEK = "deepseek/deepseek-reasoner"

# Four per-family instructions, as in the 0.731 multifamily run.
MULTIFAMILY_PENALTY = LengthPenaltyConfig(instruction_token_budget=2000, output_token_budget=2000)
DEFAULT_BETA = 2.0
#: Per-family refinement: recall-push Diagnosis (the co-present-concept gap) only; keep the
#: other families at F1 so the uniform-beta Investigations/SF over-emission damage is avoided.
PER_FAMILY_BETA: tuple[tuple[str, float], ...] = (("Diagnosis", 2.0),)


def _config(smoke: bool, beta: float, per_family: bool) -> GepaExperimentConfig:
    family_beta = PER_FAMILY_BETA if per_family else ()
    if smoke:
        return GepaExperimentConfig(
            run_id="exectv2_gepa_recall_smoke_gpt41mini",
            task_model=MINI,
            reflection_model=DEEPSEEK,
            auto=None,
            max_metric_calls=24,
            trainset_size=8,
            valset_size=6,
            final_eval_limit=4,
            num_threads=4,
            reflection_minibatch_size=8,
            task_max_tokens=8000,
            reflection_max_tokens=8000,
            length_penalty=MULTIFAMILY_PENALTY,
            recall_beta=beta,
            family_recall_beta=family_beta,
            date=DATE,
            notes="recall-weighted per-family smoke; not a result.",
        )
    if per_family:
        run_id = f"exectv2_gepa_recall_perfamily_dedup_gpt41mini_{SUFFIX}"
        notes = (
            "Per-family-beta refinement of the uniform recall run: Diagnosis F-beta=2 "
            "(recall-push its co-present-concept gap), SF/Rx/Inv F-beta=1 (protect their F1 — "
            "the uniform beta=2 run over-emitted Inv -0.075 and SF -0.046). Macro per-family "
            "objective; reported headline stays micro-F1. Compare to uniform-recall 0.721 "
            "(Dx 0.700), per-family F1 0.731, hand-tuned 0.710, v08 hybrid 0.9155."
        )
    else:
        beta_tag = str(beta).replace(".", "p")
        run_id = f"exectv2_gepa_recall_dedup_gpt41mini_b{beta_tag}_{SUFFIX}"
        notes = (
            f"Recall-oriented per-family GEPA (uniform F-beta={beta}) to push the extractor off "
            "its parsimonious F1 optimum toward the gold's exhaustive multi-concept tagging. "
            "Reported headline stays F1. Compare to per-family F1 0.731, hybrid 0.9155."
        )
    return GepaExperimentConfig(
        run_id=run_id,
        task_model=MINI,
        reflection_model=DEEPSEEK,
        task_temperature=0.0,
        task_max_tokens=12000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=12,
        reflection_minibatch_size=8,
        length_penalty=MULTIFAMILY_PENALTY,
        recall_beta=beta,
        family_recall_beta=family_beta,
        date=DATE,
        notes=notes,
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write_status(status: dict) -> None:
    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    status["updated_at"] = _now()
    STATUS_PATH.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--beta", type=float, default=DEFAULT_BETA, help="Uniform F-beta recall weight (>1).")
    parser.add_argument(
        "--per-family",
        action="store_true",
        help="Per-family-beta refinement: Diagnosis beta=2, others beta=1 (macro objective).",
    )
    args = parser.parse_args()
    dotenv.load_dotenv(ROOT / ".env")

    config = _config(args.smoke, args.beta, args.per_family)
    status: dict = {
        "started_at": _now(),
        "smoke": args.smoke,
        "run_id": config.run_id,
        "beta": args.beta,
        "per_family": args.per_family,
    }
    summary_json = EXPERIMENTS / f"{config.run_id}.json"
    if summary_json.exists():
        print(f"[recall] skip {config.run_id} (summary exists)", flush=True)
        return

    status["state"] = "running"
    _write_status(status)
    mode = "per-family-beta (Dx=2, others=1)" if args.per_family else f"uniform F-beta={args.beta}"
    print(f"[recall] start {config.run_id} ({mode}, minibatch=8)", flush=True)
    try:
        payload = run_experiment(
            config,
            register=not args.smoke,
            seed_program=build_per_family_program(),
            final_instruction_fn=combined_instruction,
        )
        headline = payload["final_eval"]["clinical_headline"]
        status.update(
            state="done",
            finished_at=_now(),
            clinical_headline_overall_f1=headline["overall_f1"],
            precision=headline["precision"],
            recall=headline["recall"],
            per_family=headline["per_family"],
            final_instruction_tokens=payload["final_instruction_tokens"],
            elapsed_seconds=payload["elapsed_seconds"],
        )
        print(
            f"[recall] done {config.run_id}: headline_f1={headline['overall_f1']} "
            f"(P={headline['precision']} R={headline['recall']}) per_family={headline['per_family']}",
            flush=True,
        )
    except Exception as exc:
        status.update(
            state="failed",
            finished_at=_now(),
            error=f"{type(exc).__name__}: {exc}",
            traceback=traceback.format_exc()[-3000:],
        )
        print(f"[recall] FAILED {config.run_id}: {exc}", flush=True)
    _write_status(status)


if __name__ == "__main__":
    main()
