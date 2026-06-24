# ExECTv2 Holistic Finding Assembly Replay

- Generated: `2026-06-24`
- Split/stage: `full_200_authorized_no_verifiers` / `full_200_authorized_no_verifiers200`
- Candidate: `exectv2_holistic_finding_assembly_v08_full200_currentcode_no_verifiers_gpt41mini`
- Gate decision: **do-not-promote**
- Claim boundary: Authorized full-200 aggregate no-verifier ablation. Diagnosis verifier and Investigations verifier lanes are omitted; Diagnosis reconciliation uses decomposer candidates only and Investigations comes directly from the structured extractor. Current-code v08-shape run, not byte-identical to archived dev140 prompt/module versions.
- JSON: `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_no_verifiers_gpt41mini_20260624.json`
- JSONL: `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_no_verifiers_gpt41mini_20260624.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. The final assembly stage is structural and introduces no live model calls; the Diagnosis no-verifier reconciler was generated live from decomposer-only candidates, while the other reused or no-call surfaces are named in the producer table.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_v08_full200_currentcode_diagnosis_reconciler_no_verifier_gpt41mini_20260624.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `diagnosis_decomposer_only_reconciler_no_verifier` |
| SeizureFrequency | `experiments/exectv2_v08_full200_currentcode_sf_union_arbitration_20260624.jsonl` | `sf_state_union_arbitration_v08` | `hybrid_sf_route+deterministic_union_arbitration` |
| Prescription | `experiments/exectv2_v08_full200_currentcode_deterministic_prescription_repair_v03_20260624.jsonl` | `prescription_regimen_v01` | `deterministic_prescription_repair_v03` |
| Investigations | `experiments/exectv2_v08_full200_currentcode_investigations_structured_direct_no_verifier_gpt41mini_20260624.jsonl` | `investigations_result_v01` | `single_gpt_structured_no_verifier` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.7816 | 0.7593 | 0.6567 | 0.8926 | 0.8563 |
| evidence_valid | `evidence_valid_score` | 0.8117 | 0.8410 | 0.6567 | 0.8926 | 0.8563 |
| benchmark_cui | `cui_projection_companion` | 0.8117 | 0.8410 | 0.6567 | 0.8926 | 0.8563 |
| clinical_headline | `headline_target` | 0.8431 | 0.8410 | 0.7850 | 0.8926 | 0.8563 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.7810 | 0.7578 | 0.6567 | 0.8926 | 0.8563 |
| `evidence_valid` | 0.7810 | 0.7578 | 0.6567 | 0.8926 | 0.8563 |
| `protocol_model_preserving_canonical` | 0.7810 | 0.7578 | 0.6567 | 0.8926 | 0.8563 |
| `dictionary_normalized` | 0.7982 | 0.8047 | 0.6567 | 0.8926 | 0.8563 |
| `residual_benchmark_added` | 0.8117 | 0.8410 | 0.6567 | 0.8926 | 0.8563 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 1439 |
| `evidence_valid` | 0 | 1439 |
| `protocol_model_preserving_canonical` | 0 | 1439 |
| `dictionary_normalized` | 0 | 1372 |
| `residual_benchmark_added` | 26 | 1372 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4598 |
| Benchmark after CUI/projection | 0.4664 |
| Diagnosis.concept_negation | 0.8410 |
| SeizureFrequency.active_rate_fidelity | 0.5564 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.0712; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control -0.0052; floor -0.0100 |
| Diagnosis headline | pass | 0.8410; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8410; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.7850; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.5564; baseline 0.2887 |
| Prescription changed-row control | fail | 189 changed rows |
| Investigations changed-row control | pass | 0 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 0 | 3 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 0 | 0 | 0 | 1.0000 |
| Investigations | 0 | 0 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 178 | assertion_or_negation_change=129, hierarchy_reconciliation_or_duplicate_collapse=129, hierarchy_reconciliation=49 |
| versus_v042_default_quarantine | SeizureFrequency | 140 | active_rate=106, seizure_free=73, unknown_or_change_state=43, projection_action=32, generic_vs_specific=5, reject_or_drop=7 |
| versus_v042_default_quarantine | Prescription | 189 | model_output=189 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.
