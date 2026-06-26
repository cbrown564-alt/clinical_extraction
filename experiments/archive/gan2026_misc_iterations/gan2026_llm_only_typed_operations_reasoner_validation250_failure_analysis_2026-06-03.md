# Gan 2026 LLM-Only Typed Operations Reasoner Validation250 Failure Analysis

- Source artifact: `experiments/gan2026_llm_only_typed_operations_reasoner_validation250_gpt41mini_v0_contractfix_max10000_2026-06-03.jsonl`
- Source report: `experiments/gan2026_llm_only_typed_operations_reasoner_validation250_gpt41mini_v0_contractfix_max10000_2026-06-03.md`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Schema: `typed_operations_v0`

## Decision

Pause the current typed-operations schema. Do not repair it locally and do not
escalate it to validation750.

If this lane is revisited, it should be a simplified-schema redesign, not a
repair pass over `typed_operations_v0`. The useful signal in this run is that
LLM-selected evidence plus deterministic arithmetic is stronger than the typed
operation graph: selected-evidence arithmetic reaches 216/250 Purist, while
typed-operation graph projection falls to 208/250 Purist.

## Summary Counts

| Bucket | Count | Interpretation |
| --- | ---: | --- |
| Structured records | 247/250 | The 10000-token budget reduced truncation but did not make the deep schema robust. |
| Parse/schema failures | 3/250 | Real failures, but too small to explain the run miss. |
| Selected evidence valid | 235/250 | Evidence exactness is below the expected contract but not the main score-limiting bucket. |
| Selected-operation trace mismatches | 1/250 | A genuine schema consistency failure, but isolated. |
| Selected-evidence arithmetic correct, graph wrong | 15/250 | Main architecture concern: the typed graph regresses correct selected-evidence outcomes. |
| Selected-evidence arithmetic wrong, graph correct | 7/250 | The graph sometimes helps, but not enough to offset regressions. |

Purist transition table from `selected_evidence_arithmetic` to
`typed_operation_graph_projection`:

| Selected evidence | Graph projection | Rows |
| --- | --- | ---: |
| Correct | Correct | 201 |
| Correct | Wrong | 15 |
| Wrong | Correct | 7 |
| Wrong | Wrong | 27 |

Net effect of the typed graph over selected-evidence arithmetic is -8 Purist
rows. That is the opposite of what a deeper typed schema is supposed to buy.

## Parse/Schema Failures

Rows: 103, 3242, 4574.

All three failures have `typed_operations_parse=ok` but `parse_schema=fail`,
`operation_extraction=fail`, `operation_selection=fail`, and graph fallback to
`no seizure frequency reference`. The call errors are Pydantic validation errors
for missing required operation fields such as `raw_phrase`, `temporality`,
`assertion_status`, `certainty`, and `operands`.

These are not good candidates for row-specific repair. They show that the schema
still sometimes emits partial operation objects under difficult evidence text,
even with a 10000-token budget. Relaxing the required fields would make the
graph more permissive, but it would also weaken the evidence contract that this
schema was created to enforce.

## Selected Evidence Invalid Rows

Rows: 40, 79, 103, 1880, 3242, 3261, 3262, 3801, 4116, 4173, 4562, 4563, 4574,
4592, 4597.

The invalid-evidence rows split into two families:

- 3 parse/schema fallback rows: 103, 3242, 4574.
- 12 evidence-copy/exactness rows with control-character or source-artifact
  corruption, including inequality, mojibake, and median-interval artifacts.

These rows do not explain the graph underperformance. Among the 15 invalid
selected-evidence rows, 6 are correct at both selected-evidence and graph layers,
and 9 are wrong at both layers. There are 0 selected-evidence-correct to
graph-wrong regressions in this invalid-evidence bucket.

Conclusion: another evidence-copy cleanup might improve the audit contract, but
it would not solve the core score regression. It should not be used as the next
typed-schema escalation step.

## Selected-Operation Trace Mismatch

Row: 5476.

