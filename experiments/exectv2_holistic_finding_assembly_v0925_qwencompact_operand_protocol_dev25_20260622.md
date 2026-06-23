# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-23`
- Split/stage: `dev` / `dev25`
- Candidate: `exectv2_holistic_finding_assembly_v0925_qwencompact_dev25`
- Gate decision: **do-not-promote**
- Claim boundary: local-qwen-v0925-qwen-compact-live-dev25-ctx12288-maxtok3000-sf-attribute-shape-balanced-json-schema-repair
- JSON: `experiments/exectv2_holistic_finding_assembly_v0925_qwencompact_operand_protocol_dev25_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v0925_qwencompact_operand_protocol_dev25_20260622.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v0925_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v0925_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v0925_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v0925_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl` | `investigations_convention_dictionary_v09` | `single_gpt+standard_dictionary_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.8525 | 0.9036 | 0.5882 | 0.9211 | 0.9500 |
| evidence_valid | `evidence_valid_score` | 0.9145 | 0.9053 | 0.8421 | 0.9333 | 1.0000 |
| benchmark_cui | `cui_projection_companion` | 0.9145 | 0.9053 | 0.8421 | 0.9333 | 1.0000 |
| clinical_headline | `headline_target` | 0.9180 | 0.9053 | 0.8571 | 0.9333 | 1.0000 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.8525 | 0.9036 | 0.5882 | 0.9211 | 0.9500 |
| `evidence_valid` | 0.8525 | 0.9036 | 0.5882 | 0.9211 | 0.9500 |
| `dictionary_normalized` | 0.8753 | 0.9262 | 0.6383 | 0.9459 | 0.9189 |
| `residual_benchmark_added` | 0.9145 | 0.9053 | 0.8421 | 0.9333 | 1.0000 |
| `final` | 0.9145 | 0.9053 | 0.8421 | 0.9333 | 1.0000 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3448 |
| Benchmark after CUI/projection | 0.3655 |
| Diagnosis.concept_negation | 0.9053 |
| SeizureFrequency.active_rate_fidelity | 0.8000 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1119; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.1385; floor -0.0100 |
| Diagnosis headline | pass | 0.9053; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.9053; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.8571; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.8000; baseline 0.2887 |
| Prescription changed-row control | fail | 3 changed rows |
| Investigations changed-row control | fail | 4 changed rows |

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
| versus_v042_default_quarantine | Diagnosis | 17 | hierarchy_reconciliation=8, assertion_or_negation_change=9, hierarchy_reconciliation_or_duplicate_collapse=9 |
| versus_v042_default_quarantine | SeizureFrequency | 10 | active_rate=8, seizure_free=7, unknown_or_change_state=4 |
| versus_v042_default_quarantine | Prescription | 3 | model_output=3 |
| versus_v042_default_quarantine | Investigations | 4 | model_output=4 |
| versus_existing_focused_route_comparator | Diagnosis | 19 | hierarchy_reconciliation=8, assertion_or_negation_change=11, hierarchy_reconciliation_or_duplicate_collapse=11 |
| versus_existing_focused_route_comparator | SeizureFrequency | 16 | active_rate=14, seizure_free=8, unknown_or_change_state=4 |
| versus_existing_focused_route_comparator | Prescription | 22 | model_output=22 |
| versus_existing_focused_route_comparator | Investigations | 12 | model_output=12 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
