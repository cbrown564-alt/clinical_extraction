# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-22`
- Split/stage: `dev` / `dev1`
- Candidate: `exectv2_holistic_finding_assembly_v097_deepseek_dev1`
- Gate decision: **diagnostic-deepseek-smoke-dev1**
- Claim boundary: hosted-deepseek-v097-full-live-dev1
- JSON: `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev1_20260622.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev1_20260622.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_llm_only_key_entities_structured_v097_dev1_deepseek_chat_20260622.jsonl` | `diagnosis_convention_dictionary_v09` | `single_gpt+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_llm_only_key_entities_structured_v097_dev1_deepseek_chat_20260622.jsonl` | `sf_convention_dictionary_v09` | `single_gpt+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_llm_only_key_entities_structured_v097_dev1_deepseek_chat_20260622.jsonl` | `prescription_dictionary_v09` | `single_gpt+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_llm_only_key_entities_structured_v097_dev1_deepseek_chat_20260622.jsonl` | `investigations_passthrough_v09` | `single_gpt_investigations_prompt_owned` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| evidence_valid | `evidence_valid_score` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| benchmark_cui | `cui_projection_companion` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| clinical_headline | `headline_target` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.5263 |
| Benchmark after CUI/projection | 0.5263 |
| Diagnosis.concept_negation | 1.0000 |
| SeizureFrequency.active_rate_fidelity | 1.0000 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1786; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.1385; floor -0.0100 |
| Diagnosis headline | pass | 1.0000; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 1.0000; baseline 0.6693 |
| SeizureFrequency headline | pass | 1.0000; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 1.0000; baseline 0.2887 |
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
| versus_v042_default_quarantine | Diagnosis | 0 | none |
| versus_v042_default_quarantine | SeizureFrequency | 0 | none |
| versus_v042_default_quarantine | Prescription | 0 | none |
| versus_v042_default_quarantine | Investigations | 0 | none |
| versus_existing_focused_route_comparator | Diagnosis | 1 | assertion_or_negation_change=1, hierarchy_reconciliation_or_duplicate_collapse=1 |
| versus_existing_focused_route_comparator | SeizureFrequency | 1 | active_rate=1 |
| versus_existing_focused_route_comparator | Prescription | 1 | model_output=1 |
| versus_existing_focused_route_comparator | Investigations | 1 | model_output=1 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
