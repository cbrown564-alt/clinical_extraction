"""Investigations-only GEPA lane, DeepSeek-reasoner task model (resumable).

Follow-up to the ev-recall consolidation re-examination plan, Phase 4
(``docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md``,
``docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md``):
Investigations is the one ``KEY_FAMILIES`` member where the GEPA-vs-hybrid evidence-recall
gap is a clean negative (genuine retrieval miss, not gold-consolidation inflation) with a
SPECIFIC, actionable shape -- the large majority of its 20 genuine ``source_near`` misses are
an absent EEG in a letter that ALSO reports an MRI (MRI-anchoring bias, not a representation
problem). This is the one well-targeted "build more retrieval" lever the four-family sweep
left standing.

This run isolates that fix with two restrictions vs the existing per-family launchers:

1. Program (``program_investigations_lane.GepaInvestigationsLaneExtractor``): Diagnosis /
   SeizureFrequency / Prescription keep program_multifamily's UNCHANGED lean seeds; only the
   Investigation predictor is reseeded with an explicit multi-modality-enumeration
   instruction naming the MRI/EEG failure mode directly.
2. Component selector: GEPA's reflective mutation is restricted to the ``investigation``
   named predictor only (a custom ``ReflectionComponentSelector``, vs the default
   round-robin that would also drift the other three lanes) -- so every reflection call and
   every accepted mutation is spent on the one family this run is testing, and the other
   three lanes are provably frozen at their seed instruction for the whole run.

Task model is ``deepseek/deepseek-reasoner`` (vs deepseek-chat used in the prior recall-lanes
run) -- reasoning is plausibly suited to the "scan the whole letter for EACH modality, don't
anchor on the first one found" instruction, the same rationale already used for the Diagnosis
lane in the focused-lanes plan's Phase 2 notes. Reflection model is also deepseek-reasoner
(dspy's existing default for this package).

Baseline note (see program_investigations_lane.py docstring for detail): the Phase 4
adjudication's reference numbers (mini per-family: Investigations headline 0.858, ev-recall
0.801) are NOT the bar this run targets -- an earlier, unrelated DeepSeek-chat model swap
already lifted Investigations to headline ~0.92-0.93 / ev-recall ~0.93-0.94, at or above the
v08 hybrid's 0.913. Compare this run's Investigations column against THAT DeepSeek-chat
number, not the mini number.

Usage:
    uv run python experiments/gepa_investigations_lane_deepseek_reasoner_exectv2.py --smoke
    uv run python experiments/gepa_investigations_lane_deepseek_reasoner_exectv2.py
"""

from __future__ import annotations

import argparse
import json
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import LengthPenaltyConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_investigations_lane import (
    build_investigations_lane_program,
    combined_instruction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import (
    EXPERIMENTS,
    GEPA_LOG_ROOT,
    GepaExperimentConfig,
    run_experiment,
)

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-30"
SUFFIX = DATE.replace("-", "")
DEEPSEEK_REASONER = "deepseek/deepseek-reasoner"

# Same four-predictor program shape as program_multifamily / program_recall_lanes.
INVESTIGATIONS_LANE_PENALTY = LengthPenaltyConfig(instruction_token_budget=2000, output_token_budget=2000)


class OnlyInvestigationSelector:
    """GEPA ReflectionComponentSelector that always proposes the 'investigation' predictor.

    Matches gepa's ReflectionComponentSelector protocol (state, trajectories,
    subsample_scores, candidate_idx, candidate) -> list[str]. Ignores all arguments;
    this run has exactly one optimization target by construction, so there is nothing
    to select between.
    """

    def __call__(self, state: Any, trajectories: Any, subsample_scores: Any,
                 candidate_idx: int, candidate: dict[str, str]) -> list[str]:
        return ["investigation"]


def _config(*, smoke: bool) -> GepaExperimentConfig:
    if smoke:
        return GepaExperimentConfig(
            run_id="exectv2_gepa_investigations_lane_deepseekreasoner_smoke",
            task_model=DEEPSEEK_REASONER,
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
            length_penalty=INVESTIGATIONS_LANE_PENALTY,
            component_selector=OnlyInvestigationSelector(),
            date=DATE,
            notes="Investigations-only lane, deepseek-reasoner, smoke; not a result.",
        )
    return GepaExperimentConfig(
        run_id=f"exectv2_gepa_investigations_lane_deepseekreasoner_{SUFFIX}",
        task_model=DEEPSEEK_REASONER,
        reflection_model=DEEPSEEK_REASONER,
        task_temperature=0.0,
        task_max_tokens=12000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=12,
        reflection_minibatch_size=8,
        length_penalty=INVESTIGATIONS_LANE_PENALTY,
        component_selector=OnlyInvestigationSelector(),
        date=DATE,
        notes=(
            "Investigations-only GEPA lane targeting the Phase 4 ev-recall consolidation "
            "check's MRI-anchoring finding (EEG dropped when an MRI is also present). "
            "Diagnosis/SeizureFrequency/Prescription frozen at program_multifamily's "
            "unchanged seeds via a single-predictor component selector; only 'investigation' "
            "is reflected on / mutated. Task+reflection model deepseek-reasoner. Compare "
            "Investigations column to the DeepSeek-chat baseline (headline ~0.92-0.93, "
            "ev-recall ~0.93-0.94), not the mini Phase-4 baseline (0.858 / 0.801)."
        ),
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    dotenv.load_dotenv(ROOT / ".env")

    config = _config(smoke=args.smoke)
    status_path = GEPA_LOG_ROOT / f"{config.run_id}_status.json"
    summary_json = EXPERIMENTS / f"{config.run_id}.json"
    if summary_json.exists():
        print(f"[inv-lane] skip {config.run_id} (summary exists)", flush=True)
        return

    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    status: dict = {"started_at": _now(), "smoke": args.smoke, "run_id": config.run_id, "state": "running"}
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[inv-lane] start {config.run_id} (task=deepseek-reasoner, investigation-only mutation)", flush=True)
    try:
        payload = run_experiment(
            config,
            register=not args.smoke,
            seed_program=build_investigations_lane_program(),
            final_instruction_fn=combined_instruction,
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
            f"[inv-lane] done {config.run_id}: Investigations headline="
            f"{headline['per_family']['Investigations']} ev_recall="
            f"{ev['per_family']['Investigations']} overall_headline={headline['overall_f1']}",
            flush=True,
        )
    except Exception as exc:
        status.update(state="failed", finished_at=_now(), error=f"{type(exc).__name__}: {exc}",
                      traceback=traceback.format_exc()[-3000:])
        print(f"[inv-lane] FAILED {config.run_id}: {exc}", flush=True)
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
