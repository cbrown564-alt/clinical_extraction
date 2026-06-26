# Gan 2026 ClinicalAssessment Projection/Render Mechanics

Projection/render mechanics only over saved validation250 artifacts. This artifact renders labels when deterministic v0 policy can do so, but scoring is disabled and no benchmark-comparable claim is made.

## Artifacts

- Projection/render JSONL: `experiments\gan2026_clinical_assessment_projection_render_validation250_v1.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_render_validation250_v1.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v2.jsonl`
- CandidateSet source: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`

## Summary

- Rows: 250
- Projection rows: 247
- Rendered-label rows: 198
- Null rendered-label rows: 49
- Row issue rows: 3

## Projection Kinds

- `cluster_frequency`: 22
- `frequency_rate`: 167
- `seizure_free`: 41
- `unknown_frequency`: 17

## Render Bases

- `cluster_cadence_with_events_per_cluster`: 5
- `cluster_cadence_without_size`: 6
- `cluster_frequency`: 11
- `frequency_rate`: 167
- `seizure_free_duration`: 41
- `unknown_frequency_internal_state`: 17

## Issues

- `Value error, frequency_rate requires primary_candidate_ids`: 1
- `Value error, supporting_candidate_ids and rejected_candidate_ids overlap`: 1
- `additive_frequency_period_mismatch`: 1
- `cluster_cadence_operands_incomplete`: 11
- `cluster_frequency_operands_unparsed`: 11
- `frequency_rate_operands_incomplete`: 14
- `frequency_rate_operands_unparsed`: 13
- `projection_semantics_missing`: 49
- `rejected_candidate_ids:unknown_candidate_id:llm:5567:5`: 1
- `seizure_free_duration_required`: 24
- `seizure_free_duration_unparsed`: 7
- `vague_count`: 25

## Null Rendered Labels

- First rows: 338, 744, 854, 1317, 1573, 1695, 1707, 1794, 2609, 2907, 2932, 2965, 2992, 3015, 3118, 3137, 3297, 3356, 3371, 3468, 3469, 3493, 3507, 3512, 4173
