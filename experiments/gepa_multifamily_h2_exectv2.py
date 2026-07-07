"""Multi-family GEPA re-run with the H1 + H2 fixes (resumable).

The per-family multi-signature program was flat at 0.631 dev140 — but that run
predated both fixes the investigation has since validated: the H1 diff-feedback
metric (now the default in ``gepa/metric.py``) and the H2 cut to selection noise
(``reflection_minibatch_size=8``; the noise-dominated minibatch=3 gate was the cap
in the monolith). This launcher re-runs the four per-family instructions
(Diagnosis, SeizureFrequency, Prescription, Investigation) with both fixes so each
family can be optimized independently — removing the single-instruction Dx↔SF
tradeoff that capped the H2 monolith at 0.719.

Compare to: multifamily pre-fix 0.631, H2 monolith 0.719, hand-tuned 0.710,
v08 hybrid 0.9155.

Usage:
    uv run python experiments/gepa_multifamily_h2_exectv2.py
    uv run python experiments/gepa_multifamily_h2_exectv2.py --smoke
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
STATUS_PATH = GEPA_LOG_ROOT / "multifamily_h2_status.json"
DATE = "2026-06-28"
SUFFIX = DATE.replace("-", "")
MINI = "openai/gpt-4.1-mini"
DEEPSEEK = "deepseek/deepseek-reasoner"

# Four instructions, so the instruction budget is larger than the monolith's 600
# (~500/family); output budget stays generous for the merged 4-family output.
MULTIFAMILY_PENALTY = LengthPenaltyConfig(instruction_token_budget=2000, output_token_budget=2000)


def _config(smoke: bool) -> GepaExperimentConfig:
    if smoke:
        return GepaExperimentConfig(
            run_id="exectv2_gepa_multifamily_h2mb8_smoke_gpt41mini",
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
            date=DATE,
            notes="multifamily H1+H2 smoke; not a result.",
        )
    return GepaExperimentConfig(
        run_id=f"exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_{SUFFIX}",
        task_model=MINI,
        reflection_model=DEEPSEEK,
        task_temperature=0.0,
        task_max_tokens=12000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=12,
        reflection_minibatch_size=8,
        length_penalty=MULTIFAMILY_PENALTY,
        date=DATE,
        notes=(
            "Multi-family multi-signature GEPA re-run with BOTH fixes: H1 diff-feedback "
            "metric (default) + H2 reflection_minibatch_size=8 (vs 3 in the flat 0.631 run). "
            "Four per-family instructions optimized independently to remove the monolith "
            "Dx<->SF tradeoff (H2 monolith: Dx 0.66 / SF 0.54 -> 0.719). Compare to "
            "multifamily pre-fix 0.631, H2 monolith 0.719, hand-tuned 0.710, hybrid 0.9155."
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
        print(f"[mf-h2] skip {config.run_id} (summary exists)", flush=True)
        return

    status["state"] = "running"
    _write_status(status)
    print(f"[mf-h2] start {config.run_id} (minibatch=8, 4 predictors)", flush=True)
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
            per_family=headline["per_family"],
            strict_benchmark_per_item_f1=payload["final_eval"]["strict_benchmark_per_item_f1"],
            final_instruction_tokens=payload["final_instruction_tokens"],
            elapsed_seconds=payload["elapsed_seconds"],
        )
        print(
            f"[mf-h2] done {config.run_id}: headline_f1={headline['overall_f1']} "
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
        print(f"[mf-h2] FAILED {config.run_id}: {exc}", flush=True)
    _write_status(status)


if __name__ == "__main__":
    main()
