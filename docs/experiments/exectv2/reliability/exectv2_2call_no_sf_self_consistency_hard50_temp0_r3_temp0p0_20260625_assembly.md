# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `hard50_temp0` / `hard50_temp050`
- Candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator_hard50_temp0_r3_temp0p0`
- Gate decision: **self-consistency-repeat**
- Claim boundary: Self-consistency repeat for selected GPT-4.1-mini 2-call no-SF-adjudicator candidate. Structured ledger and Diagnosis decomposer are live repeat surfaces; SF/Rx/Inv and final assembly are no-call deterministic rebuilds.
- JSON: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_assembly.json`
- JSONL: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_assembly.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_diagnosis_decomposer.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `diagnosis_decomposer_direct` |
| SeizureFrequency | `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_sf_union_arbitration.jsonl` | `sf_state_union_arbitration_v08` | `single_gpt_structured_sf_direct+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_prescription_deterministic_repair_v03.jsonl` | `prescription_regimen_v01` | `deterministic_prescription_repair_v03` |
| Investigations | `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_structured.jsonl` | `investigations_result_v01` | `single_gpt_structured_direct_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.8557 | 0.8266 | 0.7636 | 0.9250 | 0.9053 |
| evidence_valid | `evidence_valid_score` | 0.8722 | 0.8740 | 0.7636 | 0.9250 | 0.9053 |
| benchmark_cui | `cui_projection_companion` | 0.8722 | 0.8740 | 0.7636 | 0.9250 | 0.9053 |
| clinical_headline | `headline_target` | 0.8838 | 0.8740 | 0.8190 | 0.9250 | 0.9053 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.8557 | 0.8266 | 0.7636 | 0.9250 | 0.9053 |
| `evidence_valid` | 0.8557 | 0.8266 | 0.7636 | 0.9250 | 0.9053 |
| `protocol_model_preserving_canonical` | 0.8557 | 0.8266 | 0.7636 | 0.9250 | 0.9053 |
| `dictionary_normalized` | 0.8718 | 0.8728 | 0.7636 | 0.9250 | 0.9053 |
| `residual_benchmark_added` | 0.8722 | 0.8740 | 0.7636 | 0.9250 | 0.9053 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 357 |
| `evidence_valid` | 0 | 357 |
| `protocol_model_preserving_canonical` | 0 | 357 |
| `dictionary_normalized` | 0 | 339 |
| `residual_benchmark_added` | 2 | 339 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.5335 |
| Benchmark after CUI/projection | 0.5365 |
| Diagnosis.concept_negation | 0.8740 |
| SeizureFrequency.active_rate_fidelity | 0.6984 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1036; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0438; floor -0.0100 |
| Diagnosis headline | pass | 0.8740; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8740; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.8190; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.6984; baseline 0.2887 |
| Prescription changed-row control | fail | 48 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 39 | hierarchy_reconciliation=14, assertion_or_negation_change=25, hierarchy_reconciliation_or_duplicate_collapse=25 |
| versus_v042_default_quarantine | SeizureFrequency | 28 | active_rate=21, unknown_or_change_state=8, seizure_free=10, generic_vs_specific=1, projection_action=3, reject_or_drop=1 |
| versus_v042_default_quarantine | Prescription | 48 | model_output=48 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
