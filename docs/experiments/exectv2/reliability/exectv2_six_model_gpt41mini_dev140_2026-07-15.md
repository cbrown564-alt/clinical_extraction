# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `dev140` / `dev140140`
- Candidate: `exectv2_six_model_gpt41mini_dev140`
- Gate decision: **same-core-model-swap-dev140-readout**
- Claim boundary: ExECTv2 dev140 development comparison only.
- JSON: `experiments/exectv2_six_model_gpt41mini_dev140_20260715.json`
- JSONL: `experiments/exectv2_six_model_gpt41mini_dev140_20260715.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_six_model_gpt41mini_dev140_20260715_diagnosis_decomposer.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `named_model_diagnosis_plus_rules` |
| SeizureFrequency | `experiments/exectv2_six_model_gpt41mini_dev140_20260715_sf_unknown_suppression.jsonl` | `sf_state_projection_suppression_v01` | `named_model_sf_plus_projection_suppression` |
| Prescription | `experiments/exectv2_six_model_gpt41mini_dev140_20260715_structured.jsonl` | `prescription_dictionary_v09` | `named_model_prescription_plus_shared_rules` |
| Investigations | `experiments/exectv2_six_model_gpt41mini_dev140_20260715_structured.jsonl` | `investigations_result_v01` | `named_model_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7491 | 0.7979 | 0.4824 | 0.8501 | 0.8755 |
| evidence_valid | `evidence_valid_score` | 0.7885 | 0.8673 | 0.5114 | 0.8665 | 0.8755 |
| benchmark_cui | `cui_projection_companion` | 0.7885 | 0.8673 | 0.5114 | 0.8665 | 0.8755 |
| clinical_headline | `headline_target` | 0.8195 | 0.8673 | 0.6453 | 0.8665 | 0.8755 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7579 | 0.7962 | 0.5114 | 0.8501 | 0.8755 |
| `evidence_valid` | 0.7579 | 0.7962 | 0.5114 | 0.8501 | 0.8755 |
| `protocol_model_preserving_canonical` | 0.7579 | 0.7962 | 0.5114 | 0.8501 | 0.8755 |
| `dictionary_normalized` | 0.7834 | 0.8634 | 0.5114 | 0.8615 | 0.8755 |
| `residual_benchmark_added` | 0.7885 | 0.8673 | 0.5114 | 0.8665 | 0.8755 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 1030 |
| `evidence_valid` | 0 | 1030 |
| `protocol_model_preserving_canonical` | 0 | 1030 |
| `dictionary_normalized` | 0 | 933 |
| `residual_benchmark_added` | 53 | 933 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3952 |
| Benchmark after CUI/projection | 0.4214 |
| Diagnosis.concept_negation | 0.8435 |
| SeizureFrequency.active_rate_fidelity | 0.4444 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0451; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0140; floor -0.0100 |
| Diagnosis headline | pass | 0.8673; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8435; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.6453; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.4444; baseline 0.2887 |
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
| versus_v042_default_quarantine | Diagnosis | 117 | assertion_or_negation_change=82, hierarchy_reconciliation_or_duplicate_collapse=82, hierarchy_reconciliation=34, projection_only=1 |
| versus_v042_default_quarantine | SeizureFrequency | 20 | active_rate=17, projection_action=17, unknown_or_change_state=3, reject_or_drop=3, seizure_free=8, generic_vs_specific=1 |
| versus_v042_default_quarantine | Prescription | 76 | model_output=76 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `exectv2_decision_0040_six_model_dev140_v1`
- Model: `GPT-4.1-mini` (`openai/gpt-4.1-mini`)
- Runtime: `openai_chat`
- Prompt profile: `full`
- Calls per letter: `2.0`
- Live call components: `structured_key_family_event_ledger, diagnosis_decomposer`
- Replayed/no-call components: `sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, prescription_dictionary_lens, finding_assembly`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
