# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-21`
- Split/stage: `dev` / `dev5`
- Candidate: `exectv2_holistic_finding_assembly_v09_qwen_dev5`
- Gate decision: **do-not-promote**
- Claim boundary: Dev-only component-attributed architecture evidence. This artifact does not authorize a benchmark claim, full-200 audit, or locked-test analysis.
- JSON: `experiments/exectv2_holistic_finding_assembly_v09_qwen_dev5_20260621.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v09_qwen_dev5_20260621.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v09_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v09_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v09_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v09_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl` | `investigations_passthrough_v09` | `single_gpt_investigations_prompt_owned` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 0.7714 | 0.4211 | 0.7778 | 0.9412 | 1.0000 |
| benchmark_cui | `cui_projection_companion` | 0.7714 | 0.4211 | 0.7778 | 0.9412 | 1.0000 |
| clinical_headline | `headline_target` | 0.7714 | 0.4211 | 0.7778 | 0.9412 | 1.0000 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.2500 |
| Benchmark after CUI/projection | 0.2727 |
| Diagnosis.concept_negation | 0.4211 |
| SeizureFrequency.active_rate_fidelity | 0.5882 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1198; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.1385; floor -0.0100 |
| Diagnosis headline | fail | 0.4211; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | fail | 0.4211; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7778; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5882; baseline 0.2887 |
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
| versus_v042_default_quarantine | Diagnosis | 2 | assertion_or_negation_change=2, hierarchy_reconciliation_or_duplicate_collapse=2 |
| versus_v042_default_quarantine | SeizureFrequency | 0 | none |
| versus_v042_default_quarantine | Prescription | 0 | none |
| versus_v042_default_quarantine | Investigations | 0 | none |
| versus_existing_focused_route_comparator | Diagnosis | 5 | assertion_or_negation_change=4, hierarchy_reconciliation_or_duplicate_collapse=4, hierarchy_reconciliation=1 |
| versus_existing_focused_route_comparator | SeizureFrequency | 5 | active_rate=5, seizure_free=2 |
| versus_existing_focused_route_comparator | Prescription | 5 | model_output=5 |
| versus_existing_focused_route_comparator | Investigations | 3 | model_output=3 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
