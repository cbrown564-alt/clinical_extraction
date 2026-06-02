# Gan 2026 State-Graph Month-Bucket Duration Selection Decision

Decision: treat `month_bucket_duration_selection` as the seed for a separately
named projection ablation, not as a scorer-normalization change or production
projection promotion.

## Basis

- The enriched projection replay recovered 18/18 exact seizure-free duration
  labels on the validation hard-slice surface after exact-evidence-valid duration
  nodes were merged into the saved diagnostic graphs.
- The result depends on a named output-surface policy that prefers broad
  month-bucket seizure-free nodes over competing numeric-month or broad-year
  nodes, with special handling that preserves plural numeric-month labels.
- All affected rows come from `gan2026_split_v1` validation hard slices. No train
  or locked-test rows were used.
- All Gan scorer-facing seizure-free duration labels map to monthly frequency
  `0.0`, so this decision concerns exact label projection and benchmark-facing
  duration wording, not Purist or Pragmatic monthly-frequency scoring.

## Decision

`month_bucket_duration_selection` should remain diagnostic in its current replay
artifact, but it is strong enough to justify a new predeclared projection
ablation:

```text
gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0
```

That ablation must be implemented and reported separately from:

- `gan2026_state_graph_projection_v0`;
- `seizure_free_duration_node_normalization_v0`;
- scorer normalization;
- any production projection policy.

The ablation may use the enriched validation hard-slice replay surface as its
initial target, but promotion requires a broader predeclared regression panel
over non-duration seizure-free rows, numeric seizure-free duration rows,
frequency-versus-seizure-free conflict rows, unknown/no-reference boundary rows,
and validation rows that were already projection-correct under
`gan2026_state_graph_projection_v0`.

## Acceptance Criteria For The Next Ablation

- Report changed-label rate, exact duration corrections, exact duration
  regressions, and non-duration seizure-free regressions separately.
- Preserve exact evidence validity for selected nodes.
- Attribute the policy as projection/arbitration behavior, not normalization.
- Keep any benchmark-format granularity rule explicitly named and ablated.
- Do not run or inspect locked test rows for this decision cycle.
- Do not promote the policy unless it improves the predeclared hard slice with
  acceptable regression cost on the broader validation regression panel.

## Claim Language

Use: diagnostic validation-cycle decision. The enriched replay shows that
month-bucket duration selection is a promising projection ablation seed for the
state-graph pipeline, but it is not a benchmark result, not scorer
normalization, and not a production projection-policy change.
