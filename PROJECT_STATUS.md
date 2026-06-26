# Project Status

Last updated: 2026-06-26

## Active Objective

ExECTv2 is in a reliability/component-evidence phase after the Satellite 13
LLM-only plateau. `clinical_headline` de-duplicated clinical recovery is the
headline surface; strict benchmark/CUI results stay diagnostic. Paper-facing
language and results scaffolding live in `docs/research/`.

## Current Read

The current evidence stack is:

- ExECTv2 `clinical_headline` is the primary surface. Full-200 GPT-4.1-mini v08
  aggregate is `0.8502`; no-verifier is `0.8431`; accepted lean 2-call no-SF
  candidate is `0.8356` overall and `0.7525` SF.
- Same-core full-200 aggregate-only results: GPT-4.1-mini `0.8356`, DeepSeek
  `0.8566` overall / `0.7602` SF with `1` accepted Diagnosis parse/schema
  caveat, and Qwen repair v02 `0.8197` overall / `0.7020` SF with `0`
  call/parse failures, structured evidence validity `0.9950`, and exact
  evidence `1.0000`.
- Same-core dev140 model swap remains diagnostic context: DeepSeek `0.8596`,
  GPT-4.1-mini `0.8396`, Qwen raw `0.8018`, and Qwen repair v02 `0.8319` with
  structured evidence validity `0.9964`.
- Reliability validation: calibration ECE `0.0432`, Brier `0.2245` versus
  `0.2387`; lower-burden review routing failed validation (`0.9661` burden,
  `0.9037` catch); robustness hard-slice F1 `0.8336` across `414` eligible
  family cells; Investigations deterministic replacement is not ready
  (`0.9213` remains strongest with verifier + deterministic suppression).
- ExECTv2 component-off ablations now have a planning boundary at
  `docs/research/exectv2_component_off_reliability_ablation_plan_2026-06-26.md`:
  dev140/validation replay first, full-200 only by fresh aggregate-only
  predeclaration, and no row-level inspection.
- Gan 2026 v0.7 DeepSeek Reasoner holdout aggregate is final: test450 `346/450`
  Purist, `365/450` Pragmatic, `0` call failures; no row-level test inspection
  or post-test tuning is authorized.
- Gan consensus/fresh v0.9 validation gates passed before holdout: Gate 1
  selected Purist `733/750`, Pragmatic `735/750`, changed-label precision
  `0.7347`; Gate 2 had `24/24` desired-action matches and `0`
  correct-to-wrong.
- Gan consensus/fresh v0.9 constrained Gate 4 failed promotion
  (`348/450` Purist, `7` correct-to-wrong, precision `0.5909`), while the
  exact-source aggregate-only Gate 4 passed for the frozen source set only
  (`359/450` Purist, `+16` versus deterministic, `5` correct-to-wrong,
  precision `0.6000`). Neither result authorizes post-test tuning or row-level
  locked-test inspection.

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

- Preserve the Gan consensus/fresh v0.9 constrained Gate 4 result as
  final-evaluation evidence only; do not tune selector gates, prompts, source artifacts,
  deterministic rules, normalization, scorer, or model choice from it.
- Preserve the Gan consensus/fresh v0.9 exact-source holdout pass as a frozen
  aggregate result; do not open locked-test row-level failures, evidence,
  selected events, or transitions for development.

### Next

- If the Gan consensus/fresh path is revisited for tuning or redesign, start
  from validation-only component-generation work; the holdout aggregate results
  may be cited only as frozen evaluation evidence, not used for row-level
  debugging or tuning.
- Implement the first ExECTv2 dev140/validation component-off replay configs
  from the 2026-06-26 plan; do not advance to full-200 without a fresh
  aggregate-only predeclaration.
- Keep repo cleanup and Investigations cost work deferred.

### Blocked

- Gan holdout-facing reruns, test row analysis, and post-test tuning remain
  blocked unless separately authorized under a fresh frozen protocol.
- Gan consensus/fresh v0.9 post-test tuning remains blocked: the authorized
  constrained aggregate audit failed promotion, and the exact-source aggregate
  pass is frozen; neither result may drive locked-test row-level analysis or
  tuned reruns.
- ExECTv2 full-200/holdout row-level inspection remains blocked; current
  reliability protocols authorize aggregate validation outputs only.
- Lower-burden review-routing promotion is blocked by failed aggregate
  validation; any retry needs dev140-only redesign and a fresh predeclaration.

### Done Recently

- 2026-06-26: Completed ExECTv2 component-off reliability ablation planning;
  scorecard evidence stays separated from named same-input component deltas, and
  any full-200 audit needs a fresh aggregate-only predeclaration.
- 2026-06-26: Advanced MLflow local observability and registry hygiene: doctor,
  runbook, registry sync/reuse, scoped backfill ADR 0036, parent/child same-core
  mirroring, and controlled registry roles; registry/report artifacts remain
  the claim-of-record.
- 2026-06-26: Completed Qwen repair v02 dev140 and full-200 aggregate-only
  same-core evidence (`0.8319` dev140; `0.8197` full-200; `0` call/parse
  failures in both repaired assemblies).
- 2026-06-26: Completed Gan consensus/fresh v0.9 validation gates, constrained
  Gate 4 failed-promotion readout, exact-source replay generation, exact Gate 3,
  and user-authorized exact aggregate-only Gate 4 pass; all locked-test results
  remain frozen and no row-level tuning is authorized.
- 2026-06-26: Completed registry exhaustive-review actions and current
  ExECTv2/Gan artifact indexing, including regenerated `experiments/RUN_INDEX.md`
  and surfaced paper-facing reliability/component rows.
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
