# Gan 2026 Boundary-State Graph Builder Validation31 + Synthetic Unknown8 Interpretation

This is a hosted graph-builder diagnostic, not a benchmark result. It evaluates
whether GPT-4.1 mini can construct exact-evidence `unknown` or
`unresolved_multiple` state-graph nodes for rows that deterministic graph
coverage missed. It does not emit final Gan labels, run projection arbitration,
or report projection F1.

## Artifacts

- Validation31 live JSONL:
  `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_gpt41mini_live_2026-06-02.jsonl`
- Validation31 live report:
  `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_gpt41mini_live_2026-06-02.md`
- Synthetic unknown8 live JSONL:
  `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_gpt41mini_live_2026-06-02.jsonl`
- Synthetic unknown8 live report:
  `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_gpt41mini_live_2026-06-02.md`

## Summary

| Surface | Rows | Schema-valid rows | Call failures | Exact evidence | Gain candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| Validation hard-slice missing representability | 31 | 30/31 | 0 | 28/29 | 10/31 |
| Synthetic unknown stress | 8 | 8/8 | 0 | 0/0 | 0/8 |

The validation pass recovered 10 representability-gain candidates among the 31
validation missing-representability rows. Gain rows were 338, 1317, 3507, 3512,
3528, 3532, 3600, 4694, 5476, and 5490.

One validation row, 869, had parse/evidence errors: one evidence string was not
an exact substring and one unresolved-multiple node used
`unresolved_multiple` instead of a parseable normalized label such as
`multiple per month`. This keeps the builder revise-only.

The synthetic unknown stress pass was output-contract clean but emitted zero
nodes on all 8 rows. Treat this as a recall failure for the unknown-state
prompt on synthetic stress rows, not as negative evidence about final-label
performance.

## Decision

Keep the hosted boundary-state builder as a revise-only diagnostic component.
It has useful validation-only coverage signal for exact-evidence unknown and
unresolved-multiple nodes, but it is not yet suitable for graph merge without a
strict acceptance filter and a separate replay.

The next step is to merge only accepted validation exact-evidence nodes from the
10 gain-candidate rows into a diagnostic graph replay, excluding row 869 and all
synthetic stress rows unless a revised unknown-state prompt recovers exact
evidence. Projection and arbitration remain separate ablations for the 34
already-representable projection misses.
