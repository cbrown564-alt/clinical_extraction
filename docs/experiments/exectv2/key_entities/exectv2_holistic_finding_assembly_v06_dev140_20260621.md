# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-21`
- Split/stage: `dev` / `dev140`
- Candidate: `exectv2_holistic_finding_assembly_v06_dev140`
- Gate decision: **diagnostic-dev-sf-union-arbitration**
- Claim boundary: Dev-only component-attributed architecture evidence. This artifact does not authorize a benchmark claim, full-200 audit, or locked-test analysis.
- JSON: `experiments/exectv2_holistic_finding_assembly_v06_dev140_20260621.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v06_dev140_20260621.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `hybrid_diagnosis_route` |
| SeizureFrequency | `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl` | `sf_state_union_arbitration_v08` | `hybrid_sf_route+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl` | `prescription_regimen_v01` | `llm_first_control` |
| Investigations | `experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl` | `investigations_result_v01` | `llm_first_control` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7582 | 0.7625 | 0.7814 | 0.7316 | 0.7546 |
| evidence_valid | `evidence_valid_score` | 0.8515 | 0.9083 | 0.7814 | 0.8214 | 0.8615 |
| benchmark_cui | `cui_projection_companion` | 0.8515 | 0.9083 | 0.7814 | 0.8214 | 0.8615 |
| clinical_headline | `headline_target` | 0.8789 | 0.9083 | 0.9053 | 0.8214 | 0.8615 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3362 |
| Benchmark after CUI/projection | 0.3658 |
| Diagnosis.concept_negation | 0.9083 |
| SeizureFrequency.active_rate_fidelity | 0.5969 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0000; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0000; floor -0.0100 |
| Diagnosis headline | pass | 0.9083; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.9083; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.9053; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5969; baseline 0.2887 |
| Prescription changed-row control | pass | 0 changed rows |
| Investigations changed-row control | pass | 0 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 0 | 2 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 1 | 4 | 0 | 1.0000 |
| Investigations | 1 | 4 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 129 | assertion_or_negation_change=94, hierarchy_reconciliation_or_duplicate_collapse=93, hierarchy_reconciliation=35 |
| versus_v042_default_quarantine | SeizureFrequency | 112 | active_rate=86, seizure_free=54, projection_action=30, unknown_or_change_state=31, reject_or_drop=9, unknown=5, generic_vs_specific=1 |
| versus_v042_default_quarantine | Prescription | 0 | none |
| versus_v042_default_quarantine | Investigations | 0 | none |
| versus_existing_focused_route_comparator | Diagnosis | 0 | none |
| versus_existing_focused_route_comparator | SeizureFrequency | 80 | active_rate=57, seizure_free=41, projection_action=23, unknown_or_change_state=26, reject_or_drop=5, unknown=1 |
| versus_existing_focused_route_comparator | Prescription | 0 | none |
| versus_existing_focused_route_comparator | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
