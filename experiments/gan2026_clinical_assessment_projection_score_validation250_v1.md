# Gan 2026 ClinicalAssessment Projection Score

Validation250 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_clinical_assessment_projection_score_validation250_v1.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_score_validation250_v1.json`
- Project/render source: `experiments\gan2026_clinical_assessment_projection_render_validation250_v2.jsonl`

## Summary

- Rows: 250
- Scored rows: 204
- Non-scored rows: 46
- Purist correct on scored rows: 194 (0.951)
- Pragmatic correct on scored rows: 199 (0.9755)
- Exact normalized-label matches on scored rows: 179 (0.8775)

## Score Statuses

- `not_scored_null_rendered_label`: 46
- `scored`: 204

## Score Issues

- `rendered_label_null`: 46

## Non-Scored Rows

- First rows: 744, 854, 1317, 1363, 1695, 1794, 2609, 2907, 2932, 2965, 2992, 3015, 3118, 3137, 3297, 3356, 3371, 3468, 3469, 3493, 3507, 3512, 3532, 4345, 4690
