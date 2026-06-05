# Gan 2026 Multi-Component Assembly End-To-End Plan

Date: 2026-06-04

Status: pre-implementation plan for validation-development construction,
full-validation freeze, and frozen holdout audit. This is not a
benchmark-comparable claim.

## Objective

Construct a runnable Gan 2026 multi-component staged hybrid candidate, evaluate
it on the full validation split, freeze it if it satisfies the predeclared
promotion gates, and then evaluate the frozen candidate on the locked test
split without test-driven tuning.

The candidate family is:

```text
hybrid_multi_component_staged_assembly
```

Use this claim language:

```text
hybrid staged candidate/evidence/state architecture with deterministic
projection, safety-floor action, and abstention/review policy
```

Do not call the candidate LLM-first. Deterministic candidates, state-graph
nodes, projection/rendering, safety-floor behavior, and abstention/review policy
remain prediction-bearing.

## Current Starting Point

Already materialized:

- validation750 no-call assembly joining `hybrid_reasoner_replay`,
  `selective_safety_floor_gate_v0`, and `rq9_selective_action_router_v3`;
- explicit staged decision layer with 716 prediction-bearing validation rows,
  34 non-predictions, selective Purist accuracy 0.9469, and selective Pragmatic
  accuracy 0.9539;
- residual non-prediction audit and selective abstention-pressure review;
- frozen abstention-policy predeclaration;
- proposed trigger-context release rule that releases 1 validation row;
- last-event date instrumentation over the 8 date-policy rows, with 0 automatic
  release-ready rows until duration derivation and conflict checks exist;
- component homes for source tracing, suspicious selected-state policy,
  selective verifier, staged decision policy, residual audit, abstention
  pressure, trigger release, and last-event date instrumentation.

Known missing or incomplete inputs:

- module-shaped full-validation rich selected-state fact carrier;
- module-shaped boundary-v3 selected-state candidates;
- full-validation promoted selective verifier protocol and artifact;
- auditable last-event duration derivation and conflict checks;
- family-indexed component evidence matrix as a first-class candidate artifact;
- test450 assembly path that reuses frozen component policies without exposing
  row-level test diagnostics during development.

## Split Discipline

Use `gan2026_split_v1`.

- Validation, 750 rows: development, implementation debugging, component
  ablations, row-level error analysis, and candidate freeze decision.
- Test, 450 rows: final frozen holdout audit only. Do not inspect test row-level
  failures before freezing. Do not change prompts, code, gates, thresholds,
  normalization, projection, verifier policy, or release rules from test
  outcomes.

Because the validation surface is saturated, the full validation run is justified
only as a freeze-ready development artifact and component-evidence table, not as
another broad metric fishing run.

## Construction Plan

### 1. Name And Version The Candidate

Create a single candidate version constant and artifact stem:

```text
hybrid_multi_component_staged_assembly_v0
gan2026_hybrid_multi_component_staged_assembly_v0
```

Record in every artifact:

- candidate version;
- git commit or working-tree note;
- split and split manifest;
- source artifact paths;
- component versions and policy ids;
- model names and prompt versions for any live LLM component;
- whether each row is prediction-bearing, abstain, human review, or monitor.

### 2. Promote Component Homes Before Wiring

Keep business logic out of the final assembly runner. Each prediction-bearing or
evidence-bearing component must have an owning module before it is wired into
the candidate:

- deterministic/state-graph substrate: existing deterministic and state-graph
  modules;
- boundary selected-state candidates: promote from artifact replay into a
  component module or mark explicitly as saved diagnostic input;
- rich selected-state fact carrier: component module with source ids, selected
  evidence, state kind, normalized label, projection inputs, and missing-field
  flags;
- suspicious selected-state consistency: existing component module;
- projection/rendering: selected-evidence and projection modules with policy ids;
- safety floor: component adapter around `selective_safety_floor_gate_v0`;
- abstain/review/monitoring: staged decision, residual audit, abstention
  pressure, and predeclaration modules;
