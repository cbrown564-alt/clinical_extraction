# Gan 2026 LLM-Only Typed Operations Reasoner Validation250 Report And Simplified-Schema Ablation Plan

Date: 2026-06-03

## Executive Decision

`llm_only_typed_operations_reasoner` with `typed_operations_v0` should be paused
as a current schema and replaced by a simplified-schema ablation series.

The max10000 validation250 run answered the main question it was designed to
answer: the validation50 drop was not only a completion-budget issue. A larger
budget produced 247/250 structured records, but the deep typed schema still
created parse/schema failures, selected-evidence exactness failures, a trace
mismatch, and most importantly a negative graph-projection delta.

The strongest score layer in the run was not the full typed-operation graph. It
was the simpler `selected_evidence_arithmetic` layer:

| Layer | Scorable | Purist | Pragmatic | Interpretation |
| --- | ---: | ---: | ---: | --- |
| `raw_llm` | 113 | 99/250 (0.3960) | 102/250 (0.4080) | The model cannot be expected to emit parser-ready Gan labels directly. |
| `format_only` | 166 | 143/250 (0.5720) | 149/250 (0.5960) | Format repair helps but does not solve clinical selection/rendering. |
| `selected_evidence_arithmetic` | 247 | 216/250 (0.8640) | 222/250 (0.8880) | Best current signal: selected evidence plus deterministic arithmetic/formatting. |
| `typed_operation_graph_projection` | 250 | 208/250 (0.8320) | 215/250 (0.8600) | The graph adds negative net value over selected evidence. |

The next research move should not be another in-place repair. It should be a
systematic simplification program that tests which schema pieces are useful,
which are brittle, and where deterministic adapters cross from mechanical
rendering into hybrid clinical selection.

## Original Intention

The typed-operations lane was intended to test a sharper version of Decision
0007: can an LLM own clinical selection while deterministic code owns only
mechanical adapters?

The intended division of labor was:

- The LLM reads the note and extracts source-near seizure-frequency operations.
- The LLM selects the clinically relevant operation or operation set.
- The LLM exposes operands for rates, windows, clusters, seizure-free durations,
  temporal anchors, semiology groupings, uncertainty, and selected evidence.
- Deterministic code validates schema/evidence, repairs scorer-facing format,
  computes arithmetic over model-selected facts, and optionally builds a graph
  from model-owned operations.

The research motivation was good. Earlier LLM-heavy runs showed that models
often identify useful clinical evidence but lose points on arbitrary Gan syntax,
duration arithmetic, cluster syntax, or parser compatibility. A typed schema
promised a transparent middle ground: preserve the LLM's clinical selection and
make deterministic adapters traceable and ablatable.

The validation ladder was:

1. Use validation25 to catch output contract and evidence failures.
2. Use validation50 to check whether the contract scales beyond the smoke
   prefix.
3. Use max10000 validation250 to decide whether failures were mainly budget
   pressure or deeper schema complexity.
4. Escalate to validation750 only if validation250 showed a stable positive
   architecture signal.

Step 4 is rejected by this report.

## Implementation

