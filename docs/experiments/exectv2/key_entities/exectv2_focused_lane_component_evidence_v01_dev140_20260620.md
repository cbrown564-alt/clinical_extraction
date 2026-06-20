# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-20`
- Split/stage: `dev` / `dev140`
- Candidate: `focused_lane_component_evidence_v01_dev140`
- Gate decision: **promote-dev-focused-lane-architecture**
- Claim boundary: dev-only architecture evidence; no full-200, test, or benchmark claim.
- JSON: `experiments/exectv2_focused_lane_component_evidence_v01_dev140_20260620.json`
- JSONL: `experiments/exectv2_focused_lane_component_evidence_v01_dev140_20260620.jsonl`

## Frozen Sources

| Lane | Source | Ownership |
| --- | --- | --- |
| Diagnosis | `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl` | `hybrid_diagnosis_route` |
| SeizureFrequency | `experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl` | `hybrid_sf_route` |
| Prescription | `experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl` | `llm_first_control` |
| Investigations | `experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl` | `llm_first_control` |

## Score Ladder

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw_lane_score | 0.7114 | 0.7625 | 0.5690 | 0.7316 | 0.7546 |
| evidence_valid_score | 0.7623 | 0.7572 | 0.6354 | 0.8214 | 0.8615 |
| cui_projection_companion | 0.7623 | 0.7572 | 0.6354 | 0.8214 | 0.8615 |
| headline_target | 0.8006 | 0.7572 | 0.8068 | 0.8214 | 0.8615 |

## Benchmark And Fidelity

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.2968 |
| Benchmark after CUI/projection | 0.3157 |
| Diagnosis.concept_negation | 0.7572 |
| SeizureFrequency.active_rate_fidelity | 0.3931 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0000; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0000; floor -0.0100 |
| Diagnosis headline | pass | 0.7572; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.7572; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.8068; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.3931; baseline 0.2887 |
| Prescription changed-row control | pass | 0 changed rows |
| Investigations changed-row control | pass | 0 changed rows |

## Lane Diagnostics

| Lane | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 0 | 2 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 1 | 4 | 0 | 1.0000 |
| Investigations | 1 | 4 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 129 | assertion_or_negation_change=101, hierarchy_reconciliation_or_duplicate_collapse=101, hierarchy_reconciliation=28 |
| versus_v042_default_quarantine | SeizureFrequency | 118 | active_rate=89, seizure_free=57, projection_action=30, unknown_or_change_state=34, reject_or_drop=9, unknown=5, generic_vs_specific=1 |
| versus_v042_default_quarantine | Prescription | 0 | none |
| versus_v042_default_quarantine | Investigations | 0 | none |
| versus_existing_focused_route_comparator | Diagnosis | 0 | none |
| versus_existing_focused_route_comparator | SeizureFrequency | 0 | none |
| versus_existing_focused_route_comparator | Prescription | 134 | model_output=133, projection_only=1 |
| versus_existing_focused_route_comparator | Investigations | 98 | model_output=92, projection_only=6 |

The row-level JSONL carries per-mention source artifact, source lane, ownership, and deterministic projection/suppression provenance.
