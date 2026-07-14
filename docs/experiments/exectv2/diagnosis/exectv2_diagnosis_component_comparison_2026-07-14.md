# ExECTv2 Diagnosis component comparison

Date: 2026-07-14  
Status: dev140 development evidence; do not promote

Machine-readable result: `experiments/exectv2_diagnosis_component_comparison_dev140_20260714.json`

## Answer

The completed review separates a large representation effect from a smaller extraction problem. Shared deterministic fixes improve rules-only and hybrid Diagnosis recovery on dev140. The fixed LLM-only prompt candidate regresses, so the retained v08 reference remains the control.

## Score layers

| Architecture | Fixed baseline | Conservative sensitivity | Reviewed interpretation | Candidate fixed F1 | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| rules_only | 0.8599 | 0.9344 | 0.9520 | 0.8926 | +0.0327 |
| llm_only | 0.6861 | 0.8499 | 0.9056 | 0.6210 | -0.0652 |
| llm_with_rules | 0.8984 | 0.9789 | 0.9950 | 0.9034 | +0.0051 |

## Component attribution

| Component | F1 before | F1 after | Delta |
| --- | ---: | ---: | ---: |
| Rules: clinical context and surface handling | 0.8599 | 0.8926 | +0.0327 |
| Rules: residual dictionary marginal | 0.8926 | 0.8985 | +0.0059 |
| Hybrid: shared deterministic dictionary | 0.8984 | 0.9034 | +0.0051 |
| LLM-only: prompt v0.2 | 0.6861 | 0.6210 | -0.0652 |

## Reviewed-row effects

| Candidate | Resolved review rows | Extraction errors resolved | New residuals |
| --- | ---: | ---: | ---: |
| rules_boundary_only | 21 | 17 | 1 |
| rules_full | 48 | 24 | 30 |
| llm_only_v02 | 102 | 40 | 116 |
| llm_with_rules_full | 3 | 3 | 0 |

## Decision

- Keep v08 as the retained reference.
- Keep the rules boundary and hybrid fixes as development candidates only.
- Reject the broad rules residual dictionary as a default because it adds 30 new residuals.
- Reject the LLM-only v0.2 candidate because its fixed primary score regressed.
- Do not inspect test60 or promote any candidate from this dev140 study.