The implementation lives in
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_typed_operations_reasoner.py`.

### Typed Schema

The schema has three top-level outputs:

- `operations`: a list of `TypedOperationRecord`.
- `selection`: a `TypedOperationSelection`.
- `final_answer`: a `TypedOperationFinalAnswer`.

Each operation carries:

- `operation_id`
- `operation_kind`
- `evidence_id`
- exact `evidence`
- source-near `raw_phrase`
- `temporality`
- `assertion_status`
- `certainty`
- full `TypedOperationOperands`
- optional `model_normalized_clinical_label`

The operand object is deep. It asks for:

- event count low/high
- time-window low/high/unit
- denominator count/unit
- cluster size low/high
- seizure-free duration low/high/unit
- temporal anchor
- semiology grouping
- uncertainty type
- selected evidence id

Selection then duplicates some of the same decision state:

- selected operation ids
- rejected operation ids
- final clinical state
- selection strategy
- selected evidence id
- selected evidence
- uncertainty flags

Final answer duplicates it again:

- raw final label and kind
- selected evidence
- selected event ids
- supporting event ids
- optional rendering operands
- arithmetic trace
- rationales

This creates a useful audit trail, but it also creates multiple places where the
same clinical decision can drift.

### Prompt Contract

The prompt asks the model to:

- extract source-near seizure-frequency operations;
- copy exact evidence substrings;
- expose detailed operands;
- select the operation set that best answers clinical clarity or scoring policy;
- preserve distinctions among frequency, seizure-free, unknown, no-reference,
  and unresolved-multiple states;
- avoid headers, patient identifiers, boilerplate, escaped Unicode, HTML
  entities, and control characters.

After validation25 and validation50 issues, the contract was tightened around
evidence copying, selected-operation trace consistency, and rendering operands.
The max10000 run kept the validation50 prompt/schema and raised completion
budget to test whether the current schema could scale with more room.

### Score Layers

The run reports four layers:

| Layer | Owner | Meaning |
| --- | --- | --- |
| `raw_llm` | LLM | The model-rendered final label directly. |
| `format_only` | LLM plus benchmark-format repair | Parser-facing cleanup without intended semantic change. |
| `selected_evidence_arithmetic` | LLM-selected evidence plus deterministic adapter | Deterministic arithmetic/format repair over the selected evidence/fact. |
| `typed_operation_graph_projection` | LLM operation extraction plus deterministic graph projection | A graph is built from typed operations and projected to Gan. This is a deterministic semantic projection sidecar, not a pure LLM-owned layer. |

The layer ladder is important. It prevents the report from crediting the model
for a deterministic graph choice, and it makes the negative graph delta visible.

## Outcomes

### Contract Outcomes

| Contract item | Outcome |
| --- | ---: |
| Structured records | 247/250 |
| Parse/schema failures | 3/250 |
| Selected evidence valid | 235/250 |
| Operation graph nodes | 370 |
| Selected-operation trace mismatches | 1/250 |

Component status counts:

| Component | Failure count |
| --- | ---: |
| `parse_schema` | 3 |
| `operation_graph_projection` | 3 |
| `operation_selection` | 3 |
| `operation_extraction` | 16 |
| `final_schema_rendering` | 15 |
| `evidence_exactness` | 13 |
| `selected_operation_trace` | 1 |
| `scorer_format` | 137 |

The 137 scorer-format failures at the raw layer are expected for this family:
the raw model is not being optimized to memorize Gan grammar. They are not the
primary reason to pause the schema.

### Parse/Schema Failures

Rows: 103, 3242, 4574.

All three failures had no usable extraction record and fell back to graph
`no seizure frequency reference`. The errors were Pydantic validation errors for
missing required operation fields such as `raw_phrase`, `temporality`,
`assertion_status`, `certainty`, and `operands`.

Interpretation:

- More budget did not eliminate partial-object failures.
- Relaxing required fields would improve record count but weaken the intended
  trace contract.
- These failures are too few to explain the score gap, so local schema repair
  here would be low leverage.

### Selected Evidence Invalid Rows

Rows: 40, 79, 103, 1880, 3242, 3261, 3262, 3801, 4116, 4173, 4562, 4563, 4574,
4592, 4597.

Families:

- Parse/schema fallback rows: 103, 3242, 4574.
- Evidence-copy artifact rows: inequality/control-character/mojibake and
  median-interval source artifacts.

These rows are a contract problem, but they are not the main graph problem.
Among the invalid selected-evidence rows:

- 6 are correct at both selected-evidence and graph layers.
- 9 are wrong at both layers.
- 0 are selected-evidence-correct to graph-wrong regressions.

Interpretation:

- Evidence-copy cleanup may be useful for audit quality.
- It should not be sold as the fix for the typed graph underperformance.
- A simplified schema should still keep exact selected evidence as a hard gate.

### Selected-Operation Trace Mismatch

Row: 5476.

- Gold: `unknown`
- Selected-evidence arithmetic: `unknown`, Purist-correct
- Graph projection: `1 per month`, Purist-wrong
- Trace issue: `selection.selected_operation_ids` differs from
  `final_answer.selected_event_ids`
- Selected evidence: monthly patient-led rescue-medication use

Interpretation:

This is a small count but a large design warning. The graph converted rescue
medication use into seizure frequency. The duplicated selection fields let the
schema express inconsistent clinical ownership, then graph projection chose a
plausible numeric path.

### Graph Projection Delta

Purist transition from `selected_evidence_arithmetic` to
`typed_operation_graph_projection`:

| Selected-evidence layer | Graph layer | Rows |
| --- | --- | ---: |
| Correct | Correct | 201 |
| Correct | Wrong | 15 |
| Wrong | Correct | 7 |
| Wrong | Wrong | 27 |

Net graph effect: -8 Purist rows.

The graph rescues 7 rows where selected-evidence arithmetic is wrong:

| Row | Gold | Selected-evidence layer | Graph layer |
| ---: | --- | --- | --- |
| 704 | `2 per month` | `unknown` | `2 per month` |
| 1223 | `3 to 4 per week` | `no seizure frequency reference` | `3 to 4 per week` |
| 1573 | `11 per week` | `unknown` | `11 per 7 day` |
| 2354 | `6 to 7 per week` | `no seizure frequency reference` | `6 to 7 per week` |
| 2427 | `3 to 5 per month` | `unknown` | `3 to 5 per month` |
| 3827 | `7 per month` | `unknown` | `7 per month` |
| 3849 | `3 per day` | `unknown` | `3 per day` |

But it regresses 15 rows where selected-evidence arithmetic is correct:

| Row | Gold | Selected-evidence layer | Graph layer | Failure family |
| ---: | --- | --- | --- | --- |
| 744 | `multiple per week` | unknown-category correct | `1 per 8 week` | Secondary event overrides unresolved frequent absences. |
| 1317 | `unknown, multiple per cluster` | `unknown` | `2 per day` | One-day cluster becomes stable daily rate. |
| 1357 | `1 per day` | `1 per day` | `no seizure frequency reference` | Selected daily event lost in graph projection. |
| 2114 | `multiple per month` | unknown-category correct | `2 per month` | Vague several/month converted to arbitrary numeric low bound. |
| 3482 | `unknown` | `unknown` | `1 per month` | Perimenstrual-only window becomes ordinary monthly frequency. |
| 3988 | `multiple per week` | unknown-category correct | `3 per week` | Unresolved multiple frequency forced into numeric rate. |
| 4690 | `multiple per day` | unknown-category correct | `10 per week` | `/hour` evidence loses unit. |
| 4694 | `multiple per day` | unknown-category correct | `9 per day` | `/hour` evidence becomes daily count. |
| 4700 | `multiple per day` | unknown-category correct | `4 per day` | `/hour` evidence becomes daily count. |
| 4709 | `multiple per day` | `unknown` | `6 per day` | `/hour` evidence becomes daily count. |
| 4731 | `unknown` | unknown-category correct | `1 to 2 per month` | Rare/unclear frequency becomes numeric range. |
| 4771 | `unknown` | unknown-category correct | `2 per 6 week` | Secondary count selected despite diffuse increased activity. |
| 5476 | `unknown` | `unknown` | `1 per month` | Rescue-medication use becomes seizure frequency. |
| 5504 | `unknown` | unknown-category correct | `1 per year` | Sporadic jerks become fixed yearly rate. |
| 5551 | `multiple per day` | `multiple per day` | `1 per week` | Weekly generalized breakthroughs override daily focal burden. |

Interpretation:

The graph is not merely missing a single rule. It is overconfident whenever
typed operands make a numeric projection easy: unknown states, unresolved
multiple states, one-off cluster windows, perimenstrual windows, medication-use
frequencies, and compact `/hour` rates.

## Overall Interpretation

The current typed schema is too deep and too redundant for the present model and
task.

The main architectural problem is duplicated decision ownership:

- `selection` owns selected operation ids and clinical state.
- `final_answer` owns selected event ids and final kind/label.
- each operation owns typed operands and model-normalized labels.
- graph projection then owns selection/projection among model-extracted nodes.

That gives excellent debug material, but it also creates inconsistent paths to a
final answer. When those paths disagree, deterministic projection can become the
prediction-bearing clinical selector. Under Decision 0007, that shifts the row
from LLM-heavy to hybrid.

The best evidence from the run is narrower:

- The model often selects useful evidence.
- Deterministic formatting/arithmetic over model-selected evidence can be
  materially better than raw model labels.
- Full graph projection is not currently justified as a primary layer.

## Claim Language

On validation250 under `gan2026_split_v1`,
`llm_only_typed_operations_reasoner` with `typed_operations_v0` is a diagnostic
LLM-heavy typed-schema run with a hybrid graph-projection sidecar. It does not
support validation750 escalation, an LLM-superiority claim, or promotion of the
current typed graph. It supports a simplified-schema ablation program focused on
LLM-owned selected evidence, sparse operands, and mechanical deterministic
adapters.

## Simplified-Schema Ablation Program

### Shared Protocol

All ablations should use validation only. Do not use locked test. Follow the
validation ladder:

1. validation25 smoke
2. validation50 decision signal
3. validation250 development decision
4. validation750 only after a written promotion reason

Every ablation report should include:

- raw model layer;
- format-only layer;
- selected-evidence adapter layer;
- any sidecar graph/projection layer, clearly marked diagnostic;
- structured record count;
- parse/schema failure count;
- selected evidence valid count;
- selected evidence trace mismatch count;
- selected-evidence-correct to final-wrong regressions;
- wrong-to-correct and correct-to-wrong transitions against the previous
  ablation and against `typed_operations_v0`;
- failure rows grouped by clinical subproblem.

Primary validation25/50 gates:

- 25/25 or 49/50 structured records.
- 23/25 or 47/50 exact selected evidence.
- 0 selected-evidence trace mismatches.
- No more than 1 selected-evidence-correct to adapter-wrong regression on
  validation25; no more than 2 on validation50.
- The primary layer must be at least as good as
  `selected_evidence_arithmetic`, not merely better than the graph.

### Ablation 0: Same-Output Component Replays

Hypothesis: some negative graph delta can be explained by projection policy,
but not enough to save the current schema.

Method:

- Use the saved validation250 raw outputs.
- Replay alternative deterministic scoring policies without new model calls.
- Conditions:
  - A0.1: selected-evidence arithmetic only.
  - A0.2: graph projection as diagnostic only.
  - A0.3: graph projection blocked when selected clinical state is
    `unknown_frequency`, `no_reference`, or `unresolved_multiple`.
  - A0.4: graph projection blocked when selected evidence contains medication
    use, perimenstrual-only windows, one-off clusters, rare/sporadic language,
    or compact `/hour` rates not represented with an hour denominator.

Decision value:

- If simple blocking removes most graph regressions without many lost rescues,
  keep graph as a sidecar for later hybrid research.
- If blocking becomes a growing semantic rule stack, retire graph projection
  from the LLM-only lane.

Expected outcome:

- A0 may improve the graph sidecar, but it will likely confirm that the schema
  is too complex and rule-hungry to repair in place.

### Ablation 1: Selection-Only Minimal Schema

Hypothesis: the model performs better when asked to choose one source-grounded
clinical state and selected evidence, without full operation graphs or operand
matrices.

Schema:

```text
selected_state:
  final_kind: frequency | seizure_free | unknown | no_reference | unresolved_multiple
  selected_evidence: exact source substring
  raw_source_phrase: source-near phrase from selected evidence
  selection_reason: short rationale
  uncertainty_flags: list[str]
