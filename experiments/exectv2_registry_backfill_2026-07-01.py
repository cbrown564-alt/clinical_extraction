"""Retroactive registry backfill for silently-unregistered GEPA runs.

Phase 2 step 0 of docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md,
extended after Item 2's survivorship-bias analysis independently found a second
instance of the same gap.

Two distinct root causes, both confirmed by direct inspection before writing this:

1. `exectv2_gepa_multistage_dedup_gpt41mini_20260628` — ran through
   `run_gepa.run_experiment(..., register=True)` (the default), which DID
   attempt registration via `_register()`, but that function's own
   `try/except ValueError` around `load_run_registry` swallows any registry
   load failure and just prints a warning, so the run's artifacts were
   written but the row was silently never appended. Backfilled here with the
   exact schema `_register()` uses.
2. The `exectv2_gepa_sf_verify_*` family (6 non-smoke runs, 2026-06-28/29) —
   `experiments/gepa_sf_verify_exectv2.py` / `gepa_sf_verify_phase5_exectv2.py`
   / `gepa_sf_verify_v2_deepseek_exectv2.py` never called `run_gepa.py` at
   all; they are standalone drivers with their own save logic that never
   included a registry write. Not a bug in the shared registration path —
   this family was simply never wired to register. Backfilled here with a
   new `gepa_sf_verify` pipeline_family (materially different program/metric
   from `gepa_from_scratch`: state_profile-optimized generate->recall-additive
   -verify, not clinical_headline-optimized).

The `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator` frontier
candidate the survivorship doc also flagged is deliberately NOT backfilled
here: its exact number (0.8356 full200 clinical_headline_f1, gpt-4.1-mini,
same architecture) is already carried by the independently-registered
`exectv2_same_core_model_swap_full200_20260625` row. Adding a second row for
the same result under a different run_id would be a duplicate entry, not a
missing one — the real gap is a naming/traceability mismatch between the
frontier doc's candidate labels and that row's run_id, not an absent
registration. See `docs/research/exectv2_registry_survivorship_bias_2026-07-01.md`.

Usage: uv run python experiments/exectv2_registry_backfill_2026-07-01.py
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

MULTISTAGE_COMPARATORS = {
    "dev140_hand_tuned_single_prompt_headline": {
        "gpt-4.1-mini": 0.710,
        "deepseek-chat": 0.745,
        "qwen3.6-35b": 0.694,
    },
    "dev140_v08_hybrid_headline": 0.9155,
    "dev140_per_family_gepa_ceiling": 0.731,
}

SF_VERIFY_COMPARATORS = {
    "dedup_baseline": {"clinical_headline": 0.592, "state_profile": 0.713},
    "v08_hybrid": {"clinical_headline": 0.926, "state_profile": 0.930},
}


def _multistage_entry() -> RunRegistryEntry:
    payload = json.loads(
        (EXPERIMENTS / "exectv2_gepa_multistage_dedup_gpt41mini_20260628.json").read_text(
            encoding="utf-8"
        )
    )
    h = payload["final_eval"]["clinical_headline"]
    run_id = payload["run_id"]
    artifact_names = [
        f"{run_id}.json",
        f"{run_id}.md",
        f"{run_id}.jsonl",
        f"{run_id}.instruction.txt",
    ]
    return RunRegistryEntry(
        run_id=run_id,
        artifact_paths=tuple(f"experiments/{name}" for name in artifact_names),
        date=payload["date"],
        pipeline_family="gepa_from_scratch",
        split="dev",
        row_count=payload["final_eval"]["letters"],
        model=payload["task_model"],
        model_role=(
            f"GEPA from-scratch student ({payload['task_model']}), reflection LM "
            f"{payload['reflection_model']}; two-stage (generate->verify, 4 families x "
            "2 stages = 8 evolvable instructions) program, S0 warm-started from the "
            "evolved 0.731 per-family run, S1 lean-seeded from distilled entity_verifier "
            "rules; length-penalized clinical_headline metric; trained on optimizer-only "
            "dev sub-split, attribution-clean de-dup adapter."
        ),
        mode="live",
        replay_status="live",
        decision="inform_architecture_loop",
        primary_metrics={
            "clinical_headline_overall_f1": h["overall_f1"],
            "clinical_headline_diagnosis_f1": h["per_family"]["Diagnosis"],
            "clinical_headline_seizure_frequency_f1": h["per_family"]["SeizureFrequency"],
            "clinical_headline_prescription_f1": h["per_family"]["Prescription"],
            "clinical_headline_investigations_f1": h["per_family"]["Investigations"],
            "strict_benchmark_per_item_f1": payload["final_eval"]["strict_benchmark_per_item_f1"],
            "semantic_per_item_f1": payload["final_eval"]["semantic_per_item_f1"],
            "final_instruction_tokens": payload["final_instruction_tokens"],
            "seed_instruction_tokens": payload["seed_instruction_tokens"],
        },
        repair_mode="dedup_clinical_facts_adapter",
        cache_reuse_source=f"experiments/{run_id}.jsonl",
        evidence_validity=(
            "Development split (dev, exectv2_split_v1), NOT test. GEPA trained on an "
            "optimizer-only dev sub-split. clinical_headline is the clinical-recovery "
            "surface (decision 0027), NOT paper-comparable; strict benchmark reported "
            "beside it. Live task model; reflection deepseek-reasoner. Backfilled "
            "2026-07-01: artifacts complete since 2026-06-28, but the row was never "
            "written due to a registry-load failure inside `_register()`'s own "
            "try/except (silently swallowed, no exception propagated) — see "
            "docs/research/exectv2_registry_survivorship_bias_2026-07-01.md."
        ),
        supersedes=(),
        claim_language_notes=(
            "DSPy-native GEPA multi-stage (generate->verify) from-scratch on the de-dup "
            "clinical_headline surface. MISSED the pre-registered kill-criterion (beat "
            "0.731 per-family ceiling by >= +0.03): scored 0.7235, -0.008 below the "
            "single-pass per-family ceiling. Mechanism (evolved-instruction inspection, "
            "docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md §3): "
            "verify on an already-precision-tuned generator only filtered (recall "
            "805->783 facts); the most heavily-evolved verifier drifted into "
            "reformatting the whole list rather than filtering it — an undecomposed "
            "end-to-end clinical_headline reward gave reflection no way to credit "
            "'correctly rejected a bad candidate' separately from 'produced a good "
            "final list'. Development-surface only; not benchmark-cleared."
        ),
    )


def _sf_verify_entry(run_id: str, date: str) -> RunRegistryEntry:
    payload = json.loads((EXPERIMENTS / f"{run_id}.json").read_text(encoding="utf-8"))
    opt = payload["optimized"]
    seed = payload["seed"]
    artifact_names = [f"{run_id}.json", f"{run_id}.jsonl", f"{run_id}.instruction.txt"]
    task_model = (
        payload.get("model")
        or payload.get("verify_model")
        or payload.get("extraction_model", "unknown")
    )
    reflection_model = payload["reflection_model"]
    metrics = {
        "clinical_headline_f1": opt["clinical_headline_f1"],
        "state_profile_f1": opt["state_profile_f1"],
        "seed_clinical_headline_f1": seed["clinical_headline_f1"],
        "seed_state_profile_f1": seed["state_profile_f1"],
        "instruction_tokens": payload["instruction_tokens"],
    }
    for key in (
        "state_profile_precision",
        "state_profile_recall",
        "changed_precision",
        "changed_recall",
    ):
        if key in opt:
            metrics[key] = opt[key]
    model_role = (
        f"GEPA SF-only generate->recall-additive-verify student ({task_model}), "
        f"reflection LM {reflection_model}; optimized directly on the fair, "
        "type-agnostic state_profile metric (length-penalized), feedback naming "
        "missed clinical states so reflection learns to ADD recall, not just filter."
    )
    if "extraction_model" in payload:
        model_role += (
            f" Phase-5 arm: extraction={payload['extraction_model']}, "
            f"verify={payload['verify_model']}, "
            f"examples={'yes' if payload.get('with_examples') else 'no (feedback-only)'}."
        )
    return RunRegistryEntry(
        run_id=run_id,
        artifact_paths=tuple(f"experiments/{name}" for name in artifact_names),
        date=date,
        pipeline_family="gepa_sf_verify",
        split="dev",
        row_count=140,
        model=task_model,
        model_role=model_role,
        mode="live",
        replay_status="live",
        decision="inform_architecture_loop",
        primary_metrics=metrics,
        repair_mode="sf_generate_recall_additive_verify",
        cache_reuse_source=f"experiments/{run_id}.jsonl",
        evidence_validity=(
            "Development split (dev140, exectv2_split_v1), NOT test. Trained/evaluated "
            "on the full dev140 shuffled split (seed 20260627), not a disjoint "
            "optimizer-only sub-split like the gepa_from_scratch family — a "
            "development-only number. state_profile is the fair, type-agnostic SF "
            "metric (see docs/research/exectv2_sf_representation_not_recall_2026-06-28.md); "
            "clinical_headline reported beside it for cross-comparison. Backfilled "
            "2026-07-01: this family's launcher scripts "
            "(gepa_sf_verify_exectv2.py / gepa_sf_verify_phase5_exectv2.py / "
            "gepa_sf_verify_v2_deepseek_exectv2.py) never called the shared registration "
            "path at all — a coverage gap, not the same load-failure bug as the "
            "multistage run — see "
            "docs/research/exectv2_registry_survivorship_bias_2026-07-01.md."
        ),
        supersedes=(),
        claim_language_notes=(
            "SF verify-stage GEPA arm feeding the SF plateau/wall investigation "
            "(docs/research/exectv2_sf_verify_phase5_result_2026-06-29.md). "
            "Development-surface only; not benchmark-cleared."
        ),
    )


def _fix_unrelated_broken_artifact_path(entries: list[RunRegistryEntry]) -> list[RunRegistryEntry]:
    """Fix a pre-existing, unrelated bad row found while backfilling.

    `gan2026_reliability_p2_1_semantic_entropy_2026-06-17` (in the registry
    since before this session; predates the multistage/sf_verify runs this
    script backfills) stores one artifact path as a literal, never-expanded
    brace pattern (`..._preflight{25,150}_temp{0.3,0.5,0.7,1.0}_....jsonl`)
    instead of the 8 real files it names. This makes
    `validate_run_registry_artifacts` raise for the WHOLE registry, not just
    this row -- which is plausibly why some `_register()` calls in this
    period appeared to succeed (their own `write_run_registry` completed)
    but the run's own subsequent `validate_run_registry_artifacts` call
    (outside `_register()`'s try/except) then crashed, leaving the launcher
    to report "failed" even though the row was actually written. Fixed here
    since it blocks re-running this backfill (or any future `_register()`
    call) from validating cleanly; the 8 real files were confirmed present
    on disk before this fix.
    """

    fixed = []
    for entry in entries:
        if entry.run_id == "gan2026_reliability_p2_1_semantic_entropy_2026-06-17" and any(
            "{" in p for p in entry.artifact_paths
        ):
            new_paths = tuple(p for p in entry.artifact_paths if "{" not in p) + tuple(
                f"experiments/gan2026_reliability_p2_1_samples_preflight{n}_temp{t}_2026-06-17.jsonl"
                for n in (25, 150)
                for t in ("0.3", "0.5", "0.7", "1.0")
            )
            entry = dataclasses.replace(entry, artifact_paths=new_paths)
        fixed.append(entry)
    return fixed


def main() -> None:
    existing = _fix_unrelated_broken_artifact_path(load_run_registry(REGISTRY_PATH))
    existing_ids = {e.run_id for e in existing}

    new_entries = [_multistage_entry()]
    sf_verify_runs = [
        ("exectv2_gepa_sf_verify_gpt41mini_20260628", "2026-06-28"),
        ("exectv2_gepa_sf_verify_p5_reasoner_mini_ex_20260629", "2026-06-29"),
        ("exectv2_gepa_sf_verify_p5_reasoner_mini_fb_20260629", "2026-06-29"),
        ("exectv2_gepa_sf_verify_p5_reasoner_reasoner_ex_20260629", "2026-06-29"),
        ("exectv2_gepa_sf_verify_p5_reasoner_reasoner_fb_20260629", "2026-06-29"),
        ("exectv2_gepa_sf_verify_v2_deepseekchat_20260629", "2026-06-29"),
    ]
    for run_id, date in sf_verify_runs:
        new_entries.append(_sf_verify_entry(run_id, date))

    skipped = [e.run_id for e in new_entries if e.run_id in existing_ids]
    to_add = [e for e in new_entries if e.run_id not in existing_ids]
    if skipped:
        print(f"Already registered, skipping: {skipped}")

    entries = list(existing) + to_add
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)

    print(f"Backfilled {len(to_add)} rows: {[e.run_id for e in to_add]}")
    print(f"Registry now has {len(entries)} rows (was {len(existing)}).")


if __name__ == "__main__":
    main()
