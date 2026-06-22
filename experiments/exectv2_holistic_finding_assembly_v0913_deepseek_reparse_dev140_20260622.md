# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v0913_deepseek_reparse_dev140`
- Gate decision: **do-not-promote**
- Claim boundary: diagnostic-same-raw-deepseek-v0910-through-v0913-dictionary-dev140
- JSON: `experiments/exectv2_holistic_finding_assembly_v0913_deepseek_reparse_dev140_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v0913_deepseek_reparse_dev140_20260622.jsonl`

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
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 0.8149 | 0.8433 | 0.6217 | 0.8640 | 0.9231 |
| benchmark_cui | `cui_projection_companion` | 0.8149 | 0.8433 | 0.6217 | 0.8640 | 0.9231 |
| clinical_headline | `headline_target` | 0.8530 | 0.8433 | 0.8024 | 0.8640 | 0.9231 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3349 |
| Benchmark after CUI/projection | 0.3741 |
| Diagnosis.concept_negation | 0.8433 |
| SeizureFrequency.active_rate_fidelity | 0.5922 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0426; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0616; floor -0.0100 |
| Diagnosis headline | pass | 0.8433; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8433; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.8024; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5922; baseline 0.2887 |
| Prescription changed-row control | fail | 30 changed rows |
| Investigations changed-row control | fail | 6 changed rows |

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
| versus_v042_default_quarantine | Diagnosis | 113 | assertion_or_negation_change=71, hierarchy_reconciliation_or_duplicate_collapse=71, hierarchy_reconciliation=41, projection_only=1 |
| versus_v042_default_quarantine | SeizureFrequency | 29 | seizure_free=12, active_rate=21, unknown_or_change_state=9 |
| versus_v042_default_quarantine | Prescription | 30 | model_output=30 |
| versus_v042_default_quarantine | Investigations | 6 | model_output=6 |
| versus_existing_focused_route_comparator | Diagnosis | 128 | assertion_or_negation_change=81, hierarchy_reconciliation_or_duplicate_collapse=81, hierarchy_reconciliation=44, projection_only=3 |
| versus_existing_focused_route_comparator | SeizureFrequency | 105 | active_rate=77, seizure_free=47, unknown_or_change_state=29 |
| versus_existing_focused_route_comparator | Prescription | 105 | model_output=105 |
| versus_existing_focused_route_comparator | Investigations | 49 | model_output=49 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
