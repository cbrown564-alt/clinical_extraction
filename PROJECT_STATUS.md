# Project Status

Last updated: 2026-06-03

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions one at a
time, starting with candidate discovery, under exact-evidence, attribution,
hidden-family, and split-discipline constraints.

The project is no longer optimizing for the next whole-pipeline validation F1
increase. End-to-end assembly will come later, after the essential component
questions have high-certainty answers.

## Current Strategy

Stop broad architecture proliferation. Use the current experiment base as a
research instrument for clean component questions:

- which component finds the right candidates;
- which component selects the right evidence;
- which schema best represents the clinical frequency state;
- which projection policy chooses the right current state;
- which deterministic compiler renders safely;
- where the LLM adds reliable selective value;
- which findings transfer by hidden family and surface.

The control report for this phase is
`docs/research/gan2026_research_question_retrospective_2026-06-03.md`.

Important context:

- The hybrid deterministic safety-floor lane reached validation750 697/750
  Purist and 704/750 Pragmatic with exact evidence and no deterministic-correct
  regressions, but this is hybrid development evidence, not an LLM-first or
  benchmark claim.
- `selective_safety_floor_gate_v0` produced a valid frozen local
  generalization audit: test450 improved from 343/450 to 351/450 Purist, with
  14 changed rows, 8 wrong-to-correct, 0 correct-to-wrong, and 14/14 exact
  changed-row evidence. This remains a hybrid selective-action result.
- `typed_operations_v0` and A2 sparse operands are paused as broad candidates.
  Their evidence is useful for schema and adapter questions, but they should
  not be repaired in place to chase aggregate validation F1.
- The hidden-family/first-failure atlas and component-evidence contract are now
  mandatory framing for promotion or research-answer claims.

## Single-Question Discipline

Only one primary research question may be active at a time. The active question
owns implementation, experiments, reports, and status updates until it is
answered, rejected, or explicitly blocked.

Allowed work:

- artifact replay over saved outputs;
- hard-slice and hidden-family component analyses;
- small fresh experiments designed around one component metric;
- synthetic stress panels for a predeclared mechanism;
- same-row and same-raw-output comparisons;
- instrumentation needed to answer the active question.

Disallowed work unless explicitly justified by the active question:

- new whole-pipeline architectures;
- broad validation750 runs whose purpose is overall F1 improvement;
- prompt or adapter patches judged mainly by total Purist/Pragmatic score;
- locked-test row-level tuning;
- mixing multiple component questions in one experiment without a primary
  question and predeclared secondary readouts.

Every experiment must name:

- active research question;
- component under test;
- fixed comparison component;
- distribution or surface;
- component metric;
- hidden-family stratification;
- claim boundary.

## Research Question Queue

### RQ1. Candidate Discovery

Question: Which component produces the best candidate set for seizure-frequency
state: high gold-state recall, exact evidence, rich useful metadata, and bounded
candidate count?

Status: active next question; not answered.

Completion criterion: a report can state which candidate generator has the best
recall/precision/metadata/candidate-burden trade-off by hidden family, and what
instrumentation remains missing.

### RQ2. Evidence Selection

Question: Given the note and/or candidate set, which component best selects the
prediction-bearing evidence span?

Status: partly answered by prior LLM selected-evidence runs, but not yet cleanly
compared as its own component question.

### RQ3. Clinical State Representation

Question: What intermediate schema best represents the clinical frequency state
for downstream reasoning?

Status: partly answered negatively. A2 and typed operations show that richer
schemas can regress broad generalization when decision ownership is duplicated.

### RQ4. Projection

Question: Given a fixed candidate/state representation, which projection policy
best selects the current benchmark-relevant state?

Status: not answered. Existing artifacts expose projection failures but do not
yet benchmark projection as an isolated component.

### RQ5. Deterministic Compilation And Rendering

Question: Once the correct clinical state is selected, what deterministic
compiler renders it into Gan-compatible labels without semantic drift?

Status: partly answered. Selected-evidence arithmetic is often strong; sparse
operands and typed graph projection introduced avoidable regressions.

### RQ6. Selective LLM Value

Question: Where does the LLM add reliable value over deterministic rules under
exact-evidence and no-regression constraints?

Status: mostly answered for `selective_safety_floor_gate_v0`, not globally.

### RQ7. Generalization By Hidden Family

Question: Which component gains transfer across hidden families, validation
prefixes, later validation rows, hard slices, and frozen audit surfaces?

Status: partly answered. The atlas exists, but it must become the stratification
layer for every component question.

### RQ8. Efficiency And Operational Reliability

Question: What schema/component design gives the best performance per token,
cost, latency, parse reliability, and implementation complexity?

Status: not answered.

### RQ9. Abstention And Human Review

Question: Can the system identify underdetermined, conflicting, stale-only, or
ambiguous cases instead of forcing a brittle label?

Status: not answered.

### RQ10. Gold And Scorer Validity

Question: How much residual error reflects true extraction failure versus
benchmark convention, underdetermined notes, clinically defensible alternatives,
or possible gold-label weakness?

Status: not answered.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
  Validation is the development surface; locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Keep semantic repair, graph projection, scorer normalization, deterministic
  adapters, safety floors, and production policy separately named and ablated.
- Before promotion or LLM-superiority language, apply Decision 0008:
  component evidence matrix, exact changed-row evidence, LLM delta accounting,
  deterministic-correct regression accounting, and hidden-family breakdown.
- A broad validation or frozen-test run must be justified as answering the
  active question, not as maximizing total score.

## Key Artifacts

- Research-question control report:
  `docs/research/gan2026_research_question_retrospective_2026-06-03.md`
- Critical-analysis source:
  `literature/gan2026_critical_analysis_pathways_forward.pdf`
- Component evidence contract:
  `docs/design/component_evidence_attribution_architecture.md`
- Candidate-promotion decision:
  `docs/decisions/0008-component-evidence-contract-for-candidate-promotion.md`
- Hidden-family atlas:
  `docs/research/gan2026_hidden_family_first_failure_atlas_2026-06-03.md`
- Selective safety-floor audit:
  `experiments/gan2026_selective_safety_floor_gate_v0_component_evidence_audit_2026-06-03.md`
- A2/A3/typed operations generalization audit:
  `docs/research/gan2026_a2_a3_typed_operations_generalization_audit_2026-06-03.md`

## Work Board

### Now

- Design the RQ1 candidate-discovery protocol: surfaces, candidate generators,
  gold-state matching policy, metadata completeness fields, candidate-burden
  metrics, and hidden-family readouts.
- Reuse saved artifacts before making fresh model calls.

### Next

- Build or reuse a candidate-discovery matrix with one row per source row,
  generator, candidate, evidence status, metadata fields, hidden-family tags,
  and gold-state match.
- Run a small predeclared LLM missing-candidate proposer only if artifact replay
  cannot answer RQ1.
- Write the RQ1 answer report before moving to RQ2.

### Backlog

- RQ2 evidence-selection comparison across deterministic, selected-state,
  typed-operation, claim-table, and hybrid sidecar evidence.
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

- 2026-06-03: Reframed Gan 2026 work around single-question component research
  discipline and recorded the full retrospective in
  `docs/research/gan2026_research_question_retrospective_2026-06-03.md`.
- 2026-06-03: Recorded that A2 sparse operands and typed operations are useful
  schema/adapter evidence but should not continue as broad validation-F1 repair
  lanes.
- 2026-06-03: Completed component-evidence interpretation for
  `selective_safety_floor_gate_v0`, preserving hybrid attribution and frozen
  local-audit claim boundaries.
