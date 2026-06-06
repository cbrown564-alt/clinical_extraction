# Gan 2026 ClinicalAssessment Projection Score

validation750 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_validation750_one_family_off_seizure_free_duration_date_instrumentation_context_repair_v6_2026-06-06.score.jsonl`
- Summary JSON: `experiments\gan2026_validation750_one_family_off_seizure_free_duration_date_instrumentation_context_repair_v6_2026-06-06.score.json`
- Project/render source: `experiments\gan2026_validation750_one_family_off_seizure_free_duration_date_instrumentation_context_repair_v6_2026-06-06.projection_render.jsonl`

## Summary

- Rows: 750
- Scored rows: 539
- Non-scored rows: 211
- Purist correct on scored rows: 462 (0.8571)
- Pragmatic correct on scored rows: 494 (0.9165)
- Exact normalized-label matches on scored rows: 403 (0.7477)

## Score Statuses

- `not_scored_null_rendered_label`: 211
- `scored`: 539

## Score Issues

- `rendered_label_null`: 211

## Non-Scored Rows

- First rows: 1695, 1706, 2907, 2932, 2938, 2965, 2992, 3015, 3118, 3137, 3356, 3371, 3468, 3469, 3482, 3493, 3507, 3512, 3532, 3534, 4842, 4951, 4992, 4994, 5040
