# Project Status

Last updated: 2026-06-26

## Active Objective

ExECTv2 is in a reliability and component-evidence phase after the Satellite 13
LLM-only plateau. `clinical_headline` de-duplicated clinical recovery is the
headline surface; strict benchmark/CUI results stay diagnostic. Paper-facing
claim language is consolidated at
`docs/research/exectv2_reliability_component_evidence_paper_language_2026-06-25.md`
and the results-section scaffold is at
`docs/research/exectv2_results_section_scaffold_2026-06-25.md`.

## Current Read

The 2026-06-25 evidence stack is:

- GPT-4.1-mini current-code v08 full-200 aggregate: verifier-backed `0.8502`
  overall `clinical_headline` F1; no-verifier ablation `0.8431`; accepted lean
  2-call no-SF-adjudicator candidate `0.8356` overall and `0.7525` SF.
- Same-core full-200 aggregate-only audit is complete at
  `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`:
  GPT-4.1-mini `0.8356`; DeepSeek `0.8566` overall and `0.7602` SF, but
  DeepSeek has `1` Diagnosis parse/schema failure. That count is accepted as a
  schema-stability caveat, not a promotion blocker.
- Same-core dev140 model swap: DeepSeek `0.8596`, GPT-4.1-mini `0.8396`, Qwen
  `0.8018`, all with `1.0000` exact evidence; Qwen remains diagnostic because
  of output-contract instability and failed repairs v01/v02. Repair v02 fixed
  structured parse/schema failures on a full dev140 structured rerun; shared
  standard evidence repair reduces the same saved raw replay from `30` to `3`
  evidence-invalid mentions (`0.9964` validity). This is saved-raw replay
  evidence, not yet a completed predeclared same-core assembly rerun.
- Reliability validation: calibration ECE `0.0432`, Brier `0.2245` versus
  `0.2387`; lower-burden review routing failed validation (`0.9661` burden,
  `0.9037` catch); robustness hard-slice F1 `0.8336` across `414` eligible
  family cells with schema/evidence validity `1.0000`.
- Investigations deterministic replacement is not ready: verifier +
  deterministic suppression remains strongest at `0.9213`; v04 meets `0.2000`
  burden but drops F1.
- Gan 2026 v0.7 DeepSeek Reasoner holdout aggregate is final: test450 `346/450`
  Purist, `365/450` Pragmatic, `0` call failures; no row-level test inspection
  or post-test tuning is authorized.

The same-core full-200 audit followed
`docs/experiments/exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`.
No full-200 row-level failure analysis is authorized, and no prompt, parser,
threshold, deterministic-rule, or scorer tuning should follow from the
aggregate readout.

## Active Priorities

1. Treat `clinical_headline` de-duplicated clinical recovery as primary; strict
   benchmark/CUI results stay diagnostic/comparability-only.
2. Preserve attribution discipline: deterministic code may validate evidence and
   perform tagged projection, but must not add, select, or reject clinical facts
   inside an LLM-only score line.
3. Keep Reliability Scorecard separate from Component Impact, and label every
   score change by split, scorer, inspection boundary, and evidence tier.

## Work Board

### Now

- Use `docs/plans/recent_plan_rationalisation_2026-06-25.md` as the current
  sequence; defer MLflow and repo cleanup until the reporting/registry path is
  stable.

### Next

- Add MLflow observability Phase 0-1 after the canonical registry remains visibly
  in charge (`docs/plans/mlflow_experiment_observability_implementation_plan_2026-06-25.md`).
- If Qwen is revisited, predeclare a fresh same-core repair/assembly rerun using
  the shared standard evidence-repair family; parser/schema stability is no
  longer the limiting failure after v02.
- Plan true component-off reliability ablations only after scorecard language is
  stable; reliability is trust evidence, component impact is delta evidence.
- Keep repo cleanup and Investigations cost work deferred.

### Blocked

- Additional Gan holdout-facing reruns, row-level test analysis, and post-test
  tuning remain blocked after the authorized v0.7 aggregate audit unless
  separately authorized under a fresh frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection remains blocked; the
  reliability-audit protocol authorizes aggregate validation outputs only.
- Qwen same-core full-200 promotion is blocked unless a fresh Qwen-specific
  dev140 repair/assembly rerun is separately predeclared and passes operational,
  evidence-validity, and clinical non-regression gates.
- Promotion of the lower-burden review-routing candidate is blocked by failed
  aggregate validation; any retry needs dev140-only redesign and a fresh
  predeclaration.

### Done Recently

- 2026-06-26: Registry-driven Gan Explorer/Component Impact surfacing: curated
  validation-750 comparators (GPT-4.1-mini, DeepSeek, Qwen per hybrid/LLM-only
  family) via `run_surfacing.py`, explicit `run_id` Explorer selection, reconciled
  registry curation fields, and regenerated `pipeline-families.json` +
  `component-ablation.json`.
- 2026-06-25: Completed same-core full-200 aggregate-only audit from the frozen
  predeclaration: DeepSeek `0.8566` vs GPT-4.1-mini `0.8356` overall
  `clinical_headline`; DeepSeek is accepted with an explicit `1` Diagnosis
  parse/schema-failure caveat.
- 2026-06-25: Finished same-core dev140/Qwen repair v01-v02, paper-language,
  results scaffold, plan rationalisation, calibration/robustness/self-consistency,
  Investigations, and Gan v0.7 holdout audit updates.
- 2026-06-24: Completed current-code v08 full-200 GPT-4.1-mini architecture and
  no-verifier audits, refreshed reliability scorecard infrastructure, and froze
  the reliability-audit protocol.
- 2026-06-22 to 2026-06-24: Completed final consolidation, ExECTv2 frontend MVP,
  cross-dataset reliability scorecard, Gan component-ablation simplification,
  and Satellite 13 Phases 0-6.

## Guardrails

- Do not describe de-duplicated `clinical_headline` recovery as a strict
  benchmark win or compare it directly to the paper's strict target.
- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development;
  the current reliability-audit protocol authorizes aggregate validation only.
- Keep deterministic projection, hybrid rescue, and verifier rejection
  provenance-stamped and separated in reported score lines.
