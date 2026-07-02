# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-07-02`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v08_dev140_p7_treatment`
- Gate decision: **do-not-promote**
- Claim boundary: P7 follow-up treatment: v08 dev140 manifest with ONLY prescription_repair_v03 swapped for a P7-fixed regeneration (deterministic/all_entities/prescription.py weight-context clause scope). Every other producer is the unchanged archived artifact -- zero new LLM calls.
- JSON: `experiments/exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `hybrid_diagnosis_route` |
| SeizureFrequency | `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl` | `sf_state_union_arbitration_v08` | `hybrid_sf_route+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_deterministic_prescription_repair_v03_dev140_p7fix_20260702.jsonl` | `prescription_regimen_v01` | `deterministic_prescription_repair_v03` |
| Investigations | `experiments/exectv2_llm_investigations_arbitration_v02_dev140_20260621.jsonl` | `investigations_result_v01` | `llm_investigations_verifier+deterministic_investigations_arbitration` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.8475 | 0.7790 | 0.7836 | 0.9615 | 0.9132 |
| evidence_valid | `evidence_valid_score` | 0.8913 | 0.8984 | 0.7836 | 0.9615 | 0.9132 |
| benchmark_cui | `cui_projection_companion` | 0.8913 | 0.8984 | 0.7836 | 0.9615 | 0.9132 |
| clinical_headline | `headline_target` | 0.9189 | 0.8984 | 0.9080 | 0.9615 | 0.9132 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.8468 | 0.7770 | 0.7836 | 0.9615 | 0.9132 |
| `evidence_valid` | 0.8468 | 0.7770 | 0.7836 | 0.9615 | 0.9132 |
| `protocol_model_preserving_canonical` | 0.8468 | 0.7770 | 0.7836 | 0.9615 | 0.9132 |
| `dictionary_normalized` | 0.8830 | 0.8755 | 0.7836 | 0.9615 | 0.9132 |
| `residual_benchmark_added` | 0.8913 | 0.8984 | 0.7836 | 0.9615 | 0.9132 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 1045 |
| `evidence_valid` | 0 | 1045 |
| `protocol_model_preserving_canonical` | 0 | 1045 |
| `dictionary_normalized` | 0 | 979 |
| `residual_benchmark_added` | 45 | 979 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3555 |
| Benchmark after CUI/projection | 0.4729 |
| Diagnosis.concept_negation | 0.8853 |
| SeizureFrequency.active_rate_fidelity | 0.5907 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1401; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0517; floor -0.0100 |
| Diagnosis headline | pass | 0.8984; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8853; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.9080; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5907; baseline 0.2887 |
| Prescription changed-row control | fail | 102 changed rows |
| Investigations changed-row control | fail | 72 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 0 | 2 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 0 | 0 | 0 | 1.0000 |
| Investigations | 0 | 0 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 130 | assertion_or_negation_change=95, hierarchy_reconciliation_or_duplicate_collapse=94, hierarchy_reconciliation=34, projection_only=1 |
| versus_v042_default_quarantine | SeizureFrequency | 112 | active_rate=86, seizure_free=54, projection_action=30, unknown_or_change_state=31, reject_or_drop=9, unknown=5, generic_vs_specific=1 |
| versus_v042_default_quarantine | Prescription | 102 | model_output=102 |
| versus_v042_default_quarantine | Investigations | 72 | model_output=72 |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
