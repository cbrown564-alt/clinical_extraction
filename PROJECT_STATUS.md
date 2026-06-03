# Project Status

Last updated: 2026-06-04

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions one at a
time under exact-evidence, attribution, hidden-family, and split-discipline
constraints.

RQ1/RQ2 are reopened for single-task controls. The 2026-06-04 component
mechanics reports remain useful validation-development diagnostics, but they do
not yet establish isolated model ceilings for candidate generation, evidence
selection, or projection, nor the degradation caused by combining those tasks in
one prompt. No holdout or benchmark-comparable claim is authorized.

## Current Strategy

Use saved artifacts as research instruments for clean component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4. The next
phase isolates one LLM task at a time before returning to schema comparison or
architecture assembly.

Important context: hybrid safety-floor validation reached 697/750 Purist and
704/750 Pragmatic; local frozen `selective_safety_floor_gate_v0` improved
test450 from 343/450 to 351/450 Purist with 0 C->W. These remain development
or local-audit evidence, not LLM-first or benchmark claims.

## Active Question

RQ1/RQ2 Controls. Isolated Candidate, Evidence, And Projection Baselines

Question: when the model is asked to do only candidate generation, only evidence
selection, or only projection, with rich task-specific instructions and no
downstream F1 pressure, how well can it perform each task?

Status: protocol and fixed row surfaces are materialized; next step is to write
prompt/schema stubs and run isolated validation50 controls before paired-task
ablations. RQ3 is paused until these controls show whether schema failures are
model capability limits, prompt overload, or representation-shape problems.

Core artifacts: `docs/research/gan2026_rq1_rq2_single_task_controls_protocol_2026-06-04.md`,
`experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.jsonl`,
`experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.md`,
`experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl`,
`experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.md`,
`docs/research/gan2026_llm_component_interpretation_policy_and_controlled_experiments_2026-06-03.md`,
`docs/research/gan2026_rq5_deterministic_compilation_rendering_protocol_2026-06-04.md`,
`docs/research/gan2026_rq5_deterministic_compilation_rendering_answer_2026-06-04.md`,
`experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.jsonl`,
`experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.md`,
`docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-04.md`,
`docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-04.md`,
`docs/research/gan2026_rq2_evidence_selection_answer_2026-06-04.md`,
`docs/research/gan2026_rq4_projection_answer_2026-06-04.md`,
`experiments/gan2026_component_projection_followup_panel_2026-06-04.md`,
`docs/research/gan2026_ambiguous_case_decision_log.md`, and
`docs/research/gan2026_acd_projection_policy_predeclaration_2026-06-04.md`.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout;
  locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Do not treat "deterministic top still wins" as an RQ1-RQ4 answer.
- Before promotion or LLM-superiority language, apply Decision 0008 component
  evidence, exact changed-row evidence, LLM delta, regression, and hidden-family
  gates.
- Broad validation or frozen-test work must answer the active component
  question, not maximize total score.
- Any holdout-facing use needs a frozen predeclared audit or must keep the claim
  validation-only.
- Do not penalize projection-compatible phrases, faithful ambiguous facts, or
  multiple plausible candidates by default. Assign first-failure ownership
  before calling a row an LLM component failure.
- Isolated controls must be interpreted before paired-task prompts; final F1 is
  secondary to candidate recall, evidence exactness, projection consistency,
  metadata completeness, ambiguity preservation, and regression accounting.

## Work Board

### Now

- Write frozen prompt/schema stubs for `candidate_only`,
  `gold_query_evidence_only`, `candidate_conditioned_evidence_only`, and
  `projection_only`.
- Run validation50 isolated controls on the fixed
  `balanced_validation50` panel and inspect row-level mechanisms.

### Next

- Decide from validation50 isolated results whether and how to run the fixed
  `hidden_family_hard_panel`.
- Run paired-task overload controls only after isolated candidate, evidence, and
  projection ceilings are interpreted.

### Backlog

- Resume RQ3 schema-comparison protocol after single-task controls identify the
  representation failures that need schema comparison.
- RQ5 follow-up implementation only if a non-state-graph selected-state surface
  exposes fixed bundles that need rendering audit.
- RQ9 abstention/coverage-accuracy protocol.
- RQ10 gold/scorer ambiguity audit.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until component questions are answered.

### Done Recently

- 2026-06-04: Materialized the fixed RQ1/RQ2 control surfaces:
  `balanced_validation50` has 50 validation rows across frequency,
  seizure-free, unknown, no-reference, unresolved-multiple, cluster/diary,
  denominator/window, current-vs-historical, and competing-semiology cases;
  `hidden_family_hard_panel` has 75 validation hard rows from the atlas and
  component-projection follow-up panel. Added the pre-call
  component-control matrix with 875 row-condition records across candidate-only,
  evidence-only, projection-only, and paired-task overload conditions.
- 2026-06-04: Reopened RQ1/RQ2 for clean single-task controls and wrote the
  [RQ1/RQ2 single-task controls protocol](docs/research/gan2026_rq1_rq2_single_task_controls_protocol_2026-06-04.md):
  candidate generation, evidence selection, projection, and paired-task overload
  must be measured on fixed validation panels before RQ3 resumes.
- 2026-06-04: Wrote the
  [RQ5 deterministic compilation/rendering answer](docs/research/gan2026_rq5_deterministic_compilation_rendering_answer_2026-06-04.md):
  RQ5 is answered for saved validation replay and focused ACD fixtures. Current
  production has 0 semantic-drift rows and 0 attribution-loss rows; ACD-off
  ablation creates 6 policy-removal drifts, showing explicit ACD policy is
  component-relevant.
- 2026-06-04: Wrote final validation-development component answers for
  [RQ1](docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-04.md),
  [RQ2](docs/research/gan2026_rq2_evidence_selection_answer_2026-06-04.md),
  [RQ4](docs/research/gan2026_rq4_projection_answer_2026-06-04.md), and the
  [combined synthesis](docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-04.md):
  these remain diagnostic for the reopened single-task controls rather than a
  sufficient basis to move on to RQ3.
- 2026-06-04: Predeclared and implemented ACD-003 through ACD-010 gated
  projection policies in `docs/research/gan2026_acd_projection_policy_predeclaration_2026-06-04.md`
  and `tests/test_gan2026_state_graph.py`; claims remain validation-only.
- 2026-06-04: Ran the frozen component-projection follow-up panel and completed
  ambiguous-case/target-row inspection; `projection_policy` is the largest
  failure owner at 152 panel rows.
- 2026-06-03: Reset RQ1/RQ2/RQ4 interpretation and added the mechanism
  protocol, synthesis, error analysis, and 195-row mechanism artifact.
