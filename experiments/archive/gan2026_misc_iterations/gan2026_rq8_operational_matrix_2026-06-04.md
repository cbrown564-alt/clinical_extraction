# Gan 2026 RQ8 Operational Matrix

Validation-development no-new-call operational matrix over saved artifacts. This does not create a benchmark-comparable or new holdout claim.

- JSON: `experiments/gan2026_rq8_operational_matrix_2026-06-04.json`
- Rows: 21 component/surface summaries
- Known limitation: prompt/completion tokens, wall-clock latency, cost, and retry counts are mostly missing from saved artifacts.

## Matrix

| Component | Surface | Rows | Parse fail | Exact evidence | Source ids | Burden | Projection/Action | Complexity note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_conditioned_evidence_only | balanced_control | 50 | 0 | 0.94 | 1.0 | cand mean 0; evid mean 1.02 | projection label rate 0.0 | single component-control prompt; projection/bundled variants are overload controls |
| candidate_conditioned_evidence_only | hard_control | 75 | 0 | 0.9733 | 1.0 | cand mean 0; evid mean 1.013 | projection label rate 0.0 | single component-control prompt; projection/bundled variants are overload controls |
| candidate_only | balanced_control | 50 | 0 | 0.94 | 0.84 | cand mean 1.2; evid mean 0 | projection label rate 0.0 | single component-control prompt; projection/bundled variants are overload controls |
| candidate_only | hard_control | 75 | 0 | 0.8933 | 0.92 | cand mean 1.68; evid mean 0 | projection label rate 0.0 | single component-control prompt; projection/bundled variants are overload controls |
| candidate_plus_evidence | balanced_control | 50 | 0 | 0.8 | 0.82 | cand mean 1.38; evid mean 1.36 | projection label rate 0.0 | single component-control prompt; projection/bundled variants are overload controls |
| candidate_plus_evidence | hard_control | 75 | 0 | 0.84 | 0.92 | cand mean 1.773; evid mean 1.773 | projection label rate 0.0 | single component-control prompt; projection/bundled variants are overload controls |
| candidate_plus_evidence_plus_projection | balanced_control | 50 | 0 | 0.7 | 0.72 | cand mean 1.02; evid mean 1.1 | projection label rate 0.1 | single component-control prompt; projection/bundled variants are overload controls |
| candidate_plus_evidence_plus_projection | hard_control | 75 | 0 | 0.6933 | 0.76 | cand mean 1.32; evid mean 1.387 | projection label rate 0.1333 | single component-control prompt; projection/bundled variants are overload controls |
| evidence_plus_projection | balanced_control | 50 | 0 | 1.0 | 1.0 | cand mean 0; evid mean 1 | projection label rate 0.2 | single component-control prompt; projection/bundled variants are overload controls |
| evidence_plus_projection | hard_control | 75 | 0 | 0.9867 | 1.0 | cand mean 0; evid mean 1.027 | projection label rate 0.1733 | single component-control prompt; projection/bundled variants are overload controls |
| gold_query_evidence_only | balanced_control | 50 | 0 | 0.94 | 1.0 | cand mean 0; evid mean 2.52 | projection label rate 0.0 | single component-control prompt; projection/bundled variants are overload controls |
| gold_query_evidence_only | hard_control | 75 | 0 | 0.92 | 1.0 | cand mean 0; evid mean 3.213 | projection label rate 0.0 | single component-control prompt; projection/bundled variants are overload controls |
| projection_only | balanced_control | 50 | 0 | 0.0 | 0.0 | cand mean 0; evid mean 0 | projection label rate 0.56 | single component-control prompt; projection/bundled variants are overload controls |
| projection_only | hard_control | 75 | 0 | 0.0 | 0.0 | cand mean 0; evid mean 0 | projection label rate 0.6933 | single component-control prompt; projection/bundled variants are overload controls |
| projection_only_instruction_heavy | balanced_control | 50 | 0 | 0.0 | 0.0 | cand mean 0; evid mean 0 | projection label rate 0.4 | single component-control prompt; projection/bundled variants are overload controls |
| projection_only_instruction_heavy | hard_control | 75 | 0 | 0.0 | 0.0 | cand mean 0; evid mean 0 | projection label rate 0.4933 | single component-control prompt; projection/bundled variants are overload controls |
| selective_boundary_candidate_proposer_v2 | predeclared_22_row_boundary_candidate_rescue_slice | 22 | 1 | 0.9545 | None | cand mean 3.227 | n/a | selective proposer plus deterministic evidence/source/metadata gates; higher candidate burden than evidence-only prompts |
| rich_selected_state_v0 | hidden_family_hard_panel_75 | 75 | 3 | 0.96 | None | n/a | n/a | moderate typed selected-state schema plus deterministic renderer/policy; overuses state_kind=frequency so boundary fields must be validated |
| typed_operations_v0 | validation250 | 250 | 3 | 0.94 | None | nodes mean 1.48 | graph purist 0.832 | deep schema with duplicated decision ownership, graph sidecar, max10000 budget, 3 parse/schema failures, and negative projection delta |
| selective_safety_floor_gate_v0 | validation750_no_call | 750 | 0 | 1.0 | 1.0 | n/a | changed 21, W->C 11, C->W 0 | no-call hybrid safety-floor policy over saved projection and LLM sidecar artifacts |
| selective_safety_floor_gate_v0 | test450_frozen_no_call | 450 | 0 | 1.0 | 1.0 | n/a | changed 14, W->C 8, C->W 0 | no-call hybrid safety-floor policy over saved projection and LLM sidecar artifacts |

## Operational Gaps

- Prompt/completion token counts, wall-clock latency, cost, and retry counts are not uniformly present in saved artifacts. RQ8 cannot make cost-per-1000-note claims without a follow-up measurement run or recovered telemetry.
