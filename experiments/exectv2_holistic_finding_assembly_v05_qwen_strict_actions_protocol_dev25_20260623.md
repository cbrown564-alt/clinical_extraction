# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-23`
- Split/stage: `dev` / `dev25`
- Candidate: `exectv2_holistic_finding_assembly_v05_qwen_strict_actions_dev25`
- Gate decision: **do-not-promote**
- Claim boundary: local-qwen-strict-action-adjudication-dev25-schema-format-repair-only-for-action-json
- JSON: `experiments/exectv2_holistic_finding_assembly_v05_qwen_strict_actions_protocol_dev25_20260623.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v05_qwen_strict_actions_protocol_dev25_20260623.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev25_diagnosis_qwen36_35b_strict_actions_20260623.jsonl` | `diagnosis_convention_dictionary_v09` | `qwen_strict_action_adjudicator_diagnosis+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev25_seizurefrequency_qwen36_35b_strict_actions_20260623.jsonl` | `sf_convention_dictionary_v09` | `qwen_strict_action_adjudicator_sf+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev25_prescription_qwen36_35b_strict_actions_20260623.jsonl` | `prescription_dictionary_v09` | `qwen_strict_action_adjudicator_prescription+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev25_investigations_qwen36_35b_strict_actions_20260623.jsonl` | `investigations_convention_dictionary_v09` | `qwen_strict_action_adjudicator_investigations+standard_dictionary_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.9340 | 0.9195 | 0.9259 | 0.9610 | 0.9231 |
| evidence_valid | `evidence_valid_score` | 0.9425 | 0.9213 | 0.8929 | 0.9870 | 0.9744 |
| benchmark_cui | `cui_projection_companion` | 0.9425 | 0.9213 | 0.8929 | 0.9870 | 0.9744 |
| clinical_headline | `headline_target` | 0.9535 | 0.9213 | 0.9434 | 0.9870 | 0.9744 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.9340 | 0.9195 | 0.9259 | 0.9610 | 0.9231 |
| `evidence_valid` | 0.9340 | 0.9195 | 0.9259 | 0.9610 | 0.9231 |
| `protocol_model_preserving_canonical` | 0.9340 | 0.9195 | 0.9259 | 0.9610 | 0.9231 |
| `dictionary_normalized` | 0.9358 | 0.9524 | 0.8679 | 0.9867 | 0.8889 |
| `residual_benchmark_added` | 0.9425 | 0.9213 | 0.8929 | 0.9870 | 0.9744 |
| `final` | 0.9425 | 0.9213 | 0.8929 | 0.9870 | 0.9744 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4000 |
| Benchmark after CUI/projection | 0.4254 |
| Diagnosis.concept_negation | 0.9213 |
| SeizureFrequency.active_rate_fidelity | 0.9697 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1656; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.1129; floor -0.0100 |
| Diagnosis headline | pass | 0.9213; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.9213; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.9434; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.9697; baseline 0.2887 |
| Prescription changed-row control | fail | 20 changed rows |
| Investigations changed-row control | fail | 13 changed rows |

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
| versus_v042_default_quarantine | Diagnosis | 18 | assertion_or_negation_change=8, hierarchy_reconciliation_or_duplicate_collapse=8, hierarchy_reconciliation=10 |
| versus_v042_default_quarantine | SeizureFrequency | 15 | active_rate=12, seizure_free=7, unknown_or_change_state=3 |
| versus_v042_default_quarantine | Prescription | 20 | model_output=20 |
| versus_v042_default_quarantine | Investigations | 13 | model_output=13 |
| versus_existing_focused_route_comparator | Diagnosis | 19 | hierarchy_reconciliation=7, assertion_or_negation_change=12, hierarchy_reconciliation_or_duplicate_collapse=12 |
| versus_existing_focused_route_comparator | SeizureFrequency | 15 | active_rate=13, seizure_free=9, unknown_or_change_state=3 |
| versus_existing_focused_route_comparator | Prescription | 20 | model_output=20 |
| versus_existing_focused_route_comparator | Investigations | 7 | model_output=7 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
