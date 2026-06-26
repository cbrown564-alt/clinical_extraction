# Gan 2026 ClinicalAssessment Projection/Render Mechanics

Projection/render mechanics only over saved validation250 artifacts. This artifact renders labels when deterministic v0 policy can do so, but scoring is disabled and no benchmark-comparable claim is made.

## Artifacts

- Projection/render JSONL: `experiments\gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_v1_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_v1_2026-06-06.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_2026-06-06.jsonl`
- CandidateSet source: `experiments\gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06.jsonl`

## Summary

- Rows: 250
- Projection rows: 26
- Rendered-label rows: 22
- Null rendered-label rows: 4
- Row issue rows: 224

## Projection Kinds

- `frequency_rate`: 7
- `seizure_free`: 4
- `unknown_frequency`: 15

## Render Bases

- `frequency_rate`: 7
- `seizure_free_duration`: 4
- `unknown_frequency_internal_state`: 15

## Issues

- `additive_frequency_period_mismatch`: 1
- `assessment_draft_missing`: 224
- `frequency_rate_operands_incomplete`: 1
- `frequency_rate_operands_unparsed`: 1
- `normalization_source_phrase_missing`: 1
- `projection_semantics_missing`: 4
- `seizure_free_duration_required`: 3
- `vague_count`: 3

## Null Rendered Labels

- First rows: 2622, 3118, 5092, 5197
