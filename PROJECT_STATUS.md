# Project Status

Last updated: 2026-06-03

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions one at a
time under exact-evidence, attribution, hidden-family, and split-discipline
constraints.

The first-pass RQ1 candidate discovery, RQ2 evidence selection, and RQ4
projection reports are now classified as diagnostic baseline audits, not
completed research-question answers. They fell back to "the validation-tuned
deterministic selector/top candidate is safest," which is already known and not
the scientific question. The active work returns to RQ1/RQ2/RQ4 LLM component
mechanics before any move to RQ5 deterministic compilation and rendering.

## Current Strategy

Use saved artifacts as research instruments for clean component questions
instead of chasing whole-pipeline validation F1. End-to-end assembly comes later.
Deterministic rules are frozen comparators, safety floors, and miss-slice
definers, not eligible answers for RQ1-RQ4.

Important context: hybrid deterministic safety-floor validation evidence reached
697/750 Purist and 704/750 Pragmatic with exact evidence and no
deterministic-correct regressions; this remains development evidence, not an
LLM-first or benchmark claim. The frozen local `selective_safety_floor_gate_v0`
audit improved test450 from 343/450 to 351/450 Purist with 0 C->W, but
benchmark-comparable language remains blocked.

## Active Question

RQ1/RQ2/RQ4 Reset. LLM Component Mechanics

Question: Which LLM components generate useful candidates, select clinically
decisive evidence, and project the correct current benchmark-relevant state, and
why do they help or fail on specific rows and hidden families?

Status: active reset. The RQ1/RQ2/RQ4 artifacts remain useful as source-backed
matrices, but their deterministic-default conclusions are downgraded. The next
report should inspect row-level LLM wins, losses, and ambiguous cases before
making any aggregate claim.

Diagnostic artifacts to reuse: RQ1 answer/matrix,
`docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-03.md` and
`experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.md`; RQ2
answer/matrix,
`docs/research/gan2026_rq2_evidence_selection_answer_2026-06-03.md` and
`experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.md`; RQ4
answer/matrix, `docs/research/gan2026_rq4_projection_answer_2026-06-03.md` and
`experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.md`.

Active reset protocol:
`docs/research/gan2026_llm_component_mechanics_protocol_2026-06-03.md`

Active reset synthesis:
`docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-03.md`

Active row-level mechanism artifact:
`experiments/gan2026_llm_component_mechanics_rows_2026-06-03.md` and
`experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl`

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
  Validation is the development surface; locked test is not for row-level
  tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Do not treat "deterministic top still wins" as an RQ1-RQ4 answer.
- Before promotion or LLM-superiority language, apply Decision 0008: component
  evidence matrix, exact changed-row evidence, LLM delta accounting,
  deterministic-correct regression accounting, and hidden-family breakdown.
- Broad validation or frozen-test work must answer the active component
  question, not maximize total score.
- Any holdout-facing use of LLM component conclusions needs a frozen
  predeclared audit or must keep the claim validation-only.

## Work Board

### Now

- Use the row-level mechanism artifact to write the next deeper error-analysis
  narrative: candidate-generation mechanics, evidence-selection mechanics, and
  projection mechanics by hidden family.

### Next

- Only after LLM candidate/evidence/projection mechanics are understood, return
  to RQ5 compiler/rendering over fixed selected states.

### Backlog

- RQ3 schema comparison using selected evidence, sparse operands, typed
  operations, claim table, state graph, and possible boundary tags.
- RQ5 deterministic compilation/rendering over fixed selected states/evidence.
- Preserve RQ4 diagnostic graph policies for a future frozen gated projection
  audit: boundary-state priority and graph-gated month-bucket duration.
- RQ9 abstention/coverage-accuracy protocol.
- RQ10 gold/scorer ambiguity audit.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline architecture promotion is blocked until the relevant component
  questions are answered.

### Done Recently

- 2026-06-03: Reset RQ1/RQ2/RQ4 interpretation. The answer reports and matrices
  are retained as diagnostic artifacts, but their deterministic-default
  conclusions are not accepted as meaningful research-question answers. Active
  work returns to LLM component mechanics and row-level error analysis.
- 2026-06-03: Added the LLM component mechanics restart protocol and synthesis.
  The synthesis identifies narrow LLM rescue mechanisms for boundary/uncertainty
  candidates, high exact-evidence but weak state projection, and selective graph
  projection gains for boundary and duration mechanisms. It explicitly
  supersedes the deterministic-default conclusions in first-pass RQ1/RQ2/RQ4.
- 2026-06-03: Built the compact LLM component mechanics artifact:
  195 mechanism rows over 111 source rows, covering LLM candidate wins/losses,
  candidate burden, exact-evidence-but-wrong-state rows, changed W->C/C->W rows,
  graph projection W->C/C->W rows, and schema-near projection misses.
- 2026-06-03: First-pass RQ4 projection diagnostic: deterministic top remained
  safest on validation replay (697/750 Purist), broad state-graph projection
  regressed (655/750, 49 changed labels, 0 W->C, 42 C->W), and narrow graph
  policies looked diagnostic for boundary-state and seizure-free-duration
  surfaces. This does not answer LLM projection mechanics. Artifacts:
  `docs/research/gan2026_rq4_projection_answer_2026-06-03.md` and
  `experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.md`.
- 2026-06-03: First-pass RQ2 evidence-selection diagnostic: hybrid adjudicator
  evidence was 750/750 exact/source-id-valid, but its four changed labels were
  all deterministic-correct regressions. This supports row-level LLM evidence
  analysis, not deterministic-default completion.
- 2026-06-03: First-pass RQ1 candidate-discovery diagnostic: deterministic
  all-candidates/state-graph nodes were strong validation substrates, while the
  LLM sidecar remained a selective rescue signal. This must be reworked as an
  LLM candidate-mechanics question.
