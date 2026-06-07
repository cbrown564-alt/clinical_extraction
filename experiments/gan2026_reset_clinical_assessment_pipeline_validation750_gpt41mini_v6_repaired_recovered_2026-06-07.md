# Gan 2026 Reset ClinicalAssessment Pipeline

validation-development reset-stage composition only; no model calls, no locked-test inspection, no benchmark-comparable promotion claim, and score context remains audit-only

## Artifacts

- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.json`
- Projection/render JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.projection_render.jsonl`
- Score JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.score.jsonl`
- Route JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.route.jsonl`
- VerificationDecision JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.verification_decision.jsonl`

## Summary

- Input assessment rows: 750
- Projection rows: 750
- Rendered-label rows: 580
- Null rendered-label rows: 170
- Scored rows: 580
- Purist-correct scored rows: 504
- Routed rows: 73
- VerificationDecision rows: 73

## Verification Actions

- `abstain`: 73

## Source Artifacts

- Assessment artifact: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`
- CandidateSet artifact: `experiments\gan2026_validation750_candidate_set_v3_nested_dedupe_context_v1_2026-06-06.jsonl`
