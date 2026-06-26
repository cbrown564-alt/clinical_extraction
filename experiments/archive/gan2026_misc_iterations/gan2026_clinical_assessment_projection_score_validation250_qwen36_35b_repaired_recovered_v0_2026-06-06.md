# Gan 2026 ClinicalAssessment Projection Score

validation250 mechanics scoring over saved project/render rows only. Scoring reuses the existing label parser plus purist/pragmatic category mappers and is not a benchmark-comparable promotion claim.

## Artifacts

- Scoring JSONL: `experiments\gan2026_clinical_assessment_projection_score_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_clinical_assessment_projection_score_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.json`
- Project/render source: `experiments\gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.jsonl`

## Summary

- Rows: 250
- Scored rows: 209
- Non-scored rows: 41
- Purist correct on scored rows: 188 (0.8995)
- Pragmatic correct on scored rows: 196 (0.9378)
- Exact normalized-label matches on scored rows: 159 (0.7608)

## Score Statuses

- `not_scored_null_rendered_label`: 41
- `scored`: 209

## Score Issues

- `rendered_label_null`: 41

## Non-Scored Rows

- First rows: 763, 854, 899, 1695, 1706, 1790, 2023, 2609, 2622, 2762, 2907, 2932, 2938, 2965, 2992, 3015, 3118, 3137, 3371, 3468, 3846, 3995, 4116, 4700, 4842
