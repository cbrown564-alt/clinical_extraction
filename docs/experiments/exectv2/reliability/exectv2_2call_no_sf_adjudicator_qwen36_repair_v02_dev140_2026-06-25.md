# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `dev140` / `dev140140`
- Candidate: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140`
- Gate decision: **same-core-model-swap-dev140-readout**
- Claim boundary: Dev140 same-core Qwen 3.6 35B repair-v02 model-swap row. Qwen-specific output-contract prompt/runtime-adapter repair is allowed, but the component graph, lenses, scorer, and deterministic replay components are frozen.
- JSON: `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_20260625.json`
- JSONL: `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_20260625.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_diagnosis_decomposer.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `same_core_diagnosis_decomposer` |
| SeizureFrequency | `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_union_arbitration.jsonl` | `sf_state_union_arbitration_v08` | `same_core_structured_sf_direct+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_prescription_deterministic_repair_v03.jsonl` | `prescription_regimen_v01` | `same_core_deterministic_prescription_repair_v03` |
| Investigations | `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured.jsonl` | `investigations_result_v01` | `same_core_structured_direct_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7668 | 0.7434 | 0.6126 | 0.8895 | 0.8755 |
| evidence_valid | `evidence_valid_score` | 0.8049 | 0.8473 | 0.6126 | 0.8895 | 0.8755 |
| benchmark_cui | `cui_projection_companion` | 0.8049 | 0.8473 | 0.6126 | 0.8895 | 0.8755 |
| clinical_headline | `headline_target` | 0.8319 | 0.8473 | 0.7182 | 0.8895 | 0.8755 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7668 | 0.7434 | 0.6126 | 0.8895 | 0.8755 |
| `evidence_valid` | 0.7668 | 0.7434 | 0.6126 | 0.8895 | 0.8755 |
| `protocol_model_preserving_canonical` | 0.7668 | 0.7434 | 0.6126 | 0.8895 | 0.8755 |
| `dictionary_normalized` | 0.7955 | 0.8227 | 0.6126 | 0.8895 | 0.8755 |
| `residual_benchmark_added` | 0.8049 | 0.8473 | 0.6126 | 0.8895 | 0.8755 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 1008 |
| `evidence_valid` | 0 | 1008 |
| `protocol_model_preserving_canonical` | 0 | 1008 |
| `dictionary_normalized` | 0 | 968 |
| `residual_benchmark_added` | 14 | 968 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4601 |
| Benchmark after CUI/projection | 0.4727 |
| Diagnosis.concept_negation | 0.8473 |
| SeizureFrequency.active_rate_fidelity | 0.4314 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0681; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0140; floor -0.0100 |
| Diagnosis headline | pass | 0.8473; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8473; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7182; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.4314; baseline 0.2887 |
| Prescription changed-row control | fail | 127 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 121 | assertion_or_negation_change=86, hierarchy_reconciliation_or_duplicate_collapse=86, hierarchy_reconciliation=33, projection_only=2 |
| versus_v042_default_quarantine | SeizureFrequency | 86 | active_rate=66, generic_vs_specific=1, seizure_free=42, unknown=2, unknown_or_change_state=30, projection_action=18, reject_or_drop=1 |
| versus_v042_default_quarantine | Prescription | 127 | model_output=127 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Model: `Qwen 3.6 35B repair v02` (`ollama_chat/qwen3.6:35b`)
- Runtime: `ollama_chat_think_false_qwen_output_contract_repair_v02`
- Prompt profile: `qwen_compact`
- Calls per letter: `2.0`
- Live call components: `structured_key_family_event_ledger, diagnosis_decomposer`
- Replayed/no-call components: `sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, sf_union_arbitration, prescription_deterministic_repair, finding_assembly`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
