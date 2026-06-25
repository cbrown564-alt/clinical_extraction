# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `entropy_dev140_temps` / `entropy_dev140_temps140`
- Candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator_entropy_dev140_temps_r2_temp0p5`
- Gate decision: **do-not-promote**
- Claim boundary: Self-consistency repeat for selected GPT-4.1-mini 2-call no-SF-adjudicator candidate. Structured ledger and Diagnosis decomposer are live repeat surfaces; SF/Rx/Inv and final assembly are no-call deterministic rebuilds.
- JSON: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_assembly.json`
- JSONL: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_assembly.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_diagnosis_decomposer.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `diagnosis_decomposer_direct` |
| SeizureFrequency | `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_sf_union_arbitration.jsonl` | `sf_state_union_arbitration_v08` | `single_gpt_structured_sf_direct+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_prescription_deterministic_repair_v03.jsonl` | `prescription_regimen_v01` | `deterministic_prescription_repair_v03` |
| Investigations | `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_structured.jsonl` | `investigations_result_v01` | `single_gpt_structured_direct_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7850 | 0.7817 | 0.6472 | 0.8895 | 0.8487 |
| evidence_valid | `evidence_valid_score` | 0.8123 | 0.8561 | 0.6472 | 0.8895 | 0.8487 |
| benchmark_cui | `cui_projection_companion` | 0.8123 | 0.8561 | 0.6472 | 0.8895 | 0.8487 |
| clinical_headline | `headline_target` | 0.8419 | 0.8561 | 0.7654 | 0.8895 | 0.8487 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7850 | 0.7817 | 0.6472 | 0.8895 | 0.8487 |
| `evidence_valid` | 0.7850 | 0.7817 | 0.6472 | 0.8895 | 0.8487 |
| `protocol_model_preserving_canonical` | 0.7850 | 0.7817 | 0.6472 | 0.8895 | 0.8487 |
| `dictionary_normalized` | 0.8010 | 0.8264 | 0.6472 | 0.8895 | 0.8487 |
| `residual_benchmark_added` | 0.8123 | 0.8561 | 0.6472 | 0.8895 | 0.8487 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 984 |
| `evidence_valid` | 0 | 984 |
| `protocol_model_preserving_canonical` | 0 | 984 |
| `dictionary_normalized` | 0 | 942 |
| `residual_benchmark_added` | 19 | 942 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4811 |
| Benchmark after CUI/projection | 0.4886 |
| Diagnosis.concept_negation | 0.8561 |
| SeizureFrequency.active_rate_fidelity | 0.5745 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0681; floor -0.0100 |
| Investigations control regression | fail | delta vs v0.42 control -0.0128; floor -0.0100 |
| Diagnosis headline | pass | 0.8561; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8561; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7654; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5745; baseline 0.2887 |
| Prescription changed-row control | fail | 133 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 112 | hierarchy_reconciliation=37, assertion_or_negation_change=75, hierarchy_reconciliation_or_duplicate_collapse=75 |
| versus_v042_default_quarantine | SeizureFrequency | 83 | active_rate=63, seizure_free=48, unknown_or_change_state=27, projection_action=17, reject_or_drop=2, generic_vs_specific=2, unknown=1 |
| versus_v042_default_quarantine | Prescription | 133 | model_output=133 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
