# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v0913_qwencompact_residualrepair_dev140`
- Gate decision: **do-not-promote**
- Claim boundary: local-qwen-v0910-qwen-compact-live-dev140-ctx12288-maxtok2500-standard-dictionary-residual-repair-v4
- JSON: `experiments/exectv2_holistic_finding_assembly_v0913_qwencompact_residualrepair_dev140_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v0913_qwencompact_residualrepair_dev140_20260622.jsonl`

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
| evidence_valid | `evidence_valid_score` | 0.7869 | 0.8149 | 0.5470 | 0.9043 | 0.8764 |
| benchmark_cui | `cui_projection_companion` | 0.7869 | 0.8149 | 0.5470 | 0.9043 | 0.8764 |
| clinical_headline | `headline_target` | 0.8271 | 0.8149 | 0.7246 | 0.9043 | 0.8764 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.2098 |
| Benchmark after CUI/projection | 0.2679 |
| Diagnosis.concept_negation | 0.8149 |
| SeizureFrequency.active_rate_fidelity | 0.1229 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0829; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0149; floor -0.0100 |
| Diagnosis headline | pass | 0.8149; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8149; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7246; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | fail | 0.1229; baseline 0.2887 |
| Prescription changed-row control | fail | 19 changed rows |
| Investigations changed-row control | fail | 32 changed rows |

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
| versus_v042_default_quarantine | Diagnosis | 113 | assertion_or_negation_change=95, hierarchy_reconciliation_or_duplicate_collapse=95, hierarchy_reconciliation=18 |
| versus_v042_default_quarantine | SeizureFrequency | 70 | active_rate=48, seizure_free=31, unknown=7, unknown_or_change_state=28, generic_vs_specific=6 |
| versus_v042_default_quarantine | Prescription | 19 | model_output=19 |
| versus_v042_default_quarantine | Investigations | 32 | model_output=32 |
| versus_existing_focused_route_comparator | Diagnosis | 127 | assertion_or_negation_change=93, hierarchy_reconciliation_or_duplicate_collapse=93, hierarchy_reconciliation=33, projection_only=1 |
| versus_existing_focused_route_comparator | SeizureFrequency | 111 | active_rate=82, seizure_free=49, unknown=7, unknown_or_change_state=41, generic_vs_specific=5 |
| versus_existing_focused_route_comparator | Prescription | 109 | model_output=109 |
| versus_existing_focused_route_comparator | Investigations | 62 | model_output=62 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
