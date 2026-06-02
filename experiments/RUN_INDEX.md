# Gan 2026 Run Registry

Generated from `experiments/registry.jsonl`. The JSONL file remains the canonical machine-readable registry.

## Revise

### `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `25` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `seizure-free duration projection ablation over saved state graphs`; replay `analysis_only`.
- Model role: diagnostic seizure-free duration projection replay over saved graph rows; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `diagnostic seizure-free duration projection variants only; no scorer, graph-builder, or production projection-policy change`.
- Primary metrics: baseline_exact_matches=0, exact_node_not_selected_rows=3, non_seizure_free_selected_rows=4, numeric_duration_present_gold_absent_rows=2, numeric_duration_priority_exact_matches=7, only_broad_duration_nodes_rows=16, oracle_exact_node_matches=7, row_count=25, seizure_free_priority_exact_matches=6, shortest_duration_exact_matches=7.
- Evidence validity: Replayed saved graph nodes from exact-evidence-gated diagnostic artifacts; this artifact measures duration projection behavior, not new evidence extraction.
- Cache/reuse source: Saved validation hard-slice projection/arbitration surface reused; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02`.
- Claim language: Diagnostic validation-cycle replay only. Projection-only policies recover at most 7/25 exact seizure-free duration labels because most misses lack an exact gold duration node; the next repair target is seizure-free duration graph-node construction/normalization, not a production projection-policy promotion.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `18` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `seizure-free duration graph-node construction/normalization replay`; replay `analysis_only`.
- Model role: diagnostic seizure-free duration node-construction replay over saved graph rows; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `seizure_free_duration_node_normalization_v0 merged into saved diagnostic graphs; unchanged projection policy`.
- Primary metrics: baseline_exact_gold_duration_rows=0, exact_evidence_valid_nodes=21, month_scale_representability_gains=16, month_scale_representable_rows=18, new_duration_nodes=21, replayed_exact_gold_duration_rows=17, still_only_over_broad_year_rows=0, unchanged_projection_changed_from_baseline=0, unchanged_projection_exact_matches=0.
- Evidence validity: New duration-node replay emitted 21/21 exact-evidence-valid nodes over the 18 predeclared validation rows, with 0 row-level evidence errors.
- Cache/reuse source: Saved validation hard-slice projection/arbitration graph rows; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_ablation_design_2026-06-02`.
- Claim language: Diagnostic validation-cycle replay only. Node construction recovered month-scale representability on all 18 target rows, but unchanged projection still recovered 0/18 exact duration labels, so projection/arbitration remains separate and no production policy is promoted.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_ablation_design_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `18` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `seizure-free duration graph-node construction/normalization ablation design`; replay `analysis_only`.
- Model role: analysis-only graph-node ablation designer; model `none`.
- Repair mode/config: `planning only; no scorer, graph-builder, or projection repair`.
- Primary metrics: existing_rule_families=5, gold_multiple_month_rows=17, numeric_duration_present_gold_absent_rows=2, only_broad_duration_nodes_rows=16, target_rows=18.
- Evidence validity: Design requires exact-evidence validity for newly emitted duration nodes before any diagnostic replay can be interpreted.
- Cache/reuse source: No hosted calls; design derived from saved validation hard-slice duration projection ablation rows.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02`.
- Claim language: Diagnostic design only. Predeclares an 18-row validation hard-slice node-construction surface and acceptance criteria for month-scale seizure-free duration representability; no scorer, projection, production graph-builder, or holdout policy change.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_ablation_design_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `18` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `seizure-free duration enriched projection replay`; replay `analysis_only`.
- Model role: diagnostic duration-selection replay over enriched seizure-free duration graphs; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `diagnostic duration-selection variants over replayed_graph, including month_bucket_duration_selection; no scorer, graph-builder, or production projection-policy change`.
- Primary metrics: baseline_exact_matches=0, exact_node_not_selected_rows=17, month_bucket_duration_selection_exact_matches=18, numeric_duration_present_gold_absent_rows=1, oracle_exact_node_matches=17, row_count=18, shortest_duration_exact_matches=14.
- Evidence validity: Uses replayed graphs from the exact-evidence-valid duration-node artifact; this artifact measures projection selection over enriched graphs, not new evidence extraction.
- Cache/reuse source: Saved validation hard-slice seizure-free duration node replay JSONL; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02`.
- Claim language: Diagnostic validation-cycle replay only. The month_bucket_duration_selection variant recovers 18/18 exact duration labels on this enriched validation surface by preferring broad month-bucket nodes over numeric-month or broad-year conflicts and preserving plural numeric-month output on row 5040; no scorer normalization or production projection policy is changed.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `42` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `projection/arbitration ablation over saved state graphs`; replay `analysis_only`.
- Model role: diagnostic projection/arbitration replay over already-representable graph rows; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `diagnostic projection variants only; no scorer, graph-builder, or production projection-policy change`.
- Primary metrics: accepted_replay_projection_misses=4, baseline_exact_matches=0, boundary_state_priority_exact_matches=17, boundary_state_priority_purist_f1=0.8571, hard_slice_representable_projection_misses=38, lowest_current_frequency_exact_matches=3, oracle_gold_node_exact_matches=23, oracle_gold_node_purist_f1=1.0, row_count=42, seizure_free_priority_exact_matches=8.
- Evidence validity: Replayed only saved graph nodes from exact-evidence-gated diagnostic artifacts; this artifact measures arbitration/projection behavior, not new evidence extraction.
- Cache/reuse source: Saved validation hard-slice state-graph diagnostics plus accepted boundary-node replay JSONL; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02`.
- Claim language: Diagnostic validation-cycle replay only. Boundary-state priority is the strongest non-oracle signal, but oracle exact-label gaps show seizure-free duration projection remains separate work; do not promote a production policy from this artifact alone.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_month_bucket_duration_selection_decision_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `18` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `month-bucket duration selection projection-ablation decision`; replay `analysis_only`.
- Model role: analysis-only duration-selection policy decision; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `decision only; month_bucket_duration_selection remains diagnostic and seeds a separately named projection ablation; no scorer, graph-builder, or production projection-policy change`.
- Primary metrics: baseline_exact_matches=0, enriched_replay_rows=18, month_bucket_duration_selection_exact_matches=18, oracle_exact_node_matches=17.
- Evidence validity: Decision relies on exact-evidence-valid duration nodes from the replayed graph artifact; the next ablation must preserve selected-node evidence validity.
- Cache/reuse source: Decision derived from saved enriched validation hard-slice projection replay; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02`.
- Claim language: Diagnostic validation-cycle decision. month_bucket_duration_selection becomes a separately named projection-ablation seed, not scorer normalization, benchmark evidence, or production policy.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_month_bucket_duration_selection_decision_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_live_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices+synthetic_hard_cases`; `39` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `live boundary-state graph-builder validation31 plus synthetic unknown8 stress`; replay `live`.
- Model role: hosted boundary-state graph node builder; model `openai/gpt-4.1-mini`.
- Repair mode/config: `exact-evidence-gated unknown/unresolved_multiple node construction; no final-label projection`.
- Primary metrics: call_failures=0, synthetic_exact_evidence_total=0, synthetic_exact_evidence_valid=0, synthetic_representability_gain_candidates=0, synthetic_row_count=8, synthetic_schema_valid_rows=8, validation_exact_evidence_total=29, validation_exact_evidence_valid=28, validation_representability_gain_candidates=10, validation_row_count=31, validation_schema_valid_rows=30.
- Evidence validity: Validation31 produced 28/29 exact-evidence-valid nodes with 30/31 schema-valid rows and one row-level schema/evidence miss; synthetic unknown8 was schema-valid but emitted 0 nodes.
- Cache/reuse source: DSPy cache enabled; validation31 and synthetic unknown8 live runs recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_live_smoke_2026-06-02`.
- Claim language: Hosted graph-builder diagnostic only. It emitted no final Gan labels and did not run projection or arbitration; keep revise-only pending accepted-node graph replay and separate projection/arbitration ablations.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_gpt41mini_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_gpt41mini_live_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_gpt41mini_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_gpt41mini_live_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_interpretation_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_2026-06-02`
- Date/split: `2026-06-02`; `synthetic_hard_cases`; `8` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `live boundary-state graph-builder synthetic unknown8 v1 unknown-recall stress`; replay `live`.
- Model role: hosted boundary-state graph node builder; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v1 unknown-recall prompt + root-level JSON output contract; no final-label projection`.
- Primary metrics: call_failures=0, exact_evidence_total=8, exact_evidence_valid=8, representability_gain_candidates=8, row_count=8, schema_valid_rows=8.
- Evidence validity: Synthetic unknown8 v1 produced 8/8 exact-evidence-valid unknown nodes with 8/8 schema-valid rows, 0 call failures, and 8/8 representability-gain candidates.
- Cache/reuse source: DSPy cache enabled; synthetic unknown8 v1 live run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_live_2026-06-02`.
- Claim language: Hosted graph-builder diagnostic only. The v1 prompt fixes synthetic unknown-state node recall and root-level output shape, emits no final Gan labels, and does not run graph merge, projection, arbitration, or benchmark scoring.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_gpt41mini_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_gpt41mini_live_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_live_smoke_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `1` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `live boundary-state graph-builder smoke`; replay `live`.
- Model role: hosted boundary-state graph node builder; model `openai/gpt-4.1-mini`.
- Repair mode/config: `exact-evidence-gated unknown/unresolved_multiple node construction; no final-label projection`.
- Primary metrics: call_failures=0, exact_evidence_total=2, exact_evidence_valid=2, representability_gain_candidates=1, row_count=1, schema_valid_rows=1.
- Evidence validity: Live one-row smoke produced 2/2 exact-evidence nodes and 1/1 representability-gain candidate, with 1/1 schema-valid rows and 0 call failures.
- Cache/reuse source: DSPy cache enabled; live smoke recorded 0 reused raw outputs. Prompt-only replay seed is available at experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_smoke_reuse_2026-06-02.jsonl.
- Supersedes: `gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02`.
- Claim language: Hosted graph-builder component smoke only. It emits exact-evidence unknown/unresolved_multiple nodes and no final Gan label; projection F1 and arbitration are intentionally out of scope.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_live_smoke_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_live_smoke_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `10` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `accepted boundary-node graph replay`; replay `analysis_only`.
- Model role: diagnostic graph replay over accepted hosted boundary-state nodes; model `none; saved openai/gpt-4.1-mini boundary-builder outputs reused`.
- Repair mode/config: `accepted_boundary_state_nodes_v0 merged into deterministic graph; unchanged projection policy`.
- Primary metrics: accepted_boundary_rows=10, accepted_hosted_nodes=18, baseline_representable_rows=0, projection_changed_from_baseline=7, projection_exact_label_matches=6, projection_pragmatic_f1=0.9, projection_purist_f1=0.9, replayed_representable_rows=10, representability_gains=10.
- Evidence validity: Accepted replay used only validation gain-candidate rows with schema-valid exact-evidence nodes; row 869 and synthetic unknown stress rows were excluded.
- Cache/reuse source: Saved validation31 hosted boundary-state graph-builder JSONL; no new hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_live_2026-06-02`.
- Claim language: Diagnostic graph replay only. It shows accepted nodes recover graph representability on the 10 gain rows; projection/arbitration changes remain separate ablation work and this is not a benchmark result.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02.md`.

### `gan2026_clinical_frequency_state_graph_validation_cycle_diagnostics_2026-06-02`
- Date/split: `2026-06-02`; `validation+synthetic_hard_cases`; `381` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `validation-only state-graph diagnostics`; replay `analysis_only`.
- Model role: diagnostic graph scaffold plus saved LLM atomic claims; model `none; saved openai/gpt-4.1-mini claim-table outputs reused for atomic-claim conversion`.
- Repair mode/config: `deterministic_oracle_span_harvester_v0 + gan2026_state_graph_projection_v0 + llm_atomic_claim_graph_builder_v0`.
- Primary metrics: counterfactual_order_invariance=1.0, counterfactual_paraphrase_invariance=0.98, hard_slice_oracle_coverage=0.876, hard_slice_projection_purist_f1=0.916, llm_atomic_claim_exact_nodes=79, llm_atomic_claim_nodes=80, synthetic_oracle_coverage=0.5357, synthetic_projection_purist_f1=0.6964, validation50_oracle_coverage=0.94, validation50_projection_purist_f1=0.96.
- Evidence validity: Deterministic graph nodes preserve exact evidence offsets; saved LLM atomic-claim conversion produced 79/80 exact-evidence-certain nodes and downgraded one non-exact claim to uncertain.
- Cache/reuse source: No hosted calls for deterministic diagnostics; LLM atomic-claim rows reused saved validation25 claim-table output.
- Supersedes: `gan2026_clinical_frequency_state_graph_protocol_2026-06-02`.
- Claim language: Diagnostic architecture cycle only. Separates oracle coverage, projection-only F1, exact-evidence-gated LLM claim rows, counterfactual invariance, and validation-only grouping; no benchmark or holdout claim.
- Artifacts: `experiments/gan2026_clinical_frequency_state_graph_validation25_diagnostics_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_validation25_diagnostics_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_validation25_diagnostics_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_validation50_counterfactual_invariance_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_validation50_counterfactual_invariance_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_validation50_counterfactual_invariance_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_family_aware_validation_grouping_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_family_aware_validation_grouping_2026-06-02.md`.

### `gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices+synthetic_hard_cases`; `306` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `row/family diagnostic review`; replay `analysis_only`.
- Model role: analysis-only reviewer; model `none`.
- Repair mode/config: `planning only; no scorer or projection repair`.
- Primary metrics: hard_slice_missing_representability_rows=31, hard_slice_missing_unknown_rows=20, hard_slice_missing_unresolved_multiple_rows=11, representable_projection_miss_rows=34, synthetic_missing_frequency_rows=16, synthetic_missing_unknown_rows=8.
- Evidence validity: Review uses graph rows with exact-evidence offsets; next hosted builder must measure exact-evidence validity for newly proposed unknown/unresolved_multiple nodes.
- Cache/reuse source: No hosted calls; reviewed existing validation-only state-graph diagnostic artifacts and synthetic hard-case diagnostics.
- Supersedes: `gan2026_clinical_frequency_state_graph_validation_cycle_diagnostics_2026-06-02`.
- Claim language: Diagnostic planning artifact only. Chooses the next hosted graph-builder target from validation-only row/family review; no benchmark or holdout claim.
- Artifacts: `experiments/gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02.md`.

### `gan2026_clinical_frequency_state_graph_protocol_2026-06-02`
- Date/split: `2026-06-02`; `validation protocol`; `0` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `protocol and deterministic scaffold`; replay `analysis_only`.
- Model role: diagnostic graph scaffold; model `none`.
- Repair mode/config: `graph_oracle_coverage + deterministic_projection + counterfactual_invariance`.
- Primary metrics: scaffold_tests=5.
- Evidence validity: Graph nodes are tested for exact evidence offsets; no corpus run yet.
- Supersedes: `gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_generalization_audit_2026-06-02`.
- Claim language: Architecture scaffold only, not a benchmark result. Next results must separate graph coverage, projection, invariance, and arbitration effects.
- Artifacts: `experiments/gan2026_clinical_frequency_state_graph_protocol_2026-06-02.md`.

### `gan2026_hybrid_adjudicator_v02_validation250_live_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `250` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `live rules candidates then conservative LLM adjudicator`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: adjudicator_pragmatic_correct=245, adjudicator_purist_correct=244, call_failures=0, candidate_set_purist_recall=246, changed_final_labels=8, deterministic_correct_to_adjudicator_wrong=2, deterministic_pragmatic_correct=246, deterministic_purist_correct=246, deterministic_wrong_to_adjudicator_correct=0, parse_failures=0, raw_adjudicator_purist_correct=245, raw_changed_final_labels=9, row_count=250.
- Evidence validity: Deterministic candidate evidence 250/250 exact in component ablation; raw/gated adjudicator evidence not independently scored in this artifact.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_validation50_live_2026-06-01`.
- Claim language: Revise before any broader run or holdout: validation250 live underperformed deterministic top, made 8 gated label changes, introduced 2 deterministic-correct regressions, and produced 0 deterministic-wrong to gated-correct Purist corrections.
- Artifacts: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.jsonl`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_live_component_ablation_2026-06-01.json`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_live_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_audit_trail_interpretation_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v02_synthetic_hard_case_component_stress_2026-06-01`
- Date/split: `2026-06-01`; `synthetic_hard_cases`; `56` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `live synthetic hard-case component stress`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: candidate_set_purist_recall=42, deterministic_correct_to_adjudicator_wrong=0, deterministic_purist_correct=39, gated_changed_labels=5, gated_purist_correct=42, parse_failures=5, raw_changed_labels=7, raw_correct_to_wrong=0, raw_purist_correct=44, raw_wrong_to_correct=5, row_count=56.
- Evidence validity: Row-level failure review completed: schema failures are enum/output-contract hygiene; cluster/diary misses are candidate-recall limited; proxy boundary demotions need a separate gate ablation.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_saturated_surface_analysis_2026-06-01`.
- Claim language: Diagnostic/revise-only synthetic hard-case component stress. Row-level review chose cluster/diary candidate-generation recall as the single next v0.2 revision target; schema repair and proxy/boundary gate relaxation stay separate named ablations.
- Artifacts: `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_failure_review_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v02_saturated_surface_analysis_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `250` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `validation hard-slice and selective-action analysis`; replay `analysis_only`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `conservative_overreach_gates + deterministic_fallback; no new repair`.
- Primary metrics: candidate_absent_or_weak_rows=4, deterministic_miss_rows=4, flag_only_actions=10, gated_action_rate=0.032, gated_changed_labels=8, gated_correct_to_wrong=2, gated_wrong_to_correct=0, raw_action_rate=0.036, raw_changed_labels=9, raw_correct_to_wrong=2, raw_wrong_to_correct=1, row_count=250, synthetic_hard_cases=56.
- Evidence validity: Accepted-change evidence proxy counted 2 evidence-valid raw/gated changes; exact LLM evidence validity still requires hard-case/component-stress review.
- Cache/reuse source: Saved v0.2 validation250 live JSONL; no hosted calls.
- Supersedes: `gan2026_hybrid_adjudicator_v02_validation250_live_2026-06-01`.
- Claim language: Analysis-only saturated-surface report: raw changes show one useful correction but gated changes have 0 corrections and 2 regressions. Keep v0.2 revise-only and move to manual review of the synthetic hard-case panel or stricter selective-action design before any holdout audit.
- Artifacts: `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slices_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01.jsonl`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_case_schema_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slice_schema_2026-06-01.json`.

### `gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_case_component_stress_2026-06-01`
- Date/split: `2026-06-01`; `synthetic_hard_cases`; `56` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `live synthetic hard-case component stress with cluster_diary_candidate_recall`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `cluster_diary_candidate_recall + conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: candidate_set_purist_recall=50, deterministic_correct_to_adjudicator_wrong=0, deterministic_purist_correct=39, gated_changed_labels=13, gated_purist_correct=50, parse_failures=1, raw_changed_labels=15, raw_correct_to_wrong=0, raw_purist_correct=52, raw_wrong_to_correct=13, row_count=56.
- Evidence validity: Candidate revision preserves exact evidence substrings for added cluster/diary candidates; raw/gated adjudicator evidence still not independently scored beyond selected candidate support and gate checks.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_synthetic_hard_case_component_stress_2026-06-01`.
- Claim language: Diagnostic/revise-only named hybrid v0.2 candidate-recall revision outside frozen deterministic V1. The branch fixed all targeted cluster/diary recall misses on the synthetic panel and improved gated hard-case performance without regressions, but remaining proxy/boundary, seizure-free, shorthand, and schema failures stay separate ablation targets.
- Artifacts: `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl`, `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_gpt41mini_live_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_component_stress_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_component_stress_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v01_validation750_schema_replay_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `750` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `rules candidates then LLM adjudicator schema replay`; replay `schema_replay`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `parser defaults + clean_scorer_facing`.
- Primary metrics: deterministic_top_purist_correct=697, parse_failures=0, pragmatic_correct=689, purist_correct=680, row_count=750.
- Evidence validity: See full-validation interpretation report.
- Cache/reuse source: saved raw outputs from hybrid v0.1 validation750.
- Supersedes: `gan2026_hybrid_adjudicator_v01_validation250_schema_replay_2026-06-01`.
- Claim language: Revise before holdout; underperformed deterministic top on full validation because adjudicator introduced 24 deterministic-correct regressions against 7 corrections.
- Artifacts: `experiments/gan2026_arch2_validation750_gpt41mini_v01_schema_replay_2026-06-01.jsonl`, `experiments/gan2026_arch2_validation750_gpt41mini_v01_schema_replay_2026-06-01.md`, `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v01_validation250_schema_replay_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `250` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `rules candidates then LLM adjudicator schema replay`; replay `schema_replay`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `parser defaults + clean_scorer_facing`.
- Primary metrics: candidate_set_purist_recall=246, parse_failures=0, pragmatic_correct=244, purist_correct=243, row_count=250.
- Evidence validity: Candidate-set Purist recall 246/250.
- Cache/reuse source: saved raw outputs from hybrid v0.1 validation250.
- Superseded by: `gan2026_hybrid_adjudicator_v01_validation750_schema_replay_2026-06-01`.
- Claim language: Strongest 250-row validation candidate, but deterministic-correct regressions and candidate-recall misses required full failure review before any promotion.
- Artifacts: `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.jsonl`, `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`, `experiments/gan2026_arch2_validation250_v01_failure_review_2026-06-01.md`.

### `gan2026_claim_table_v4_validation250_schema_replay_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `250` rows.
- Pipeline: `llm_only_claim_table_selector`; mode `prompt-only schema replay`; replay `schema_replay`.
- Model role: LLM-only claim-table selector; model `openai/gpt-4.1-mini`.
- Repair mode/config: `strict_format + clean_scorer_facing`.
- Primary metrics: clean_pragmatic_correct=238, clean_purist_correct=231, parse_schema_failures=0, row_count=250, structured_rows=250.
- Evidence validity: 247/250 selected evidence exact in live diagnostic; replay repaired non-semantic output shape.
- Cache/reuse source: saved raw outputs from v4 validation250.
- Supersedes: `gan2026_claim_table_v4_validation250_live_2026-06-01`.
- Superseded by: `gan2026_claim_table_v4_validation750_2026-06-01`.
- Claim language: Development diagnostic cleared 0.9000 on 250 rows after schema replay, but semantic failure families keep it revise-only.
- Artifacts: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.jsonl`, `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`.

## Reject

### `gan2026_claim_table_v4_validation750_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `750` rows.
- Pipeline: `llm_only_claim_table_selector`; mode `prompt-only`; replay `cache_first`.
- Model role: LLM-only claim-table selector; model `openai/gpt-4.1-mini`.
- Repair mode/config: `clean_scorer_facing`.
- Primary metrics: clean_pragmatic_correct=577, clean_purist_correct=528, row_count=750.
- Evidence validity: See full-validation interpretation report.
- Cache/reuse source: DSPy cache/live completion mix recorded in artifact metadata.
- Supersedes: `gan2026_claim_table_v4_validation250_schema_replay_2026-06-01`.
- Claim language: Reject for holdout; full validation exposed cluster-axis and boundary-state collapse.
- Artifacts: `experiments/gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.jsonl`, `experiments/gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.md`, `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`.

