# Gan 2026 Validation-Test Surface Map v0

Split manifest: `gan2026_split_v1`

This report is aggregate-only for locked test surfaces. It does not expose locked-test row-level failures.

## Candidate Gap Summary

| Candidate | Validation proxy | Test proxy | Gap | Validation rows | Test rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| direct_labeler_targeted_switch | 0.9560 | 0.7867 | 0.1693 |  | 450 |
| fewshot_train_exemplar | 0.9680 | 0.7933 | 0.1747 | 750 | 450 |
| structural_guard | 0.9320 | 0.7622 | 0.1698 | 750 | 450 |

## Surface Summaries

| Artifact | Distribution | Rows | Final proxy | Changed | W->C | C->W | Inspection |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| rules_only_v1_baseline | validation_development_reference |  |  |  |  |  | validation_summary_reference |
| staged_assembly_validation750_component_matrix | validation750 | 750 |  |  |  |  | validation_row_level_allowed |
| staged_assembly_validation750_no_call | validation750 |  |  |  |  |  | validation_row_level_allowed |
| hidden_family_first_failure_atlas | validation750 | 1000 |  |  |  |  | validation_row_level_allowed |
| rq7_family_component_matrix | validation_development |  |  |  |  |  | validation_summary_and_row_examples_allowed |
| selective_safety_floor_validation750 | validation750 | 750 |  |  |  |  | validation_row_level_allowed |
| selective_safety_floor_test450_frozen_readout | locked_test450 |  |  |  |  |  | locked_test_aggregate_only |
| staged_assembly_test450_nonprediction_selector | locked_test450 | 450 |  |  |  |  | locked_test_aggregate_only |
| direct_labeler_targeted_switch_validation750 | validation750 |  | 0.9560 |  |  |  | validation_row_level_allowed |
| direct_labeler_targeted_switch_test450 | locked_test450 | 450 | 0.7867 | 34 |  |  | locked_test_aggregate_only |
| structured_candidate_direct_labeler_validation750 | validation750 | 750 |  |  |  |  | validation_row_level_allowed |
| fewshot_train_exemplar_validation750 | validation750 | 750 | 0.9680 |  |  |  | validation_row_level_allowed |
| fewshot_train_exemplar_test450 | locked_test450 | 450 | 0.7933 | 35 |  |  | locked_test_aggregate_only |
| structural_guard_validation750 | validation750 | 750 | 0.9320 |  |  |  | validation_row_level_allowed |
| structural_guard_test450 | locked_test450 | 450 | 0.7622 |  |  |  | locked_test_aggregate_only |
| llm_structured_validation750_repair_ladders | validation750 |  |  |  |  |  | validation_row_level_allowed_after_provenance_check |

## Known Gaps

- Metrics are aggregate-only and depend on fields present in saved artifacts.
- Locked-test summaries intentionally omit row-level records.
- Candidate gaps are computed only when comparable validation and locked-test final Purist proxies are available.