- trigger-context release: existing component, unpromoted until accepted;
- last-event date policy: extend current instrumentation with duration
  derivation and conflict checks before any prediction-bearing release;
- selective verifier: existing component home, but blocked from broad use until
  full-validation protocol exists;
- component evidence matrix: new reporting/component-evidence module.

### 3. Build The Assembly Row Contract

The final assembly JSONL row must contain, at minimum:

- `source_row_index`, `split`, `split_manifest`;
- source candidate provenance by component;
- rich selected-state fields and selected source ids;
- exact selected evidence and source-id validity booleans;
- suspicious-state flags and policy result;
- projection/rendering policy id, selected label, and label source;
- safety-floor fallback status;
- abstain/review/monitoring action and reason;
- verifier status, including `not_run`, `not_applicable`, `used`, or
  `blocked_by_protocol`;
- final action and prediction label when prediction-bearing;
- deterministic comparator label and row-level W->C/C->W accounting on
  validation only;
- hidden-family tags and first-failure owner when available;
- parse/evidence/schema issue counters.

For test rows, include the same operational fields, but do not include
development row-review fields derived from test failure inspection.

### 4. Implement Missing Last-Event Policy

Add a `last_event_duration_policy` component before changing any last-event row
from non-prediction to prediction.

Required behavior:

- parse explicit full or partial selected-evidence dates;
- extract source record reference date from `Clinic Date:` or `Sent:` headers;
- derive elapsed duration only when date precision and reference date make the
  interval auditable;
- block automatic release when date precision is insufficient, the selected
  evidence lacks an event target, multiple conflicting last-event candidates
  exist, or the derived label would depend on an unstated benchmark convention;
- emit release, block, and conflict reasons for each row.

Validation promotion gate:

- 0 automatic releases unless every released row has exact evidence, valid source
  ids, an auditable duration, and no conflict flags;
- no deterministic-correct regression from any released row.

### 5. Decide Trigger-Context Release Promotion

Keep `trigger_context_release_rule_v0` as a validation proposal until reviewed
against the assembly row contract.

Promotion gate:

- release only predeclared trigger-context release candidates;
- selected evidence itself names the event target and countable rate;
- no release on exclusive trigger, conditional-only, sentinel, or missing-anchor
  wording;
- validation W->C/C->W accounting remains 1 W->C and 0 C->W for the currently
  proposed release set.

If accepted, encode it as a policy version in the candidate. If rejected, keep
the current 716 prediction-bearing baseline.

### 6. Add The Component Evidence Matrix

Create an artifact that can become the paper-facing component table:

- one row per source row;
- one column group per component;
- final action and label;
- comparator transition accounting;
- hidden-family tags;
- first-failure owner for non-correct validation rows;
- evidence/source-id/schema validity counts;
- cost/latency/call telemetry when live model calls occur.

The evidence matrix is a promotion requirement, not optional reporting.

### 7. Build Candidate CLI Or Runner

Add a narrow runner under the Gan 2026 task package. It should support:

```text
--split validation
--split test
--mode saved-replay
--mode live
--candidate-version hybrid_multi_component_staged_assembly_v0
--output-dir experiments/
```

The validation saved-replay mode may reuse existing full-validation artifacts.
The test mode must either use frozen saved test artifacts already authorized by
protocol or perform live calls with the frozen model/prompt settings. It must not
branch on test row-level failures.

## Validation Evaluation Plan

### Validation Pre-Flight

Before running full validation:

- run focused unit tests for every component touched;
- run assembly contract tests on small synthetic rows;
- materialize validation artifacts with deterministic output paths;
- verify row count is exactly 750 and every source row appears once;
- verify selected evidence exactness and source-id validity summaries;
- verify no verifier rows are silently used unless the full-validation verifier
  protocol is approved.

### Full Validation Artifact

Produce:

```text
experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_2026-06-04.jsonl
experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_2026-06-04.json
experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_2026-06-04.md
experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv
```

Report:

