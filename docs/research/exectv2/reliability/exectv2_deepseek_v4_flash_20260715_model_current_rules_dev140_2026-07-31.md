# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-07-31`
- Split/stage: `dev140` / `dev140140`
- Candidate: `exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140`
- Gate decision: **same-core-model-swap-dev140-readout**
- Claim boundary: Current-rules no-call replay of 2026-07-15 DeepSeek structured outputs only.
- JSON: `experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731.json`
- JSONL: `experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_six_model_single_call_deepseek_v4_flash_dev140_20260715_structured.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `named_model_structured_diagnosis_plus_rules` |
| SeizureFrequency | `experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731_sf_unknown_suppression.jsonl` | `sf_state_projection_suppression_v01` | `named_model_sf_plus_projection_suppression` |
| Prescription | `experiments/exectv2_six_model_single_call_deepseek_v4_flash_dev140_20260715_structured.jsonl` | `prescription_dictionary_v09` | `named_model_prescription_plus_shared_rules` |
| Investigations | `experiments/exectv2_six_model_single_call_deepseek_v4_flash_dev140_20260715_structured.jsonl` | `investigations_result_v01` | `named_model_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7915 | 0.7432 | 0.5818 | 0.9380 | 0.9389 |
| evidence_valid | `evidence_valid_score` | 0.8444 | 0.8764 | 0.6025 | 0.9280 | 0.9389 |
| benchmark_cui | `cui_projection_companion` | 0.8444 | 0.8764 | 0.6025 | 0.9280 | 0.9389 |
| clinical_headline | `headline_target` | 0.8767 | 0.8764 | 0.7610 | 0.9280 | 0.9389 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7967 | 0.7432 | 0.6025 | 0.9380 | 0.9389 |
| `evidence_valid` | 0.7967 | 0.7432 | 0.6025 | 0.9380 | 0.9389 |
| `protocol_model_preserving_canonical` | 0.7967 | 0.7432 | 0.6025 | 0.9380 | 0.9389 |
| `dictionary_normalized` | 0.8308 | 0.8420 | 0.6025 | 0.9293 | 0.9389 |
| `residual_benchmark_added` | 0.8444 | 0.8764 | 0.6025 | 0.9280 | 0.9389 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 819 |
| `evidence_valid` | 0 | 819 |
| `protocol_model_preserving_canonical` | 0 | 819 |
| `dictionary_normalized` | 0 | 783 |
| `residual_benchmark_added` | 68 | 783 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4527 |
| Benchmark after CUI/projection | 0.5020 |
| Diagnosis.concept_negation | 0.8731 |
| SeizureFrequency.active_rate_fidelity | 0.6023 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1066; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0774; floor -0.0100 |
| Diagnosis headline | pass | 0.8764; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8731; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7610; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.6023; baseline 0.2887 |
| Prescription changed-row control | fail | 52 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 88 | hierarchy_reconciliation=29, assertion_or_negation_change=58, hierarchy_reconciliation_or_duplicate_collapse=58, projection_only=1 |
| versus_v042_default_quarantine | SeizureFrequency | 10 | active_rate=8, projection_action=9, seizure_free=3, unknown_or_change_state=2, reject_or_drop=1 |
| versus_v042_default_quarantine | Prescription | 52 | model_output=52 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `exectv2_decision_0041_six_model_single_call_dev140_v1`
- Model: `DeepSeek V4 Flash 2026-07-15 model / current rules` (`deepseek/deepseek-v4-flash`)
- Runtime: `no_call_replay_20260715_structured_through_current_rules`
- Prompt profile: `full`
- Calls per letter: `0.0`
- Live call components: ``
- Replayed/no-call components: `structured_key_family_event_ledger, sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, prescription_dictionary_lens, finding_assembly`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
