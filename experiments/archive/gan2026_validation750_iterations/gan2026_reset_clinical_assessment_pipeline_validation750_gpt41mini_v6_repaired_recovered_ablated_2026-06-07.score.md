# Gan 2026 ClinicalAssessment Projection Score

validation750 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_ablated_2026-06-07.score.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_ablated_2026-06-07.score.json`
- Project/render source: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_ablated_2026-06-07.projection_render.jsonl`

## Summary

- Rows: 750
- Scored rows: 580
- Non-scored rows: 170
- Purist correct on scored rows: 494 (0.8517)
- Pragmatic correct on scored rows: 525 (0.9052)
- Exact normalized-label matches on scored rows: 426 (0.7345)

## Score Statuses

- `not_scored_null_rendered_label`: 170
- `scored`: 580

## Score Issues

- `rendered_label_null`: 170

## Non-Scored Rows

- First rows: 1695, 1706, 3118, 3137, 3356, 3371, 3468, 3469, 3482, 3493, 3507, 3512, 3532, 3534, 4842, 4951, 5040, 5082, 5092, 5110, 5121, 5136, 5197, 5210, 5345
