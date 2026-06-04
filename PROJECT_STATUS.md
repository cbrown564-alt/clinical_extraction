# Project Status

Last updated: 2026-06-04

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

## Current Strategy

Use saved artifacts as research instruments for component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

RQ9 is answered for saved validation replay in
`docs/research/gan2026_rq9_selective_action_answer_2026-06-04.md`: selective
action with bounded prediction, abstention, human review, and monitoring. The
v3 router covers 716/750 validation rows, abstains on 26, routes 8 to human
review, and has covered-row Purist accuracy 0.9469. It is a
validation-development artifact only.

The frozen RQ9 selective-action holdout audit protocol is written in
`docs/research/gan2026_rq9_selective_action_frozen_holdout_audit_protocol_2026-06-04.md`.
It fixes v3, the source candidate, monitoring slices, required metrics, allowed
first readout, and post-run inspection limits before any locked-test use. It
does not run or authorize locked-test evaluation.

RQ10 is answered for saved validation replay: among 53 residual Purist misses,
23 are `underdetermined_note`, 19 are `true_extraction_failure`, and 11 are
`benchmark_convention_dominated`; 0 are strong likely gold defects. A full
validation750 gold/reference review CSV exists for manual adjudication.

Candidate-union and ambiguity ownership are answered for saved validation
artifacts in
`docs/research/gan2026_candidate_union_and_ambiguity_ownership_report_2026-06-04.md`.
Saved union recall improved from 25/75 deterministic rows to 47/75, with 22
saved boundary rescues and 0 deterministic-recall losses. V3 boundary candidates
are useful as selected-state inputs, but primary v3 candidate-state projection
would regress 6 deterministic-correct rows, so deterministic safety-floor
projection remains the policy boundary.

## Active Question

Candidate Union And Ambiguity Ownership

Status: candidate-union, selective boundary-candidate, suspicious-state routing,
selected-state union replay, verifier predeclarations, and RQ9
abstention/review routing are materialized on saved artifacts. The current
answer is parallel deterministic plus gated selective boundary-candidate
proposal, rich selected-state fact carrying, and deterministic
render/unknown/review policy. A selective verifier remains a predeclared backup
for stable suspicious slices because naive deterministic unknown-routing caused
6 C->W regressions.

Core artifacts:

- Architecture: `docs/research/gan2026_candidate_union_and_ambiguity_ownership_report_2026-06-04.md`
- RQ9 contract: `docs/research/gan2026_rq9_selective_action_evaluation_contract_2026-06-04.md`
- RQ9 answer: `docs/research/gan2026_rq9_selective_action_answer_2026-06-04.md`
- RQ9 frozen holdout protocol: `docs/research/gan2026_rq9_selective_action_frozen_holdout_audit_protocol_2026-06-04.md`
- RQ9 v3 router: `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.*`
- RQ9 cluster/convention monitoring: `experiments/gan2026_rq9_cluster_convention_monitoring_2026-06-04.*`
- Candidate-union artifacts: `experiments/gan2026_candidate_union_saved_artifact_2026-06-04.*`
- Selected-state replay: `experiments/gan2026_selected_state_union_replay_v3_2026-06-04.*`

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Any holdout-facing use needs a frozen predeclared audit and explicit user
  authorization.
- Do not change scorer/gold policy from RQ10 alone; use it for abstention,
  review routing, or separate policy predeclaration.
- Final F1 is secondary to candidate recall, evidence exactness, projection
  consistency, metadata completeness, ambiguity preservation, and regression
  accounting.

## Work Board

### Now

- No active implementation task is open. Keep RQ9 holdout use blocked until a
  user explicitly authorizes verifying a runnable locked-test audit command
  against the frozen protocol.

### Next

- If holdout is later authorized, verify the runnable command against
  `docs/research/gan2026_rq9_selective_action_frozen_holdout_audit_protocol_2026-06-04.md`
  and record all frozen inputs before execution.
- Keep missing-anchor abstentions and last-event human-review routing unchanged
  unless a new predeclared policy targets a narrower source-backed slice.

### Backlog

- Rewrite `llm_only_minimal_evidence_selector.py` under prompt-language audit
  before any new minimal-evidence calls.
- RQ5 follow-up implementation only if a non-state-graph selected-state surface
  exposes fixed bundles that need rendering audit.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until component questions are answered.

### Done Recently

- 2026-06-04: Wrote the frozen RQ9 selective-action holdout audit protocol.
- 2026-06-04: Wrote the RQ9 selective-action answer and promotion boundary.
- 2026-06-04: Materialized RQ9 v3 trigger-context narrowing, last-event routing,
  and cluster/convention monitoring artifacts.
