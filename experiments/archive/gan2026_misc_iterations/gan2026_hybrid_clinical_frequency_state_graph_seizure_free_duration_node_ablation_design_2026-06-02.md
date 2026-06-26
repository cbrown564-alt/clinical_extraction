# Gan 2026 State-Graph Seizure-Free Duration Node Ablation Design

Diagnostic only: this is a validation-cycle graph-node construction and normalization design, not a benchmark result, scorer change, or production projection-policy promotion.

## Experiment Unit

- Hypothesis: the seizure-free duration bottleneck is mostly node construction/normalization, not projection. The current graph often turns vague month-scale evidence into `seizure free for multiple year`, and projection-only replay cannot recover exact duration labels when the graph lacks an exact or benchmark-equivalent month node.
- Minimal change under test: add a named validation-only node-builder variant, `seizure_free_duration_node_normalization_v0`, that emits candidate seizure-free duration nodes from exact evidence spans and records the rule family that created each node.
- Data surface: validation hard-slice rows from `gan2026_split_v1`; no train or locked test rows.
- Scorer: exact normalized duration-label match for seizure-free rows. Purist and Pragmatic F1 are not primary because Gan scoring maps all seizure-free durations to monthly frequency `0.0`.
- Comparator: saved `gan2026_state_graph_projection_v0` graph rows from `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.jsonl`.
- Decision: keep as diagnostic unless node coverage improves with exact evidence validity and without projection-policy promotion.

## Target Surface

The projection ablation found 25 seizure-free duration rows. This node-construction design targets the 18 rows where existing graph nodes cannot express the needed duration semantics.

| Target slice | Rows |
| --- | ---: |
| Gold `seizure free for multiple month` | 17 |
| Gold `seizure free for 6 months` with only broad year node | 1 |
| `only_broad_duration_nodes` | 16 |
| `numeric_duration_present_but_gold_absent` | 2 |

Affected existing graph rules:

| Existing rule family | Nodes |
| --- | ---: |
| `seizure_free.current_control_phrase` | 11 |
| `seizure_free.generic_duration_or_since` | 6 |
| `seizure_free.no_definite_events` | 2 |
| `seizure_free.absence_for_duration` | 1 |
| `seizure_free.last_epileptic_event` | 1 |

Predeclared target row ids: 3118, 3137, 4839, 4842, 4951, 5040, 5082, 5092, 5110, 5121, 5136, 5141, 5197, 5210, 5221, 5345, 5379, 5406.

## Ablation Conditions

| Condition | Purpose | Expected learning |
| --- | --- | --- |
| `baseline_saved_graph` | Existing saved graph rows and unchanged projection | Confirms the 18-row surface and baseline labels. |
| `month_vague_from_evidence` | Convert source-near phrases such as `many months`, `several months`, `extended period`, and `absence of events for over four months` into month-scale seizure-free nodes when the evidence span says months or month-scale duration. | Tests whether broad month evidence can replace over-broad `multiple year` nodes. |
| `since_without_date_boundary` | Keep `since` or current-control phrases without a resolvable date as broad but non-year-specific month-scale candidates only when nearby text supports a months-level follow-up interval. | Separates clinical reasoning from benchmark-friendly overreach. |
| `numeric_to_broad_month_projection_surface` | Emit both numeric and broad month nodes when a numeric duration is approximate or benchmark gold uses `multiple month`. | Measures whether exact-label failure is a normalization granularity problem rather than missing evidence. |
| `no_definite_events_boundary` | Treat `no definite seizure events` as seizure-free duration only when the surrounding evidence has a duration cue; otherwise leave it as boundary-state/unknown-compatible evidence. | Prevents a new broad seizure-free overreach rule. |

## Metrics And Acceptance Criteria

Primary node metrics:

- Exact-evidence-valid newly emitted nodes.
- Exact gold-duration node coverage on the 18 target rows.
- Month-scale representability: rows with either exact gold node or a predeclared broad-month equivalent node.
- Over-broad year reduction: rows where the strongest seizure-free node remains only `seizure free for multiple year`.

Secondary projection replay metrics:

- Exact duration matches after replay with unchanged projection.
- Exact duration matches under `seizure_free_priority`, reported separately.
- Regressions on the seven rows that already have exact gold nodes in the prior 25-row surface.

Promotion is not allowed from this design alone. A successful implementation may move to a diagnostic replay if:

- New node evidence is exact for at least 95% of emitted nodes.
- At least 12 of the 18 target rows gain month-scale representability.
- No more than one of the seven already-exact-node rows loses exact-node representability.
- All new rules are named as seizure-frequency or Gan-specific benchmark-normalization behavior, not scorer normalization.

## Implementation Notes

Keep this outside frozen `rules_only_v1` and outside production scorer-facing normalization. The first implementation should be a named graph-builder variant or replay helper that reads saved validation graph rows, creates additional candidate nodes, and writes JSONL plus a compact Markdown report.

Rule taxonomy:

- General duration parsing: `general`.
- Seizure-free phrase recognition: `seizure_frequency`.
- Mapping vague month phrases to `seizure free for multiple month`: `benchmark_format` unless the evidence explicitly says months.
- Any fallback from unresolved `since` to month/year duration: `gan2026_specific` or disabled until justified by validation-only row review.

Stop rule: if the first implementation mainly changes projection exact labels without improving node representability, reject the design as projection leakage and return to evidence/claim construction.

