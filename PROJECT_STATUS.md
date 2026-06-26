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
  `0.8018`, all with `1.0000` exact evidence. Qwen repair v02 dev140 assembly:
  overall `0.8319`, SeizureFrequency `0.7182`, `0` call/parse failures, and
  structured evidence validity `0.9964`.
- Qwen repair v02 same-core full-200 aggregate-only run is complete:
  overall `0.8197`, SeizureFrequency `0.7020`, `0` call/parse failures,
  structured evidence validity `0.9950`, final-lane exact evidence `1.0000`;
  passes the predeclared stop rule as a separate model-family row, trailing
  GPT-4.1-mini (`0.8356`) and DeepSeek (`0.8566`) without altering their
  predeclaration.
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
- Gan consensus/fresh v0.9 frozen Gate 1 hard-slice audit passed on validation:
  selected Purist `733/750`, Pragmatic `735/750`, `36` wrong-to-correct,
  `0` correct-to-wrong, changed-label precision `0.7347`; submonthly `1/5`
  and weekly `4/10` changed-label precision remain portability risks, and
  `11/17` residual wrong rows have no correct component available.
- Gan consensus/fresh v0.9 frozen Gate 2 robustness/stress panel passed:
  `24/24` desired-action matches across all eight predeclared mechanism
  families, `0` Purist correct-to-wrong, `0` deterministic-correct
  false-positive actions, `0` cluster demotions, and `0` forbidden
  no-reference-to-unknown churn.
- Gan consensus/fresh v0.9 frozen Gate 3 source-symmetry preflight passed only
  as constrained source-symmetry: deterministic, available two-agent
  consensus, fresh-evidence, and GPT/Qwen/DeepSeek source substrates each cover
  `450/450` locked test rows with `0` duplicates and `0` off-manifest rows.
  Exact three-agent consensus replay is not present, so the completed path can
  support only constrained holdout evidence, not an exact v0.9 selector holdout
  claim.
- Gan consensus/fresh v0.9 Gate 4 constrained aggregate audit was
  user-authorized and completed as final-evaluation evidence: selected Purist
  `348/450` versus deterministic `329/450` (`+19`), selected Pragmatic
  `358/450`, `44` changed labels, `26` wrong-to-correct, `7`
  correct-to-wrong, and changed-label precision `0.5909`. The numeric promotion
  gate failed (`correct_to_wrong` > `5` and precision < `0.60`), so no
  holdout-backed selector promotion is made and any follow-up must restart on
  validation-only component-generation work.
- Gan consensus/fresh v0.9 exact-source follow-up is complete: the missing
  GPT+Qwen+DeepSeek unanimous consensus test component was generated and
  hash-pinned; exact-source Gate 3 passed with `450/450` coverage, `0`
  duplicates, `0` off-manifest rows, deterministic role parity, prompt hygiene,
  and a protocol-documented fresh-evidence holdout counterpart; the
  user-authorized aggregate-only exact Gate 4 passed promotion bars with
  selected Purist `359/450` versus validation-matched deterministic `343/450`
  (`+16`), selected Pragmatic `368/450`, `35` changed labels, `21`
  wrong-to-correct, `5` correct-to-wrong, and changed-label precision `0.6000`.
  This supports an exact v0.9 selector holdout claim for the frozen source set
  only; no post-test tuning or locked-test row-level inspection is authorized.

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
- Plan true component-off reliability ablations only after scorecard language is
  stable; reliability is trust evidence, component impact is delta evidence.
- Scope any broader MLflow registry backfill explicitly; reuse is implemented,
  but backfill remains local observability only and non-canonical.
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

- 2026-06-26: Decided and implemented MLflow existing-run reuse before broader
  backfill: ADR 0035, lookup by `registry_run_id`/`comparison_id`, and refresh
  of tags/metrics/artifacts on re-sync; broader backfill remains explicitly
  scoped and non-canonical.