- Gold: `unknown`
- Selected-evidence arithmetic: `unknown` and Purist-correct
- Typed-operation graph projection: `1 per month` and Purist-wrong
- Trace issue: `selection.selected_operation_ids` contains `op1` and `op2`, but
  `final_answer.selected_event_ids` contains only `op1`.
- Selected evidence: `Clobazam 5 mg at night as needed for clusters
  (patient-led use approximately once monthly)`

This is clinically meaningful, not just syntactic. The graph converts
patient-led rescue-medication use into a seizure frequency. The mismatch is only
1 row, but it is a compact example of the deeper issue: duplicated selection
fields give the graph enough rope to choose a cleaner operand path than the
clinical state actually supports.

## Selected-Evidence-Correct to Graph-Wrong Regressions

Rows: 744, 1317, 1357, 2114, 3482, 3988, 4690, 4694, 4700, 4709, 4731, 4771,
5476, 5504, 5551.

Major families:

- Unknown/unresolved state overwritten by numeric operands: 744, 1317, 2114,
  3482, 3988, 4731, 4771, 5476, 5504.
- Hour-rate or compact-rate operands projected with the wrong unit: 4690, 4694,
  4700, 4709.
- Competing selected operations where the graph chooses a lower-burden or
  fallback interpretation despite a correct selected-evidence layer: 1357, 5551.

Representative examples:

| Row | Gold | Selected evidence layer | Graph projection | Failure |
| ---: | --- | --- | --- | --- |
| 744 | `multiple per week` | `no seizure frequency reference` Purist-correct via unknown category | `1 per 8 week` | Graph prefers a secondary 8-week tonic-clonic count over unresolved frequent absences. |
| 1317 | `unknown, multiple per cluster` | `unknown` | `2 per day` | Graph quantifies a one-day cluster as a stable daily rate. |
| 3482 | `unknown` | `unknown` | `1 per month` | Graph treats perimenstrual-only clustering as an ordinary monthly frequency. |
| 4690 | `multiple per day` | `no seizure frequency reference` Purist-correct via unknown category | `10 per week` | Graph loses the `/hour` unit from EEG evidence. |
| 5476 | `unknown` | `unknown` | `1 per month` | Graph treats monthly rescue-medication use as seizure frequency. |
| 5551 | `multiple per day` | `multiple per day` | `1 per week` | Graph prefers weekly generalized breakthroughs over the selected daily focal burden. |

These regressions are not one narrow parser bug. They arise from duplicated
clinical state across raw labels, selected evidence, operation operands,
selection ids, and final-answer rendering operands. The graph layer can choose a
plausible numeric projection even when the selected evidence layer correctly
keeps the row unknown or selects the higher-burden state.

## Recommendation

Do not repair `typed_operations_v0` in place. The likely repairs would add more
rules for unknown/unresolved states, per-hour units, medication-use exclusion,
cluster semantics, and competing-operation priority. That would turn the lane
into another deterministic semantic projection stack while still carrying a
large, fragile LLM output schema.

Do not simply raise the token budget again. The max10000 run still produced
schema failures, evidence-copy failures, and graph regressions. The bottleneck is
schema complexity and duplicated decision ownership, not only completion length.

The viable future version is a simplified redesign:

- Keep exact selected evidence as the primary LLM-owned object.
- Keep one selected clinical state and one selected operation id list, not
  duplicated selection ids in `selection` and `final_answer`.
- Remove or demote full graph projection unless an ablation shows positive net
  value over selected-evidence arithmetic.
- Make operands sparse and source-near, with explicit abstention for unknown,
  unresolved multiple, medication-use frequency, perimenstrual-only windows,
  and one-off cluster windows.
- Treat graph projection as an experimental sidecar until it beats
  selected-evidence arithmetic without deterministic semantic repair creep.

Current disposition: paused. Return near-term effort to the hybrid
safety-floor/component-stress lane unless a predeclared simplified-schema
ablation is opened as a separate validation-cycle experiment.
