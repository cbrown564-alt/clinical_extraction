# Gan 2026 Selective Safety-Floor Gate v0 Validation Replay (No-Call)

Validation-cycle full-validation replay over saved artifacts only. This is a validation development result and does not imply production promotion or holdout performance.

- Source artifact: `experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation50_gpt-41-mini_paired_gate_v0_live_2026-06-03.jsonl`
- Slice manifest: `experiments\gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.json`
- Predeclaration/input manifest: `experiments\gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.json`
- Split manifest: `gan2026_split_v1`
- Rows: 50
- JSONL artifact: `experiments\gan2026_selective_safety_floor_gate_v0_validation50_gpt-41-mini_paired_replay_live_2026-06-03.jsonl`
- Summary JSON: `experiments\gan2026_selective_safety_floor_gate_v0_validation50_gpt-41-mini_paired_replay_live_2026-06-03.json`

## Slice-level Summary

| Slice | Variant | Rows | Purist correct | Pragmatic correct | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions | Evidence-exact changed | Source-id valid changed | Fallback |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| validation50 | baseline_safety_floor_v2 | 50 | 50 | 50 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| validation50 | projection_boundary_state_priority_gate_v0 | 50 | 50 | 50 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| validation50 | competing_frequency_uncertainty | 50 | 43 | 43 | 5 | 0 | 5 | 0.0000 | 5 | 5 | 5 | 0 |
| validation50 | lowest_current_frequency | 50 | 46 | 48 | 4 | 0 | 2 | 0.0000 | 2 | 4 | 4 | 0 |
| validation50 | llm_candidate_sidecar_rescue_gate_v0 | 50 | 50 | 50 | 0 | 0 | 0 |  | 0 | 0 | 0 | 50 |
| validation50 | combined_selective_gate_v0 | 50 | 50 | 50 | 0 | 0 | 0 |  | 0 | 0 | 0 | 50 |
| validation50 | selective_safety_floor_gate_v0 | 50 | 50 | 50 | 0 | 0 | 0 |  | 0 | 0 | 0 | 50 |

## Frozen Fixed-Slice Summary

Prior fixed-slice accounting from the frozen manifest source. `combined_selective_gate_v0` is the candidate seed for `selective_safety_floor_gate_v0`.

| Slice | Candidate seed Purist | Candidate seed Pragmatic | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| candidate_generation_rescue | 6 | 10 | 9 | 6 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | 6 | 6 | 8 | 6 | 0 | 1.0000 | 0 |
| projection_arbitration | 5 | 8 | 5 | 5 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | 4 | 6 | 4 | 4 | 0 | 1.0000 | 0 |

## Hidden-Family Summary

| Slice | Family | Variant | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| validation50 | unclassified | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation50 | unclassified | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation50 | unclassified | competing_frequency_uncertainty | 5 | 0 | 5 | 0.0000 | 5 |
| validation50 | unclassified | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation50 | unclassified | lowest_current_frequency | 4 | 0 | 2 | 0.0000 | 2 |
| validation50 | unclassified | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation50 | unclassified | selective_safety_floor_gate_v0 | 0 | 0 | 0 |  | 0 |

## Would-Change Rows

### Projection Boundary-State Priority
No rows changed.

### LLM Candidate Sidecar Rescue
No rows changed.

### Combined Selective Gate
No rows changed.

### Selective Safety-Floor Gate v0
No rows changed.
