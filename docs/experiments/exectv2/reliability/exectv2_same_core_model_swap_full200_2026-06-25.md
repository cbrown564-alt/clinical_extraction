# ExECTv2 Same-Core Model-Swap Full-200 Aggregate Validation

- Generated: `2026-06-25`
- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Primary score: `clinical_headline`
- Row inspection policy: `aggregate_only_no_full200_or_holdout_row_level_inspection`
- Overall status: **ready_for_same_core_scorecard_review**
- Claim boundary: Full-200 aggregate-only same-core validation is complete and accepted with an explicit schema-stability caveat: one Diagnosis parse/schema failure is tolerated, strict benchmark/CUI scores are diagnostic only, and no full-200 row-level failure analysis or tuning is authorized.
- Predeclaration: `docs/experiments/exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`

Historical evidence note: `deepseek/deepseek-chat` is the API identifier for
DeepSeek V4 Flash, but this run has incomplete runtime metadata. Its score
remains reproducible audit evidence but is not eligible as the final paper
result for DeepSeek. The final table uses the display name **DeepSeek V4 Flash**.

## Model Rows

| Candidate | Model | Status | Overall | Dx | SF | Presc | Inv | Call failures | Parse/schema failures | Min evidence rate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | GPT-4.1-mini | complete | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 | 0 | 0 | 1.0000 |
| `exectv2_2call_no_sf_adjudicator_deepseek_full200` | DeepSeek V4 Flash API run (incomplete runtime metadata) | complete | 0.8566 | 0.8708 | 0.7602 | 0.8926 | 0.9091 | 0 | 1 | 1.0000 |

## Readiness Gates

| Gate | Status | Detail |
| --- | --- | --- |
| architecture_parity | pass | All configs share the frozen component graph. |
| attribution_clarity | pass | Configs separate model-generated structured/Diagnosis outputs from deterministic SF projection and Prescription repair. |
| evidence_validity | pass | Completed rows minimum exact evidence rate is 1.0000; 0 model row(s) still pending. |
| operational_stability | pass_with_caveat | Completed rows call failures=0, parse/schema failures=1; 0 model row(s) still pending. Full-200 tolerance allows up to 1 parse/schema failure with zero call failures. |
| family_parity | pass | Per-family clinical-headline metrics are available for every model. |
| claim_boundary | pass | This artifact is aggregate-only and does not inspect full-200 or holdout row-level failures. |

## Historical Diagnostic Boundary

Retain as historical diagnostics/path evidence only. Do not use them as final same-core model swaps.

- `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`
- `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140`
- `exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140`
- `exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_dev140`

## Next Actions

- Record the same-core full-200 aggregate-only comparison as accepted with a schema-stability caveat.
- Move registry-driven run surfacing to the active work item.
