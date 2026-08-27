# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `dev140` / `dev140140`
- Candidate: `exectv2_six_model_single_call_gpt41mini_dev140`
- Gate decision: **same-core-model-swap-dev140-readout**
- Claim boundary: ExECTv2 dev140 single-call development comparison only.
- JSON: `experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715.json`
- JSONL: `experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715_structured.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `named_model_structured_diagnosis_plus_rules` |
| SeizureFrequency | `experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715_sf_unknown_suppression.jsonl` | `sf_state_projection_suppression_v01` | `named_model_sf_plus_projection_suppression` |
| Prescription | `experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715_structured.jsonl` | `prescription_dictionary_v09` | `named_model_prescription_plus_shared_rules` |
| Investigations | `experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715_structured.jsonl` | `investigations_result_v01` | `named_model_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7128 | 0.6864 | 0.4986 | 0.8530 | 0.8538 |
| evidence_valid | `evidence_valid_score` | 0.7849 | 0.8470 | 0.5341 | 0.8672 | 0.8538 |
| benchmark_cui | `cui_projection_companion` | 0.7849 | 0.8470 | 0.5341 | 0.8672 | 0.8538 |
| clinical_headline | `headline_target` | 0.8202 | 0.8470 | 0.6936 | 0.8672 | 0.8538 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7228 | 0.6864 | 0.5341 | 0.8530 | 0.8538 |
| `evidence_valid` | 0.7228 | 0.6864 | 0.5341 | 0.8530 | 0.8538 |
| `protocol_model_preserving_canonical` | 0.7228 | 0.6864 | 0.5341 | 0.8530 | 0.8538 |
| `dictionary_normalized` | 0.7662 | 0.8036 | 0.5341 | 0.8651 | 0.8538 |
| `residual_benchmark_added` | 0.7849 | 0.8470 | 0.5341 | 0.8672 | 0.8538 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 950 |
| `evidence_valid` | 0 | 950 |
| `protocol_model_preserving_canonical` | 0 | 950 |
| `dictionary_normalized` | 0 | 856 |
| `residual_benchmark_added` | 76 | 856 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3859 |
| Benchmark after CUI/projection | 0.4373 |
| Diagnosis.concept_negation | 0.8337 |
| SeizureFrequency.active_rate_fidelity | 0.4199 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0458; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control -0.0077; floor -0.0100 |
| Diagnosis headline | pass | 0.8470; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8337; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.6936; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.4199; baseline 0.2887 |
| Prescription changed-row control | fail | 76 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 98 | assertion_or_negation_change=66, hierarchy_reconciliation_or_duplicate_collapse=65, hierarchy_reconciliation=29, projection_only=3 |
| versus_v042_default_quarantine | SeizureFrequency | 20 | active_rate=17, seizure_free=10, projection_action=18, unknown_or_change_state=3, reject_or_drop=2, generic_vs_specific=1 |
| versus_v042_default_quarantine | Prescription | 76 | model_output=76 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `exectv2_decision_0041_six_model_single_call_dev140_v1`
- Model: `GPT-4.1-mini` (`openai/gpt-4.1-mini`)
- Runtime: `openai_chat`
- Prompt profile: `full`
- Calls per letter: `1.0`
- Live call components: `structured_key_family_event_ledger`
- Replayed/no-call components: `sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, prescription_dictionary_lens, finding_assembly`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
