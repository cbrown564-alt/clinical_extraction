# Gan 2026 ClinicalAssessment Projection/Render Mechanics

Projection/render mechanics only over saved validation250 artifacts. This artifact renders labels when deterministic v0 policy can do so, but scoring is disabled and no benchmark-comparable claim is made.

## Artifacts

- Projection/render JSONL: `experiments\gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_2026-06-06.jsonl`
- CandidateSet source: `experiments\gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06.jsonl`

## Summary

- Rows: 250
- Projection rows: 250
- Rendered-label rows: 209
- Null rendered-label rows: 41
- Row issue rows: 0

## Projection Kinds

- `cluster_frequency`: 8
- `frequency_rate`: 158
- `seizure_free`: 43
- `unknown_frequency`: 41

## Projection Owners

- `benchmark_renderer`: 41
- `boundary_projection_policy`: 43
- `cluster_projection_policy`: 8
- `rate_projection_policy`: 158

## Projection Rules

- `cluster_cadence_as_event_rate_when_size_absent_v0`: 2
- `cluster_cadence_operands_required_v0`: 1
- `cluster_cadence_with_events_per_cluster_v0`: 5
- `frequency_rate_operands_v0`: 158
- `seizure_free_duration_projection_v0`: 14
- `seizure_free_duration_required_v0`: 29
- `unknown_frequency_sentinel_render_v0`: 41

## Render Bases

- `cluster_cadence_with_events_per_cluster`: 5
- `cluster_cadence_without_size`: 2
- `cluster_frequency`: 1
- `frequency_rate`: 158
- `seizure_free_duration`: 43
- `unknown_frequency_internal_state`: 41

## Issues

- `additive_frequency_period_mismatch`: 4
- `aggregation_policy_defaulted:seizure_free_state`: 2
- `cluster_axis_without_cluster_primary_to_primary_with_context`: 2
- `cluster_cadence_operands_incomplete`: 1
- `frequency_rate_operands_incomplete`: 11
- `frequency_rate_operands_unparsed`: 9
- `historical_primary_replaced_with_current:llm:2762:2`: 1
- `multi_primary_nonadditive_demoted_to_supporting`: 6
- `multi_primary_nonadditive_to_additive_same_window`: 1
- `normalization_source_phrase_missing`: 1
- `projection_semantics_missing`: 41
- `seizure_free_duration_required`: 29
- `seizure_free_duration_unparsed`: 12
- `single_primary_additive_same_window_to_single_fact`: 7
- `single_primary_cluster_axis_to_single_fact`: 4
- `vague_count`: 23

## Null Rendered Labels

- First rows: 763, 854, 899, 1695, 1706, 1790, 2023, 2609, 2622, 2762, 2907, 2932, 2938, 2965, 2992, 3015, 3118, 3137, 3371, 3468, 3846, 3995, 4116, 4700, 4842
