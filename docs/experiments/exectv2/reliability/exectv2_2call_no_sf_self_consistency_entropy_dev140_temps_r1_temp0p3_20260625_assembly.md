> **Superseded for navigation —** canonical summary: [`SELF_CONSISTENCY_RELIABILITY_CANON.md`](../../../canon/workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md). Full detail retained below.

# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `entropy_dev140_temps` / `entropy_dev140_temps140`
- Candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator_entropy_dev140_temps_r1_temp0p3`
- Gate decision: **self-consistency-repeat**
- Claim boundary: Self-consistency repeat for selected GPT-4.1-mini 2-call no-SF-adjudicator candidate. Structured ledger and Diagnosis decomposer are live repeat surfaces; SF/Rx/Inv and final assembly are no-call deterministic rebuilds.
- JSON: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_assembly.json`
- JSONL: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_assembly.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_diagnosis_decomposer.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `diagnosis_decomposer_direct` |
| SeizureFrequency | `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_sf_union_arbitration.jsonl` | `sf_state_union_arbitration_v08` | `single_gpt_structured_sf_direct+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_prescription_deterministic_repair_v03.jsonl` | `prescription_regimen_v01` | `deterministic_prescription_repair_v03` |
| Investigations | `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_structured.jsonl` | `investigations_result_v01` | `single_gpt_structured_direct_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7813 | 0.7791 | 0.6457 | 0.8895 | 0.8347 |
| evidence_valid | `evidence_valid_score` | 0.8095 | 0.8573 | 0.6457 | 0.8895 | 0.8347 |
| benchmark_cui | `cui_projection_companion` | 0.8095 | 0.8573 | 0.6457 | 0.8895 | 0.8347 |
| clinical_headline | `headline_target` | 0.8396 | 0.8573 | 0.7645 | 0.8895 | 0.8347 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7811 | 0.7787 | 0.6457 | 0.8895 | 0.8347 |
| `evidence_valid` | 0.7811 | 0.7787 | 0.6457 | 0.8895 | 0.8347 |
| `protocol_model_preserving_canonical` | 0.7811 | 0.7787 | 0.6457 | 0.8895 | 0.8347 |
| `dictionary_normalized` | 0.7982 | 0.8272 | 0.6457 | 0.8895 | 0.8347 |
| `residual_benchmark_added` | 0.8095 | 0.8573 | 0.6457 | 0.8895 | 0.8347 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 987 |
| `evidence_valid` | 0 | 987 |
| `protocol_model_preserving_canonical` | 0 | 987 |
| `dictionary_normalized` | 0 | 934 |
| `residual_benchmark_added` | 19 | 934 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4779 |
| Benchmark after CUI/projection | 0.4853 |
| Diagnosis.concept_negation | 0.8573 |
| SeizureFrequency.active_rate_fidelity | 0.5978 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0681; floor -0.0100 |
| Investigations control regression | fail | delta vs v0.42 control -0.0268; floor -0.0100 |
| Diagnosis headline | pass | 0.8573; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8573; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7645; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5978; baseline 0.2887 |
| Prescription changed-row control | fail | 131 changed rows |
| Investigations changed-row control | pass | 0 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 0 | 0 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 0 | 0 | 0 | 1.0000 |
| Investigations | 0 | 0 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 112 | assertion_or_negation_change=79, hierarchy_reconciliation_or_duplicate_collapse=79, hierarchy_reconciliation=33 |
| versus_v042_default_quarantine | SeizureFrequency | 80 | active_rate=59, unknown_or_change_state=29, seizure_free=48, generic_vs_specific=4, projection_action=15, reject_or_drop=2 |
| versus_v042_default_quarantine | Prescription | 131 | model_output=131 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
