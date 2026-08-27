# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `dev140` / `dev140140`
- Candidate: `exectv2_six_model_single_call_gemma4_26b_dev140`
- Gate decision: **same-core-model-swap-dev140-readout**
- Claim boundary: ExECTv2 dev140 single-call development comparison only.
- JSON: `experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715.json`
- JSONL: `experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `named_model_structured_diagnosis_plus_rules` |
| SeizureFrequency | `experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715_sf_unknown_suppression.jsonl` | `sf_state_projection_suppression_v01` | `named_model_sf_plus_projection_suppression` |
| Prescription | `experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl` | `prescription_dictionary_v09` | `named_model_prescription_plus_shared_rules` |
| Investigations | `experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl` | `investigations_result_v01` | `named_model_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7010 | 0.6982 | 0.4364 | 0.8878 | 0.8047 |
| evidence_valid | `evidence_valid_score` | 0.7645 | 0.8378 | 0.4607 | 0.9046 | 0.8047 |
| benchmark_cui | `cui_projection_companion` | 0.7645 | 0.8378 | 0.4607 | 0.9046 | 0.8047 |
| clinical_headline | `headline_target` | 0.8016 | 0.8378 | 0.6226 | 0.9046 | 0.8047 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7095 | 0.6982 | 0.4607 | 0.8878 | 0.8047 |
| `evidence_valid` | 0.7095 | 0.6982 | 0.4607 | 0.8878 | 0.8047 |
| `protocol_model_preserving_canonical` | 0.7095 | 0.6982 | 0.4607 | 0.8878 | 0.8047 |
| `dictionary_normalized` | 0.7404 | 0.7883 | 0.4607 | 0.8978 | 0.8047 |
| `residual_benchmark_added` | 0.7645 | 0.8378 | 0.4607 | 0.9046 | 0.8047 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 944 |
| `evidence_valid` | 0 | 944 |
| `protocol_model_preserving_canonical` | 0 | 944 |
| `dictionary_normalized` | 0 | 876 |
| `residual_benchmark_added` | 98 | 876 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3480 |
| Benchmark after CUI/projection | 0.4088 |
| Diagnosis.concept_negation | 0.8231 |
| SeizureFrequency.active_rate_fidelity | 0.3053 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0832; floor -0.0100 |
| Investigations control regression | fail | delta vs v0.42 control -0.0568; floor -0.0100 |
| Diagnosis headline | pass | 0.8378; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8231; baseline 0.6693 |
| SeizureFrequency headline | fail | 0.6226; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.3053; baseline 0.2887 |
| Prescription changed-row control | fail | 63 changed rows |
| Investigations changed-row control | pass | 0 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 2 | 0 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 0 | 2 | 0 | 1.0000 |
| Investigations | 0 | 2 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 94 | assertion_or_negation_change=72, hierarchy_reconciliation_or_duplicate_collapse=67, hierarchy_reconciliation=20, projection_only=2 |
| versus_v042_default_quarantine | SeizureFrequency | 19 | active_rate=15, projection_action=17, seizure_free=8, unknown_or_change_state=5, reject_or_drop=3, unknown=2, generic_vs_specific=2 |
| versus_v042_default_quarantine | Prescription | 63 | model_output=63 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `exectv2_decision_0041_six_model_single_call_dev140_v1`
- Model: `Gemma 4 26B` (`ollama_chat/gemma4:26b`)
- Runtime: `ollama_native_chat_think_false`
- Prompt profile: `full`
- Calls per letter: `1.0`
- Live call components: `structured_key_family_event_ledger`
- Replayed/no-call components: `sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, prescription_dictionary_lens, finding_assembly`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
