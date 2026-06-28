"""GEPA over the multi-stage (generate -> verify) ExECTv2 program (resumable).

Phase 1 of the multi-stage scope (docs/plans/exectv2_gepa_multistage_program_scope_
2026-06-28.md). The single-pass per-family run plateaued at 0.731 dev140
clinical_headline, ~0.18 below the v08 hybrid (0.9155); the gap is architectural
(the hybrid's lift comes from generate->verify->arbitrate stages). This launcher
gives GEPA a two-stage program to optimize: four per-family generate instructions
(S0) plus four per-family verify instructions (S1), all evolved jointly under the
length-penalized diff-feedback metric.

S0 warm-starts from the evolved 0.731 per-family instructions by default (the scope
Phase 1 design); pass ``--lean-s0`` to seed S0 from the lean per-family signatures
instead (open question 1: lean lets GEPA co-adapt generate+verify). S1 always seeds
from the lean distilled verify rules.

Kill-criterion (scope §2): if this does not beat 0.731 by >= +0.03 on dev140, the
architectural lift is not single-model instruction-recoverable — stop and write the
negative.

~8 LLM calls/letter, so GPT-4.1-mini is the default arm.

Usage:
    uv run python experiments/gepa_multistage_exectv2.py
    uv run python experiments/gepa_multistage_exectv2.py --lean-s0
    uv run python experiments/gepa_multistage_exectv2.py --smoke
"""

from __future__ import annotations

import argparse
import json
import traceback
from datetime import UTC, datetime
from pathlib import Path

import dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import LengthPenaltyConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multistage import (
    build_multistage_program,
    combined_instruction,
    load_evolved_s0_seeds,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import (
    EXPERIMENTS,
    GEPA_LOG_ROOT,
    GepaExperimentConfig,
    run_experiment,
)

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = GEPA_LOG_ROOT / "multistage_status.json"
DATE = "2026-06-28"
SUFFIX = DATE.replace("-", "")
MINI = "openai/gpt-4.1-mini"
DEEPSEEK = "deepseek/deepseek-reasoner"

# Eight evolvable instructions (4 generate + 4 verify), so the instruction budget is
# larger than the multifamily's 2000 (~500/instruction). Output budget stays generous
# for the merged 4-family final output (the draft/verify intermediates are not stamped).
MULTISTAGE_PENALTY = LengthPenaltyConfig(instruction_token_budget=4000, output_token_budget=2000)


def _s0_seeds(lean_s0: bool) -> dict[str, str] | None:
    """Warm-start S0 from the evolved 0.731 instructions unless --lean-s0 is set.

    Falls back to lean (with a warning) if the evolved artifact is missing, so the
    smoke path never hard-fails on a clean checkout."""

    if lean_s0:
        return None
    try:
        return load_evolved_s0_seeds()
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ms] WARNING: warm-start unavailable ({exc}); seeding lean S0.", flush=True)
        return None


def _config(smoke: bool) -> GepaExperimentConfig:
    if smoke:
        return GepaExperimentConfig(
            run_id="exectv2_gepa_multistage_smoke_gpt41mini",
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
            length_penalty=MULTISTAGE_PENALTY,
            date=DATE,
            notes="multistage S0+S1 smoke; not a result.",
        )
    return GepaExperimentConfig(
        run_id=f"exectv2_gepa_multistage_dedup_gpt41mini_{SUFFIX}",
        task_model=MINI,
        reflection_model=DEEPSEEK,
        task_temperature=0.0,
        task_max_tokens=12000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=12,
        reflection_minibatch_size=8,
        length_penalty=MULTISTAGE_PENALTY,
        date=DATE,
        notes=(
            "Multi-stage (generate->verify) GEPA, Phase 1 of the multistage scope. Four "
            "per-family generate instructions (S0, warm-started from the 0.731 evolved "
            "run) + four per-family verify instructions (S1, lean distilled from the "
            "entity_verifier rules), evolved jointly with H1 diff-feedback + H2 "
            "minibatch=8. Tests whether an evolvable verify stage closes the architectural "
            "gap. Kill-criterion: beat 0.731 by >= +0.03 on dev140. Compare to per-family "
            "0.731, hand-tuned 0.710, v08 hybrid 0.9155."
        ),
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
    parser.add_argument(
        "--lean-s0",
        action="store_true",
        help="Seed S0 from the lean per-family signatures instead of warm-starting from 0.731.",
    )
    args = parser.parse_args()
    dotenv.load_dotenv(ROOT / ".env")

    config = _config(args.smoke)
    s0_seeds = _s0_seeds(args.lean_s0)
    warm_start = s0_seeds is not None
    status: dict = {
        "started_at": _now(),
        "smoke": args.smoke,
        "run_id": config.run_id,
        "s0_warm_start": warm_start,
    }
    summary_json = EXPERIMENTS / f"{config.run_id}.json"
    if summary_json.exists():
        print(f"[ms] skip {config.run_id} (summary exists)", flush=True)
        return

    status["state"] = "running"
    _write_status(status)
    print(
        f"[ms] start {config.run_id} (minibatch=8, 8 predictors, "
        f"S0={'warm-start' if warm_start else 'lean'})",
        flush=True,
    )
    try:
        payload = run_experiment(
            config,
            register=not args.smoke,
            seed_program=build_multistage_program(s0_seed_instructions=s0_seeds),
            final_instruction_fn=combined_instruction,
        )
        headline = payload["final_eval"]["clinical_headline"]
        status.update(
            state="done",
            finished_at=_now(),
            clinical_headline_overall_f1=headline["overall_f1"],
            per_family=headline["per_family"],
            strict_benchmark_per_item_f1=payload["final_eval"]["strict_benchmark_per_item_f1"],
            final_instruction_tokens=payload["final_instruction_tokens"],
            elapsed_seconds=payload["elapsed_seconds"],
        )
        print(
            f"[ms] done {config.run_id}: headline_f1={headline['overall_f1']} "
            f"per_family={headline['per_family']}",
            flush=True,
        )
    except Exception as exc:
        status.update(
            state="failed",
            finished_at=_now(),
            error=f"{type(exc).__name__}: {exc}",
            traceback=traceback.format_exc()[-3000:],
        )
        print(f"[ms] FAILED {config.run_id}: {exc}", flush=True)
    _write_status(status)


if __name__ == "__main__":
    main()
