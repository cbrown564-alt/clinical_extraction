# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-07-03`
- Split/stage: `full_200_authorized` / `full_200_authorized200`
- Candidate: `exectv2_v08_full200_rx_llm_tuned_treatment`
- Gate decision: **do-not-promote**
- Claim boundary: LLM-vs-deterministic Rx comparator treatment: v08 full200 manifest with ONLY prescription_repair_v03 swapped for the LLM-tuned extractor (canonical GEPA + probe #2 current-vs-future + probe #3 AED-only with emit-if-unsure safety clause). Every other producer is the unchanged archived artifact.
- JSON: `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_v08_full200_rx_llm_tuned_treatment_20260703.json`
- JSONL: `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_v08_full200_rx_llm_tuned_treatment_20260703.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_v08_full200_currentcode_diagnosis_reconciler_gpt41mini_20260624.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `hybrid_diagnosis_route` |
| SeizureFrequency | `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_v08_full200_currentcode_sf_union_arbitration_20260624.jsonl` | `sf_state_union_arbitration_v08` | `hybrid_sf_route+deterministic_union_arbitration` |
| Prescription | `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_llm_rx_tuned_extractor_full200_20260703.jsonl` | `prescription_regimen_v01` | `deterministic_prescription_repair_v03` |
| Investigations | `C:/Users/cbrow/Code/clinical_extraction/experiments/exectv2_v08_full200_currentcode_investigations_arbitration_20260624.jsonl` | `investigations_result_v01` | `llm_investigations_verifier+deterministic_investigations_arbitration` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.8165 | 0.7818 | 0.6592 | 0.9492 | 0.9213 |
| evidence_valid | `evidence_valid_score` | 0.8431 | 0.8546 | 0.6592 | 0.9492 | 0.9213 |
| benchmark_cui | `cui_projection_companion` | 0.8431 | 0.8546 | 0.6592 | 0.9492 | 0.9213 |
| clinical_headline | `headline_target` | 0.8730 | 0.8546 | 0.7842 | 0.9492 | 0.9213 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.8165 | 0.7818 | 0.6592 | 0.9492 | 0.9213 |
| `evidence_valid` | 0.8165 | 0.7818 | 0.6592 | 0.9492 | 0.9213 |
| `protocol_model_preserving_canonical` | 0.8165 | 0.7818 | 0.6592 | 0.9492 | 0.9213 |
| `dictionary_normalized` | 0.8378 | 0.8406 | 0.6592 | 0.9492 | 0.9213 |
| `residual_benchmark_added` | 0.8431 | 0.8546 | 0.6592 | 0.9492 | 0.9213 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 1437 |
| `evidence_valid` | 0 | 1437 |
| `protocol_model_preserving_canonical` | 0 | 1437 |
| `dictionary_normalized` | 0 | 1367 |
| `residual_benchmark_added` | 64 | 1367 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3952 |
| Benchmark after CUI/projection | 0.4178 |
| Diagnosis.concept_negation | 0.8360 |
| SeizureFrequency.active_rate_fidelity | 0.5502 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1278; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0598; floor -0.0100 |
| Diagnosis headline | pass | 0.8546; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8360; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7842; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5502; baseline 0.2887 |
| Prescription changed-row control | fail | 191 changed rows |
| Investigations changed-row control | fail | 59 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 0 | 1 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 0 | 0 | 0 | 1.0000 |
| Investigations | 0 | 0 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 179 | assertion_or_negation_change=120, hierarchy_reconciliation_or_duplicate_collapse=120, hierarchy_reconciliation=58, projection_only=2 |
| versus_v042_default_quarantine | SeizureFrequency | 140 | active_rate=106, seizure_free=73, unknown_or_change_state=43, projection_action=32, generic_vs_specific=5, reject_or_drop=7 |
| versus_v042_default_quarantine | Prescription | 191 | model_output=191 |
| versus_v042_default_quarantine | Investigations | 59 | model_output=59 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
