"""Qwen cross-model GEPA runs for ExECTv2 de-dup clinical facts (resumable).

Closes the one cross-model gap the GEPA-from-scratch investigation left open: every
result so far ran GPT-4.1-mini (and a deepseek-reasoner transfer arm) as the task
model, never the local Qwen, which was skipped for practicality at the time. This
orchestrator replays the two *best* mini configurations with Qwen 3.6 35B as the
task model and deepseek-reasoner as the reflection (teacher) model, so the numbers
sit beside the mini ones on exactly the same surface:

  - SINGLE-PROMPT monolith  -> mirrors ``gepa_h2_minibatch_exectv2.py``
        (mini best: dev140 clinical_headline 0.719)
  - MULTI-FAMILY 4-signature -> mirrors ``gepa_multifamily_h2_exectv2.py``
        (mini best: dev140 clinical_headline 0.731)

Both carry the H1 diff-feedback metric (now the default in ``gepa/metric.py``) and
the H2 fix ``reflection_minibatch_size=8``; the ONLY deliberately changed variables
vs the mini runs are the task model and the local-hardware knobs (single-threaded,
generous output budget inside the OOM-safe 16k context). Budget is ``auto="medium"``
to stay apples-to-apples with the mini runs.

Comparators (dev140 clinical_headline): Qwen hand-tuned single-prompt plateau 0.694,
mini GEPA single 0.719 / multi 0.731, v08 hybrid 0.9155.

Qwen is a LOCAL 35B on Ollama (partial GPU offload). Start the server and pull the
model first; the run is single-threaded and slow (~16s/call warm), so expect a long
overnight for both arms at medium budget. Each arm is resumable at experiment
granularity (an arm whose summary JSON already exists is skipped), and a status JSON
is rewritten after every state change.

Usage:
    uv run python experiments/gepa_qwen_cross_model_exectv2.py
    uv run python experiments/gepa_qwen_cross_model_exectv2.py --only single
    uv run python experiments/gepa_qwen_cross_model_exectv2.py --only multi
    uv run python experiments/gepa_qwen_cross_model_exectv2.py --smoke
"""

from __future__ import annotations

import argparse
import json
import os
import traceback
from dataclasses import dataclass
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
STATUS_PATH = GEPA_LOG_ROOT / "qwen_cross_model_status.json"
DATE = "2026-06-29"
SUFFIX = DATE.replace("-", "")

QWEN = "ollama_chat/qwen3.6:35b"
DEEPSEEK = "deepseek/deepseek-reasoner"

#: OOM-safe local context window for the 35B on partial GPU offload (verified note).
#: dev letters are tiny (max ~1071 tok, median 296), so 16k comfortably holds the
#: letter + schema + evolved instruction with room to spare for the output budget.
OLLAMA_NUM_CTX = "16384"
#: The multi-family arm carries four instructions, so it gets the same larger
#: instruction/output budget the mini multi-family run used.
MULTIFAMILY_PENALTY = LengthPenaltyConfig(instruction_token_budget=2000, output_token_budget=2000)


@dataclass(frozen=True)
class QwenRun:
    """One Qwen GEPA arm: its config plus which program shape to optimize."""

    config: GepaExperimentConfig
    is_multifamily: bool


def _single_config(*, smoke: bool) -> GepaExperimentConfig:
    if smoke:
        return GepaExperimentConfig(
            run_id="exectv2_gepa_dedup_qwen3p6_35b_smoke",
            task_model=QWEN,
            reflection_model=DEEPSEEK,
            auto=None,
            max_metric_calls=12,
            trainset_size=6,
            valset_size=4,
            final_eval_limit=4,
            num_threads=1,
            reflection_minibatch_size=8,
            task_max_tokens=4000,
            reflection_max_tokens=8000,
            date=DATE,
            notes="Qwen single-prompt smoke; not a result.",
        )
    return GepaExperimentConfig(
        run_id=f"exectv2_gepa_dedup_qwen3p6_35b_h2mb8_{SUFFIX}",
        task_model=QWEN,
        reflection_model=DEEPSEEK,
        task_temperature=0.0,
        task_max_tokens=6000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=1,
        reflection_minibatch_size=8,
        length_penalty=LengthPenaltyConfig(),
        date=DATE,
        notes=(
            "Qwen 3.6 35B (local) single-instruction monolith, deepseek-reasoner reflection. "
            "Cross-model replay of the mini H2 best (0.719): H1 diff-feedback metric (default) "
            "+ reflection_minibatch_size=8, auto=medium. Single-threaded local 35B. Compare to "
            "Qwen hand-tuned 0.694, mini GEPA single 0.719, multi 0.731, v08 hybrid 0.9155."
        ),
    )


