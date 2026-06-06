# Gan 2026 ClinicalAssessment Projection Score

Validation250 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_clinical_assessment_projection_score_validation250_v3.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_score_validation250_v3.json`
- Project/render source: `experiments\gan2026_clinical_assessment_projection_render_validation250_v4.jsonl`

## Summary

- Rows: 250
- Scored rows: 205
- Non-scored rows: 45
- Purist correct on scored rows: 195 (0.9512)
- Pragmatic correct on scored rows: 200 (0.9756)
- Exact normalized-label matches on scored rows: 180 (0.878)

## Score Statuses

- `not_scored_null_rendered_label`: 45
- `scored`: 205

## Score Issues

- `rendered_label_null`: 45

## Non-Scored Rows

- First rows: 744, 854, 1363, 1695, 1794, 2609, 2907, 2932, 2965, 2992, 3015, 3118, 3137, 3297, 3356, 3371, 3468, 3469, 3493, 3507, 3512, 3532, 4345, 4690, 4694
