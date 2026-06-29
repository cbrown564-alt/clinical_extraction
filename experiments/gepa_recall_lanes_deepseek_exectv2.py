"""Phase 0c/1 of the focused-lanes recall plan: replicate the hybrid's producer recall
with GEPA, on a DeepSeek task model.

Plan: docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md. The GEPA->hybrid
gap is producer evidence-retrieval (ev-recall 0.694 vs 0.883), so this run (a) swaps the
extraction model to DeepSeek (less GPT reliance; hand-tuned dev140 DeepSeek 0.745 > mini
0.710) and (b) reseeds the Diagnosis + SeizureFrequency lanes with recall-oriented
instructions (program_recall_lanes). The run_gepa summary now reports producer evidence-
recall (source_near) alongside clinical_headline so the retrieval lever is visible.

Arms:
* ``--baseline``  Phase 0c: the EXISTING per-family program (program_multifamily) on the
  DeepSeek task model — isolates the model swap from the schema change.
* default          Phase 1: the recall-oriented lanes (program_recall_lanes) on DeepSeek.

Compare to: per-family F1 baseline (mini) 0.731 / ev-recall 0.694; v08 hybrid 0.920 /
ev-recall 0.883. Gate (Phase 1): >= 0.761 headline AND ev-recall >= 0.74.

Usage:
    uv run python experiments/gepa_recall_lanes_deepseek_exectv2.py --smoke
    uv run python experiments/gepa_recall_lanes_deepseek_exectv2.py --baseline
    uv run python experiments/gepa_recall_lanes_deepseek_exectv2.py
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
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multifamily import (
    combined_instruction as multifamily_combined_instruction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_recall_lanes import (
    build_recall_lanes_program,
    combined_instruction as recall_combined_instruction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import (
    EXPERIMENTS,
    GEPA_LOG_ROOT,
    GepaExperimentConfig,
    run_experiment,
)

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-28"
SUFFIX = DATE.replace("-", "")
DEEPSEEK_CHAT = "deepseek/deepseek-chat"
DEEPSEEK_REASONER = "deepseek/deepseek-reasoner"

# Four instructions; recall lanes run a touch longer than the lean per-family seeds.
RECALL_PENALTY = LengthPenaltyConfig(instruction_token_budget=2400, output_token_budget=2400)


def _config(*, smoke: bool, baseline: bool) -> GepaExperimentConfig:
    arm = "baseline_multifamily" if baseline else "recall_lanes"
    if smoke:
        return GepaExperimentConfig(
            run_id=f"exectv2_gepa_{arm}_deepseekchat_smoke",
            task_model=DEEPSEEK_CHAT,
            reflection_model=DEEPSEEK_REASONER,
            auto=None,
            max_metric_calls=24,
            trainset_size=8,
            valset_size=6,
            final_eval_limit=4,
            num_threads=4,
            reflection_minibatch_size=8,
            task_max_tokens=8000,
            reflection_max_tokens=8000,
            length_penalty=RECALL_PENALTY,
            date=DATE,
            notes=f"{arm} DeepSeek-chat smoke; not a result.",
        )
    return GepaExperimentConfig(
        run_id=f"exectv2_gepa_{arm}_deepseekchat_{SUFFIX}",
        task_model=DEEPSEEK_CHAT,
        reflection_model=DEEPSEEK_REASONER,
        task_temperature=0.0,
        task_max_tokens=12000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=12,
        reflection_minibatch_size=8,
        length_penalty=RECALL_PENALTY,
        date=DATE,
        notes=(
            f"Focused-lanes recall plan, arm={arm}, task model DeepSeek-chat. "
            "Phase 0c baseline = existing per-family program (model swap only); "
            "Phase 1 recall_lanes = recall-oriented Dx (exhaustive co-present) + SF "
            "(per-type multiplicity + changed class) seeds. run_gepa now reports producer "
            "evidence-recall (source_near). Compare: mini per-family 0.731 / ev-recall 0.694; "
            "v08 hybrid 0.920 / ev-recall 0.883."
        ),
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--baseline", action="store_true",
                        help="Phase 0c: existing per-family program on DeepSeek (model swap only).")
    args = parser.parse_args()
    dotenv.load_dotenv(ROOT / ".env")

    config = _config(smoke=args.smoke, baseline=args.baseline)
    status_path = GEPA_LOG_ROOT / f"{config.run_id}_status.json"
    summary_json = EXPERIMENTS / f"{config.run_id}.json"
    if summary_json.exists():
        print(f"[recall-lanes] skip {config.run_id} (summary exists)", flush=True)
        return

    if args.baseline:
        seed_program = build_per_family_program()
        final_instruction_fn = multifamily_combined_instruction
    else:
        seed_program = build_recall_lanes_program()
        final_instruction_fn = recall_combined_instruction

    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    status: dict = {"started_at": _now(), "smoke": args.smoke, "run_id": config.run_id,
                    "arm": "baseline" if args.baseline else "recall_lanes", "state": "running"}
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[recall-lanes] start {config.run_id} (task=DeepSeek-chat, 4 predictors)", flush=True)
    try:
        payload = run_experiment(
            config,
            register=not args.smoke,
            seed_program=seed_program,
            final_instruction_fn=final_instruction_fn,
        )
        headline = payload["final_eval"]["clinical_headline"]
        ev = payload["final_eval"]["evidence_recall"]
        status.update(
            state="done", finished_at=_now(),
            clinical_headline_overall_f1=headline["overall_f1"],
            per_family=headline["per_family"],
            evidence_recall_overall=ev["overall_recall"],
            evidence_recall_per_family=ev["per_family"],
            final_instruction_tokens=payload["final_instruction_tokens"],
            elapsed_seconds=payload["elapsed_seconds"],
        )
        print(
            f"[recall-lanes] done {config.run_id}: headline_f1={headline['overall_f1']} "
            f"ev_recall={ev['overall_recall']} per_family={headline['per_family']}",
            flush=True,
        )
    except Exception as exc:
        status.update(state="failed", finished_at=_now(), error=f"{type(exc).__name__}: {exc}",
                      traceback=traceback.format_exc()[-3000:])
        print(f"[recall-lanes] FAILED {config.run_id}: {exc}", flush=True)
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
