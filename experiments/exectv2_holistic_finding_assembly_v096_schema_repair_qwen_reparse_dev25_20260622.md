# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev25`
- Candidate: `exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25`
- Gate decision: **do-not-promote**
- Claim boundary: diagnostic-no-call-qwen-v096-schema-repair-reparse-dev25
- JSON: `experiments/exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25_20260622.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v096_schema_repair_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v096_schema_repair_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v096_schema_repair_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v096_schema_repair_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `investigations_passthrough_v09` | `single_gpt_investigations_prompt_owned` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 0.7899 | 0.8112 | 0.5614 | 0.8608 | 0.9268 |
| benchmark_cui | `cui_projection_companion` | 0.7899 | 0.8112 | 0.5614 | 0.8608 | 0.9268 |
| clinical_headline | `headline_target` | 0.8082 | 0.8112 | 0.6429 | 0.8608 | 0.9268 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.2915 |
| Benchmark after CUI/projection | 0.2915 |
| Diagnosis.concept_negation | 0.8112 |
| SeizureFrequency.active_rate_fidelity | 0.3750 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0394; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0653; floor -0.0100 |
| Diagnosis headline | pass | 0.8112; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8112; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.6429; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.3750; baseline 0.2887 |
| Prescription changed-row control | fail | 1 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 8 | assertion_or_negation_change=8, hierarchy_reconciliation_or_duplicate_collapse=8 |
| versus_v042_default_quarantine | SeizureFrequency | 0 | none |
| versus_v042_default_quarantine | Prescription | 1 | model_output=1 |
| versus_v042_default_quarantine | Investigations | 0 | none |
| versus_existing_focused_route_comparator | Diagnosis | 19 | assertion_or_negation_change=13, hierarchy_reconciliation_or_duplicate_collapse=13, hierarchy_reconciliation=6 |
| versus_existing_focused_route_comparator | SeizureFrequency | 21 | active_rate=14, unknown_or_change_state=8, seizure_free=7, unknown=1 |
| versus_existing_focused_route_comparator | Prescription | 21 | model_output=21 |
| versus_existing_focused_route_comparator | Investigations | 8 | model_output=8 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