- row count and action counts;
- prediction-bearing coverage;
- selective Purist and Pragmatic accuracy over prediction-bearing rows;
- full-row accounting where non-predictions are reported separately, not scored
  as hidden successes;
- deterministic comparator transitions: W->C, C->W, C->review, W->review;
- trigger release and last-event release counts;
- verifier use count;
- evidence exactness, source-id validity, parse/schema issue counts;
- top validation failure owners and hard-slice counts.

### Validation Freeze Gate

Freeze for test only if all are true:

- candidate version, source artifacts, prompts, models, and policies are fixed;
- 750/750 validation rows assembled exactly once;
- no silent semantic override after rich selected state;
- all changed prediction-bearing rows have exact evidence and valid source ids;
- no automatic label-changing gate introduces deterministic-correct regression;
- trigger-context and last-event policies are either promoted with gates or kept
  non-prediction;
- verifier use is either absent or governed by a full-validation verifier
  protocol;
- component evidence matrix exists and explains first-failure ownership;
- final report explicitly labels the result as validation development.

If any gate fails, revise on validation only and do not run test.

## Test Evaluation Plan

### Frozen Test Protocol

Before touching test:

- write a short frozen-test protocol addendum naming the candidate version,
  commit, component policy ids, source artifacts, model and prompt settings,
  scorer, output paths, and permitted readouts;
- confirm no test row-level failures will be inspected for development;
- record that any post-test fix starts a new validation cycle.

### Test Run

Produce:

```text
experiments/gan2026_hybrid_multi_component_staged_assembly_v0_test450_2026-06-04.jsonl
experiments/gan2026_hybrid_multi_component_staged_assembly_v0_test450_2026-06-04.json
experiments/gan2026_hybrid_multi_component_staged_assembly_v0_test450_2026-06-04.md
experiments/gan2026_hybrid_multi_component_staged_assembly_v0_test450_component_matrix_2026-06-04.csv
```

Permitted test readouts:

- aggregate Purist and Pragmatic metrics;
- prediction-bearing coverage and action counts;
- predeclared slice aggregates only if slice definitions were frozen before the
  test run;
- evidence/source-id/schema validity counts;
- component usage and telemetry summaries;
- comparator transition counts if computed without using row-level failures to
  alter the candidate.

Do not use test row examples or row-level failure inspection in the development
loop. If the final report needs row-level examples, label them post-hoc
final-evaluation analysis and do not tune from them.

## Implementation Order

1. Add assembly candidate versioning and output stems.
2. Add or finish component homes for rich selected state, boundary candidates,
   last-event duration policy, and component evidence matrix.
3. Add assembly row contract tests.
4. Wire validation saved-replay assembly into the candidate runner.
5. Implement optional trigger-context promotion switch, defaulting to the current
   unpromoted proposal until accepted.
6. Implement last-event duration policy and keep releases blocked until the gate
   passes.
7. Materialize validation750 assembly and component matrix.
8. Run focused tests, then the full test suite if feasible.
9. Interpret validation against the freeze gate.
10. If frozen, write the test protocol addendum and run test450 once.
11. Record final validation and test artifacts in `PROJECT_STATUS.md`.

## Suggested Verification Commands

Run commands inside the repo `.venv`:

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_staged_hybrid_assembly.py \
  tests/test_gan2026_component_staged_decision_policy.py \
  tests/test_gan2026_component_trigger_context_release_rule.py \
  tests/test_gan2026_component_last_event_date_instrumentation.py
python -m pytest
python -m clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.staged_hybrid_assembly \
  --mode validation750
```

Replace the final command with the new candidate runner once it exists.

## Stop Rules

Promote to frozen test audit only when the validation freeze gate passes.

Revise on validation when a component contract, evidence/source-id gate, or
deterministic-correct regression gate fails.

Reject or keep diagnostic if the assembled candidate mostly preserves the same
saturated aggregate without improving component transparency, coverage, or
selective-action reliability.

Block test evaluation if the candidate version, source artifacts, verifier
policy, trigger/last-event release policy, or component evidence matrix is not
frozen.
