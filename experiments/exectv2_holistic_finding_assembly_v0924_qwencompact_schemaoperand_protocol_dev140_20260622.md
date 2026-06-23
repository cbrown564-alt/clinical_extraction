# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-23`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140`
- Gate decision: **do-not-promote**
- Claim boundary: local-qwen-v0924-qwen-compact-live-dev140-ctx12288-maxtok3000-balanced-json-schema-repair-model-preserving-sf-operand-repair
- JSON: `experiments/exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_protocol_dev140_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_protocol_dev140_20260622.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v0924_qwencompact_schemaoperand_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v0924_qwencompact_schemaoperand_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v0924_qwencompact_schemaoperand_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v0924_qwencompact_schemaoperand_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl` | `investigations_convention_dictionary_v09` | `single_gpt+standard_dictionary_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.6688 | 0.6533 | 0.4306 | 0.8405 | 0.7630 |
| evidence_valid | `evidence_valid_score` | 0.8093 | 0.8174 | 0.6154 | 0.8832 | 0.9470 |
| benchmark_cui | `cui_projection_companion` | 0.8093 | 0.8174 | 0.6154 | 0.8832 | 0.9470 |
| clinical_headline | `headline_target` | 0.8483 | 0.8174 | 0.7887 | 0.8832 | 0.9470 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.6688 | 0.6533 | 0.4306 | 0.8405 | 0.7630 |
| `evidence_valid` | 0.6688 | 0.6533 | 0.4306 | 0.8405 | 0.7630 |
| `dictionary_normalized` | 0.7446 | 0.7637 | 0.5108 | 0.8721 | 0.8155 |
| `residual_benchmark_added` | 0.8093 | 0.8174 | 0.6154 | 0.8832 | 0.9470 |
| `final` | 0.8093 | 0.8174 | 0.6154 | 0.8832 | 0.9470 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.2573 |
| Benchmark after CUI/projection | 0.3200 |
| Diagnosis.concept_negation | 0.8174 |
| SeizureFrequency.active_rate_fidelity | 0.3671 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0618; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0855; floor -0.0100 |
| Diagnosis headline | pass | 0.8174; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8174; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7887; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.3671; baseline 0.2887 |
| Prescription changed-row control | fail | 23 changed rows |
| Investigations changed-row control | fail | 37 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 3 | 0 | 1.0000 |
| SeizureFrequency | 0 | 3 | 0 | 1.0000 |
| Prescription | 0 | 3 | 0 | 1.0000 |
| Investigations | 0 | 3 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 111 | hierarchy_reconciliation=44, assertion_or_negation_change=67, hierarchy_reconciliation_or_duplicate_collapse=67 |
| versus_v042_default_quarantine | SeizureFrequency | 85 | seizure_free=35, unknown_or_change_state=26, active_rate=65, generic_vs_specific=6, unknown=9 |
| versus_v042_default_quarantine | Prescription | 23 | model_output=23 |
| versus_v042_default_quarantine | Investigations | 37 | model_output=37 |
| versus_existing_focused_route_comparator | Diagnosis | 126 | hierarchy_reconciliation=43, assertion_or_negation_change=83, hierarchy_reconciliation_or_duplicate_collapse=81 |
| versus_existing_focused_route_comparator | SeizureFrequency | 110 | active_rate=82, seizure_free=49, unknown_or_change_state=38, generic_vs_specific=6, unknown=10 |
| versus_existing_focused_route_comparator | Prescription | 116 | model_output=116 |
| versus_existing_focused_route_comparator | Investigations | 67 | model_output=65, projection_only=2 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
