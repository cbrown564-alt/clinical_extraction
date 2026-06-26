# Gan 2026 ClinicalAssessment Projection Score

validation750 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.score.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.score.json`
- Project/render source: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.projection_render.jsonl`

## Summary

- Rows: 750
- Scored rows: 581
- Non-scored rows: 169
- Purist correct on scored rows: 486 (0.8365)
- Pragmatic correct on scored rows: 516 (0.8881)
- Exact normalized-label matches on scored rows: 402 (0.6919)

## Score Statuses

- `not_scored_null_rendered_label`: 169
- `scored`: 581

## Score Issues

- `rendered_label_null`: 169

## Non-Scored Rows

- First rows: 1706, 2907, 2932, 2938, 2965, 2992, 3015, 3118, 3137, 3356, 3371, 3468, 3493, 3532, 3534, 4771, 4842, 4951, 4992, 4994, 5040, 5082, 5092, 5110, 5121
