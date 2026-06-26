# Gan 2026 ClinicalAssessment Projection Score

Validation250 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_clinical_assessment_projection_score_validation250_qwen36_35b_v0_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_score_validation250_qwen36_35b_v0_2026-06-06.json`
- Project/render source: `experiments\gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_v1_2026-06-06.jsonl`

## Summary

- Rows: 250
- Scored rows: 22
- Non-scored rows: 228
- Purist correct on scored rows: 21 (0.9545)
- Pragmatic correct on scored rows: 21 (0.9545)
- Exact normalized-label matches on scored rows: 18 (0.8182)

## Score Statuses

- `not_scored_null_rendered_label`: 228
- `scored`: 22

## Score Issues

- `rendered_label_null`: 228

## Non-Scored Rows

- First rows: 10, 40, 79, 103, 128, 156, 180, 182, 187, 190, 198, 212, 218, 243, 278, 280, 338, 409, 419, 446, 466, 467, 531, 598, 659
