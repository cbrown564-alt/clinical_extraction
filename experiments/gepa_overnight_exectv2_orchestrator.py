"""Overnight GEPA orchestrator for ExECTv2 de-dup clinical facts (resumable).

Runs a sequential queue of GEPA from-scratch experiments on the de-dup
``clinical_headline`` surface: GPT-4.1-mini first (apples-to-apples with the
hand-tuned 0.710 dev140 plateau), then deepseek-reasoner, then a length-penalty
ablation arm (penalty disabled) to confirm the penalty is what controls prompt
bloat. Each experiment is resumable at experiment granularity (one whose summary
JSON already exists is skipped). A status JSON is rewritten after every state
change so a monitoring loop can report progress without parsing logs.

Usage:
    uv run python experiments/gepa_overnight_exectv2_orchestrator.py
    uv run python experiments/gepa_overnight_exectv2_orchestrator.py --only mini
    uv run python experiments/gepa_overnight_exectv2_orchestrator.py --smoke
"""

from __future__ import annotations

import argparse
import json
import traceback
from datetime import UTC, datetime
from pathlib import Path

import dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import LengthPenaltyConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import (
    EXPERIMENTS,
    GEPA_LOG_ROOT,
    GepaExperimentConfig,
    run_experiment,
)

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = GEPA_LOG_ROOT / "orchestrator_status.json"
DATE = "2026-06-27"
SUFFIX = DATE.replace("-", "")

MINI = "openai/gpt-4.1-mini"
DEEPSEEK = "deepseek/deepseek-reasoner"


def _queue() -> list[GepaExperimentConfig]:
    """mini -> deepseek -> mini length-penalty ablation (operator-requested order)."""

    return [
        GepaExperimentConfig(
            run_id=f"exectv2_gepa_from_scratch_dedup_gpt41mini_{SUFFIX}",
            task_model=MINI,
            reflection_model=DEEPSEEK,
            task_temperature=0.0,
            task_max_tokens=12000,
            reflection_max_tokens=12000,
            auto="medium",
            num_threads=12,
            length_penalty=LengthPenaltyConfig(),
            date=DATE,
            notes=(
                "From-scratch GEPA on the de-dup clinical_headline surface, GPT-4.1-mini "
                "task + deepseek-reasoner reflection, length-penalized. Apples-to-apples "
                "with the hand-tuned 0.710 dev140 single-prompt plateau (plan 13)."
            ),
        ),
        GepaExperimentConfig(
            run_id=f"exectv2_gepa_from_scratch_dedup_deepseek_reasoner_{SUFFIX}",
            task_model=DEEPSEEK,
            reflection_model=DEEPSEEK,
            task_temperature=0.0,
            task_max_tokens=12000,
            reflection_max_tokens=12000,
            auto="medium",
            num_threads=12,
            length_penalty=LengthPenaltyConfig(),
            date=DATE,
            notes=(
                "From-scratch GEPA, deepseek-reasoner task+reflection, length-penalized. "
                "Mirrors the Gan run's single-model setup; transfer arm vs the mini run."
            ),
        ),
        GepaExperimentConfig(
            run_id=f"exectv2_gepa_from_scratch_dedup_gpt41mini_nolengthpenalty_{SUFFIX}",
            task_model=MINI,
            reflection_model=DEEPSEEK,
            task_temperature=0.0,
            task_max_tokens=12000,
            reflection_max_tokens=12000,
            auto="medium",
            num_threads=12,
            length_penalty=LengthPenaltyConfig(enabled=False),
            date=DATE,
            notes=(
                "Length-penalty ABLATION: penalty disabled in both selection and feedback. "
                "Tests whether the penalty is what keeps the evolved instruction lean "
                "(the Gan finding) on ExECTv2."
            ),
        ),
    ]


def _smoke_queue() -> list[GepaExperimentConfig]:
    return [
        GepaExperimentConfig(
            run_id="exectv2_gepa_smoke_gpt41mini",
            task_model=MINI,
            reflection_model=DEEPSEEK,
            task_max_tokens=8000,
            reflection_max_tokens=8000,
            auto=None,
            max_metric_calls=12,
            trainset_size=6,
            valset_size=4,
            final_eval_limit=4,
            num_threads=4,
            date=DATE,
            notes="End-to-end smoke; not a result.",
        ),
    ]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write_status(status: dict) -> None:
    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    status["updated_at"] = _now()
    STATUS_PATH.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["mini", "deepseek", "ablation"], default=None)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    dotenv.load_dotenv(ROOT / ".env")

    queue = _smoke_queue() if args.smoke else _queue()
    if args.only == "mini":
        queue = [c for c in queue if c.task_model == MINI and c.length_penalty.enabled]
    elif args.only == "deepseek":
        queue = [c for c in queue if c.task_model == DEEPSEEK]
    elif args.only == "ablation":
        queue = [c for c in queue if not c.length_penalty.enabled]

    status: dict = {
        "started_at": _now(),
        "smoke": args.smoke,
        "queue": [c.run_id for c in queue],
        "experiments": {},
    }
    _write_status(status)

    for config in queue:
        summary_json = EXPERIMENTS / f"{config.run_id}.json"
        if summary_json.exists():
            status["experiments"][config.run_id] = {
                "state": "skipped_already_done",
                "task_model": config.task_model,
            }
            _write_status(status)
            print(f"[orchestrator] skip {config.run_id} (summary exists)", flush=True)
            continue

        status["experiments"][config.run_id] = {
            "state": "running",
            "task_model": config.task_model,
            "started_at": _now(),
        }
        _write_status(status)
        print(f"[orchestrator] start {config.run_id} ({config.task_model})", flush=True)

        try:
            payload = run_experiment(config, register=not args.smoke)
            headline = payload["final_eval"]["clinical_headline"]
            status["experiments"][config.run_id] = {
                "state": "done",
                "task_model": config.task_model,
                "finished_at": _now(),
                "clinical_headline_overall_f1": headline["overall_f1"],
                "per_family": headline["per_family"],
                "strict_benchmark_per_item_f1": payload["final_eval"][
                    "strict_benchmark_per_item_f1"
                ],
                "final_instruction_tokens": payload["final_instruction_tokens"],
                "seed_instruction_tokens": payload["seed_instruction_tokens"],
                "elapsed_seconds": payload["elapsed_seconds"],
            }
            print(
                f"[orchestrator] done {config.run_id}: "
                f"headline_f1={headline['overall_f1']} "
                f"instr_tokens={payload['final_instruction_tokens']}",
                flush=True,
            )
        except Exception as exc:  # keep the queue alive; record the failure
            status["experiments"][config.run_id] = {
                "state": "failed",
                "task_model": config.task_model,
                "finished_at": _now(),
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc()[-3000:],
            }
            print(f"[orchestrator] FAILED {config.run_id}: {exc}", flush=True)
        _write_status(status)

    status["finished_at"] = _now()
    _write_status(status)
    print("[orchestrator] queue complete", flush=True)


if __name__ == "__main__":
    main()
