# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-23`
- Split/stage: `dev` / `dev5`
- Candidate: `exectv2_holistic_finding_assembly_v05_qwen_strict_actions_dev5`
- Gate decision: **do-not-promote**
- Claim boundary: local-qwen-strict-action-adjudication-dev5-schema-format-repair-only-for-action-json
- JSON: `experiments/exectv2_holistic_finding_assembly_v05_qwen_strict_actions_protocol_dev5_20260623.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v05_qwen_strict_actions_protocol_dev5_20260623.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev5_diagnosis_qwen36_35b_strict_actions_20260623.jsonl` | `diagnosis_convention_dictionary_v09` | `qwen_strict_action_adjudicator_diagnosis+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev5_seizurefrequency_qwen36_35b_strict_actions_20260623.jsonl` | `sf_convention_dictionary_v09` | `qwen_strict_action_adjudicator_sf+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev5_prescription_qwen36_35b_strict_actions_20260623.jsonl` | `prescription_dictionary_v09` | `qwen_strict_action_adjudicator_prescription+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev5_investigations_qwen36_35b_strict_actions_20260623.jsonl` | `investigations_convention_dictionary_v09` | `qwen_strict_action_adjudicator_investigations+standard_dictionary_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.9444 | 0.9091 | 0.9412 | 1.0000 | 0.9333 |
| evidence_valid | `evidence_valid_score` | 0.9589 | 0.9524 | 0.8889 | 1.0000 | 1.0000 |
| benchmark_cui | `cui_projection_companion` | 0.9589 | 0.9524 | 0.8889 | 1.0000 | 1.0000 |
| clinical_headline | `headline_target` | 0.9722 | 0.9524 | 0.9412 | 1.0000 | 1.0000 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.9444 | 0.9091 | 0.9412 | 1.0000 | 0.9333 |
| `evidence_valid` | 0.9444 | 0.9091 | 0.9412 | 1.0000 | 0.9333 |
| `dictionary_normalized` | 0.9714 | 1.0000 | 0.9412 | 1.0000 | 0.9333 |
| `residual_benchmark_added` | 0.9589 | 0.9524 | 0.8889 | 1.0000 | 1.0000 |
| `final` | 0.9589 | 0.9524 | 0.8889 | 1.0000 | 1.0000 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4694 |
| Benchmark after CUI/projection | 0.5102 |
| Diagnosis.concept_negation | 0.9524 |
| SeizureFrequency.active_rate_fidelity | 1.0000 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1786; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.1385; floor -0.0100 |
| Diagnosis headline | pass | 0.9524; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.9524; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.9412; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 1.0000; baseline 0.2887 |
| Prescription changed-row control | fail | 5 changed rows |
| Investigations changed-row control | fail | 5 changed rows |

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
| versus_v042_default_quarantine | Diagnosis | 4 | assertion_or_negation_change=2, hierarchy_reconciliation_or_duplicate_collapse=2, hierarchy_reconciliation=2 |
| versus_v042_default_quarantine | SeizureFrequency | 5 | active_rate=5, seizure_free=2 |
| versus_v042_default_quarantine | Prescription | 5 | model_output=5 |
| versus_v042_default_quarantine | Investigations | 5 | model_output=5 |
| versus_existing_focused_route_comparator | Diagnosis | 4 | hierarchy_reconciliation=2, assertion_or_negation_change=2, hierarchy_reconciliation_or_duplicate_collapse=2 |
| versus_existing_focused_route_comparator | SeizureFrequency | 5 | active_rate=5, seizure_free=2, unknown_or_change_state=1 |
| versus_existing_focused_route_comparator | Prescription | 5 | model_output=5 |
| versus_existing_focused_route_comparator | Investigations | 4 | model_output=4 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
