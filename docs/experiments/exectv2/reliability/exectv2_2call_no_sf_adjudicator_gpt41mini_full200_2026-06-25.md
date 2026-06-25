# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `full200` / `full200200`
- Candidate: `exectv2_2call_no_sf_adjudicator_gpt41mini_full200`
- Gate decision: **same-core-model-swap-full200-readout**
- Claim boundary: Full-200 aggregate-only same-core GPT-4.1-mini reference row replayed from the accepted 2-call no-SF-adjudicator simplification artifacts. Strict benchmark/CUI scores are diagnostic only.
- JSON: `experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_full200_20260625.json`
- JSONL: `experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_full200_20260625.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. The final assembly stage is structural and introduces no live model calls; upstream same-core producer artifacts are live-or-replayed according to the frozen full-200 aggregate protocol.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_v08_full200_currentcode_diagnosis_decomposer_gpt41mini_20260624.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `same_core_diagnosis_decomposer` |
| SeizureFrequency | `experiments/exectv2_v08_full200_currentcode_sf_structured_direct_union_arbitration_20260624.jsonl` | `sf_state_union_arbitration_v08` | `same_core_structured_sf_direct+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_v08_full200_currentcode_deterministic_prescription_repair_v03_20260624.jsonl` | `prescription_regimen_v01` | `same_core_deterministic_prescription_repair_v03` |
| Investigations | `experiments/exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl` | `investigations_result_v01` | `same_core_structured_direct_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7736 | 0.7579 | 0.6221 | 0.8926 | 0.8563 |
| evidence_valid | `evidence_valid_score` | 0.8039 | 0.8397 | 0.6221 | 0.8926 | 0.8563 |
| benchmark_cui | `cui_projection_companion` | 0.8039 | 0.8397 | 0.6221 | 0.8926 | 0.8563 |
| clinical_headline | `headline_target` | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7736 | 0.7579 | 0.6221 | 0.8926 | 0.8563 |
| `evidence_valid` | 0.7736 | 0.7579 | 0.6221 | 0.8926 | 0.8563 |
| `protocol_model_preserving_canonical` | 0.7736 | 0.7579 | 0.6221 | 0.8926 | 0.8563 |
| `dictionary_normalized` | 0.7922 | 0.8087 | 0.6221 | 0.8926 | 0.8563 |
| `residual_benchmark_added` | 0.8039 | 0.8397 | 0.6221 | 0.8926 | 0.8563 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 1404 |
| `evidence_valid` | 0 | 1404 |
| `protocol_model_preserving_canonical` | 0 | 1404 |
| `dictionary_normalized` | 0 | 1330 |
| `residual_benchmark_added` | 27 | 1330 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4586 |
| Benchmark after CUI/projection | 0.4638 |
| Diagnosis.concept_negation | 0.8397 |
| SeizureFrequency.active_rate_fidelity | 0.5344 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0712; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control -0.0052; floor -0.0100 |
| Diagnosis headline | pass | 0.8397; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8397; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7525; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5344; baseline 0.2887 |
| Prescription changed-row control | fail | 189 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 167 | assertion_or_negation_change=116, hierarchy_reconciliation_or_duplicate_collapse=116, hierarchy_reconciliation=51 |
| versus_v042_default_quarantine | SeizureFrequency | 123 | active_rate=93, projection_action=25, seizure_free=68, unknown_or_change_state=39, generic_vs_specific=5, reject_or_drop=3 |
| versus_v042_default_quarantine | Prescription | 189 | model_output=189 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Model: `GPT-4.1-mini` (`openai/gpt-4.1-mini`)
- Runtime: `openai_chat`
- Prompt profile: `full`
- Calls per letter: `2.0`
- Live call components: `structured_key_family_event_ledger, diagnosis_decomposer`
- Replayed/no-call components: `sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, sf_union_arbitration, prescription_deterministic_repair, finding_assembly`
- Row inspection policy: `aggregate_only_no_full200_or_holdout_row_level_inspection`
