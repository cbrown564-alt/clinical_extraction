"""H1 test: GEPA monolith with diff-enriched reflection feedback (resumable).

The metric (`gepa/metric.py`) now feeds the reflection LM a concrete per-family
gold-vs-pred diff (missed gold facts + spurious predicted facts) instead of only a
scalar score and generic hints. This launcher re-runs the single-instruction
monolith on mini under a NEW run_id so the result is directly comparable to the
pre-H1 monolith (0.628) and the hand-tuned plateau (0.710).

Usage:
    uv run python experiments/gepa_h1_diff_exectv2.py
    uv run python experiments/gepa_h1_diff_exectv2.py --smoke
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
STATUS_PATH = GEPA_LOG_ROOT / "h1_diff_status.json"
DATE = "2026-06-27"
SUFFIX = DATE.replace("-", "")
MINI = "openai/gpt-4.1-mini"
DEEPSEEK = "deepseek/deepseek-reasoner"


def _config(smoke: bool) -> GepaExperimentConfig:
    if smoke:
        return GepaExperimentConfig(
            run_id="exectv2_gepa_h1diff_smoke_gpt41mini",
            task_model=MINI,
            reflection_model=DEEPSEEK,
            auto=None,
            max_metric_calls=12,
            trainset_size=6,
            valset_size=4,
            final_eval_limit=4,
            num_threads=4,
            task_max_tokens=8000,
            reflection_max_tokens=8000,
            date=DATE,
            notes="H1 diff-feedback smoke; not a result.",
        )
    return GepaExperimentConfig(
        run_id=f"exectv2_gepa_dedup_gpt41mini_h1diff_{SUFFIX}",
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
            "H1: single-instruction monolith with diff-enriched reflection feedback "
            "(per-family missed-gold + spurious-pred). Compare to pre-H1 monolith 0.628 "
            "and hand-tuned 0.710. Tests whether uninformative feedback was the GEPA cap."
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
    args = parser.parse_args()
    dotenv.load_dotenv(ROOT / ".env")

    config = _config(args.smoke)
    status: dict = {"started_at": _now(), "smoke": args.smoke, "run_id": config.run_id}
    summary_json = EXPERIMENTS / f"{config.run_id}.json"
    if summary_json.exists():
        print(f"[h1] skip {config.run_id} (summary exists)", flush=True)
        return

    status["state"] = "running"
    _write_status(status)
    print(f"[h1] start {config.run_id} ({config.task_model})", flush=True)
    try:
        payload = run_experiment(config, register=not args.smoke)
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
            f"[h1] done {config.run_id}: headline_f1={headline['overall_f1']} "
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
        print(f"[h1] FAILED {config.run_id}: {exc}", flush=True)
    _write_status(status)


if __name__ == "__main__":
    main()