```

Deterministic layers:

- raw model label if present;
- format-only repair;
- selected-evidence derivation/arithmetic;
- no graph projection.

Primary question:

Can a compact LLM-owned selection object match or beat 216/250 Purist while
improving evidence validity and reducing schema failures?

Stop rules:

- Stop after validation25 if exact evidence is below 23/25 or if selected-state
  trace is ambiguous.
- Move to validation50 only if the row-level misses are interpretable.
- Move to validation250 only if validation50 is at least 47/50 Purist or shows a
  clear improvement in the hard families that hurt the current schema.

Interpretation:

- Success means the project does not need a full typed operation graph for the
  LLM-only lane.
- Failure means selected evidence alone is not enough; proceed to sparse
  operands.

### Ablation 2: Selection Plus Sparse Operands

Hypothesis: the useful part of typed operations is not the full graph; it is a
small operand object for count/window/cluster/duration when the model is
confident.

Schema:

```text
selected_state:
  final_kind
  selected_evidence
  raw_source_phrase
  selected_operation_kind:
    frequency_rate | cluster_frequency | seizure_free | unknown_frequency | no_reference
  operands:
    count_low
    count_high
    period_count
    period_unit
    cluster_count
    seizures_per_cluster_low
    seizures_per_cluster_high
    seizure_free_duration_count
    seizure_free_duration_unit
    abstain_reason
