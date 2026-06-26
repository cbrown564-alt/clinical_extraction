# Gan 2026 Validation-Test Gap Hypothesis Selection v0

Split manifest: `gan2026_split_v1`

Validation-development hypothesis selection only. Locked-test row-level failure inspection remains unauthorized.

## Decision

Start with H2/H4 combined validation hard/control panel; use H6 selective action as the no-regression control and do not inspect locked-test rows.

## Selected Hypotheses

| Priority | Hypothesis | Status | Next experiment |
| ---: | --- | --- | --- |
| 1 | `H2` component_ownership | selected_for_controlled_validation_experiment | Build a family-indexed component-owner hard/control panel over validation rows, with deterministic-adapter, safety-floor, and monitor-policy strata. |
| 2 | `H4` evidence_transfers_projection_does_not | selected_for_score_layer_ladder | Run a score-layer ladder on validation hard slices that separates selected evidence, source ids, projection choice, adapter rendering, and final action policy. |
| 3 | `H6` selective_action_transfers | selected_as_transfer_control | Use selective-action behavior as a control arm for any H2/H4 component-stress panel; do not broaden it without matched controls. |

## Component Owner Summary

| Component owner | Rows | Correct | Incorrect | Nonprediction | Changed | Exact evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| deterministic_adapter | 701 | 671 | 30 | 0 | 0 | 701 |
| safety_floor | 49 | 7 | 8 | 34 | 34 | 15 |

## Hidden Family Summary

| Hidden family | Rows | Correct | Incorrect | Nonprediction | Changed | Exact evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| seizure_free_duration | 27 | 0 | 17 | 10 | 10 | 17 |
| competing_semiologies | 26 | 1 | 18 | 7 | 7 | 19 |
| current_vs_historical | 25 | 0 | 17 | 8 | 8 | 17 |
| uncertainty_or_ambiguity | 24 | 0 | 13 | 11 | 11 | 13 |
| unknown_boundary | 20 | 0 | 9 | 11 | 11 | 9 |
| none | 695 | 676 | 0 | 19 | 19 | 676 |
| rate_bucket_or_denominator | 20 | 1 | 17 | 2 | 2 | 18 |
| cluster_burden | 11 | 0 | 11 | 0 | 0 | 11 |
| benchmark_format_convention | 10 | 0 | 10 | 0 | 0 | 10 |
| diary_or_log_aggregation | 4 | 1 | 3 | 0 | 0 | 4 |
| unclassified | 2 | 0 | 1 | 1 | 1 | 1 |

## Evidence Summary

| Evidence status | Rows | Correct | Incorrect | Nonprediction | Changed | Exact evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| exact_evidence_and_source_ids | 716 | 678 | 38 | 0 | 0 | 716 |
| nonprediction_no_selected_evidence | 34 | 0 | 0 | 34 | 34 | 0 |

## Monitor Summary

| Action or reason | Rows |
| --- | ---: |
| action:abstain | 26 |
| reason:trigger_conditioned_frequency | 24 |
| action:human_review | 8 |
| reason:last_event_boundary | 8 |
| reason:missing_denominator_anchor | 2 |

## Surface Gap Context

| Candidate | Validation proxy | Test proxy | Gap |
| --- | ---: | ---: | ---: |
| direct_labeler_targeted_switch | 0.9560 | 0.7867 | 0.1693 |
| fewshot_train_exemplar | 0.9680 | 0.7933 | 0.1747 |
| structural_guard | 0.9320 | 0.7622 | 0.1698 |

## Selective Action Context

| Split | Rows | Changed | W->C | C->W | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| validation750 | 750 | 21 | 11 | 0 | 1.0000 |
| locked_test450 | 450 | 14 | 8 | 0 | 0.8889 |

## Deferred Hypotheses

| Hypothesis | Reason |
| --- | --- |
| `H1` | Needs predeclared test slice aggregates before accepting hidden-family mix. |
| `H3` | Requires candidate-exposure instrumentation not present in gap_matrix_v0. |
| `H5` | Requires same-raw-output repair ladders with explicit semantic repair ownership. |
| `H7` | Requires synthetic or adversarial minimal-pair panels. |
| `H8` | Benchmark-format rows are visible but not yet isolated as the primary gap driver. |
| `H9` | Monitor-policy rows are available, but H2/H4 should own first stress panels. |
| `H10` | No live rerun or same-raw-output variance signal in this artifact. |
