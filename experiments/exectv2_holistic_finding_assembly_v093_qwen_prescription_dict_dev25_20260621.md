# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev25`
- Candidate: `exectv2_holistic_finding_assembly_v093_qwen_prescription_dict_dev25`
- Gate decision: **do-not-promote**
- Claim boundary: diagnostic-no-call-qwen-prescription-dictionary-repair
- JSON: `experiments/exectv2_holistic_finding_assembly_v093_qwen_prescription_dict_dev25_20260621.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v093_qwen_prescription_dict_dev25_20260621.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v092_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v092_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v092_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v092_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl` | `investigations_passthrough_v09` | `single_gpt_investigations_prompt_owned` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 0.7742 | 0.6464 | 0.6207 | 0.9459 | 0.9500 |
| benchmark_cui | `cui_projection_companion` | 0.7742 | 0.6464 | 0.6207 | 0.9459 | 0.9500 |
| clinical_headline | `headline_target` | 0.7772 | 0.6464 | 0.6316 | 0.9459 | 0.9500 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.2746 |
| Benchmark after CUI/projection | 0.2746 |
| Diagnosis.concept_negation | 0.6464 |
| SeizureFrequency.active_rate_fidelity | 0.3030 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1245; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0885; floor -0.0100 |
| Diagnosis headline | fail | 0.6464; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | fail | 0.6464; baseline 0.6693 |
| SeizureFrequency headline | fail | 0.6316; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.3030; baseline 0.2887 |
| Prescription changed-row control | fail | 3 changed rows |
| Investigations changed-row control | pass | 0 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 1 | 0 | 1.0000 |
| SeizureFrequency | 0 | 1 | 0 | 1.0000 |
| Prescription | 0 | 1 | 0 | 1.0000 |
| Investigations | 0 | 1 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 7 | assertion_or_negation_change=6, hierarchy_reconciliation_or_duplicate_collapse=6, hierarchy_reconciliation=1 |
| versus_v042_default_quarantine | SeizureFrequency | 0 | none |
| versus_v042_default_quarantine | Prescription | 3 | model_output=3 |
| versus_v042_default_quarantine | Investigations | 0 | none |
| versus_existing_focused_route_comparator | Diagnosis | 20 | assertion_or_negation_change=15, hierarchy_reconciliation_or_duplicate_collapse=15, hierarchy_reconciliation=5 |
| versus_existing_focused_route_comparator | SeizureFrequency | 20 | active_rate=13, seizure_free=7, unknown_or_change_state=7 |
| versus_existing_focused_route_comparator | Prescription | 22 | model_output=22 |
| versus_existing_focused_route_comparator | Investigations | 9 | model_output=9 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
