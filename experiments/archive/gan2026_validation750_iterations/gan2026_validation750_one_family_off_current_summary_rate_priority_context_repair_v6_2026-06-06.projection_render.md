# Gan 2026 ClinicalAssessment Projection/Render Mechanics

Projection/render mechanics only over saved validation750 artifacts. This artifact renders labels when deterministic v0 policy can do so, but scoring is disabled and no benchmark-comparable claim is made.

## Artifacts

- Projection/render JSONL: `experiments\gan2026_validation750_one_family_off_current_summary_rate_priority_context_repair_v6_2026-06-06.projection_render.jsonl`
- Summary JSON: `experiments\gan2026_validation750_one_family_off_current_summary_rate_priority_context_repair_v6_2026-06-06.projection_render.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`
- CandidateSet source: `experiments\gan2026_validation750_candidate_set_v3_nested_dedupe_context_v1_2026-06-06.jsonl`
- Disabled ablation switches: `['project_current_summary_rate_priority']`

## Summary

- Rows: 750
- Projection rows: 750
- Rendered-label rows: 580
- Null rendered-label rows: 170
- Row issue rows: 0

## Projection Kinds

- `cluster_frequency`: 84
- `frequency_rate`: 426
- `no_reference`: 25
- `seizure_free`: 143
- `unknown_frequency`: 71
- `unresolved_multiple`: 1

## Projection Owners

- `benchmark_renderer`: 97
- `boundary_projection_policy`: 143
- `cluster_projection_policy`: 84
- `rate_projection_policy`: 426

## Projection Rules

- `cluster_cadence_as_event_rate_when_size_absent_v0`: 30
- `cluster_cadence_values_required_v0`: 18
- `cluster_cadence_with_events_per_cluster_v0`: 32
- `frequency_rate_values_v0`: 426
- `no_reference_sentinel_render_v0`: 25
- `seizure_free_duration_projection_v0`: 67
- `seizure_free_duration_required_v0`: 75
- `seizure_free_proxy_evidence_block_v0`: 1
- `unknown_cadence_multiple_per_cluster_v0`: 4
- `unknown_frequency_sentinel_render_v0`: 71
- `unresolved_multiple_no_render_v0`: 1

## Render Bases

- `cluster_cadence_with_events_per_cluster`: 32
- `cluster_cadence_without_size`: 30
- `cluster_frequency`: 18
- `frequency_rate`: 426
- `no_reference_internal_state`: 25
- `seizure_free_duration`: 142
- `seizure_free_proxy_evidence`: 1
- `unknown_cadence_cluster_burden`: 4
- `unknown_frequency_internal_state`: 71
- `unresolved_multiple`: 1

## Issues

- `additive_frequency_count_unparsed`: 1
- `additive_frequency_period_mismatch`: 28
- `candidate_role_duplicate_removed:primary_candidate_ids:llm:12412:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:11118:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:11350:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:12502:3`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:12665:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:12667:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:12749:3`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:12751:5`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:15021:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:15513:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:15802:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:8355:2`: 1
- `candidate_role_duplicate_removed:supporting_candidate_ids:llm:9496:2`: 2
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:11350:2:kept_supporting_candidate_ids`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:12548:4:kept_supporting_candidate_ids`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:12749:3:kept_supporting_candidate_ids`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:12751:2:kept_primary_candidate_ids`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:15513:2:kept_supporting_candidate_ids`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:15802:2:kept_supporting_candidate_ids`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:7196:2:kept_supporting_candidate_ids`: 1
- `candidate_role_overlap_removed:rejected_candidate_ids:llm:9496:2:kept_supporting_candidate_ids`: 1
- `candidate_role_overlap_removed:supporting_candidate_ids:llm:12412:2:kept_primary_candidate_ids`: 1
- `candidate_role_overlap_removed:supporting_candidate_ids:llm:12679:2:kept_primary_candidate_ids`: 1
- `candidate_role_overlap_removed:supporting_candidate_ids:llm:12679:3:kept_primary_candidate_ids`: 1
- `candidate_role_overlap_removed:supporting_candidate_ids:llm:12679:4:kept_primary_candidate_ids`: 1
- `candidate_role_overlap_removed:supporting_candidate_ids:llm:12749:1:kept_primary_candidate_ids`: 1
- `candidate_role_overlap_removed:supporting_candidate_ids:llm:16757:1:kept_primary_candidate_ids`: 1
- `candidate_role_overlap_removed:supporting_candidate_ids:llm:8079:2:kept_primary_candidate_ids`: 1
- `cluster_assessment_promoted_to_frequency_rate`: 21
- `cluster_cadence_unknown_with_per_cluster_burden`: 4
- `cluster_cadence_values_incomplete`: 18
- `cluster_frequency_values_unparsed`: 19
- `conditional_only_trigger_without_baseline`: 1
- `cyclic_window_without_event_count`: 5
- `frequency_rate_values_incomplete`: 75
- `frequency_rate_values_repaired_from_primary_candidate`: 24
- `frequency_rate_values_unparsed`: 72
- `historical_primary_replaced_with_current:llm:15639:3`: 1
- `historical_primary_replaced_with_current:llm:15715:1`: 1
- `historical_primary_replaced_with_current:llm:15783:3`: 1
- `normalization_source_phrase_missing`: 9
- `prior_encounter_derived_seizure_free_duration`: 1
- `projection_semantics_missing`: 170
- `relative_change_without_current_baseline`: 2
- `seizure_free_anchor_approximate_start_month_policy`: 9
- `seizure_free_anchor_from_event_phrase`: 5
- `seizure_free_anchor_from_last_event_phrase`: 4
- `seizure_free_anchor_from_prior_encounter_context`: 1
- `seizure_free_anchor_from_same_note_antecedent`: 2
- `seizure_free_anchor_year_inferred_from_reference_date`: 15
- `seizure_free_duration_instrumented_from_since_date`: 41
- `seizure_free_duration_required`: 75
- `seizure_free_duration_unparsed`: 37
- `seizure_free_proxy_evidence_overreach`: 1
- `seizure_free_since_date_anchor_unparsed`: 19
- `single_primary_additive_same_window_to_single_fact`: 2
- `unresolved_multiple_not_renderable`: 1
- `vague_count`: 135
- `vague_frequency_with_explicit_time_period`: 24

## Null Rendered Labels

- First rows: 1695, 1706, 3118, 3137, 3356, 3371, 3468, 3469, 3482, 3493, 3507, 3512, 3532, 3534, 4842, 4951, 5040, 5082, 5092, 5110, 5121, 5136, 5197, 5210, 5345