```

Differences from `typed_operations_v0`:

- one selected object, not operations plus selection plus final answer;
- no rejected-operation list;
- no duplicated selected ids;
- no temporal anchor or semiology grouping in the primary scoring schema;
- operands are nullable and must be ignored when `final_kind` is unknown or
  no-reference;
- deterministic adapters may render only from selected evidence and selected
  operands.

Primary question:

Do sparse operands rescue the 7 rows the graph helped without recreating the 15
graph regressions?

Stop rules:

- Any recurring selected-evidence-correct to adapter-wrong regression caused by
  operands becoming the clinical selector blocks escalation.
- If sparse operands improve only scorer syntax but not clinical selection,
  keep them as mechanical adapters only.

### Ablation 3: Explicit Abstention And Boundary Tags

Hypothesis: the model needs an explicit abstention contract for cases where a
numeric operand is tempting but clinically unsafe.

Add fields:

```text
boundary_tags:
  medication_use_not_seizure_frequency
  one_off_cluster_window
  perimenstrual_only_window
  rare_or_sporadic_unclear_rate
  compact_hour_rate
  unresolved_multiple_current_states
  competing_semiologies
  historical_or_negated_frequency
adapter_permission:
  render_frequency | render_seizure_free | sentinel_unknown | sentinel_no_reference
