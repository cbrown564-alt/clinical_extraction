# ExECTv2 Same-Core Model-Swap Dev140 Readiness

- Generated: `2026-06-25`
- Architecture core: `same_core_test`
- Primary surface: `clinical_headline`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
- Overall status: **pending_same_core_model_runs**
- Claim boundary: Development same-core model-swap readiness. Final cross-model scorecard comparison is blocked until GPT-4.1-mini, DeepSeek, and Qwen all have rows on the frozen core.

## Model Rows

| Candidate | Model | Status | Overall | Dx | SF | Presc | Inv | Call failures | Parse/schema failures | Min evidence rate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `swap_gpt` | GPT-4.1-mini | complete | 0.7500 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 0 | 0 | 1.0000 |
| `swap_deepseek` | DeepSeek chat | pending_source_artifacts | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

## Readiness Gates

| Gate | Status | Detail |
| --- | --- | --- |
| architecture_parity | pass | All configs share the frozen component graph. |
| attribution_clarity | pass | Configs separate model-generated structured/Diagnosis outputs from deterministic SF projection and Prescription repair. |
| evidence_validity | pending | Completed rows minimum exact evidence rate is 1.0000; 1 model row(s) still pending. |
| operational_stability | pending | Completed rows call failures=0, parse/schema failures=0; 1 model row(s) still pending. |
| family_parity | pending | Per-family comparison waits for all same-core model rows. |
| claim_boundary | pass | This artifact is dev140-only and does not inspect full-200 or holdout row-level failures. |

## Historical Diagnostic Boundary

Retain as historical diagnostics/path evidence only. Do not use them as final same-core model swaps.

- `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`
- `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140`
- `exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140`
- `exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_dev140`

## Next Actions

- Run or replay `swap_deepseek` using the frozen config at `C:/Users/cbrow/Code/clinical_extraction/.status-pytest-temp-20260718b/test_model_swap_readiness_mark0/swap_deepseek.json`.
