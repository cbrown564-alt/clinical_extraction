# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v0921_qwencompact_residualrepair_dev140`
- Gate decision: **do-not-promote**
- Claim boundary: local-qwen-v0910-qwen-compact-live-dev140-ctx12288-maxtok2500-standard-dictionary-residual-repair-v12
- JSON: `experiments/exectv2_holistic_finding_assembly_v0921_qwencompact_residualrepair_dev140_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v0921_qwencompact_residualrepair_dev140_20260622.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `investigations_convention_dictionary_v09` | `single_gpt+standard_dictionary_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 0.8542 | 0.8502 | 0.6899 | 0.9343 | 0.9579 |
| benchmark_cui | `cui_projection_companion` | 0.8542 | 0.8502 | 0.6899 | 0.9343 | 0.9579 |
| clinical_headline | `headline_target` | 0.8953 | 0.8502 | 0.8783 | 0.9343 | 0.9579 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.2409 |
| Benchmark after CUI/projection | 0.3115 |
| Diagnosis.concept_negation | 0.8502 |
| SeizureFrequency.active_rate_fidelity | 0.3731 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1129; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0964; floor -0.0100 |
| Diagnosis headline | pass | 0.8502; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8502; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.8783; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.3731; baseline 0.2887 |
| Prescription changed-row control | fail | 29 changed rows |
| Investigations changed-row control | fail | 48 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 10 | 0 | 1.0000 |
| SeizureFrequency | 0 | 10 | 0 | 1.0000 |
| Prescription | 0 | 10 | 0 | 1.0000 |
| Investigations | 0 | 10 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 105 | hierarchy_reconciliation=21, assertion_or_negation_change=84, hierarchy_reconciliation_or_duplicate_collapse=84 |
| versus_v042_default_quarantine | SeizureFrequency | 91 | active_rate=66, seizure_free=41, unknown=5, unknown_or_change_state=36, generic_vs_specific=5 |
| versus_v042_default_quarantine | Prescription | 29 | model_output=29 |
| versus_v042_default_quarantine | Investigations | 48 | model_output=48 |
| versus_existing_focused_route_comparator | Diagnosis | 124 | assertion_or_negation_change=86, hierarchy_reconciliation_or_duplicate_collapse=86, hierarchy_reconciliation=38 |
| versus_existing_focused_route_comparator | SeizureFrequency | 106 | active_rate=74, seizure_free=48, unknown_or_change_state=36, unknown=4, generic_vs_specific=4 |
| versus_existing_focused_route_comparator | Prescription | 113 | model_output=113 |
| versus_existing_focused_route_comparator | Investigations | 64 | model_output=64 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
