# Gan 2026 ClinicalAssessment Projection Score

validation750 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v3_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v3_2026-06-06.json`
- Project/render source: `experiments\gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v3_2026-06-06.jsonl`

## Summary

- Rows: 750
- Scored rows: 571
- Non-scored rows: 179
- Purist correct on scored rows: 482 (0.8441)
- Pragmatic correct on scored rows: 514 (0.9002)
- Exact normalized-label matches on scored rows: 414 (0.725)

## Score Statuses

- `not_scored_null_rendered_label`: 179
- `scored`: 571

## Score Issues

- `rendered_label_null`: 179

## Non-Scored Rows

- First rows: 1695, 1706, 2609, 3118, 3137, 3356, 3371, 3468, 3469, 3482, 3493, 3507, 3512, 3532, 3534, 4690, 4694, 4700, 4709, 4842, 4951, 5040, 5082, 5092, 5110
