# Project Status

Last updated: 2026-06-26

## Active Objective

ExECTv2 is in a reliability/component-evidence phase after the Satellite 13
LLM-only plateau. `clinical_headline` de-duplicated clinical recovery is the
headline surface; strict benchmark/CUI results stay diagnostic. Paper-facing
language and results scaffolding live in `docs/research/`.

## Current Read

The 2026-06-25 evidence stack is:

- GPT-4.1-mini v08 full-200 aggregate: verifier-backed `0.8502`
  `clinical_headline` F1; no-verifier `0.8431`; accepted lean 2-call no-SF
  candidate `0.8356` overall and `0.7525` SF.
- Same-core full-200 aggregate-only audit is complete at
  `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`:
  GPT-4.1-mini `0.8356`; DeepSeek `0.8566` overall and `0.7602` SF, with `1`
  DeepSeek Diagnosis parse/schema failure accepted as a caveat.
- Same-core dev140 model swap: DeepSeek `0.8596`, GPT-4.1-mini `0.8396`, Qwen
  `0.8018`, all with `1.0000` exact evidence. Qwen repair v02 completed a
  frozen same-core downstream assembly: overall `0.8319`, SeizureFrequency
  `0.7182`, `0` call/parse failures, and structured evidence validity `0.9964`;
  this passes dev140 repair gates but is not a full-200 promotion.
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
   perform tagged projection, not add/select/reject facts in an LLM-only line.
3. Keep Reliability Scorecard separate from Component Impact, and label every
   score change by split, scorer, inspection boundary, and evidence tier.

## Work Board

### Now

- Add a short MLflow local runbook/doctor if observability work continues.

### Next

- Decide whether MLflow sync needs existing-run lookup by `registry_run_id`
  before any broader backfill; the first same-core group is intentionally local
  observability, not claim-of-record.
- Decide whether to add Qwen repair v02 to a fresh same-core full-200
  aggregate-only candidate predeclaration or keep the already-written
  GPT-4.1-mini plus DeepSeek full-200 plan unchanged.
- Plan true component-off reliability ablations only after scorecard language is
  stable; reliability is trust evidence, component impact is delta evidence.
- Keep repo cleanup and Investigations cost work deferred.

### Blocked

- Gan holdout-facing reruns, test row analysis, and post-test tuning remain
  blocked unless separately authorized under a fresh frozen protocol.
- ExECTv2 full-200/holdout row-level inspection remains blocked; current
  reliability protocols authorize aggregate validation outputs only.
- Qwen full-200 promotion remains blocked until a fresh aggregate-only full-200
  predeclaration includes it; v02 has passed dev140 repair gates only.
- Lower-burden review-routing promotion is blocked by failed aggregate
  validation; any retry needs dev140-only redesign and a fresh predeclaration.

### Done Recently

- 2026-06-26: Mirrored same-core dev140 as the first MLflow parent/child group
  and updated the Qwen repair-v02 child in place after full assembly completion;
  added registry rows, guarded group sync, tests, and MLflow 3 file-store
  handling.
- 2026-06-26: Added shared standard evidence repair for Qwen v02, replayed the
  frozen structured producer to `0.9964` evidence validity, and completed the
  downstream same-core dev140 assembly: overall `0.8319`, SeizureFrequency
  `0.7182`, `0` call/parse failures. Qwen v02 passes dev140 repair gates and
  now needs a separate full-200 inclusion decision.
- 2026-06-26: Added registry-first MLflow dry-run sync planning:
  `clinical_extraction.core.mlflow_registry_sync`,
  `scripts/sync_registry_to_mlflow.py`, `clinical-extraction-mlflow-sync`, and
  tests. Restricted/full-200 row-level artifacts are pointer-only; MLflow still
  remains optional observability, not the claim-of-record.
- 2026-06-26: Completed MLflow Phase 0-1 and registry-driven Gan
  Explorer/Component Impact surfacing; registry/report artifacts remain the
  claim-of-record.
- 2026-06-25: Completed same-core full-200 aggregate audit, same-core dev140/Qwen
  repair v01-v02, paper/results scaffolding, reliability validations,
  Investigations, and Gan v0.7 holdout aggregate updates.
- 2026-06-22 to 2026-06-24: Completed v08 full-200 audits, final consolidation,
  frontend MVP, reliability scorecard, Gan component-ablation simplification,
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
