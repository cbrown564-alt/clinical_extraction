# Gan 2026 Selective Safety-Floor Gate v0 Frozen-Test Audit First Readout (No-Call)

Frozen-test first readout over saved holdout artifacts only. This report intentionally suppresses row-level locked-test details; it is a hybrid deterministic-safety-floor generalization audit, not an LLM-first or benchmark-comparable claim.

- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`
- Slice manifest: `experiments/gan2026_selective_safety_floor_gate_v0_frozen_test_audit_manifest_2026-06-03.json`
- Predeclaration/input manifest: `experiments/gan2026_selective_safety_floor_gate_v0_frozen_test_audit_manifest_2026-06-03.json`
- Split manifest: `gan2026_split_v1`
- Rows: 450
- JSONL artifact: `experiments/gan2026_selective_safety_floor_gate_v0_test450_frozen_audit_first_readout_2026-06-03.jsonl`
- Summary JSON: `experiments/gan2026_selective_safety_floor_gate_v0_test450_frozen_audit_first_readout_2026-06-03.json`

## Slice-level Summary

| Slice | Variant | Rows | Purist correct | Pragmatic correct | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions | Evidence-exact changed | Source-id valid changed | Fallback |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| test450 | baseline_safety_floor_v2 | 450 | 343 | 354 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| test450 | projection_boundary_state_priority_gate_v0 | 450 | 345 | 357 | 9 | 6 | 0 | 1.0000 | 0 | 9 | 9 | 104 |
| test450 | competing_frequency_uncertainty | 450 | 270 | 276 | 82 | 2 | 67 | 0.0270 | 67 | 82 | 82 | 0 |
| test450 | lowest_current_frequency | 450 | 291 | 316 | 77 | 6 | 50 | 0.1071 | 50 | 77 | 77 | 0 |
| test450 | llm_candidate_sidecar_rescue_gate_v0 | 450 | 346 | 356 | 6 | 3 | 0 | 0.7500 | 0 | 6 | 6 | 444 |
| test450 | combined_selective_gate_v0 | 450 | 351 | 361 | 14 | 8 | 0 | 0.8889 | 0 | 14 | 14 | 436 |
| test450 | selective_safety_floor_gate_v0 | 450 | 351 | 361 | 14 | 8 | 0 | 0.8889 | 0 | 14 | 14 | 436 |

## Predeclared Test Slice Summary

| Slice | Variant | Rows | Purist correct | Pragmatic correct | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions | Evidence-exact changed | Source-id valid changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_test_rows | selective_safety_floor_gate_v0 | 450 | 351 | 361 | 14 | 8 | 0 | 0.8889 | 0 | 14 | 14 |
| all_test_rows | baseline_safety_floor_v2 | 450 | 343 | 354 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| all_test_rows | projection_boundary_state_priority_gate_v0 | 450 | 345 | 357 | 9 | 6 | 0 | 1.0000 | 0 | 9 | 9 |
| all_test_rows | llm_candidate_sidecar_rescue_gate_v0 | 450 | 346 | 356 | 6 | 3 | 0 | 0.7500 | 0 | 6 | 6 |
| all_test_rows | combined_selective_gate_v0 | 450 | 351 | 361 | 14 | 8 | 0 | 0.8889 | 0 | 14 | 14 |
| boundary:no_reference | selective_safety_floor_gate_v0 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| boundary:no_reference | baseline_safety_floor_v2 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| boundary:no_reference | projection_boundary_state_priority_gate_v0 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| boundary:no_reference | llm_candidate_sidecar_rescue_gate_v0 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| boundary:no_reference | combined_selective_gate_v0 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| boundary:unknown | selective_safety_floor_gate_v0 | 60 | 47 | 47 | 3 | 2 | 0 | 1.0000 | 0 | 3 | 3 |
| boundary:unknown | baseline_safety_floor_v2 | 60 | 45 | 45 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| boundary:unknown | projection_boundary_state_priority_gate_v0 | 60 | 47 | 47 | 3 | 2 | 0 | 1.0000 | 0 | 3 | 3 |
| boundary:unknown | llm_candidate_sidecar_rescue_gate_v0 | 60 | 46 | 46 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 |
| boundary:unknown | combined_selective_gate_v0 | 60 | 47 | 47 | 3 | 2 | 0 | 1.0000 | 0 | 3 | 3 |
| gold_kind:frequency | selective_safety_floor_gate_v0 | 281 | 226 | 236 | 4 | 1 | 0 | 0.5000 | 0 | 4 | 4 |
| gold_kind:frequency | baseline_safety_floor_v2 | 281 | 225 | 236 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:frequency | projection_boundary_state_priority_gate_v0 | 281 | 225 | 237 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 |
| gold_kind:frequency | llm_candidate_sidecar_rescue_gate_v0 | 281 | 225 | 235 | 3 | 0 | 0 | 0.0000 | 0 | 3 | 3 |
| gold_kind:frequency | combined_selective_gate_v0 | 281 | 226 | 236 | 4 | 1 | 0 | 0.5000 | 0 | 4 | 4 |
| gold_kind:no_reference | selective_safety_floor_gate_v0 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:no_reference | baseline_safety_floor_v2 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:no_reference | projection_boundary_state_priority_gate_v0 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:no_reference | llm_candidate_sidecar_rescue_gate_v0 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:no_reference | combined_selective_gate_v0 | 16 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:seizure_free | selective_safety_floor_gate_v0 | 67 | 40 | 40 | 3 | 2 | 0 | 1.0000 | 0 | 3 | 3 |
| gold_kind:seizure_free | baseline_safety_floor_v2 | 67 | 38 | 38 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:seizure_free | projection_boundary_state_priority_gate_v0 | 67 | 35 | 35 | 1 | 0 | 0 |  | 0 | 1 | 1 |
| gold_kind:seizure_free | llm_candidate_sidecar_rescue_gate_v0 | 67 | 40 | 40 | 2 | 2 | 0 | 1.0000 | 0 | 2 | 2 |
| gold_kind:seizure_free | combined_selective_gate_v0 | 67 | 40 | 40 | 3 | 2 | 0 | 1.0000 | 0 | 3 | 3 |
| gold_kind:unknown | selective_safety_floor_gate_v0 | 60 | 47 | 47 | 3 | 2 | 0 | 1.0000 | 0 | 3 | 3 |
| gold_kind:unknown | baseline_safety_floor_v2 | 60 | 45 | 45 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:unknown | projection_boundary_state_priority_gate_v0 | 60 | 47 | 47 | 3 | 2 | 0 | 1.0000 | 0 | 3 | 3 |
| gold_kind:unknown | llm_candidate_sidecar_rescue_gate_v0 | 60 | 46 | 46 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 |
| gold_kind:unknown | combined_selective_gate_v0 | 60 | 47 | 47 | 3 | 2 | 0 | 1.0000 | 0 | 3 | 3 |
| gold_kind:unresolved_multiple | selective_safety_floor_gate_v0 | 26 | 22 | 22 | 4 | 3 | 0 | 1.0000 | 0 | 4 | 4 |
| gold_kind:unresolved_multiple | baseline_safety_floor_v2 | 26 | 19 | 19 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:unresolved_multiple | projection_boundary_state_priority_gate_v0 | 26 | 22 | 22 | 4 | 3 | 0 | 1.0000 | 0 | 4 | 4 |
| gold_kind:unresolved_multiple | llm_candidate_sidecar_rescue_gate_v0 | 26 | 19 | 19 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| gold_kind:unresolved_multiple | combined_selective_gate_v0 | 26 | 22 | 22 | 4 | 3 | 0 | 1.0000 | 0 | 4 | 4 |
| label_form:numeric_rate | selective_safety_floor_gate_v0 | 263 | 218 | 227 | 3 | 1 | 0 | 0.5000 | 0 | 3 | 3 |
| label_form:numeric_rate | baseline_safety_floor_v2 | 263 | 217 | 227 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| label_form:numeric_rate | projection_boundary_state_priority_gate_v0 | 263 | 217 | 228 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 |
| label_form:numeric_rate | llm_candidate_sidecar_rescue_gate_v0 | 263 | 217 | 226 | 2 | 0 | 0 | 0.0000 | 0 | 2 | 2 |
| label_form:numeric_rate | combined_selective_gate_v0 | 263 | 218 | 227 | 3 | 1 | 0 | 0.5000 | 0 | 3 | 3 |
| label_form:vague_or_multiple | selective_safety_floor_gate_v0 | 44 | 30 | 31 | 5 | 3 | 0 | 1.0000 | 0 | 5 | 5 |
| label_form:vague_or_multiple | baseline_safety_floor_v2 | 44 | 27 | 28 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| label_form:vague_or_multiple | projection_boundary_state_priority_gate_v0 | 44 | 30 | 31 | 4 | 3 | 0 | 1.0000 | 0 | 4 | 4 |
| label_form:vague_or_multiple | llm_candidate_sidecar_rescue_gate_v0 | 44 | 27 | 28 | 1 | 0 | 0 |  | 0 | 1 | 1 |
| label_form:vague_or_multiple | combined_selective_gate_v0 | 44 | 30 | 31 | 5 | 3 | 0 | 1.0000 | 0 | 5 | 5 |
| llm_sidecar_gate:abstained | selective_safety_floor_gate_v0 | 444 | 348 | 358 | 8 | 5 | 0 | 1.0000 | 0 | 8 | 8 |
| llm_sidecar_gate:abstained | baseline_safety_floor_v2 | 444 | 343 | 353 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| llm_sidecar_gate:abstained | projection_boundary_state_priority_gate_v0 | 444 | 344 | 355 | 8 | 5 | 0 | 1.0000 | 0 | 8 | 8 |
| llm_sidecar_gate:abstained | llm_candidate_sidecar_rescue_gate_v0 | 444 | 343 | 353 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| llm_sidecar_gate:abstained | combined_selective_gate_v0 | 444 | 348 | 358 | 8 | 5 | 0 | 1.0000 | 0 | 8 | 8 |
| llm_sidecar_gate:fired | selective_safety_floor_gate_v0 | 6 | 3 | 3 | 6 | 3 | 0 | 0.7500 | 0 | 6 | 6 |
| llm_sidecar_gate:fired | baseline_safety_floor_v2 | 6 | 0 | 1 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| llm_sidecar_gate:fired | projection_boundary_state_priority_gate_v0 | 6 | 1 | 2 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 |
| llm_sidecar_gate:fired | llm_candidate_sidecar_rescue_gate_v0 | 6 | 3 | 3 | 6 | 3 | 0 | 0.7500 | 0 | 6 | 6 |
| llm_sidecar_gate:fired | combined_selective_gate_v0 | 6 | 3 | 3 | 6 | 3 | 0 | 0.7500 | 0 | 6 | 6 |
| projection_gate:abstained | selective_safety_floor_gate_v0 | 441 | 342 | 352 | 5 | 2 | 0 | 0.6667 | 0 | 5 | 5 |
| projection_gate:abstained | baseline_safety_floor_v2 | 441 | 340 | 351 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| projection_gate:abstained | projection_boundary_state_priority_gate_v0 | 441 | 336 | 348 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| projection_gate:abstained | llm_candidate_sidecar_rescue_gate_v0 | 441 | 342 | 352 | 5 | 2 | 0 | 0.6667 | 0 | 5 | 5 |
| projection_gate:abstained | combined_selective_gate_v0 | 441 | 342 | 352 | 5 | 2 | 0 | 0.6667 | 0 | 5 | 5 |
| projection_gate:fired | selective_safety_floor_gate_v0 | 9 | 9 | 9 | 9 | 6 | 0 | 1.0000 | 0 | 9 | 9 |
| projection_gate:fired | baseline_safety_floor_v2 | 9 | 3 | 3 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| projection_gate:fired | projection_boundary_state_priority_gate_v0 | 9 | 9 | 9 | 9 | 6 | 0 | 1.0000 | 0 | 9 | 9 |
| projection_gate:fired | llm_candidate_sidecar_rescue_gate_v0 | 9 | 4 | 4 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 |
| projection_gate:fired | combined_selective_gate_v0 | 9 | 9 | 9 | 9 | 6 | 0 | 1.0000 | 0 | 9 | 9 |
| seizure_free_duration:one_year_or_longer | selective_safety_floor_gate_v0 | 18 | 16 | 16 | 1 | 0 | 0 |  | 0 | 1 | 1 |
| seizure_free_duration:one_year_or_longer | baseline_safety_floor_v2 | 18 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| seizure_free_duration:one_year_or_longer | projection_boundary_state_priority_gate_v0 | 18 | 13 | 13 | 1 | 0 | 0 |  | 0 | 1 | 1 |
| seizure_free_duration:one_year_or_longer | llm_candidate_sidecar_rescue_gate_v0 | 18 | 16 | 16 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| seizure_free_duration:one_year_or_longer | combined_selective_gate_v0 | 18 | 16 | 16 | 1 | 0 | 0 |  | 0 | 1 | 1 |
| seizure_free_duration:shorter_than_one_year | selective_safety_floor_gate_v0 | 49 | 24 | 24 | 2 | 2 | 0 | 1.0000 | 0 | 2 | 2 |
| seizure_free_duration:shorter_than_one_year | baseline_safety_floor_v2 | 49 | 22 | 22 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| seizure_free_duration:shorter_than_one_year | projection_boundary_state_priority_gate_v0 | 49 | 22 | 22 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| seizure_free_duration:shorter_than_one_year | llm_candidate_sidecar_rescue_gate_v0 | 49 | 24 | 24 | 2 | 2 | 0 | 1.0000 | 0 | 2 | 2 |
| seizure_free_duration:shorter_than_one_year | combined_selective_gate_v0 | 49 | 24 | 24 | 2 | 2 | 0 | 1.0000 | 0 | 2 | 2 |
| sidecars:both_abstained | selective_safety_floor_gate_v0 | 436 | 340 | 350 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| sidecars:both_abstained | baseline_safety_floor_v2 | 436 | 340 | 350 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| sidecars:both_abstained | projection_boundary_state_priority_gate_v0 | 436 | 336 | 347 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| sidecars:both_abstained | llm_candidate_sidecar_rescue_gate_v0 | 436 | 340 | 350 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| sidecars:both_abstained | combined_selective_gate_v0 | 436 | 340 | 350 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| text_marker:ambiguity | selective_safety_floor_gate_v0 | 139 | 107 | 110 | 2 | 1 | 0 | 1.0000 | 0 | 2 | 2 |
| text_marker:ambiguity | baseline_safety_floor_v2 | 139 | 106 | 109 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| text_marker:ambiguity | projection_boundary_state_priority_gate_v0 | 139 | 106 | 110 | 2 | 1 | 0 | 1.0000 | 0 | 2 | 2 |
| text_marker:ambiguity | llm_candidate_sidecar_rescue_gate_v0 | 139 | 107 | 110 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 |
| text_marker:ambiguity | combined_selective_gate_v0 | 139 | 107 | 110 | 2 | 1 | 0 | 1.0000 | 0 | 2 | 2 |
| text_marker:cluster_language | selective_safety_floor_gate_v0 | 262 | 205 | 211 | 9 | 5 | 0 | 0.8333 | 0 | 9 | 9 |
| text_marker:cluster_language | baseline_safety_floor_v2 | 262 | 200 | 207 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| text_marker:cluster_language | projection_boundary_state_priority_gate_v0 | 262 | 201 | 209 | 7 | 5 | 0 | 1.0000 | 0 | 7 | 7 |
| text_marker:cluster_language | llm_candidate_sidecar_rescue_gate_v0 | 262 | 201 | 207 | 3 | 1 | 0 | 0.5000 | 0 | 3 | 3 |
| text_marker:cluster_language | combined_selective_gate_v0 | 262 | 205 | 211 | 9 | 5 | 0 | 0.8333 | 0 | 9 | 9 |
| text_marker:current_state | selective_safety_floor_gate_v0 | 441 | 342 | 352 | 14 | 8 | 0 | 0.8889 | 0 | 14 | 14 |
| text_marker:current_state | baseline_safety_floor_v2 | 441 | 334 | 345 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| text_marker:current_state | projection_boundary_state_priority_gate_v0 | 441 | 336 | 348 | 9 | 6 | 0 | 1.0000 | 0 | 9 | 9 |
| text_marker:current_state | llm_candidate_sidecar_rescue_gate_v0 | 441 | 337 | 347 | 6 | 3 | 0 | 0.7500 | 0 | 6 | 6 |
| text_marker:current_state | combined_selective_gate_v0 | 441 | 342 | 352 | 14 | 8 | 0 | 0.8889 | 0 | 14 | 14 |
| text_marker:historical_or_negated | selective_safety_floor_gate_v0 | 450 | 351 | 361 | 14 | 8 | 0 | 0.8889 | 0 | 14 | 14 |
| text_marker:historical_or_negated | baseline_safety_floor_v2 | 450 | 343 | 354 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| text_marker:historical_or_negated | projection_boundary_state_priority_gate_v0 | 450 | 345 | 357 | 9 | 6 | 0 | 1.0000 | 0 | 9 | 9 |
| text_marker:historical_or_negated | llm_candidate_sidecar_rescue_gate_v0 | 450 | 346 | 356 | 6 | 3 | 0 | 0.7500 | 0 | 6 | 6 |
| text_marker:historical_or_negated | combined_selective_gate_v0 | 450 | 351 | 361 | 14 | 8 | 0 | 0.8889 | 0 | 14 | 14 |

## Row-Level Inspection Boundary

Row-level locked-test details are intentionally omitted from this first readout. Any later row-level review is post-hoc final-evaluation analysis and must not drive tuning of this candidate.
