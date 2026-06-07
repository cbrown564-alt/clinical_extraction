# Gan 2026 Reset ClinicalAssessment Pipeline

validation-development reset-stage composition only; no model calls, no locked-test inspection, no benchmark-comparable promotion claim, and score context remains audit-only

## Artifacts

- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.json`
- Projection/render JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.projection_render.jsonl`
- Score JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.score.jsonl`
- Route JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.route.jsonl`
- VerificationDecision JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.verification_decision.jsonl`

## Summary

- Input assessment rows: 450
- Projection rows: 449
- Rendered-label rows: 341
- Null rendered-label rows: 108
- Scored rows: 341
- Purist-correct scored rows: 271
- Routed rows: 41
- VerificationDecision rows: 41

## Verification Actions

- `abstain`: 41

## Source Artifacts

- Assessment artifact: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_test450_gpt41mini_v3nested_v3_2026-06-07.jsonl`
- CandidateSet artifact: `experiments\gan2026_test450_candidate_set_v3_nested_dedupe_context_v1_2026-06-07.jsonl`
