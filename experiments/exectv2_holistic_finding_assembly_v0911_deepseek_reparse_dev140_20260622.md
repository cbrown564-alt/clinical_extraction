# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v0911_deepseek_reparse_dev140`
- Gate decision: **do-not-promote**
- Claim boundary: diagnostic-same-raw-deepseek-v0910-through-v0911-dictionary-dev140
- JSON: `experiments/exectv2_holistic_finding_assembly_v0911_deepseek_reparse_dev140_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v0911_deepseek_reparse_dev140_20260622.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `investigations_passthrough_v09` | `single_gpt_investigations_prompt_owned` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 0.7953 | 0.8350 | 0.5675 | 0.8683 | 0.9062 |
| benchmark_cui | `cui_projection_companion` | 0.7953 | 0.8350 | 0.5675 | 0.8683 | 0.9062 |
| clinical_headline | `headline_target` | 0.8347 | 0.8350 | 0.7437 | 0.8683 | 0.9062 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3332 |
| Benchmark after CUI/projection | 0.3678 |
| Diagnosis.concept_negation | 0.8350 |
| SeizureFrequency.active_rate_fidelity | 0.5579 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0469; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0447; floor -0.0100 |
| Diagnosis headline | pass | 0.8350; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8350; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7437; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5579; baseline 0.2887 |
| Prescription changed-row control | fail | 7 changed rows |
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
| versus_v042_default_quarantine | Diagnosis | 112 | assertion_or_negation_change=68, hierarchy_reconciliation_or_duplicate_collapse=68, hierarchy_reconciliation=43, projection_only=1 |
| versus_v042_default_quarantine | SeizureFrequency | 2 | active_rate=2, unknown_or_change_state=1 |
| versus_v042_default_quarantine | Prescription | 7 | model_output=7 |
| versus_v042_default_quarantine | Investigations | 0 | none |
| versus_existing_focused_route_comparator | Diagnosis | 129 | assertion_or_negation_change=82, hierarchy_reconciliation_or_duplicate_collapse=82, hierarchy_reconciliation=44, projection_only=3 |
| versus_existing_focused_route_comparator | SeizureFrequency | 113 | active_rate=82, seizure_free=54, unknown_or_change_state=34 |
| versus_existing_focused_route_comparator | Prescription | 112 | model_output=112 |
| versus_existing_focused_route_comparator | Investigations | 48 | model_output=48 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
