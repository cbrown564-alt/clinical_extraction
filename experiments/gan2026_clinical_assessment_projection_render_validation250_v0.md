# Gan 2026 ClinicalAssessment Projection/Render Mechanics

Projection/render mechanics only over saved validation250 artifacts. This artifact renders labels when deterministic v0 policy can do so, but scoring is disabled and no benchmark-comparable claim is made.

## Artifacts

- Projection/render JSONL: `experiments\gan2026_clinical_assessment_projection_render_validation250_v0.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_render_validation250_v0.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v2.jsonl`
- CandidateSet source: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`

## Summary

- Rows: 250
- Projection rows: 247
- Rendered-label rows: 130
- Null rendered-label rows: 117
- Row issue rows: 3

## Projection Kinds

- `cluster_frequency`: 22
- `frequency_rate`: 167
- `seizure_free`: 41
- `unknown_frequency`: 17

## Render Bases

- `cluster_cadence_with_events_per_cluster`: 3
- `cluster_cadence_without_size`: 1
- `cluster_frequency`: 18
- `frequency_rate`: 167
- `seizure_free_duration`: 41
- `unknown_frequency_internal_state`: 17

## Issues

- `Value error, frequency_rate requires primary_candidate_ids`: 1
- `Value error, supporting_candidate_ids and rejected_candidate_ids overlap`: 1
- `additive_frequency_count_unparsed`: 3
- `cluster_cadence_operands_incomplete`: 18
- `cluster_frequency_operands_unparsed`: 15
- `frequency_rate_operands_incomplete`: 77
- `frequency_rate_operands_unparsed`: 78
- `projection_semantics_missing`: 117
- `rejected_candidate_ids:unknown_candidate_id:llm:5567:5`: 1
- `seizure_free_duration_required`: 22
- `seizure_free_duration_unparsed`: 21
- `vague_count`: 3

## Null Rendered Labels

- First rows: 190, 278, 280, 338, 665, 694, 704, 744, 891, 899, 959, 960, 978, 987, 1165, 1207, 1281, 1317, 1357, 1454, 1486, 1573, 1591, 1596, 1597
