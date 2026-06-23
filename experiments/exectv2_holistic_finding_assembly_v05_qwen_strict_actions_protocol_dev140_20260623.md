# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-23`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v05_qwen_strict_actions_dev140`
- Gate decision: **do-not-promote**
- Claim boundary: local-qwen-strict-action-adjudication-dev140-best-diagnosis-candidate-pool-schema-format-repair-only-for-action-json
- JSON: `experiments/exectv2_holistic_finding_assembly_v05_qwen_strict_actions_protocol_dev140_20260623.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v05_qwen_strict_actions_protocol_dev140_20260623.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev140_diagnosis_v08hybrid_qwen36_35b_strict_actions_20260623.jsonl` | `diagnosis_convention_dictionary_v09` | `qwen_strict_action_adjudicator_diagnosis+standard_dictionary_diagnosis` |
| SeizureFrequency | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev140_seizurefrequency_qwen36_35b_strict_actions_20260623.jsonl` | `sf_convention_dictionary_v09` | `qwen_strict_action_adjudicator_sf+standard_dictionary_sf` |
| Prescription | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev140_prescription_qwen36_35b_strict_actions_20260623.jsonl` | `prescription_dictionary_v09` | `qwen_strict_action_adjudicator_prescription+standard_dictionary_prescription` |
| Investigations | `experiments/exectv2_family_conditioned_candidate_adjudicator_v05_dev140_investigations_qwen36_35b_strict_actions_20260623.jsonl` | `investigations_convention_dictionary_v09` | `qwen_strict_action_adjudicator_investigations+standard_dictionary_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.8684 | 0.8795 | 0.7781 | 0.9247 | 0.8880 |
| evidence_valid | `evidence_valid_score` | 0.8728 | 0.8735 | 0.7660 | 0.9239 | 0.9502 |
| benchmark_cui | `cui_projection_companion` | 0.8728 | 0.8735 | 0.7660 | 0.9239 | 0.9502 |
| clinical_headline | `headline_target` | 0.9020 | 0.8735 | 0.8908 | 0.9239 | 0.9502 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.8684 | 0.8795 | 0.7781 | 0.9247 | 0.8880 |
| `evidence_valid` | 0.8684 | 0.8795 | 0.7781 | 0.9247 | 0.8880 |
| `protocol_model_preserving_canonical` | 0.8684 | 0.8795 | 0.7781 | 0.9247 | 0.8880 |
| `dictionary_normalized` | 0.8489 | 0.8640 | 0.7500 | 0.9251 | 0.8426 |
| `residual_benchmark_added` | 0.8728 | 0.8735 | 0.7660 | 0.9239 | 0.9502 |
| `final` | 0.8728 | 0.8735 | 0.7660 | 0.9239 | 0.9502 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3689 |
| Benchmark after CUI/projection | 0.4010 |
| Diagnosis.concept_negation | 0.8735 |
| SeizureFrequency.active_rate_fidelity | 0.6804 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1025; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0887; floor -0.0100 |
| Diagnosis headline | pass | 0.8735; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8735; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.8908; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.6804; baseline 0.2887 |
| Prescription changed-row control | fail | 105 changed rows |
| Investigations changed-row control | fail | 78 changed rows |

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
| versus_v042_default_quarantine | Diagnosis | 103 | assertion_or_negation_change=28, hierarchy_reconciliation_or_duplicate_collapse=28, hierarchy_reconciliation=71, projection_only=4 |
| versus_v042_default_quarantine | SeizureFrequency | 103 | active_rate=70, seizure_free=48, unknown_or_change_state=22, unknown=2, generic_vs_specific=3 |
| versus_v042_default_quarantine | Prescription | 105 | model_output=105 |
| versus_v042_default_quarantine | Investigations | 78 | model_output=78 |
| versus_existing_focused_route_comparator | Diagnosis | 126 | assertion_or_negation_change=81, hierarchy_reconciliation_or_duplicate_collapse=79, hierarchy_reconciliation=45 |
| versus_existing_focused_route_comparator | SeizureFrequency | 108 | active_rate=80, seizure_free=49, unknown_or_change_state=34, generic_vs_specific=6, unknown=10 |
| versus_existing_focused_route_comparator | Prescription | 109 | model_output=109 |
| versus_existing_focused_route_comparator | Investigations | 52 | model_output=50, projection_only=2 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
