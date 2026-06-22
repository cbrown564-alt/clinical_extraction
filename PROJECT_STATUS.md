# Project Status

Last updated: 2026-06-22

## Active Objective

Final project consolidation is active. The goal is to preserve the canonical
Gan 2026 and ExECTv2 evidence spine, report the final model/architecture
comparison conservatively, make ExECTv2 reviewable in the frontend, and plan
repo simplification without deleting or moving evidence.

## Current Read

ExECTv2 v08 is the achieved dev140 performance control:
`exectv2_holistic_finding_assembly_v08_dev140`. Official family headlines are
Diagnosis `0.9083`, SeizureFrequency `0.9053`, Prescription `0.9357`,
Investigations `0.9132`, overall `0.9152`. Claim boundary: dev-only
component-attributed evidence, not a full-200, locked-test, or benchmark claim.

ExECTv2 v09 partial hybrid is the simplification control:
`exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140`, overall
`0.9059`. It keeps focused Diagnosis/SF and deterministic Prescription while
dropping the v08 Investigations stack. It is not the performance control because
Investigations falls to `0.8549`.

DeepSeek v0.9.16 dev140 is the final hosted non-GPT diagnostic comparator:
`exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`, overall
`0.9010`, Diagnosis `0.8828`, SeizureFrequency `0.8675`, Prescription
`0.9430`, Investigations `0.9231`, exact evidence `1.0000`. It is strong
transfer evidence, but its final gate decision is `do-not-promote` because
Dx/SF remain below the GPT control and changed-row controls fail.

Qwen v0.9.22 dev140 is the final local-model diagnostic comparator:
`exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140`,
overall `0.9001`, Diagnosis `0.8563`, SeizureFrequency `0.8908`,
Prescription `0.9343`, Investigations `0.9579`, exact evidence `1.0000`.
It remains `do-not-promote` because Diagnosis and active-rate fidelity remain
weak and ten parse/schema failures are visible on each family lens surface.

Phase 0 consolidation artifacts now exist:
`docs/experiments/final_artifact_index_2026-06-22.md`,
`docs/experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md`,
`docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`,
`docs/research/final_architecture_selection_2026-06-22.md`, and
`docs/plans/repo_simplification_plan_2026-06-22.md`.

Frontend Phase 0 ExECTv2 support is present at `/exectv2`: static ExECTv2 mock
data, task-aware registry entries, ExECTv2 frontend types, and a letter/result
explorer for the earlier Phase 0 selected set. This route is now explicitly an
interim prototype and data source, not the target app architecture. The
frontend mock data and registry still need a refresh if the final DeepSeek
v0.9.16 and Qwen v0.9.22 dev140 diagnostics should be visible in-app.

The target frontend architecture is dataset-aware integration: ExECTv2 should
be selectable as a sticky top-right dataset option and should drive the shared
Example Explorer, Aggregate Performance, Component Impact, and Error Gallery
surfaces. Implementation plan:
`docs/plans/exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md`.

## Active Priorities

1. Treat v08 as the ExECTv2 performance control and v09 partial hybrid as the
   simplification control.
2. Treat final DeepSeek/Qwen dev140 rows as diagnostic portability evidence
   unless a future predeclared gate changes that.
3. Keep deterministic semantic lenses and dictionary repairs visible as
   prediction-bearing when they change clinical facts or attributes.
4. Do not run ExECTv2 full-200 or holdout-facing row-level analysis without a
   frozen aggregate/readout protocol.
5. Integrate ExECTv2 into the existing explorer surfaces as a dataset, not as a
   standalone tab or route.
6. Defer destructive repo cleanup until the artifact index and report set are
   accepted as the evidence spine.

## Work Board

### Now

- Review Phase 0 closeout docs for final-paper wording and decide whether
  final DeepSeek/Qwen diagnostic wording is ready for paper tables.
- Begin the dataset-integration frontend plan: add shared dataset descriptors,
  sticky dataset selection, dataset-indexed static data, and a workbench
  `SpecimenRef` path that supports both Gan rows and ExECTv2 letters.

### Next

- Refresh frontend static data and registry so `/exectv2` or the future
  dataset-integrated explorer shows DeepSeek v0.9.16 and Qwen v0.9.22 dev140.
- Stop non-GPT model iteration unless a new predeclared portability or
  review-routing question justifies it.
- Start a cleanup branch that archives/quarantines superseded diagnostics only
  after the final index is accepted.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection needs benchmark-facing
  protocol, scorer surface, stop rule, and inspection boundary.

### Done Recently

- 2026-06-22: Updated the final artifact index, ExECTv2 cross-model closeout,
  reliability scorecard, architecture selection, and frontend integration plan
  for final DeepSeek v0.9.16 and Qwen v0.9.22 dev140 diagnostics.
- 2026-06-22: Added a separate ExECTv2 frontend dataset-integration plan that
  supersedes `/exectv2` as the target destination.
- 2026-06-22: Completed Phase 0 final consolidation docs and frontend ExECTv2
  static-review slice.
- 2026-06-21: Completed ExECTv2 v08 all-four clearance and reliability
  scorecard.
- 2026-06-21: Completed Gan 2026 Qwen v0.6 hybrid repairfix frozen aggregate
  test450 audit without row-level test inspection for development.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development
  without explicit authorization and a frozen protocol.
- Do not make benchmark/full-200 claims from dev140 or dev25 evidence.
- Keep deterministic certainty/CUI/format repairs and semantic add/drop/replace
  actions provenance-stamped and attribution-clean.