- 2026-06-26: Added MLflow local observability runbook and doctor:
  `docs/runbooks/mlflow_local_tracking.md` and
  `clinical-extraction-mlflow-doctor` for install/config/status checks and
  guardrail warnings; registry remains claim-of-record.
- 2026-06-26: Completed the authorized Qwen repair v02 same-core full-200
  aggregate-only run: overall `0.8197`, SeizureFrequency `0.7020`, `0`
  call/parse failures, structured evidence validity `0.9950`, and final-lane
  exact evidence `1.0000`. Passes the predeclared stop rule as separate
  same-core model-family evidence; readout at
  `docs/experiments/exectv2/reliability/exectv2_qwen_model_swap_repair_v02_full200_readout_2026-06-26.md`.
- 2026-06-26: Upgraded registry roles for paper-facing reliability/component
  evidence: Gan reliability D gating, confidence one-vs-two, fresh-evidence
  validation lineage, cross-model comparison, and selected ExECTv2 specialist
  ladders; added a frozen hard-slice/robustness/test protocol for Gan
  consensus/fresh selector v0.9 without authorizing a holdout run.
- 2026-06-26: Completed Gan consensus/fresh v0.9 frozen Gate 1 hard-slice audit:
  validation-only pass with `733/750` selected Purist, `0` correct-to-wrong,
  and `0.7347` changed-label precision; next gate is robustness/stress, not
  locked test.
- 2026-06-26: Completed Gan consensus/fresh v0.9 frozen Gate 2 robustness/stress
  panel: `24/24` desired-action matches, `0` correct-to-wrong, `0`
  deterministic-correct false-positive selector actions, `0` cluster demotions,
  and `0` forbidden no-reference-to-unknown churn; next gate is source-symmetry
  preflight, not locked test.
- 2026-06-26: Completed Gan consensus/fresh v0.9 frozen Gate 3 source-symmetry
  preflight: constrained pass with `450/450` coverage for deterministic,
  available two-agent consensus, fresh-evidence, and GPT/Qwen/DeepSeek source
  substrates, `0` duplicates, and `0` off-manifest rows; exact three-agent
  consensus replay remains unavailable, so Gate 4 requires explicit
  authorization and constrained claim language.
- 2026-06-26: Completed the user-authorized Gan consensus/fresh v0.9 Gate 4
  constrained aggregate audit: selected Purist `348/450` versus deterministic
  `329/450`, but promotion failed with `7` correct-to-wrong and `0.5909`
  changed-label precision; no row-level test failures, evidence, selected
  events, or transitions were written or inspected for development.
- 2026-06-26: Clarified the exact v0.9 selector holdout path: the constrained
  Gate 4 cannot be upgraded by language alone. Exact-source evidence requires a
  newly generated and frozen three-agent consensus test replay, deterministic
  and fresh-evidence parity proof, exact-source Gate 3, and fresh Gate 4
  authorization.
- 2026-06-26: Generated and froze the missing exact three-agent consensus
  `test450` component, reran Gate 3 as exact source-symmetry, and completed the
  user-authorized aggregate-only exact Gate 4 audit. The exact-source selector
  passed promotion bars: selected Purist `359/450` versus deterministic
  `343/450`, `+16` net Purist, `5` correct-to-wrong, and `0.6000`
  changed-label precision. This is an exact v0.9 selector holdout result for
  the frozen source set, with no post-test tuning or row-level test inspection
  authorized.
- 2026-06-26: Completed registry exhaustive-review actions: backfilled surfaced
  Qwen Phase 1 metrics, added controlled `registry_roles`, indexed current
  ExECTv2 aggregate/study artifacts, regenerated `experiments/RUN_INDEX.md`,
  kept SE v0.6 as unsurfaced model-family variants, and recorded the
  now-authorized separate Qwen repair v02 full-200 aggregate-only
  predeclaration.
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
