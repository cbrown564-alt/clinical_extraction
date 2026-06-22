# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev25`
- Candidate: `exectv2_holistic_finding_assembly_v0910_qwencompact_dev25`
- Gate decision: **do-not-promote**
- Claim boundary: local-qwen-v0910-qwen-compact-live-dev25-ctx12288-maxtok2500-standard-dictionary-repair
- JSON: `experiments/exectv2_holistic_finding_assembly_v0910_qwencompact_residualrepair_dev25_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v0910_qwencompact_residualrepair_dev25_20260622.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `investigations_convention_dictionary_v09` | `single_gpt+standard_dictionary_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 0.9171 | 0.8189 | 0.9615 | 0.9487 | 0.9744 |
| benchmark_cui | `cui_projection_companion` | 0.9171 | 0.8189 | 0.9615 | 0.9487 | 0.9744 |
| clinical_headline | `headline_target` | 0.9208 | 0.8189 | 0.9804 | 0.9487 | 0.9744 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3321 |
| Benchmark after CUI/projection | 0.3469 |
| Diagnosis.concept_negation | 0.8189 |
| SeizureFrequency.active_rate_fidelity | 0.5000 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1273; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.1129; floor -0.0100 |
| Diagnosis headline | pass | 0.8189; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8189; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.9804; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5000; baseline 0.2887 |
| Prescription changed-row control | pass | 0 changed rows |
| Investigations changed-row control | fail | 1 changed rows |

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
| versus_v042_default_quarantine | Diagnosis | 13 | assertion_or_negation_change=8, hierarchy_reconciliation_or_duplicate_collapse=8, hierarchy_reconciliation=5 |
| versus_v042_default_quarantine | SeizureFrequency | 12 | active_rate=8, seizure_free=6, unknown_or_change_state=4 |
| versus_v042_default_quarantine | Prescription | 0 | none |
| versus_v042_default_quarantine | Investigations | 1 | model_output=1 |
| versus_existing_focused_route_comparator | Diagnosis | 19 | assertion_or_negation_change=14, hierarchy_reconciliation_or_duplicate_collapse=14, hierarchy_reconciliation=5 |
| versus_existing_focused_route_comparator | SeizureFrequency | 15 | active_rate=11, seizure_free=6, unknown_or_change_state=4 |
| versus_existing_focused_route_comparator | Prescription | 21 | model_output=21 |
| versus_existing_focused_route_comparator | Investigations | 12 | model_output=12 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
