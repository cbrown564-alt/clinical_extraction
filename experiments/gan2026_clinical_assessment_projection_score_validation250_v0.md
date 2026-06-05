# Gan 2026 ClinicalAssessment Projection Score

Validation250 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_clinical_assessment_projection_score_validation250_v0.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_score_validation250_v0.json`
- Project/render source: `experiments\gan2026_clinical_assessment_projection_render_validation250_v1.jsonl`

## Summary

- Rows: 250
- Scored rows: 198
- Non-scored rows: 52
- Purist correct on scored rows: 188 (0.9495)
- Pragmatic correct on scored rows: 193 (0.9747)
- Exact normalized-label matches on scored rows: 173 (0.8737)

## Score Statuses

- `not_scored_null_rendered_label`: 52
- `scored`: 198

## Score Issues

- `rendered_label_null`: 52

## Non-Scored Rows

- First rows: 338, 744, 854, 1317, 1363, 1573, 1695, 1707, 1794, 2609, 2907, 2932, 2965, 2992, 3015, 3118, 3137, 3297, 3356, 3371, 3468, 3469, 3493, 3507, 3512
