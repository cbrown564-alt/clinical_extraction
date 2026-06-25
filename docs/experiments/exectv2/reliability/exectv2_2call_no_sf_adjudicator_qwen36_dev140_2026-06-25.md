# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `dev140` / `dev140140`
- Candidate: `exectv2_2call_no_sf_adjudicator_qwen36_dev140`
- Gate decision: **same-core-model-swap-dev140-readout**
- Claim boundary: Dev140 same-core Qwen 3.6 35B model-swap row. Pending live/replay producer artifacts; Qwen-specific compact JSON prompt is allowed but the component graph is frozen.
- JSON: `experiments/exectv2_2call_no_sf_adjudicator_qwen36_dev140_20260625.json`
- JSONL: `experiments/exectv2_2call_no_sf_adjudicator_qwen36_dev140_20260625.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_diagnosis_decomposer.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `same_core_diagnosis_decomposer` |
| SeizureFrequency | `experiments/exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_sf_union_arbitration.jsonl` | `sf_state_union_arbitration_v08` | `same_core_structured_sf_direct+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_prescription_deterministic_repair_v03.jsonl` | `prescription_regimen_v01` | `same_core_deterministic_prescription_repair_v03` |
| Investigations | `experiments/exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_structured.jsonl` | `investigations_result_v01` | `same_core_structured_direct_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7426 | 0.7110 | 0.5913 | 0.8895 | 0.8354 |
| evidence_valid | `evidence_valid_score` | 0.7750 | 0.8027 | 0.5913 | 0.8895 | 0.8354 |
| benchmark_cui | `cui_projection_companion` | 0.7750 | 0.8027 | 0.5913 | 0.8895 | 0.8354 |
| clinical_headline | `headline_target` | 0.8018 | 0.8027 | 0.6919 | 0.8895 | 0.8354 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7422 | 0.7101 | 0.5913 | 0.8895 | 0.8354 |
| `evidence_valid` | 0.7422 | 0.7101 | 0.5913 | 0.8895 | 0.8354 |
| `protocol_model_preserving_canonical` | 0.7422 | 0.7101 | 0.5913 | 0.8895 | 0.8354 |
| `dictionary_normalized` | 0.7660 | 0.7780 | 0.5913 | 0.8895 | 0.8354 |
| `residual_benchmark_added` | 0.7750 | 0.8027 | 0.5913 | 0.8895 | 0.8354 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 952 |
| `evidence_valid` | 0 | 952 |
| `protocol_model_preserving_canonical` | 0 | 952 |
| `dictionary_normalized` | 0 | 921 |
| `residual_benchmark_added` | 13 | 921 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4170 |
| Benchmark after CUI/projection | 0.4256 |
| Diagnosis.concept_negation | 0.8027 |
| SeizureFrequency.active_rate_fidelity | 0.3922 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0681; floor -0.0100 |
| Investigations control regression | fail | delta vs v0.42 control -0.0261; floor -0.0100 |
| Diagnosis headline | pass | 0.8027; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8027; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.6919; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.3922; baseline 0.2887 |
| Prescription changed-row control | fail | 121 changed rows |
| Investigations changed-row control | pass | 0 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 11 | 0 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 0 | 0 | 0 | 1.0000 |
| Investigations | 1 | 1 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 121 | assertion_or_negation_change=94, hierarchy_reconciliation_or_duplicate_collapse=94, hierarchy_reconciliation=27 |
| versus_v042_default_quarantine | SeizureFrequency | 82 | active_rate=67, seizure_free=37, unknown_or_change_state=27, unknown=2, projection_action=18, reject_or_drop=1, generic_vs_specific=1 |
| versus_v042_default_quarantine | Prescription | 121 | model_output=121 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Model: `Qwen 3.6 35B` (`ollama_chat/qwen3.6:35b`)
- Runtime: `ollama_chat_think_false`
- Prompt profile: `qwen_compact`
- Calls per letter: `2.0`
- Live call components: `structured_key_family_event_ledger, diagnosis_decomposer`
- Replayed/no-call components: `sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, sf_union_arbitration, prescription_deterministic_repair, finding_assembly`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
