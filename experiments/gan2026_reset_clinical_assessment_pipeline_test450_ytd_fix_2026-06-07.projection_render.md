# Gan 2026 ClinicalAssessment Projection/Render Mechanics

Projection/render mechanics only over saved validation450 artifacts. This artifact renders labels when deterministic v0 policy can do so, but scoring is disabled and no benchmark-comparable claim is made.

## Artifacts

- Projection/render JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.projection_render.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.projection_render.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_test450_gpt41mini_v3nested_v3_2026-06-07.jsonl`
- CandidateSet source: `experiments\gan2026_test450_candidate_set_v3_nested_dedupe_context_v1_2026-06-07.jsonl`
- Disabled ablation switches: `[]`

## Summary

- Rows: 450
- Projection rows: 449
- Rendered-label rows: 341
- Null rendered-label rows: 108
- Row issue rows: 1

## Projection Kinds

- `cluster_frequency`: 44
- `frequency_rate`: 262
- `no_reference`: 18
- `seizure_free`: 83
- `unknown_frequency`: 42

## Projection Owners

- `benchmark_renderer`: 60
- `boundary_projection_policy`: 87
- `cluster_projection_policy`: 42
- `rate_projection_policy`: 260

## Projection Rules

- `cluster_cadence_default_multiple_per_cluster_v0`: 13
- `cluster_cadence_values_required_v0`: 7
- `cluster_cadence_with_events_per_cluster_v0`: 17
- `cyclic_pattern_with_explicit_operands_rendered_v0`: 10
- `cyclic_window_pattern_routed_v0`: 4
- `date_anchored_ytd_denominator_v0`: 3
- `frequency_rate_values_v0`: 248
- `no_reference_sentinel_render_v0`: 18
- `seizure_free_duration_projection_v0`: 44
- `seizure_free_duration_required_v0`: 39
- `unknown_cadence_multiple_per_cluster_v0`: 4
- `unknown_frequency_sentinel_render_v0`: 42

## Render Bases

- `cluster_cadence_with_events_per_cluster`: 17
- `cluster_cadence_without_size`: 14
- `cluster_frequency`: 7
- `cyclic_window_pattern`: 4
- `date_anchored_ytd_denominator`: 3
- `frequency_rate`: 257
- `no_reference_internal_state`: 18
- `seizure_free_duration`: 83
- `unknown_cadence_cluster_burden`: 4
- `unknown_frequency_internal_state`: 42

## Issues

- `additive_frequency_count_unparsed`: 5
- `additive_frequency_period_mismatch`: 8
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:12504:3`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:12643:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:14944:1`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:15302:1`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:13162:2:kept_primary_candidate_ids`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:15434:1:kept_supporting_candidate_ids`: 1
- `candidate_role_overlap_removed:supporting_candidate_ids:llm:15302:2:kept_primary_candidate_ids`: 1
- `cluster_assessment_promoted_to_frequency_rate`: 18
- `cluster_cadence_unknown_with_per_cluster_burden`: 4
- `cluster_cadence_values_incomplete`: 7
- `cluster_frequency_values_unparsed`: 12
- `cluster_label_values_unparsed`: 1
- `cyclic_window_pattern_routed`: 4
- `frequency_rate_values_incomplete`: 58
- `frequency_rate_values_repaired_from_primary_candidate`: 18
- `frequency_rate_values_unparsed`: 73
- `historical_primary_replaced_with_current:llm:10621:1`: 1
- `historical_primary_replaced_with_current:llm:15609:3`: 1
- `historical_primary_replaced_with_current:llm:2684:2`: 1
- `normalization_source_phrase_missing`: 2
- `projection_semantics_missing`: 108
- `relative_change_without_current_baseline`: 1
- `seizure_free_anchor_approximate_start_month_policy`: 7
- `seizure_free_anchor_from_event_phrase`: 2
- `seizure_free_anchor_from_last_event_phrase`: 1
- `seizure_free_anchor_from_same_note_antecedent`: 1
- `seizure_free_anchor_year_inferred_from_reference_date`: 18
- `seizure_free_duration_instrumented_from_since_date`: 27
- `seizure_free_duration_required`: 39
- `seizure_free_duration_unparsed`: 32
- `seizure_free_since_date_anchor_unparsed`: 10
- `single_primary_additive_same_window_to_single_fact`: 1
- `supporting_candidate_ids:unknown_candidate_id:llm:13167:6`: 1
- `vague_count`: 58
- `vague_frequency_with_explicit_time_period`: 9

## Null Rendered Labels

- First rows: 804, 824, 892, 934, 938, 1629, 1705, 2135, 2725, 2978, 3407, 3514, 4197, 4217, 4707, 4967, 5088, 5174, 5213, 5540, 5764, 6025, 6164, 6303, 6387