## Historical

### `gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_generalization_audit_2026-06-02`
- Date/split: `2026-06-02`; `validation+test`; `1200` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `frozen generalization audit with cluster_diary_candidate_recall`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `cluster_diary_candidate_recall + conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: test_candidate_set_purist_recall=359, test_correct_to_wrong=9, test_deterministic_purist_correct=343, test_gated_pragmatic_correct=353, test_gated_purist_correct=343, test_wrong_to_correct=9, validation_candidate_set_purist_recall=707, validation_deterministic_purist_correct=697, validation_gated_pragmatic_correct=686, validation_gated_purist_correct=677.
- Evidence validity: Aggregate and slice-level locked-test audit only; no test row text inspection for tuning.
- Cache/reuse source: DSPy cache enabled; validation/test artifacts recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_case_component_stress_2026-06-01`.
- Claim language: Frozen comparator-only generalization audit. Do not tune v0.2 gates, prompts, candidate generation, or repair policy from locked-test behavior; use the state-graph validation cycle for new development.
- Artifacts: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation750_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation750_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.md`, `experiments/gan2026_generalization_gap_research_report_2026-06-02.md`.

### `gan2026_hybrid_adjudicator_v02_validation50_live_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `50` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `live rules candidates then conservative LLM adjudicator`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: adjudicator_pragmatic_correct=49, adjudicator_purist_correct=48, call_failures=0, changed_final_labels=3, deterministic_correct_to_adjudicator_wrong=2, deterministic_pragmatic_correct=50, deterministic_purist_correct=50, deterministic_wrong_to_adjudicator_correct=0, parse_failures=0, row_count=50.
- Evidence validity: Deterministic candidate evidence 50/50 exact in component ablation; raw/gated adjudicator evidence not independently scored in this artifact.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Claim language: Validation50 is output-contract clean but the prefix is saturated; 2 deterministic-correct Purist regressions are a row-review note, not enough evidence for a revise decision. Escalate to 250 rows before tuning gates.
- Artifacts: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.jsonl`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_v02_live_component_ablation_2026-06-01.json`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_v02_live_component_ablation_2026-06-01.md`.

### `gan2026_rules_only_v1_baseline_2026-05-31`
- Date/split: `2026-05-31`; `validation+test`; `1200` rows.
- Pipeline: `rules_only`; mode `rules_only_v1`; replay `analysis_only`.
- Model role: deterministic comparator; model `none`.
- Repair mode/config: `deterministic_v1`.
- Primary metrics: test_pragmatic=0.7867, test_purist=0.76, validation_pragmatic=0.9387, validation_purist=0.9293.
- Evidence validity: Report-level deterministic evidence summary.
- Claim language: Frozen rules_only_v1 comparator; aggregate locked-test context is historical, not a tuning surface.
- Artifacts: `experiments/gan2026_v1_deterministic_baseline_2026-05-31.md`.
