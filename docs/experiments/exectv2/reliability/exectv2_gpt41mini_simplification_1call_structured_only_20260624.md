# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-06-24`
- Split/stage: `full_200_authorized_simplification` / `full_200_authorized_simplification200`
- Candidate: `exectv2_gpt41mini_simplification_1call_structured_only`
- Gate decision: **simplification-frontier-aggregate-readout**
- Claim boundary: Authorized full-200 aggregate-only diagnostic simplification candidate. All four families come directly from the saved structured GPT draft; deterministic Prescription repair is removed.
- JSON: `experiments/exectv2_gpt41mini_simplification_1call_structured_only_20260624.json`
- JSONL: `experiments/exectv2_gpt41mini_simplification_1call_structured_only_20260624.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `single_gpt_structured_direct_diagnosis` |
| SeizureFrequency | `experiments/exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl` | `sf_state_direct_v01` | `single_gpt_structured_direct_sf` |
| Prescription | `experiments/exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl` | `prescription_regimen_v01` | `single_gpt_structured_direct_prescription` |
| Investigations | `experiments/exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl` | `investigations_result_v01` | `single_gpt_structured_direct_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.6967 | 0.6878 | 0.4630 | 0.8219 | 0.8563 |
| evidence_valid | `evidence_valid_score` | 0.7231 | 0.7597 | 0.4630 | 0.8219 | 0.8563 |
| benchmark_cui | `cui_projection_companion` | 0.7231 | 0.7597 | 0.4630 | 0.8219 | 0.8563 |
| clinical_headline | `headline_target` | 0.7571 | 0.7597 | 0.6114 | 0.8219 | 0.8563 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.6967 | 0.6878 | 0.4630 | 0.8219 | 0.8563 |
| `evidence_valid` | 0.6967 | 0.6878 | 0.4630 | 0.8219 | 0.8563 |
| `protocol_model_preserving_canonical` | 0.6967 | 0.6878 | 0.4630 | 0.8219 | 0.8563 |
| `dictionary_normalized` | 0.7090 | 0.7221 | 0.4630 | 0.8219 | 0.8563 |
| `residual_benchmark_added` | 0.7231 | 0.7597 | 0.4630 | 0.8219 | 0.8563 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 1396 |
| `evidence_valid` | 0 | 1396 |
| `protocol_model_preserving_canonical` | 0 | 1396 |
| `dictionary_normalized` | 0 | 1354 |
| `residual_benchmark_added` | 29 | 1354 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3829 |
| Benchmark after CUI/projection | 0.3918 |
| Diagnosis.concept_negation | 0.7597 |
| SeizureFrequency.active_rate_fidelity | 0.3178 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0005; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control -0.0052; floor -0.0100 |
| Diagnosis headline | pass | 0.7597; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.7597; baseline 0.6693 |
| SeizureFrequency headline | fail | 0.6114; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.3178; baseline 0.2887 |
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
| versus_v042_default_quarantine | Diagnosis | 61 | assertion_or_negation_change=50, hierarchy_reconciliation_or_duplicate_collapse=49, hierarchy_reconciliation=11 |
| versus_v042_default_quarantine | SeizureFrequency | 0 | none |
| versus_v042_default_quarantine | Prescription | 0 | none |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Simplification Contract

- Stage: `stage_5_structured_only`
- Role: `post_stop_absolute_minimum_diagnostic`
- Calls per letter: `1.0`
- Full-200 calls: `200.0`
- Live call components: `structured_key_family_event_ledger`
- Replayed/no-call components: `finding_assembly`
- Removed components: `diagnosis_verifier, diagnosis_decomposer, diagnosis_reconciler, sf_state_adjudicator, sf_state_projection, sf_unknown_suppression, sf_union_arbitration, deterministic_prescription_repair, investigations_verifier, investigations_arbitration`
- Acceptability: **fail**

| Guardrail | Value | Floor | Status |
| --- | ---: | ---: | --- |
| overall | 0.7571 | 0.8350 | fail |
| Diagnosis | 0.7597 | 0.8300 | fail |
| SeizureFrequency | 0.6114 | 0.7500 | fail |
| Prescription | 0.8219 | 0.8800 | fail |
| Investigations | 0.8563 | 0.8400 | pass |
