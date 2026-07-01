"""GEPA over the multi-stage program with S0 frozen and a stage-local verify metric.

Phase 2 of docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md,
testing the review's verify-stage credit-assignment hypothesis: the prior
multi-stage run (`exectv2_gepa_multistage_dedup_gpt41mini_20260628`, dev140
0.7235) missed its kill-criterion (beat the 0.731 single-pass per-family
ceiling by >= +0.03) because the verify stage was scored on the same
undecomposed end-to-end `clinical_headline` F1 as the generator -- evolved-
instruction inspection showed the most heavily-evolved verifier drifted into
"output a complete corrected list in hyphenated-lowercase canonical
representation" (reformatting) rather than filtering (recall 805->783 facts).

This run isolates that fix with two restrictions vs the prior multistage run:

1. **Frozen S0.** Generate predictors warm-start from `load_evolved_s0_seeds()`
   (the evolved 0.731 per-family instructions) AND are excluded from mutation
   via a custom `ReflectionComponentSelector` restricted to the four
   `verify_<family>` predictors -- GEPA cannot touch the generator at all.
2. **Stage-local reflection feedback.** `metric.py`'s `build_metric()` now
   branches on `pred_name`: a `verify_<family>` reflective-mutation call gets
   an accept/reject/add audit of that predictor's own decisions against the
   draft it was given, independent of the merged-output diff (see
   `metric._verify_stage_feedback`). The SELECTION score stays the unchanged
   end-to-end `clinical_headline` objective (comparable across the whole
   program); only the feedback TEXT used for reflection is decomposed.

Kill-criterion (same standard as the prior multistage run): beat the 0.731
per-family ceiling by >= +0.03 on dev140. Secondary check: does the evolved
verify instruction text become filter-shaped (explicit keep/reject criteria)
rather than reformat-shaped, and does the recall-loss pattern (805->783 facts
in the prior run) shrink?

Usage:
    uv run python experiments/gepa_multistage_verifyonly_exectv2.py --smoke
    uv run python experiments/gepa_multistage_verifyonly_exectv2.py
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multistage import (
    FAMILIES,
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
DATE = "2026-07-01"
SUFFIX = DATE.replace("-", "")
MINI = "openai/gpt-4.1-mini"
DEEPSEEK_REASONER = "deepseek/deepseek-reasoner"

#: Same 4000-token instruction budget as the prior multistage run: S0 is
#: frozen at ~2272 tokens (unchanged, still summed into the length penalty
#: since forward() stamps all 8 predictors' tokens), leaving verify's growth
#: room effectively unchanged from that run.
VERIFYONLY_PENALTY = LengthPenaltyConfig(instruction_token_budget=4000, output_token_budget=2000)

_VERIFY_NAMES = [f"verify_{family}" for family in FAMILIES]


class VerifyOnlySelector:
    """GEPA ReflectionComponentSelector restricted to the four verify_<family> predictors.

    Matches gepa's ReflectionComponentSelector protocol (state, trajectories,
    subsample_scores, candidate_idx, candidate) -> list[str]. Ignores all
    arguments and always offers the same four names, so GEPA's own selection
    logic still picks among them each round but can never propose a
    generate_<family> predictor -- S0 is provably frozen at its warm-started
    instruction for the whole run.
    """

    def __call__(
        self, state: Any, trajectories: Any, subsample_scores: Any,
        candidate_idx: int, candidate: dict[str, str],
    ) -> list[str]:
        return list(_VERIFY_NAMES)


def _config(smoke: bool) -> GepaExperimentConfig:
    if smoke:
        return GepaExperimentConfig(
            run_id="exectv2_gepa_multistage_verifystage_smoke_gpt41mini",
            task_model=MINI,
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
            length_penalty=VERIFYONLY_PENALTY,
            component_selector=VerifyOnlySelector(),
            date=DATE,
            notes="Verify-only multistage smoke; not a result.",
        )
    return GepaExperimentConfig(
        run_id=f"exectv2_gepa_multistage_verifystage_dedup_gpt41mini_{SUFFIX}",
        task_model=MINI,
        reflection_model=DEEPSEEK_REASONER,
        task_temperature=0.0,
        task_max_tokens=12000,
        reflection_max_tokens=12000,
        auto="medium",
        num_threads=12,
        reflection_minibatch_size=8,
        length_penalty=VERIFYONLY_PENALTY,
        component_selector=VerifyOnlySelector(),
        date=DATE,
        notes=(
            "Verify-stage credit-assignment test (implementation plan Phase 2, "
            "2026-07-01). S0 warm-started from the evolved 0.731 per-family run and "
            "FROZEN (component_selector restricted to verify_<family> only); S1 "
            "lean-seeded from distilled entity_verifier rules, evolved under a NEW "
            "stage-local accept/reject/add feedback metric (metric.py "
            "_verify_stage_feedback) independent of the merged-output diff -- "
            "selection score stays end-to-end clinical_headline (unchanged). Prior "
            "jointly-evolved multistage run (both S0+S1 mutable, whole-program "
            "feedback shared) scored 0.7235, missing the kill-criterion by -0.008; "
            "diagnosed as a credit-assignment failure (verify drifted into "
            "reformatting, recall 805->783 facts). Kill-criterion: beat 0.731 by "
            ">= +0.03. Compare to per-family 0.731, hand-tuned 0.710, prior "
            "multistage 0.7235, v08 hybrid 0.9155."
        ),
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    dotenv.load_dotenv(ROOT / ".env")

    config = _config(args.smoke)
    s0_seeds = load_evolved_s0_seeds()  # hard-fail loudly if missing; no lean fallback -- S0 MUST be the evolved seed for this test to isolate the intended variable.
    status_path = GEPA_LOG_ROOT / f"{config.run_id}_status.json"
    summary_json = EXPERIMENTS / f"{config.run_id}.json"
    if summary_json.exists():
        print(f"[verify-only] skip {config.run_id} (summary exists)", flush=True)
        return

    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    status: dict = {"started_at": _now(), "smoke": args.smoke, "run_id": config.run_id, "state": "running"}
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[verify-only] start {config.run_id} (S0 frozen, verify-only mutation, stage-local feedback)", flush=True)
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
            n_facts_total=payload["final_eval"]["n_facts_total"],
            n_scored_total=payload["final_eval"]["n_scored_total"],
        )
        print(
            f"[verify-only] done {config.run_id}: headline_f1={headline['overall_f1']} "
            f"per_family={headline['per_family']} facts={payload['final_eval']['n_facts_total']}",
            flush=True,
        )
    except Exception as exc:
        status.update(
            state="failed", finished_at=_now(), error=f"{type(exc).__name__}: {exc}",
            traceback=traceback.format_exc()[-3000:],
        )
        print(f"[verify-only] FAILED {config.run_id}: {exc}", flush=True)
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
