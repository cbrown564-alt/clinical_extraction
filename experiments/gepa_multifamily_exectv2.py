"""GEPA over the per-family multi-signature ExECTv2 program (resumable).

Follow-up to the monolith negative result: optimize four per-family instructions
(Diagnosis, SeizureFrequency, Prescription, Investigation) independently, so GEPA
can grow the dedicated per-family scaffolding the single instruction could not.
Each rollout is 4 LLM calls/letter, so GPT-4.1-mini is the default arm; the
deepseek-reasoner arm is opt-in (--deepseek) because 4x reasoning-model calls are
slow/costly.

Usage:
    uv run python experiments/gepa_multifamily_exectv2.py
    uv run python experiments/gepa_multifamily_exectv2.py --deepseek
    uv run python experiments/gepa_multifamily_exectv2.py --smoke
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
STATUS_PATH = GEPA_LOG_ROOT / "multifamily_status.json"
DATE = "2026-06-27"
SUFFIX = DATE.replace("-", "")

MINI = "openai/gpt-4.1-mini"
DEEPSEEK = "deepseek/deepseek-reasoner"

# Four instructions, so the total instruction budget is larger than the monolith's
# 600 (~500/family). Output budget stays generous (merged 4-family output).
MULTIFAMILY_PENALTY = LengthPenaltyConfig(instruction_token_budget=2000, output_token_budget=2000)


def _config(run_id: str, task_model: str, **overrides) -> GepaExperimentConfig:
    base = dict(
        run_id=run_id,
        task_model=task_model,
        reflection_model=DEEPSEEK,
        task_temperature=0.0,
        task_max_tokens=12000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=12,
        length_penalty=MULTIFAMILY_PENALTY,
        date=DATE,
        notes=(
            "GEPA over the per-family multi-signature program (4 evolvable instructions, "
            "4 LLM calls/letter). Tests whether dedicated per-family scaffolding closes "
            "the Diagnosis/SeizureFrequency gap the monolith could not."
        ),
    )
    base.update(overrides)
    return GepaExperimentConfig(**base)


def _queue(args: argparse.Namespace) -> list[GepaExperimentConfig]:
    if args.smoke:
        return [
            _config(
                "exectv2_gepa_multifamily_smoke_gpt41mini",
                MINI,
                auto=None,
                max_metric_calls=12,
                trainset_size=6,
                valset_size=4,
                final_eval_limit=4,
                num_threads=4,
                task_max_tokens=8000,
                reflection_max_tokens=8000,
            )
        ]
    queue = [_config(f"exectv2_gepa_multifamily_dedup_gpt41mini_{SUFFIX}", MINI)]
    if args.deepseek:
        queue.append(
            _config(f"exectv2_gepa_multifamily_dedup_deepseek_reasoner_{SUFFIX}", DEEPSEEK)
        )
    return queue


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write_status(status: dict) -> None:
    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    status["updated_at"] = _now()
    STATUS_PATH.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deepseek", action="store_true", help="Also run the deepseek-reasoner arm."
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    dotenv.load_dotenv(ROOT / ".env")
    queue = _queue(args)

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
            status["experiments"][config.run_id] = {"state": "skipped_already_done"}
            _write_status(status)
            print(f"[multifamily] skip {config.run_id} (summary exists)", flush=True)
            continue

        status["experiments"][config.run_id] = {
            "state": "running",
            "task_model": config.task_model,
            "started_at": _now(),
        }
        _write_status(status)
        print(f"[multifamily] start {config.run_id} ({config.task_model})", flush=True)

        try:
            payload = run_experiment(
                config,
                register=not args.smoke,
                seed_program=build_per_family_program(),
                final_instruction_fn=combined_instruction,
            )
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
                f"[multifamily] done {config.run_id}: headline_f1={headline['overall_f1']} "
                f"per_family={headline['per_family']}",
                flush=True,
            )
        except Exception as exc:
            status["experiments"][config.run_id] = {
                "state": "failed",
                "task_model": config.task_model,
                "finished_at": _now(),
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc()[-3000:],
            }
            print(f"[multifamily] FAILED {config.run_id}: {exc}", flush=True)
        _write_status(status)

    status["finished_at"] = _now()
    _write_status(status)
    print("[multifamily] queue complete", flush=True)


if __name__ == "__main__":
    main()
