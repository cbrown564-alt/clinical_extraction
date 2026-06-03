# Project Status

Last updated: 2026-06-03

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions one at a
time under exact-evidence, attribution, hidden-family, and split-discipline
constraints.

RQ1 candidate discovery is answered for saved validation replay as a
development-control question, not as a holdout-transfer claim. The active
question is now RQ2 evidence selection.

## Current Strategy

Use saved artifacts as research instruments for clean component questions
instead of chasing whole-pipeline validation F1. End-to-end assembly comes later.

Important context:

- Hybrid deterministic safety-floor validation evidence reached 697/750 Purist
  and 704/750 Pragmatic with exact evidence and no deterministic-correct
  regressions; this remains hybrid development evidence, not an LLM-first or
  benchmark claim.
- `selective_safety_floor_gate_v0` produced a frozen local audit: test450 moved
  from 343/450 to 351/450 Purist, with 14 changed rows, 8 wrong-to-correct, 0
  correct-to-wrong, and 14/14 exact changed-row evidence.
- `typed_operations_v0` and A2 sparse operands are paused as broad candidates,
  but their artifacts remain useful for schema and adapter questions.

## Active Question

RQ2. Evidence Selection

Question: Given the note and/or a fixed candidate set, which component best
selects the prediction-bearing evidence span?

Status: active next question. Prior LLM selected-evidence runs are promising,
but evidence selection has not yet been cleanly compared as its own component
question.

RQ1 answer:
`docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-03.md`

RQ1 matrix:
`experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.md`

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
  Validation is the development surface; locked test is not for row-level
  tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Before promotion or LLM-superiority language, apply Decision 0008: component
  evidence matrix, exact changed-row evidence, LLM delta accounting,
  deterministic-correct regression accounting, and hidden-family breakdown.
- Broad validation or frozen-test work must answer the active question, not
  maximize total score.
- Any holdout-facing use of the RQ1 conclusion needs a predeclared
  boundary/uncertainty stress check or must keep the claim validation-only.

## Key Artifacts

- RQ retrospective:
  `docs/research/gan2026_research_question_retrospective_2026-06-03.md`
- RQ1 protocol:
  `docs/research/gan2026_rq1_candidate_discovery_protocol_2026-06-03.md`
- RQ1 answer:
  `docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-03.md`
- Component evidence contract:
  `docs/design/component_evidence_attribution_architecture.md`
- Hidden-family atlas:
  `docs/research/gan2026_hidden_family_first_failure_atlas_2026-06-03.md`
- Candidate-promotion decision:
  `docs/decisions/0008-component-evidence-contract-for-candidate-promotion.md`

## Work Board

### Now

- Design the RQ2 evidence-selection protocol using deterministic all-candidates
  or state-graph nodes as the fixed candidate substrate.

### Next

- Compare selected evidence across deterministic, LLM selected-state/evidence,
  typed-operation, claim-table, and hybrid sidecar artifacts.
- Keep the LLM missing-candidate proposer as an optional RQ1 follow-up only if
  fixed-candidate evidence selection reveals missing candidates still dominate.

### Backlog

- RQ4 projection-only benchmark over fixed candidates/states.
- RQ3 schema comparison using selected evidence, sparse operands, typed
  operations, claim table, state graph, and possible boundary tags.
- RQ9 abstention/coverage-accuracy protocol.
- RQ10 gold/scorer ambiguity audit.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline architecture promotion is blocked until the relevant component
  questions are answered.

### Done Recently

- 2026-06-03: Wrote and tightened the RQ1 answer report. RQ1 is answered for
  saved validation replay only: deterministic all-candidates/state-graph nodes
  are the best broad substrates, while the LLM sidecar is a selective rescue
  hypothesis that still needs anti-overfit stress testing.
- 2026-06-03: Built the RQ1 candidate-discovery matrix from saved validation
  artifacts: 5,442 candidate rows across 750 source rows.
