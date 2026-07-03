# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-07-03`
- Split/stage: `dev140` / `dev140140`
- Candidate: `exectv2_v08_dev140_inv_llm_tuned_treatment_20260703`
- Gate decision: **do-not-promote**
- Claim boundary: Dev-only component-attributed architecture evidence. This artifact does not authorize a benchmark claim, full-200 audit, or locked-test analysis.
- JSON: `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_v08_dev140_inv_llm_tuned_treatment_20260703.json`
- JSONL: `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_v08_dev140_inv_llm_tuned_treatment_20260703.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `hybrid_diagnosis_route` |
| SeizureFrequency | `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl` | `sf_state_union_arbitration_v08` | `hybrid_sf_route+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_deterministic_prescription_repair_v03_dev140_20260621.jsonl` | `prescription_regimen_v01` | `deterministic_prescription_repair_v03` |
| Investigations | `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_llm_inv_tuned_extractor_dev140_20260703.jsonl` | `investigations_result_v01` | `llm_investigations_verifier+deterministic_investigations_arbitration` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.8380 | 0.7790 | 0.7836 | 0.9386 | 0.8949 |
| evidence_valid | `evidence_valid_score` | 0.8823 | 0.8984 | 0.7836 | 0.9386 | 0.8949 |
| benchmark_cui | `cui_projection_companion` | 0.8823 | 0.8984 | 0.7836 | 0.9386 | 0.8949 |
| clinical_headline | `headline_target` | 0.9100 | 0.8984 | 0.9080 | 0.9386 | 0.8949 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.8373 | 0.7770 | 0.7836 | 0.9386 | 0.8949 |
| `evidence_valid` | 0.8373 | 0.7770 | 0.7836 | 0.9386 | 0.8949 |
| `protocol_model_preserving_canonical` | 0.8373 | 0.7770 | 0.7836 | 0.9386 | 0.8949 |
| `dictionary_normalized` | 0.8736 | 0.8755 | 0.7836 | 0.9386 | 0.8949 |
| `residual_benchmark_added` | 0.8823 | 0.8984 | 0.7836 | 0.9386 | 0.8949 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 1028 |
| `evidence_valid` | 0 | 1028 |
| `protocol_model_preserving_canonical` | 0 | 1028 |
| `dictionary_normalized` | 0 | 962 |
| `residual_benchmark_added` | 45 | 962 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3679 |
| Benchmark after CUI/projection | 0.4863 |
| Diagnosis.concept_negation | 0.8853 |
| SeizureFrequency.active_rate_fidelity | 0.5907 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1172; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0334; floor -0.0100 |
| Diagnosis headline | pass | 0.8984; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8853; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.9080; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5907; baseline 0.2887 |
| Prescription changed-row control | fail | 96 changed rows |
| Investigations changed-row control | fail | 70 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 0 | 2 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 0 | 0 | 0 | 1.0000 |
| Investigations | 0 | 0 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 130 | assertion_or_negation_change=95, hierarchy_reconciliation_or_duplicate_collapse=94, hierarchy_reconciliation=34, projection_only=1 |
| versus_v042_default_quarantine | SeizureFrequency | 112 | active_rate=86, seizure_free=54, projection_action=30, unknown_or_change_state=31, reject_or_drop=9, unknown=5, generic_vs_specific=1 |
| versus_v042_default_quarantine | Prescription | 96 | model_output=96 |
| versus_v042_default_quarantine | Investigations | 70 | model_output=70 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
