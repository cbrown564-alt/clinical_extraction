"""Overnight GEPA orchestrator for Gan 2026 (resumable, status-emitting).

Runs a sequential queue of GEPA from-scratch experiments — deepseek-reasoner
first, Qwen second, per operator request — each resumable at experiment
granularity (an experiment whose summary JSON already exists is skipped). A
status JSON is rewritten after every state change so a monitoring loop can
report progress without parsing logs.

Usage:
    uv run python experiments/gepa_overnight_orchestrator.py
    uv run python experiments/gepa_overnight_orchestrator.py --only deepseek
    uv run python experiments/gepa_overnight_orchestrator.py --smoke
"""

from __future__ import annotations

import argparse
import json
import traceback
from datetime import UTC, datetime
from pathlib import Path

import dotenv

from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.metric import LengthPenaltyConfig
from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.run_gepa import (
    EXPERIMENTS,
    GEPA_LOG_ROOT,
    GepaExperimentConfig,
    run_experiment,
)

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = GEPA_LOG_ROOT / "orchestrator_status.json"
DATE = "2026-06-27"


def _queue() -> list[GepaExperimentConfig]:
    """The overnight queue: from-scratch GEPA on deepseek-reasoner, then Qwen.

    DeepSeek is API-parallel so it runs at medium. Qwen is a local 35B on partial
    GPU offload; its budget is sized down (and final eval narrowed) so it actually
    completes overnight. This down-sizing is deliberate and recorded, not silent.
    """

    return [
        GepaExperimentConfig(
            run_id=f"gan2026_gepa_from_scratch_deepseek_reasoner_{DATE.replace('-', '')}",
            task_model="deepseek/deepseek-reasoner",
            reflection_model="deepseek/deepseek-reasoner",
            task_temperature=0.0,
            task_max_tokens=12000,
            reflection_max_tokens=12000,
            auto="medium",
            valset_size=200,
            final_eval_split="validation",
            num_threads=12,
            length_penalty=LengthPenaltyConfig(),
            date=DATE,
            notes="From-scratch GEPA, deepseek-reasoner task+reflection, length-penalized.",
        ),
        GepaExperimentConfig(
            # Model substitution (overnight hardware reality, recorded not silent):
            #  - qwen3.6:35b OOM-killed the driver (~21GB RAM, only ~1.5GB free).
            #  - qwen3.6:27b fit RAM (~6GB free) but was far too slow (~43s for a
            #    trivial call at ~27% GPU offload -> a 750-call run would take 12-25h).
            #  - qwen3.5:9b fits with huge headroom and returns valid JSON in ~1-5s/call,
            #    so it is the only local Qwen that completes overnight here. Re-run a
            #    larger Qwen once the machine has free RAM + better GPU offload.
            run_id=f"gan2026_gepa_from_scratch_qwen3p5_9b_{DATE.replace('-', '')}",
            task_model="ollama_chat/qwen3.5:9b",
            reflection_model="deepseek/deepseek-reasoner",
            task_temperature=0.0,
            task_max_tokens=3000,
            reflection_max_tokens=12000,
            auto=None,
            max_metric_calls=500,
            valset_size=80,
            final_eval_split="validation",
            final_eval_limit=250,
            num_threads=1,
            length_penalty=LengthPenaltyConfig(),
            date=DATE,
            notes=(
                "From-scratch GEPA, local Qwen 3.5 9B task model (substituted for 35B "
                "OOM and 27B too-slow on this box; 9B is the only local Qwen that "
                "completes overnight here), deepseek-reasoner reflection. Budget+eval "
                "down-sized for local throughput; model substitution + reduced surface "
                "recorded. Result is a small-model lower bound, not the 35B intent."
            ),
        ),
    ]


def _smoke_queue() -> list[GepaExperimentConfig]:
    return [
        GepaExperimentConfig(
            run_id="gan2026_gepa_smoke_deepseek_reasoner",
            task_model="deepseek/deepseek-reasoner",
            reflection_model="deepseek/deepseek-reasoner",
            task_max_tokens=8000,
            reflection_max_tokens=8000,
            auto=None,
            max_metric_calls=12,
            valset_size=4,
            trainset_size=6,
            final_eval_split="validation",
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
    parser.add_argument("--only", choices=["deepseek", "qwen"], default=None)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    dotenv.load_dotenv(ROOT / ".env")

    queue = _smoke_queue() if args.smoke else _queue()
    if args.only == "deepseek":
        queue = [c for c in queue if "deepseek" in c.task_model]
    elif args.only == "qwen":
        queue = [c for c in queue if "qwen" in c.task_model]

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
            status["experiments"][config.run_id] = {
                "state": "done",
                "task_model": config.task_model,
                "finished_at": _now(),
                "purist_accuracy": payload["final_eval"]["purist_accuracy"],
                "final_instruction_tokens": payload["final_instruction_tokens"],
                "seed_instruction_tokens": payload["seed_instruction_tokens"],
                "elapsed_seconds": payload["elapsed_seconds"],
            }
            print(
                f"[orchestrator] done {config.run_id}: "
                f"purist={payload['final_eval']['purist_accuracy']} "
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
