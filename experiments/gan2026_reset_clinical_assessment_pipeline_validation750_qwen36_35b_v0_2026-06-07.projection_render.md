# Gan 2026 ClinicalAssessment Projection/Render Mechanics

Projection/render mechanics only over saved validation750 artifacts. This artifact renders labels when deterministic v0 policy can do so, but scoring is disabled and no benchmark-comparable claim is made.

## Artifacts

- Projection/render JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.projection_render.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.projection_render.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_qwen36_35b_v3nested_v0_2026-06-07.jsonl`
- CandidateSet source: `experiments\gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- Disabled ablation switches: `[]`

## Summary

- Rows: 750
- Projection rows: 749
- Rendered-label rows: 581
- Null rendered-label rows: 168
- Row issue rows: 1

## Projection Kinds

- `cluster_frequency`: 77
- `frequency_rate`: 387
- `no_reference`: 17
- `seizure_free`: 140
- `unknown_frequency`: 128

## Projection Owners

- `benchmark_renderer`: 145
- `boundary_projection_policy`: 147
- `cluster_projection_policy`: 74
- `rate_projection_policy`: 383

## Projection Rules

- `cluster_cadence_default_multiple_per_cluster_v0`: 28
- `cluster_cadence_values_required_v0`: 10
- `cluster_cadence_with_events_per_cluster_v0`: 31
- `cyclic_pattern_with_explicit_operands_rendered_v0`: 9
- `cyclic_window_pattern_routed_v0`: 4
- `frequency_rate_values_v0`: 375
- `no_reference_sentinel_render_v0`: 17
- `seizure_free_duration_projection_v0`: 23
- `seizure_free_duration_required_v0`: 117
- `sleep_restricted_pattern_routed_v0`: 3
- `unknown_cadence_multiple_per_cluster_v0`: 4
- `unknown_frequency_sentinel_render_v0`: 128

## Render Bases

- `cluster_cadence_with_events_per_cluster`: 31
- `cluster_cadence_without_size`: 29
- `cluster_frequency`: 10
- `cyclic_window_pattern`: 4
- `frequency_rate`: 383
- `no_reference_internal_state`: 17
- `seizure_free_duration`: 140
- `sleep_restricted_pattern`: 3
- `unknown_cadence_cluster_burden`: 4
- `unknown_frequency_internal_state`: 128

## Issues

- `additive_frequency_count_unparsed`: 3
- `additive_frequency_fallback_to_primary_candidate`: 33
- `additive_frequency_period_mismatch`: 32
- `cluster_assessment_promoted_to_frequency_rate`: 17
- `cluster_axis_without_cluster_primary_to_primary_with_context`: 1
- `cluster_cadence_unknown_with_per_cluster_burden`: 4
- `cluster_cadence_values_incomplete`: 10
- `cluster_frequency_values_unparsed`: 15
- `conditional_only_trigger_without_baseline`: 1
- `cyclic_window_pattern_routed`: 4
- `frequency_rate_values_incomplete`: 34
- `frequency_rate_values_repaired_from_primary_candidate`: 22
- `frequency_rate_values_unparsed`: 67
- `historical_primary_replaced_with_current:llm:15639:3`: 1
- `historical_primary_replaced_with_current:llm:15715:1`: 1
- `historical_primary_replaced_with_current:llm:15783:3`: 1
- `normalization_source_phrase_missing`: 19
- `prior_encounter_derived_seizure_free_duration`: 1
- `projection_semantics_missing`: 168
- `reference_date_missing_for_since_date`: 26
- `seizure_free_anchor_from_prior_encounter_context`: 1
- `seizure_free_duration_repaired_from_primary_candidate`: 1
- `seizure_free_duration_required`: 117
- `seizure_free_duration_unparsed`: 41
- `seizure_free_since_date_anchor_unparsed`: 31
- `single_primary_additive_same_window_to_single_fact`: 38
- `single_primary_cluster_axis_to_single_fact`: 27
- `sleep_restricted_pattern_routed`: 3
- `supporting_candidate_ids:unknown_candidate_id:llm:1248:2`: 1
- `vague_count`: 109
- `vague_frequency_with_explicit_time_period`: 6

## Null Rendered Labels

- First rows: 1706, 2907, 2932, 2938, 2965, 2992, 3015, 3118, 3137, 3356, 3371, 3468, 3493, 3532, 3534, 4771, 4842, 4951, 4992, 4994, 5040, 5082, 5092, 5110, 5121
