# Project Status

Last updated: 2026-06-04

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions one at a
time under exact-evidence, attribution, hidden-family, and split-discipline
constraints.

The first-pass RQ1/RQ2/RQ4 reports are diagnostic baseline audits, not completed
answers. They fell back to the already-known deterministic safety answer; active
work now isolates LLM component mechanics before any move to RQ5.

## Current Strategy

Use saved artifacts as research instruments for clean component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

Important context: hybrid safety-floor validation reached 697/750 Purist and
704/750 Pragmatic; local frozen `selective_safety_floor_gate_v0` improved
test450 from 343/450 to 351/450 Purist with 0 C->W. These remain development
or local-audit evidence, not LLM-first or benchmark claims.

## Active Question

RQ1/RQ2/RQ4 Reset. LLM Component Mechanics

Question: Which LLM components generate useful candidates, select decisive
evidence, and project the correct current benchmark-relevant state, and why do
they help or fail on specific rows and hidden families?

Status: active reset. The first-pass RQ1/RQ2/RQ4 reports and matrices remain
diagnostic sources, but their deterministic-default conclusions are downgraded.

Core artifacts:
`docs/research/gan2026_llm_component_mechanics_protocol_2026-06-03.md`
`docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-03.md`
`experiments/gan2026_llm_component_mechanics_rows_2026-06-03.md` and
`experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl`
`docs/research/gan2026_llm_component_mechanics_error_analysis_2026-06-03.md`
`docs/research/gan2026_llm_component_interpretation_policy_and_controlled_experiments_2026-06-03.md`
`docs/research/gan2026_ambiguous_case_decision_log.md`

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
- Do not penalize projection-compatible phrases, faithful ambiguous facts, or
  multiple plausible candidates by default. Assign first-failure ownership
  before calling a row an LLM component failure.

## Work Board

### Now

- Run the frozen follow-up component-projection panel with the interpretation
  policy applied: propagate hidden-family tags through RQ2/RQ4 rows, add
  first-failure-owner labels, and predeclare gated projection slices plus
  regression panels.
- Catalogue recurring ambiguous representation cases in
  `docs/research/gan2026_ambiguous_case_decision_log.md` and make firm
  projection/ownership decisions before treating them as component failures.

### Next

- If the frozen panel remains confounded, run controlled single-task experiments
  for candidate generation, evidence selection, projection, schema
  representation, and combined-task ablations before returning to RQ5.
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

- 2026-06-04: Created the running ambiguous-case decision log with initial firm
  decisions for `multiple times per week` and `multiple per shift`; added the
  catalogue task to the active work board so recurring representation cases get
  explicit projection and ownership policy.
- 2026-06-03: Cemented interpretation policy for the reset: projection-compatible
  clinical phrases, faithful ambiguous facts, and multiple plausible candidates
  are not LLM failures by default; added controlled experiment plan and deeper
  mechanism error analysis.
- 2026-06-03: Reset RQ1/RQ2/RQ4 interpretation and added the restart protocol,
  synthesis, and compact row artifact: 195 mechanism rows over 111 source rows.
  First-pass RQ reports remain source matrices but are downgraded as answers.
