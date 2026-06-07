# Gan 2026 ClinicalAssessment Projection Score

validation750 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_contract_replay_2026-06-07.score.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_contract_replay_2026-06-07.score.json`
- Project/render source: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_contract_replay_2026-06-07.projection_render.jsonl`

## Summary

- Rows: 750
- Scored rows: 597
- Non-scored rows: 153
- Purist correct on scored rows: 500 (0.8375)
- Pragmatic correct on scored rows: 531 (0.8894)
- Exact normalized-label matches on scored rows: 424 (0.7102)

## Score Statuses

- `not_scored_null_rendered_label`: 153
- `scored`: 597

## Score Issues

- `rendered_label_null`: 153

## Non-Scored Rows

- First rows: 1695, 1706, 3118, 3137, 3356, 3371, 3468, 3469, 3482, 3493, 3507, 3512, 3532, 3534, 4337, 4345, 4368, 4562, 4563, 4574, 4592, 4597, 4842, 4951, 5040