```

Primary question:

Can model-owned boundary tags prevent the major graph-regression families while
preserving adapter value?

Important attribution rule:

If deterministic code assigns these boundary tags from regexes, this becomes a
hybrid deterministic rule ablation. For an LLM-heavy claim, the tags must be
model-owned or used only as diagnostics.

Stop rules:

- If the tags are mostly ignored or conflict with selected evidence, simplify
  back to Ablation 2.
- If tags work but require deterministic override rules, move that branch to a
  hybrid sidecar lane.

### Ablation 4: Two-Call Decomposition

Hypothesis: schema complexity is partly attention allocation. Separating
evidence selection from operand rendering will outperform one large schema.

Call 1: clinical selector

- selected clinical state;
- selected evidence;
- boundary tags;
- short rationale.

Call 2: adapter-facing operand extractor

- receives only the selected evidence plus minimal note context;
- emits sparse operands or abstains;
- cannot change selected evidence or final clinical state.

Primary question:

Does isolating operand extraction improve arithmetic/rendering without allowing
the operand extractor to choose a different clinical fact?

Stop rules:

- If Call 2 changes selected evidence or clinical state, block the run as an
  attribution failure.
- If cost/latency is not acceptable for validation250, keep this as a targeted
  hard-slice diagnostic rather than a broad candidate.

### Ablation 5: Hard-Slice Stress Before Broad Escalation

Hypothesis: broad validation250 can hide whether the schema fixed the actual
families that matter.

Build fixed validation hard slices from the current failure rows:

- unknown/unresolved overwritten by numeric operands;
- hour-rate compact notation;
- medication-use frequency;
- perimenstrual-only windows;
- one-off clusters;
- competing high-burden versus lower-burden event selection;
- evidence-copy artifact rows.

Primary question:

Which simplified schema variant is robust on the failure families before
spending another broad validation250 run?

Stop rules:

- Do not run validation750 from a broad aggregate alone.
- Require family-level improvement over `typed_operations_v0` and no new
  high-severity family regression.

### Ablation 6: Hybrid Sidecar Graph, Not LLM-Only Primary

Hypothesis: graph projection may still be useful as a hybrid diagnostic or
selective-action sidecar, even though it should not be the LLM-only primary
layer.

Method:

- Keep simplified LLM selected-state layer as primary.
- Run graph projection only on rows where:
  - exact evidence is valid;
  - selected state is frequency or seizure-free, not unknown/no-reference;
  - sparse operands are complete;
  - no boundary tag blocks numeric projection.
- Report changed-label precision against the primary layer and against
  `rules_only_v1` or safety floor.

Primary question:

Can graph projection become a selective hybrid action with positive precision
and controlled regressions?

Claim language:

- If it selects among facts, it is hybrid.
- If it only renders already selected operands, it is deterministic adapter.

## Recommended Sequence

1. A0 same-output replay over saved validation250 outputs.
2. A1 selection-only validation25.
3. A2 sparse-operands validation25 if A1 evidence and state selection are clean.
4. A1 versus A2 validation50 comparison.
5. A3 boundary-tag validation50 on hard families if A2 still over-numericizes.
6. A5 hard-slice stress for the best simplified schema.
7. One validation250 live run only after the 50-row and hard-slice results name
   the specific hypothesis being decided.
8. A6 graph sidecar only after the primary simplified schema is stable.

## Success Criteria For A Better Place

A simplified schema is worth continuing only if it satisfies all of these on
validation250:

- structured records at least 247/250;
- selected evidence valid at least 240/250, with invalid rows classified;
- 0 selected-evidence trace mismatches;
- primary layer Purist at least 216/250, with a path toward 225/250;
- fewer than 5 selected-evidence-correct to adapter-wrong regressions;
- no recurring medication-use, perimenstrual-only, one-off-cluster, or `/hour`
  unit regression family;
- score-layer attribution remains honest: raw model, format-only, selected
  evidence adapter, and sidecar projection are separate.

Promotion to validation750 should require either:

- validation250 primary layer at or above 225/250 Purist with strong evidence
  validity and low regressions; or
- targeted hard-slice evidence showing the simplified schema solves the
  mechanism failures that block the hybrid/LLM-heavy lane.

## Immediate Implementation Target

Implement Ablation 1 first as a new candidate rather than mutating
`typed_operations_v0`.

Suggested candidate name:

```text
llm_only_simplified_selected_state_reasoner
```

Suggested schema version:

```text
simplified_selected_state_v0
```

Suggested first artifact:

```text
experiments/gan2026_llm_only_simplified_selected_state_reasoner_validation25_gpt41mini_v0_2026-06-03.*
```

This keeps the old typed-operations lane available for comparison while making
the new lane's hypothesis clear: simplify decision ownership before adding back
operands or graph behavior.
