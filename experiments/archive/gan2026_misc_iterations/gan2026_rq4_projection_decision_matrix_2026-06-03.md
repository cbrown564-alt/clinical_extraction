# Gan 2026 RQ4 Projection-Decision Matrix

Replay-first component matrix for RQ4 projection. This is a validation-development artifact over saved decisions and diagnostic ablations, not a benchmark or locked-holdout claim.

- JSONL artifact: `experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl`
- Matrix rows: 3250
- Source rows represented: 750

## Component Summary

| Component | Rows | Projection correct | Changed | W->C | C->W | Exact evidence | Source-id valid |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_v0 | 42 | 0.000 | 0 | 0 | 0 | 1.000 | 1.000 |
| boundary_state_priority | 42 | 0.405 | 20 | 17 | 0 | 1.000 | 1.000 |
| claim_table_final_query | 248 | 0.921 | 0 | 0 | 0 | 0.992 | 1.000 |
| competing_frequency_uncertainty | 42 | 0.024 | 10 | 1 | 0 | 1.000 | 1.000 |
| deterministic_top_candidate | 750 | 0.929 | 0 | 0 | 0 | 0.847 | 1.000 |
| graph_gated_month_bucket_duration | 250 | 0.796 | 18 | 18 | 0 | 1.000 | 1.000 |
| hybrid_adjudicator_raw | 750 | 0.924 | 4 | 0 | 4 | 1.000 | 1.000 |
| llm_heavy_selected_fact | 250 | 0.846 | 0 | 0 | 0 | 0.968 | 0.000 |
| lowest_current_frequency | 42 | 0.071 | 5 | 3 | 0 | 1.000 | 1.000 |
| oracle_gold_node | 42 | 0.548 | 24 | 23 | 0 | 1.000 | 1.000 |
| seizure_free_priority | 42 | 0.191 | 13 | 8 | 0 | 1.000 | 1.000 |
| state_graph_projection | 750 | 0.873 | 49 | 0 | 42 | 0.844 | 1.000 |

## Surface Summary

| Surface | Rows | Projection correct | Changed | W->C | C->W |
| --- | ---: | ---: | ---: | ---: | ---: |
| regression_validation_hard_slice | 232 | 0.780 | 0 | 0 | 0 |
| target_duration_enriched | 18 | 1.000 | 18 | 18 | 0 |
| validation25 | 498 | 0.884 | 0 | 0 | 0 |
| validation750 | 2250 | 0.909 | 53 | 0 | 46 |
| validation_hard_slice_projection_arbitration | 252 | 0.206 | 72 | 52 | 0 |

## Claim Boundary

Rows from validation750 compare saved scorer-facing labels against the deterministic top candidate. Rows from projection ablations compare named graph policies only on preselected diagnostic surfaces where candidate/state representation already exists. The matrix therefore answers projection as a development-control question; it does not promote a production policy or make a holdout-transfer claim.
