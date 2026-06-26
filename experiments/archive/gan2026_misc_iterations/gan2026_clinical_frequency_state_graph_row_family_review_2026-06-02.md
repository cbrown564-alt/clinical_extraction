# Gan 2026 Clinical Frequency State Graph Row/Family Review

Date: 2026-06-02

This is validation-cycle diagnostic review, not a benchmark result. It uses
validation-only artifacts and the reviewed synthetic hard-case development
panel; it does not inspect locked-test row text or tune from holdout behavior.

## Inputs

- State-graph protocol:
  `experiments/gan2026_clinical_frequency_state_graph_protocol_2026-06-02.md`
- Validation hard-slice diagnostics:
  `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.jsonl`
- Family-aware grouping:
  `experiments/gan2026_clinical_frequency_state_graph_family_aware_validation_grouping_2026-06-02.md`
- Synthetic hard-case diagnostics:
  `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.jsonl`

## Main Finding

The first hosted graph-builder/adjudicator should target boundary-state graph
construction, not final projection policy. On the 250-row validation hard-slice
union, oracle coverage is 219/250. All 31 missing-representability rows are
gold `unknown` or `unresolved_multiple`; no ordinary frequency or seizure-free
gold is missing from the graph. The dominant miss shape is a boundary state
collapsing to `no seizure frequency reference` or to an over-strong
`seizure_free` node.

Projection is still imperfect, but it is a separate second target. There are
34 representable projection misses: 25 seizure-free duration/ranking misses,
5 frequency arbitration misses, 4 unresolved-multiple arbitration misses, and
4 unknown arbitration misses. Those rows already contain a graph node for the
gold state, so a hosted builder aimed at finding absent spans would not be the
right first experiment for them.

## Validation Hard-Slice Review

Coverage by gold semantic kind:

| Gold kind | Rows | Representable | Missing | Projection note |
| --- | ---: | ---: | ---: | --- |
| frequency | 167 | 167 | 0 | 5 representable projection misses, mostly competing current/history frequencies. |
| seizure_free | 38 | 38 | 0 | 25 representable projection misses, mostly duration/ranking or breakthrough conflict. |
| unknown | 24 | 4 | 20 | Boundary-state construction failure dominates. |
| unresolved_multiple | 21 | 10 | 11 | Some gold nodes exist, but absent-span/no-reference collapse is still common. |

The missing-representability rows overlap heavily across hard-slice tags:

| Hard-slice tag | Missing rows | Interpretation |
| --- | ---: | --- |
| `seizure_free_overreach` | 31 | Every missing row is also an overreach/boundary case. |
| `cluster_or_diary` | 30 | Cluster/diary language is a surface marker, but not sufficient as the hosted target. |
| `unknown_no_reference_boundary` | 27 | Core span/state construction gap. |
| `temporal_conflict` | 22 | Current/history conflict often masks the boundary state. |
| `shorthand_interval_range` | 6 | Smaller contributor; keep as a later projection/normalization ablation. |
| `candidate_absent_or_weak` | 4 | The narrow deterministic-miss subset. |
| `deterministic_miss` | 4 | Same four rows as candidate_absent_or_weak. |

Rows missing gold representability:

| Source rows | Gold kind | Projected shape | Notes |
| --- | --- | --- | --- |
| 338, 743, 869, 1695, 1707, 2080, 4694, 4700, 4709 | `unresolved_multiple` | `no_reference` | Graph finds only no-reference fallback; hosted builder should propose unresolved-frequency states with exact evidence. |
| 4690, 5534 | `unresolved_multiple` | `seizure_free` | Boundary/overreach rows where seizure-free evidence outvotes missing unresolved-frequency state. |
| 1317, 2149, 2166, 3436, 3468, 3493, 3507, 3512, 3532, 3600, 4731, 4732, 4771, 5476, 5490, 5491, 5504, 5507 | `unknown` | `no_reference` | Unknown-state evidence is absent from the graph; no-reference fallback should not be treated as equivalent. |
| 3356, 3528 | `unknown` | `seizure_free` | Unknown-state evidence is absent and seizure-free language dominates projection. |

Representative rows where gold is representable but projection is wrong:

| Source rows | Gold kind | Dominant issue |
| --- | --- | --- |
| 278, 744, 1687, 5567 | `unresolved_multiple` | Projection ranks concrete frequency or seizure-free over an unresolved-multiple node. |
| 2907, 2932, 2938, 3118, 3137, 4839, 4842, 4951, 5040, 5082, 5092, 5110, 5121, 5136, 5141, 5197, 5210, 5221, 5345, 5379, 5406 | `seizure_free` | Duration specificity/ranking; graph contains a seizure-free node, but the selected duration differs from gold. |
| 2965, 3082, 4992, 5351 | `seizure_free` | Breakthrough/current-frequency arbitration beats seizure-free state. |
| 3281, 3995, 4026, 4116, 4592 | `frequency` | Competing current/history frequency ranking. |
| 3371, 3469, 3482, 3534 | `unknown` | Unknown node is present but projection prefers a concrete frequency or seizure-free state. |

## Synthetic Hard-Case Cross-Check

The synthetic hard-case panel confirms that span/state construction is the
first bottleneck, but its failure distribution differs from validation:

| Gold kind | Rows | Representable | Missing |
| --- | ---: | ---: | ---: |
| frequency | 36 | 20 | 16 |
| no_reference | 11 | 9 | 2 |
| seizure_free | 1 | 1 | 0 |
| unknown | 8 | 0 | 8 |

Synthetic rows stress cluster arithmetic, range normalization, and proxy
boundary cases more aggressively than validation. Use them as a component
stress panel after the validation hard-slice hosted builder run, not as the
primary success metric for the first hosted experiment.

## Decision For Next Experiment

Run the first hosted `hybrid_clinical_frequency_state_graph` experiment as a
graph-builder diagnostic over validation hard-slice boundary rows, with these
constraints:

1. Target rows: the 31 validation hard-slice rows missing oracle
   representability, plus the 8 synthetic unknown rows as a stress-only panel.
2. Model role: construct exact-evidence-gated graph nodes for `unknown` and
   `unresolved_multiple`; do not ask the model to emit a final Gan label.
3. Required outputs: node semantic kind, exact evidence span, certainty,
   temporality, assertion status, and a no-reference-vs-unknown rationale.
4. Primary metrics: gold representability gained, exact-evidence validity, and
   schema validity. Projection F1 is secondary and should be reported only as a
   replayed projection after graph construction.
5. Holdout policy: no locked-test row inspection or prompt/gate tuning.

Projection and arbitration ablations should follow only after the hosted builder
shows that it can recover boundary-state nodes without inflating unsupported
unknown or unresolved-multiple states.
