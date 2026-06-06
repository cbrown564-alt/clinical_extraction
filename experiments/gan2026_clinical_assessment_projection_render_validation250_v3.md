# Gan 2026 ClinicalAssessment Projection/Render Mechanics

Projection/render mechanics only over saved validation250 artifacts. This artifact renders labels when deterministic v0 policy can do so, but scoring is disabled and no benchmark-comparable claim is made.

## Artifacts

- Projection/render JSONL: `experiments\gan2026_clinical_assessment_projection_render_validation250_v3.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_render_validation250_v3.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v2.jsonl`
- CandidateSet source: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`

## Summary

- Rows: 250
- Projection rows: 247
- Rendered-label rows: 204
- Null rendered-label rows: 43
- Row issue rows: 3

## Projection Kinds

- `cluster_frequency`: 16
- `frequency_rate`: 173
- `seizure_free`: 41
- `unknown_frequency`: 17

## Projection Owners

- `benchmark_renderer`: 17
- `boundary_projection_policy`: 41
- `cluster_projection_policy`: 16
- `rate_projection_policy`: 173

## Projection Rules

- `cluster_cadence_as_event_rate_when_size_absent_v0`: 6
- `cluster_cadence_operands_required_v0`: 5
- `cluster_cadence_with_events_per_cluster_v0`: 5
- `frequency_rate_operands_v0`: 173
- `seizure_free_duration_projection_v0`: 17
- `seizure_free_duration_required_v0`: 24
- `unknown_frequency_sentinel_render_v0`: 17

## Render Bases

- `cluster_cadence_with_events_per_cluster`: 5
- `cluster_cadence_without_size`: 6
- `cluster_frequency`: 5
- `frequency_rate`: 173
- `seizure_free_duration`: 41
- `unknown_frequency_internal_state`: 17

## Issues

- `Value error, frequency_rate requires primary_candidate_ids`: 1
- `Value error, supporting_candidate_ids and rejected_candidate_ids overlap`: 1
- `additive_frequency_period_mismatch`: 1
- `cluster_assessment_promoted_to_frequency_rate`: 6
- `cluster_cadence_operands_incomplete`: 5
- `cluster_frequency_operands_unparsed`: 5
- `frequency_rate_operands_incomplete`: 14
- `frequency_rate_operands_unparsed`: 13
- `medication_cadence_ambiguity`: 1
- `projection_semantics_missing`: 43
- `rejected_candidate_ids:unknown_candidate_id:llm:5567:5`: 1
- `seizure_free_duration_required`: 24
- `seizure_free_duration_unparsed`: 7
- `vague_count`: 28

## Null Rendered Labels

- First rows: 744, 854, 1317, 1695, 1794, 2609, 2907, 2932, 2965, 2992, 3015, 3118, 3137, 3297, 3356, 3371, 3468, 3469, 3493, 3507, 3512, 4345, 4690, 4694, 4700
