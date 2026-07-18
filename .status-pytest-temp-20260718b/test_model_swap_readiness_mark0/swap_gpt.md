# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-25`
- Split/stage: `toy` / `toy2`
- Candidate: `swap_gpt`
- Gate decision: **same-core-model-swap-dev140-readout**
- Claim boundary: toy model swap
- JSON: `C:/Users/cbrow/Code/clinical_extraction/.status-pytest-temp-20260718b/test_model_swap_readiness_mark0/swap_gpt.json`
- JSONL: `C:/Users/cbrow/Code/clinical_extraction/.status-pytest-temp-20260718b/test_model_swap_readiness_mark0/swap_gpt.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `C:/Users/cbrow/Code/clinical_extraction/.status-pytest-temp-20260718b/test_model_swap_readiness_mark0/rows.jsonl` | `diagnosis_hierarchy_negation_v01` | `toy_dx` |
| SeizureFrequency | `C:/Users/cbrow/Code/clinical_extraction/.status-pytest-temp-20260718b/test_model_swap_readiness_mark0/rows.jsonl` | `sf_state_projection_suppression_v01` | `toy_model_sf` |
| Prescription | `C:/Users/cbrow/Code/clinical_extraction/.status-pytest-temp-20260718b/test_model_swap_readiness_mark0/rows.jsonl` | `prescription_regimen_v01` | `toy_rx` |
| Investigations | `C:/Users/cbrow/Code/clinical_extraction/.status-pytest-temp-20260718b/test_model_swap_readiness_mark0/rows.jsonl` | `investigations_result_v01` | `toy_inv` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| evidence_valid | `evidence_valid_score` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| benchmark_cui | `cui_projection_companion` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| clinical_headline | `headline_target` | 0.7500 | 1.0000 | 0.0000 | 1.0000 | 1.0000 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `evidence_valid` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `protocol_model_preserving_canonical` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `dictionary_normalized` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `residual_benchmark_added` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Fact-Origin Accounting

| Surface | target_model_generated |
| --- | ---: |
| `source_scored` | 8 |
| `evidence_valid` | 8 |
| `protocol_model_preserving_canonical` | 8 |
| `dictionary_normalized` | 8 |
| `residual_benchmark_added` | 8 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 1.0000 |
| Benchmark after CUI/projection | 0.0000 |
| Diagnosis.concept_negation | 1.0000 |
| SeizureFrequency.active_rate_fidelity | 1.0000 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1786; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.1385; floor -0.0100 |
| Diagnosis headline | pass | 1.0000; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 1.0000; baseline 0.6693 |
| SeizureFrequency headline | fail | 0.0000; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 1.0000; baseline 0.2887 |
| Prescription changed-row control | pass | 0 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 0 | none |
| versus_v042_default_quarantine | SeizureFrequency | 0 | none |
| versus_v042_default_quarantine | Prescription | 0 | none |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `same_core_test`
- Model: `GPT-4.1-mini` (`openai/gpt-4.1-mini`)
- Runtime: `openai_chat`
- Prompt profile: `full`
- Calls per letter: `2.0`
- Live call components: `structured_key_family_event_ledger, diagnosis_decomposer`
- Replayed/no-call components: `sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, sf_union_arbitration, prescription_deterministic_repair, finding_assembly`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`
