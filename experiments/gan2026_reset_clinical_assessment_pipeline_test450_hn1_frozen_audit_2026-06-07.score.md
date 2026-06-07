# Gan 2026 ClinicalAssessment Projection Score

validation450 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_hn1_frozen_audit_2026-06-07.score.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_hn1_frozen_audit_2026-06-07.score.json`
- Project/render source: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_hn1_frozen_audit_2026-06-07.projection_render.jsonl`

## Summary

- Rows: 450
- Scored rows: 358
- Non-scored rows: 92
- Purist correct on scored rows: 282 (0.7877)
- Pragmatic correct on scored rows: 294 (0.8212)
- Exact normalized-label matches on scored rows: 237 (0.662)

## Score Statuses

- `not_scored_null_rendered_label`: 92
- `scored`: 358

## Score Issues

- `rendered_label_null`: 92

## Non-Scored Rows

- First rows: 804, 824, 938, 1705, 2135, 2978, 3407, 3514, 4197, 4217, 4707, 4967, 5088, 5174, 5213, 5540, 5764, 6025, 6164, 6303, 6387, 6592, 7232, 7405, 7688
