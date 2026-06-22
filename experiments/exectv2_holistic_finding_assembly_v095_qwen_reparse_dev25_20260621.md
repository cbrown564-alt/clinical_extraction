# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev25`
- Candidate: `exectv2_holistic_finding_assembly_v095_qwen_reparse_dev25`
- Gate decision: **do-not-promote**
- Claim boundary: diagnostic-no-call-qwen-v095-parser-evidence-reparse-dev25
- JSON: `experiments/exectv2_holistic_finding_assembly_v095_qwen_reparse_dev25_20260621.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v095_qwen_reparse_dev25_20260621.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v095_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v095_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v095_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v095_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `investigations_passthrough_v09` | `single_gpt_investigations_prompt_owned` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 0.8266 | 0.8104 | 0.6316 | 0.9231 | 0.9500 |
| benchmark_cui | `cui_projection_companion` | 0.8266 | 0.8104 | 0.6316 | 0.9231 | 0.9500 |
| clinical_headline | `headline_target` | 0.8297 | 0.8104 | 0.6429 | 0.9231 | 0.9500 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3144 |
| Benchmark after CUI/projection | 0.3144 |
| Diagnosis.concept_negation | 0.8104 |
| SeizureFrequency.active_rate_fidelity | 0.4118 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1017; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0885; floor -0.0100 |
| Diagnosis headline | pass | 0.8104; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8104; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.6429; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.4118; baseline 0.2887 |
| Prescription changed-row control | fail | 4 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 9 | assertion_or_negation_change=9, hierarchy_reconciliation_or_duplicate_collapse=9 |
| versus_v042_default_quarantine | SeizureFrequency | 0 | none |
| versus_v042_default_quarantine | Prescription | 4 | model_output=4 |
| versus_v042_default_quarantine | Investigations | 0 | none |
| versus_existing_focused_route_comparator | Diagnosis | 21 | assertion_or_negation_change=17, hierarchy_reconciliation_or_duplicate_collapse=17, hierarchy_reconciliation=4 |
| versus_existing_focused_route_comparator | SeizureFrequency | 22 | active_rate=16, unknown_or_change_state=9, seizure_free=8 |
| versus_existing_focused_route_comparator | Prescription | 22 | model_output=22 |
| versus_existing_focused_route_comparator | Investigations | 9 | model_output=9 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
