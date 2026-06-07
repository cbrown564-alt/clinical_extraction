# Gan 2026 ClinicalAssessment Projection Score

validation450 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_gpt41mini_v0.score.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_gpt41mini_v0.score.json`
- Project/render source: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_gpt41mini_v0.projection_render.jsonl`

## Summary

- Rows: 450
- Scored rows: 341
- Non-scored rows: 109
- Purist correct on scored rows: 268 (0.7859)
- Pragmatic correct on scored rows: 280 (0.8211)
- Exact normalized-label matches on scored rows: 229 (0.6716)

## Score Statuses

- `not_scored_null_rendered_label`: 109
- `scored`: 341

## Score Issues

- `rendered_label_null`: 109

## Non-Scored Rows

- First rows: 804, 824, 892, 934, 938, 1629, 1705, 2135, 2725, 2978, 3407, 3514, 4197, 4217, 4707, 4967, 5088, 5174, 5213, 5540, 5764, 6025, 6164, 6303, 6387
