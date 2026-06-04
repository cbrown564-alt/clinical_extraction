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

RQ1-RQ10 now have bounded validation-development answers or explicit claim
boundaries. RQ3 remains a positive hard-panel direction with unresolved
projection-policy work, and no benchmark-comparable claim is authorized.

Key answer docs: RQ6
`docs/research/gan2026_rq6_selective_llm_value_answer_2026-06-04.md`, RQ7
`docs/research/gan2026_rq7_family_indexed_component_matrix_answer_2026-06-04.md`,
RQ8
`docs/research/gan2026_rq8_efficiency_operational_reliability_answer_2026-06-04.md`,
RQ9 `docs/research/gan2026_rq9_selective_action_answer_2026-06-04.md`, and
RQ10
`docs/research/gan2026_rq10_gold_scorer_ambiguity_audit_answer_2026-06-04.md`.

Important numbers: `selective_safety_floor_gate_v0` changed 21 validation750
rows with 11 W->C and 0 C->W, and 14 frozen local test450 rows with 8 W->C and
0 C->W. RQ9 v3 covers 716/750 validation rows, abstains on 26, routes 8 to
human review, and has covered-row Purist accuracy 0.9469. RQ10 found 23
`underdetermined_note`, 19 `true_extraction_failure`, 11
`benchmark_convention_dominated`, and 0 strong likely gold defects among 53
residual Purist misses.

## Active Question

Staged Hybrid Assembly

Status: architecture assembly readiness is accepted for validation
development. The older broad LLM-first V1 hypothesis is superseded by the
staged hybrid assembly decision.

Core artifacts:

- RQ8 answer: `docs/research/gan2026_rq8_efficiency_operational_reliability_answer_2026-06-04.md`
- RQ8 matrix: `experiments/gan2026_rq8_operational_matrix_2026-06-04.*`
- RQ7 matrix: `experiments/gan2026_rq7_family_component_matrix_2026-06-04.*`
- Component-control matrix: `experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.*`
- Assembly decision: `docs/research/gan2026_architecture_assembly_readiness_decision_2026-06-04.md`
- ADR: `docs/decisions/0009-gan2026-staged-hybrid-assembly.md`

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

- Replay the assembled validation-development policy on existing hard-panel
  artifacts before any new model calls.

### Next

- Regenerate the suspicious selected-state routing artifact over saved rich-state
  rows with the new source-id trace.
- Add projection/source-id consistency checks to the assembled candidate report.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until the family-indexed matrix is
  implemented as an auditable assembled candidate and any holdout-facing use
  has a frozen protocol.

### Done Recently

- 2026-06-04: Started the smallest staged-hybrid assembly slice: rich
  selected-state extraction now derives `selected_source_ids=["note"]` and
  `source_id_status` from exact evidence, and suspicious routing sends invalid
  source-id traces to review.
- 2026-06-04: Added RQ6 selective LLM value answer, RQ7 hidden-family
  synthesis/family matrix answer, and RQ8 operational-reliability
  protocol/answer after the RQ1-RQ10 review.
- 2026-06-04: Accepted staged hybrid assembly for validation development in
  ADR 0009 and the architecture readiness report.