def _multi_config(*, smoke: bool) -> GepaExperimentConfig:
    if smoke:
        return GepaExperimentConfig(
            run_id="exectv2_gepa_multifamily_dedup_qwen3p6_35b_smoke",
            task_model=QWEN,
            reflection_model=DEEPSEEK,
            auto=None,
            max_metric_calls=12,
            trainset_size=6,
            valset_size=4,
            final_eval_limit=4,
            num_threads=1,
            reflection_minibatch_size=8,
            task_max_tokens=4000,
            reflection_max_tokens=8000,
            length_penalty=MULTIFAMILY_PENALTY,
            date=DATE,
            notes="Qwen multi-family smoke; not a result.",
        )
    return GepaExperimentConfig(
        run_id=f"exectv2_gepa_multifamily_dedup_qwen3p6_35b_h2mb8_{SUFFIX}",
        task_model=QWEN,
        reflection_model=DEEPSEEK,
        task_temperature=0.0,
        task_max_tokens=6000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=1,
        reflection_minibatch_size=8,
        length_penalty=MULTIFAMILY_PENALTY,
        date=DATE,
        notes=(
            "Qwen 3.6 35B (local) multi-family 4-signature program, deepseek-reasoner reflection. "
            "Cross-model replay of the mini multi-family H2 best (0.731): H1 diff-feedback metric "
            "(default) + reflection_minibatch_size=8, auto=medium, four per-family instructions "
            "optimized independently. Single-threaded local 35B. Compare to Qwen hand-tuned 0.694, "
            "mini GEPA single 0.719, multi 0.731, v08 hybrid 0.9155."
        ),
    )


def _queue(*, smoke: bool) -> list[QwenRun]:
    return [
        QwenRun(_single_config(smoke=smoke), is_multifamily=False),
        QwenRun(_multi_config(smoke=smoke), is_multifamily=True),
    ]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write_status(status: dict) -> None:
    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    status["updated_at"] = _now()
    STATUS_PATH.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_arm(arm: QwenRun, *, register: bool):
    if arm.is_multifamily:
        return run_experiment(
            arm.config,
            register=register,
            seed_program=build_per_family_program(),
            final_instruction_fn=combined_instruction,
        )
    return run_experiment(arm.config, register=register)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["single", "multi"], default=None)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    dotenv.load_dotenv(ROOT / ".env")
    # Pin the local context window for the 35B (OOM-safe value); leave num_gpu unset
    # so Ollama keeps its auto partial-GPU offload (pinning num_gpu=0 forces CPU-only).
    os.environ.setdefault("CLINICAL_EXTRACTION_OLLAMA_NUM_CTX", OLLAMA_NUM_CTX)

    queue = _queue(smoke=args.smoke)
    if args.only == "single":
        queue = [a for a in queue if not a.is_multifamily]
    elif args.only == "multi":
        queue = [a for a in queue if a.is_multifamily]

    status: dict = {
        "started_at": _now(),
        "smoke": args.smoke,
        "task_model": QWEN,
        "reflection_model": DEEPSEEK,
        "num_ctx": os.environ.get("CLINICAL_EXTRACTION_OLLAMA_NUM_CTX"),
        "queue": [a.config.run_id for a in queue],
        "experiments": {},
    }
    _write_status(status)

    for arm in queue:
        config = arm.config
        summary_json = EXPERIMENTS / f"{config.run_id}.json"
        if summary_json.exists():
            status["experiments"][config.run_id] = {"state": "skipped_already_done"}
            _write_status(status)
            print(f"[qwen-xm] skip {config.run_id} (summary exists)", flush=True)
            continue

        status["experiments"][config.run_id] = {"state": "running", "started_at": _now()}
        _write_status(status)
        shape = "multi-family" if arm.is_multifamily else "single-prompt"
        print(f"[qwen-xm] start {config.run_id} ({shape}, {config.task_model})", flush=True)

        try:
            payload = _run_arm(arm, register=not args.smoke)
            eval_summary = payload["final_eval"]
            headline = eval_summary["clinical_headline"]
            status["experiments"][config.run_id] = {
                "state": "done",
                "finished_at": _now(),
                "clinical_headline_overall_f1": headline["overall_f1"],
                "per_family": headline["per_family"],
                "strict_benchmark_per_item_f1": eval_summary["strict_benchmark_per_item_f1"],
                "final_instruction_tokens": payload["final_instruction_tokens"],
                "elapsed_seconds": payload["elapsed_seconds"],
            }
            print(
                f"[qwen-xm] done {config.run_id}: headline_f1={headline['overall_f1']} "
                f"per_family={headline['per_family']}",
                flush=True,
            )
        except Exception as exc:  # keep the queue alive; record the failure
            status["experiments"][config.run_id] = {
                "state": "failed",
                "finished_at": _now(),
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc()[-3000:],
            }
            print(f"[qwen-xm] FAILED {config.run_id}: {exc}", flush=True)
        _write_status(status)

    status["finished_at"] = _now()
    _write_status(status)
    print("[qwen-xm] queue complete", flush=True)


if __name__ == "__main__":
    main()
