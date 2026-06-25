# ExECTv2 Same-Core Model-Swap Dev140 Readiness

- Generated: `2026-06-25`
- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Primary surface: `clinical_headline`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
- Overall status: **blocked_architecture_or_operational_gate**
- Claim boundary: Development same-core model-swap rows are complete on the frozen core, but operational stability is not promoted because at least one row has call or parse/schema failures. Use the dev140 scores with this caveat; do not advance to full-200 without a fresh aggregate-only predeclaration.

## Model Rows

| Candidate | Model | Status | Overall | Dx | SF | Presc | Inv | Call failures | Parse/schema failures | Min evidence rate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `exectv2_2call_no_sf_adjudicator_deepseek_dev140` | DeepSeek chat | complete | 0.8596 | 0.8845 | 0.7658 | 0.8895 | 0.8966 | 0 | 1 | 1.0000 |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` | GPT-4.1-mini | complete | 0.8396 | 0.8573 | 0.7645 | 0.8895 | 0.8347 | 0 | 0 | 1.0000 |
| `exectv2_2call_no_sf_adjudicator_qwen36_dev140` | Qwen 3.6 35B | complete | 0.8018 | 0.8027 | 0.6919 | 0.8895 | 0.8354 | 1 | 12 | 1.0000 |

## Readiness Gates

| Gate | Status | Detail |
| --- | --- | --- |
| architecture_parity | pass | All configs share the frozen component graph. |
| attribution_clarity | pass | Configs separate model-generated structured/Diagnosis outputs from deterministic SF projection and Prescription repair. |
| evidence_validity | pass | Completed rows minimum exact evidence rate is 1.0000; 0 model row(s) still pending. |
| operational_stability | fail | Completed rows call failures=1, parse/schema failures=13; 0 model row(s) still pending. |
| family_parity | pass | Per-family clinical-headline metrics are available for every model. |
| claim_boundary | pass | This artifact is dev140-only and does not inspect full-200 or holdout row-level failures. |

## Historical Diagnostic Boundary

Retain as historical diagnostics/path evidence only. Do not use them as final same-core model swaps.

- `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`
- `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140`
- `exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140`
- `exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_dev140`

## Next Actions

- Record the completed dev140 same-core comparison with an operational-stability caveat.
- Review Qwen call/parse failures before any full-200 aggregate-only predeclaration.
