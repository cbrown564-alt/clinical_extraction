# Gan 2026 RQ2 Evidence-Selection Matrix

Replay-first component matrix for RQ2 evidence selection. This is a validation-development artifact, not a benchmark or locked-holdout claim.

- JSONL artifact: `experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl`
- Matrix rows: 3489
- Source rows represented: 750

## Component Summary

| Component | Rows | Exact evidence | Source-id valid | Scorable | Purist correct | Operand complete | Changed | W->C | C->W |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| claim_table_final_query | 250 | 0.984 | 1.000 | 0.968 | 0.921 | 0.000 | 0 | 0 | 0 |
| deterministic_top_candidate | 750 | 0.847 | 1.000 | 1.000 | 0.929 | 0.000 | 0 | 0 | 0 |
| hybrid_adjudicator_raw | 750 | 1.000 | 1.000 | 1.000 | 0.924 | 0.000 | 4 | 0 | 4 |
| llm_candidate_selector_raw | 739 | 0.984 | 1.000 | 0.218 | 0.665 | 0.000 | 724 | 7 | 49 |
| llm_heavy_selected_fact | 250 | 0.968 | 0.000 | 0.960 | 0.846 | 0.908 | 0 | 0 | 0 |
| state_graph_projection | 750 | 0.844 | 1.000 | 1.000 | 0.873 | 0.000 | 49 | 0 | 42 |

## Claim Boundary

This matrix measures selected evidence validity, selected source-id validity, typed operand completeness, and correctness of the label supported by the selected evidence where saved artifacts expose those fields. Missing source-id instrumentation is reported separately and does not support an exact-source-id claim.
