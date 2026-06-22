# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`
- Gate decision: **do-not-promote**
- Claim boundary: diagnostic-same-raw-deepseek-v0910-through-v0916-dictionary-dev140
- JSON: `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `investigations_convention_dictionary_v09` | `single_gpt+standard_dictionary_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7498 | 0.7183 | 0.5620 | 0.8655 | 0.9062 |
| evidence_valid | `evidence_valid_score` | 0.8728 | 0.8898 | 0.6986 | 0.9415 | 0.9658 |
| benchmark_cui | `cui_projection_companion` | 0.8728 | 0.8898 | 0.6986 | 0.9415 | 0.9658 |
| clinical_headline | `headline_target` | 0.9174 | 0.8898 | 0.9017 | 0.9415 | 0.9658 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7498 | 0.7183 | 0.5620 | 0.8655 | 0.9062 |
| `evidence_valid` | 0.7498 | 0.7183 | 0.5620 | 0.8655 | 0.9062 |
| `dictionary_normalized` | 0.8334 | 0.8565 | 0.6444 | 0.9430 | 0.8619 |
| `residual_benchmark_added` | 0.8728 | 0.8898 | 0.6986 | 0.9415 | 0.9658 |
| `final` | 0.8728 | 0.8898 | 0.6986 | 0.9415 | 0.9658 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3505 |
| Benchmark after CUI/projection | 0.3991 |
| Diagnosis.concept_negation | 0.8898 |
| SeizureFrequency.active_rate_fidelity | 0.6310 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1201; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.1043; floor -0.0100 |
| Diagnosis headline | pass | 0.8898; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8898; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.9017; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.6310; baseline 0.2887 |
| Prescription changed-row control | fail | 37 changed rows |
| Investigations changed-row control | fail | 25 changed rows |

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
| versus_v042_default_quarantine | Diagnosis | 107 | hierarchy_reconciliation=52, assertion_or_negation_change=54, hierarchy_reconciliation_or_duplicate_collapse=54, projection_only=1 |
| versus_v042_default_quarantine | SeizureFrequency | 63 | active_rate=48, seizure_free=32, unknown_or_change_state=19, unknown=5, generic_vs_specific=3 |
| versus_v042_default_quarantine | Prescription | 37 | model_output=37 |
| versus_v042_default_quarantine | Investigations | 25 | model_output=24, projection_only=1 |
| versus_existing_focused_route_comparator | Diagnosis | 124 | hierarchy_reconciliation=52, assertion_or_negation_change=70, hierarchy_reconciliation_or_duplicate_collapse=70, projection_only=2 |
| versus_existing_focused_route_comparator | SeizureFrequency | 104 | active_rate=75, seizure_free=46, unknown_or_change_state=29, unknown=5, generic_vs_specific=3 |
| versus_existing_focused_route_comparator | Prescription | 109 | model_output=109 |
| versus_existing_focused_route_comparator | Investigations | 55 | model_output=55 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
