# Gan 2026 Run Registry

Generated from `experiments/registry.jsonl`. The JSONL file remains the canonical machine-readable registry.

## Promote

### `gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_boundary_guide_rescue_replay`; mode `no_call_replay`; replay `saved_output_replay`.
- Model role: D0 no-call boundary-guide rescue replay over saved E1/E2 validation hard50 traces; tests rescue-only policies using direct_no_tool_context and single_self_consistency_temperature fallbacks.; model `none`.
- Repair mode/config: `saved-output policy replay; no scorer or label repair changes`.
- Primary metrics: best_promotable_policy=higher_burden_only, cluster_restore_only_correct_to_wrong=0, cluster_restore_only_wrong_to_correct=2, higher_burden_only_changed_label_precision=0.75, higher_burden_only_changed_labels=4, higher_burden_only_correct_to_wrong=0, higher_burden_only_net_purist_gain=3, higher_burden_only_pragmatic_correct=36, higher_burden_only_purist_correct=35, higher_burden_only_wrong_to_correct=3, holdout_authorized=no, promoted_policy_count=1, rows=50.
- Evidence validity: No new prediction evidence. Replay uses saved validation hard50 E1/E2 final labels, normalized vote features, repair notes, and manifest slice tags for validation-only analysis.
- Cache/reuse source: experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.jsonl; experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl.
- Claim language: Validation-development no-call replay only. higher_burden_only passed the D0 gate (3 wrong-to-correct, 0 correct-to-wrong, precision 0.750), but this does not by itself authorize holdout use, benchmark claims, or live validation250 escalation.
- Artifacts: `experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.jsonl`, `experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.md`.

### `gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `12` rows.
- Pipeline: `agentic_boundary_audit_prompt_v2`; mode `saved_output_reparse`; replay `saved_output_replay`.
- Model role: D1 one-call boundary-audit prompt v2 over the predeclared validation micro-panel; fixed boundary-guide context only, parser candidates disabled.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `format-only audit-field shape repair plus existing label/evidence repair; parser candidates disabled as prompt context`.
- Primary metrics: call_failures=0, changed_label_precision=0.4286, changed_labels_vs_reference=7, e2_loss_sentinel_regressions=0, holdout_authorized=no, losses_vs_single_self_consistency_temperature=1, panel_gate=pass, parse_or_validation_failures=0, pragmatic_correct=10, purist_correct=10, rows=12, wins_vs_single_self_consistency_temperature=3.
- Evidence validity: 10/12 exact evidence substrings after saved-output reparse; no new prediction evidence during reparse.
- Cache/reuse source: live raw outputs in experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.jsonl.
- Supersedes: `gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12`.
- Claim language: Validation micro-panel development result only. Panel gate passed and authorized D1 hard50, but this artifact does not authorize broader validation or holdout use.
- Artifacts: `experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.jsonl`, `experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.md`.

## Promote Hybrid Structured Events Direction

### `gan2026_failure_mode_comparison_table_2026-06-12`
- Date/split: `2026-06-12`; `validation+test_aggregate`; `1200` rows.
- Pipeline: `gan2026_failure_mode_comparison`; mode `analysis-only`; replay `analysis_only`.
- Model role: Paper-facing consolidation of existing Gan 2026 failure-mode evidence for deterministic, fully LLM, hybrid_structured_events, CandidateSet hybrid, tool-using single-agent, and matched multi-agent comparators.; model `none`.
- Primary metrics: agentic_hard50_multi_agent_matched_purist=22, agentic_hard50_single_agent_tools_purist=20, agentic_hard50_single_greedy_purist=34, holdout_row_level_analysis=no, se_test450_purist_correct_of_rendered=364, se_test450_rendered=448, se_validation750_purist_correct_of_rendered=661, se_validation750_rendered=748.
- Evidence validity: No new run. Consolidates architecture-specific evidence metrics from existing validation750, aggregate test450, and validation hard50 artifacts; evidence metrics are not treated as interchangeable.
- Claim language: Analysis-only close-off table. Validation results are development evidence; locked test450 values are aggregate-only. Does not authorize row-level holdout tuning or any benchmark-comparable claim. Describes hybrid_structured_events as hybrid LLM extraction plus deterministic normalization/projection.
- Artifacts: `docs/research/gan2026_failure_mode_comparison_table_2026-06-12.md`.

### `gan2026_closeoff_report_2026-06-12`
- Date/split: `2026-06-12`; `validation+test`; `1200` rows.
- Pipeline: `gan2026_closeoff_synthesis`; mode `analysis-only`; replay `analysis_only`.
- Model role: Synthesis-only close-off report over existing Gan 2026 comparison, prompt-optimization, and frozen aggregate audit artifacts.; model `none`.
- Primary metrics: deepseek_se_v06_validation250_delta_purist_correct=5, gpt41mini_test450_se_pragmatic_correct_of_rendered=381, gpt41mini_test450_se_purist_correct_of_rendered=364, gpt41mini_test450_se_rendered=448, gpt41mini_validation750_se_purist_correct_of_rendered=661, gpt41mini_validation750_se_rendered=748, promoted_architecture=hybrid_structured_events, qwen_se_v06_validation250_delta_purist_correct=5.
- Evidence validity: Surfaces that evidence metrics differ by architecture: evidence_valid, evidence_text_contained, and CandidateSet source-id validity are not interchangeable.
- Claim language: Close-off implementation-direction synthesis. Promotes hybrid_structured_events as the current Gan 2026 direction while preserving split discipline: validation is development evidence; completed test450 audit is aggregate-only; no row-level holdout tuning or new benchmark claim is authorized.
- Artifacts: `docs/research/gan2026_closeoff_report_2026-06-12.md`.

## Promote To Phase3 Report

### `gan2026_hybrid_v5_validation750_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `hybrid`; mode `live`; replay `assessment_stage_only`.
- Model role: hybrid clinical assessment probe (v5): CandidateSet -> clinical assessment schema; deterministic downstream (normalize/project/render/score/route) applied in deep-replay.; model `openai/gpt-4.1-mini`.
- Primary metrics: call_errors=0, parse_errors=1, prompt_version=gan2026_candidate_set_clinical_assessment_probe_v5, rows=750.
- Evidence validity: Assessment-stage probe only -- CandidateSet source-id validity rates are computed in deep-replay during report build, not in this artifact directly.
- Supersedes: `gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08`.
- Claim language: Phase 3 hybrid v5 prompt run (validation750, gpt-4.1-mini). Prompt bumped from v4 to gan2026_candidate_set_clinical_assessment_probe_v5. Four new instructions added to address Phase 3 failure modes: FM-6 (highest-frequency-type selection, not highest-severity), FM-2a (menstrual/cyclic risk-window seizure-free FP suppression), FM-2b (recent burst + seizure-free run stays frequency_rate not seizure_free), FM-5b (cluster_frequency only for true recurring grouped-episode patterns, not incidental use of word cluster). 750/750 rows, 0 call errors, 1 parse error, all at v5. Supersedes Phase 1 hybrid run (v4 prompt, gan2026_candidate_set_clinical_assessment_probe_v4).
- Artifacts: `experiments/gan2026_hybrid_v5_validation750_gpt41mini_2026-06-09.jsonl`.

## Revise

### `gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: Local Qwen LLM structured-events extractor and selector using SE v0.6; deterministic code limited to Gan normalization, evidence validation, and scoring/repair after structured model selection.; model `ollama_chat/qwen3.6:35b`.
- Repair mode/config: `hybrid_full_stack`.
- Primary metrics: call_failures=0, evidence_valid_rows=581, json_dialect_repairs=746, parse_or_validation_failures=4, pragmatic_accuracy=0.8747, pragmatic_correct=656, prompt_version=gan2026_hybrid_structured_events_v0.6, purist_accuracy=0.8507, purist_correct=638, rendered_rows=746, structured_records=746.
- Evidence validity: 581/750 rows carry an evidence_valid substring-presence trace; 0 call failures; 4 unrendered rows in the combined summary. Qwen still relies heavily on JSON dialect repair.
- Cache/reuse source: Resumed from completed validation250 prefix artifact experiments/gan2026_v06_validation250_hybrid_structured_events_qwen3635b_2026-06-11.jsonl; --resume-existing skipped 250 completed rows and ran the remaining 500 validation rows live through local Ollama.
- Supersedes: `gan2026_v06_validation250_hybrid_structured_events_qwen3635b_2026-06-11`.
- Claim language: User-approved close-off confirmation for SE v0.6 on the full validation750 surface. Validation development evidence only, not a holdout or benchmark claim. Qwen SE v0.6 improves over the Phase 1 validation750 SE result, with 638/746 Purist rendered-correct versus the earlier 624/746 and 656/746 Pragmatic rendered-correct.
- Artifacts: `experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl`, `experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.md`.

### `gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: LLM structured-events extractor and selector using SE v0.6; deterministic code limited to Gan normalization, evidence validation, and scoring/repair after structured model selection.; model `deepseek/deepseek-chat`.
- Repair mode/config: `hybrid_full_stack`.
- Primary metrics: call_failures=0, evidence_valid_rows=719, parse_or_validation_failures=5, pragmatic_accuracy=0.8613, pragmatic_correct=646, prompt_version=gan2026_hybrid_structured_events_v0.6, purist_accuracy=0.8293, purist_correct=622, rendered_rows=745, structured_records=745.
- Evidence validity: 719/750 rows carry an evidence_valid substring-presence trace; 0 call failures; 5 unrendered rows in the combined summary.
- Cache/reuse source: Resumed from completed validation250 prefix artifact experiments/gan2026_v06_validation250_hybrid_structured_events_deepseek_2026-06-10.jsonl; --resume-existing skipped 250 completed rows and ran the remaining 500 validation rows live.
- Supersedes: `gan2026_v06_validation250_hybrid_structured_events_deepseek_2026-06-10`.
- Claim language: User-approved close-off confirmation for SE v0.6 on the full validation750 surface. Validation development evidence only, not a holdout or benchmark claim. Compared to the earlier DeepSeek SE Phase 1 validation750 result, v0.6 improves Purist from 609/742 rendered to 622/745 rendered and Pragmatic from 634/742 to 646/745.
- Artifacts: `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.jsonl`, `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.md`.

### `gan2026_agentic_pipeline_phase_plan_2026-06-12`
- Date/split: `2026-06-12`; `none`; `0` rows.
- Pipeline: `gan2026_agentic_pipeline_plan`; mode `analysis-only`; replay `analysis_only`.
- Model role: Research and implementation plan defining the final Gan 2026 agentic phases: matched-budget self-consistency, tool-using single-agent pipelines, and matched-budget multi-agent comparison.; model `none`.
- Primary metrics: holdout_authorized=no, planned_phase_5=agent definition and matched-budget protocol, planned_phase_6=tool-using single-agent versus matched-budget multi-agent evaluation.
- Evidence validity: No data run. The plan requires future tool traces to report evidence validity with architecture-specific definitions and explicit attribution.
- Claim language: Planning artifact only. Does not authorize new holdout use, test-row inspection, or benchmark-facing claims. Establishes that multi-agent claims must be compared against single-agent self-consistency under matched model-call, token, tool-call, and aggregation budgets.
- Artifacts: `docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`.

### `gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `25` rows.
- Pipeline: `agentic_matched_budget`; mode `live`; replay `native_run_split`.
- Model role: Gan Phase 6 validation25 post-voting live single-agent comparison restricted to single_greedy, single_self_consistency_temperature, and single_agent_tools; cross-model and multi-agent conditions intentionally skipped until the single-agent comparator is stable.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair + deterministic normalized-label vote`.
- Primary metrics: call_failures=0, condition_disagreement_rows=5, conditions=3, decision_records=150, holdout_authorized=no, model_calls_attempted=150, normalized_label_vote_repairs=70, parse_or_validation_failures=0, pragmatic_correct_call_level=150, prediction_bearing_rows=25, purist_correct_call_level=150, row187_status=scoring_equivalent_disagreement, row_final_pragmatic_correct=25, row_final_purist_correct=25, rows=25, single_agent_tools_purist_correct=25, single_greedy_purist_correct=25, single_self_consistency_temperature_purist_correct=25, tool_smoke_calls=52.
- Evidence validity: Prediction-bearing validation development smoke: 150/150 decision records, 0 call failures, 0 blocking parse/validation failures, 52 parser/guide tool smoke calls, 70 normalized-label vote repairs, and no holdout use.
- Supersedes: `gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12`.
- Claim language: Validation development result only, not a benchmark claim. Deterministic normalized-label voting stabilizes all three active single-agent condition finals at 25/25 Purist/Pragmatic with no call or blocking parse failures. Five condition-label disagreements remain scoring-equivalent; row 187 remains 1 per 7 to 9 day versus 2 per month. This clears the planned single-agent comparator gate before spending matched multi_agent_matched calls.
- Artifacts: `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12.jsonl`, `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12.md`.

### `gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `25` rows.
- Pipeline: `agentic_matched_budget`; mode `live`; replay `native_run_split`.
- Model role: Gan Phase 6 validation25 live single-agent comparison restricted to single_greedy, single_self_consistency_temperature, and single_agent_tools; cross-model and multi-agent conditions intentionally skipped until the single-agent comparator is understood.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair only`.
- Primary metrics: call_failures=0, condition_disagreement_rows=3, conditions=3, decision_records=150, holdout_authorized=no, model_calls_attempted=150, parse_or_validation_failures=0, pragmatic_correct_call_level=147, prediction_bearing_rows=25, purist_correct_call_level=147, row_final_pragmatic_correct=24, row_final_purist_correct=24, rows=25, single_agent_tools_purist_correct=24, single_greedy_purist_correct=24, single_self_consistency_temperature_purist_correct=25, tool_smoke_calls=52.
- Evidence validity: Prediction-bearing validation development smoke: 150/150 decision records, 0 call failures, 0 blocking parse/validation failures, 52 parser/guide tool smoke calls, and no holdout use. Format repairs were common and should be treated as direct-label parser/schema repair, not semantic promotion.
- Supersedes: `gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12`.
- Claim language: Validation development result only, not a benchmark claim. The condition filter prevented multi_agent_matched and single_self_consistency_cross_model calls; single_self_consistency_temperature was 25/25 Purist-correct at condition-final level, while single_greedy and single_agent_tools were each 24/25. Next work should inspect/repair label-format normalization and disagreement rows before spending matched multi-agent calls.
- Artifacts: `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12.jsonl`, `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12.md`.

### `gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `25` rows.
- Pipeline: `agentic_matched_budget`; mode `prompt-only`; replay `native_run_split`.
- Model role: Gan Phase 6 prompt-only/no-call matched-budget runner surface covering single_greedy, single_self_consistency_temperature, single_self_consistency_cross_model, single_agent_tools, and multi_agent_matched conditions.; model `openai/gpt-4.1-mini`.
- Primary metrics: conditions=5, holdout_authorized=no, prediction_bearing_rows=0, rows=25, tool_smoke_calls=104.
- Evidence validity: No prediction-bearing evidence metric. Tool contract smoke emitted parser/guide traces only: 104 tool smoke calls and 0 prediction-bearing rows.
- Claim language: Phase 6 runner-surface contract artifact only. Validation25 prompt-only run made no model calls and produces no accuracy claim. It verifies shared CLI wiring, matched budget trace shape, parser-as-tool output, boundary-guide retrieval, and no-prediction attribution before live agentic comparisons.
- Artifacts: `experiments/gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12.jsonl`, `experiments/gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12.md`.

### `gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `1` rows.
- Pipeline: `agentic_matched_budget`; mode `live`; replay `native_run_split`.
- Model role: Gan Phase 6 live matched-budget smoke over all five initial conditions: single_greedy, single_self_consistency_temperature, single_self_consistency_cross_model, single_agent_tools, and multi_agent_matched.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair only`.
- Primary metrics: call_failures=0, conditions=5, decision_records=14, holdout_authorized=no, model_calls_attempted=14, parse_or_validation_failures=0, pragmatic_correct_call_level=11, prediction_bearing_rows=1, purist_correct_call_level=11, rows=1.
- Evidence validity: First live transport smoke only; 14 model calls attempted, 14 decision records, 0 call failures, 0 parse/validation failures, and tool traces preserved for tool-using conditions.
- Supersedes: `gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12`.
- Claim language: Validation development live smoke only, not an accuracy comparison or benchmark claim. Confirms that the agentic matched-budget runner can make live calls, parse prediction-bearing labels, score call-level outputs, and preserve tool/no-tool trace attribution. Validation25 live comparison remains the next scale-up before any multi-agent value claim.
- Artifacts: `experiments/gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12.jsonl`, `experiments/gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12.md`.

### `gan2026_agentic_hard50_tool_context_ablation_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_tool_context_ablation`; mode `live`; replay `live`.
- Model role: E1 one-call direct-label context ablation over fixed validation hard50: no tool context, parser only, boundary guide only, and parser plus boundary guide.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair + deterministic normalized-label vote`.
- Primary metrics: call_failures=0, decision_records=200, direct_boundary_guide_only_purist_correct=34, direct_no_tool_context_purist_correct=30, direct_parser_only_purist_correct=21, direct_parser_plus_boundary_guide_purist_correct=19, holdout_authorized=no, model_calls_attempted=200, non_harmful_contexts=['direct_boundary_guide_only'], parse_or_validation_failures=0, rows=50.
- Evidence validity: Prediction-bearing validation hard50 development run: 200/200 decision records, 0 call failures, 0 parse/schema/label failures. Evidence substring metric not computed for this ablation artifact.
- Claim language: Validation-development hard-slice result only. Parser context was harmful, while boundary-guide-only was non-harmful and improved to 34/50 Purist; E2 therefore used boundary guides only and excluded parser candidates.
- Artifacts: `experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.jsonl`, `experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.md`.

### `gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_redesign_protocol`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only validation-cycle redesign after E2 hard50 stop; reframes follow-up work as rescue-only boundary auditing with parser context excluded.; model `none`.
- Primary metrics: e1_boundary_guide_only_purist_correct=34, e1_parser_only_purist_correct=21, e2_losses_vs_reference=2, e2_purist_correct=34, e2_wins_vs_reference=4, holdout_authorized=no, rows=50.
- Evidence validity: No new prediction evidence. Consolidates E5/E1/E2 validation hard50 artifacts and predeclares D0-D4 surfaces, gates, and attribution requirements.
- Supersedes: `gan2026_agentic_hard50_tool_self_consistency_2026-06-12`.
- Claim language: Validation-development design artifact only. It supersedes only unrun E3/E4 live designs from the prior hard50 plan and does not authorize holdout use, scorer changes, or validation250/full-validation escalation without a D-series hard50 gate.
- Artifacts: `experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`.

### `gan2026_three_way_comparison_validation750_deterministic_phase2_gan_shorthand_generalized_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `deterministic`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator -- rules-only candidate extraction, normalization, and projection; no model calls. Phase 2 iteration 1: GAN_SHORTHAND group de-overfitted (word-number patterns removed, separator-prefix patterns removed).; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=683, purist_correct_of_rendered=674, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace (this architecture's reported evidence-trace metric); formal CandidateSet source-id validity is not computed for single-shot architectures.
- Claim language: Phase 2 de-overfitting iteration 1 data point (validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4): GAN_SHORTHAND rules rewritten to generalized clinical shorthand patterns -- digit-only counts, no special separator prefixes (asterisk/X/times), portability promoted from GAN2026_SPECIFIC to SEIZURE_FREQUENCY or CLINICAL_EPILEPSY. Expected and intentional regression of 14 rows (688 -> 674 purist-correct) -- these rows depended on benchmark-specific notation not present in real clinical documentation. Not a standalone promote/reject verdict -- see gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09 for cross-architecture synthesis.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_phase2_gan_shorthand_generalized_2026-06-09.jsonl`.

### `gan2026_three_way_comparison_validation750_deterministic_phase2_cluster_diary_digit_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `deterministic`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator -- rules-only candidate extraction, normalization, and projection; no model calls. Phase 2 iteration 2: CLUSTER_ARITHMETIC (cluster.compact_count_per_period) and DIARY_LOG_AGGREGATION (diary.seizure_days_fraction) de-overfitted to digit-only compact shorthand.; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=681, purist_correct_of_rendered=673, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace.
- Claim language: Phase 2 de-overfitting iteration 2 data point (validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4): CLUSTER_ARITHMETIC and DIARY_LOG_AGGREGATION rules generalized -- cluster.compact_count_per_period and diary.seizure_days_fraction now require digit-only counts in compact shorthand notation (word numbers in compact notation are GAN-dataset-specific). Word numbers in running prose (PORTABLE_RATE_EXPRESSIONS family) assessed and confirmed NOT GAN-specific; no change to that family. Expected and intentional regression of 1 row (674 -> 673 purist-correct) relative to iteration 1: row 148 (Seizure days: six/30 this month) depended on GAN-specific compact notation. Not a standalone promote/reject verdict -- see gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09 for cross-architecture synthesis.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_phase2_cluster_diary_digit_2026-06-09.jsonl`.

### `gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_gan_shorthand_generalized_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `deterministic_canonical_pipeline`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator routed through the staged canonical-pipeline architecture -- rules-only; no model calls. Phase 2 iteration 1: GAN_SHORTHAND group de-overfitted (word-number patterns removed, separator-prefix patterns removed).; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=683, purist_correct_of_rendered=674, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace; identical to the deterministic architecture's numbers on this split -- the staged canonical-pipeline wrapper converges on the same rendered answers as the unstaged baseline (confirmed in Phase 1 and still holds in Phase 2).
- Claim language: Phase 2 de-overfitting iteration 1 data point (validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4): same GAN_SHORTHAND rule rewrite as the deterministic counterpart, routed through the staged canonical-pipeline architecture. Produces identical purist/pragmatic/distribution numbers as the unstaged deterministic architecture (staged wrapper converges on the same rendered answers). Expected and intentional regression of 14 rows (688 -> 674 purist-correct). Not a standalone promote/reject verdict -- see gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09 for cross-architecture synthesis.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_gan_shorthand_generalized_2026-06-09.jsonl`.

### `gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_cluster_diary_digit_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `deterministic_canonical_pipeline`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator routed through the staged canonical-pipeline architecture -- rules-only candidate extraction, normalization, and projection; no model calls. Phase 2 iteration 2: CLUSTER_ARITHMETIC (cluster.compact_count_per_period) and DIARY_LOG_AGGREGATION (diary.seizure_days_fraction) de-overfitted to digit-only compact shorthand.; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=681, purist_correct_of_rendered=673, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace.
- Claim language: Phase 2 de-overfitting iteration 2 data point (validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4): same CLUSTER_ARITHMETIC and DIARY_LOG_AGGREGATION rule generalization as the deterministic counterpart; routed through the staged canonical-pipeline architecture -- cluster.compact_count_per_period and diary.seizure_days_fraction now require digit-only counts in compact shorthand notation (word numbers in compact notation are GAN-dataset-specific). Word numbers in running prose (PORTABLE_RATE_EXPRESSIONS family) assessed and confirmed NOT GAN-specific; no change to that family. Expected and intentional regression of 1 row (674 -> 673 purist-correct) relative to iteration 1: row 148 (Seizure days: six/30 this month) depended on GAN-specific compact notation. Not a standalone promote/reject verdict -- see gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09 for cross-architecture synthesis.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_cluster_diary_digit_2026-06-09.jsonl`.

### `gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase2_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis -- reads Phase 2 deterministic/deterministic_canonical_pipeline artifacts and Phase 1 LLM-architecture artifacts; assembles a shared comparison table plus a hybrid-only routing-taxonomy appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=674, deterministic_purist_correct_of_rendered=674, hybrid_purist_correct_of_rendered=500, hybrid_structured_events_purist_correct_of_rendered=661, llm_only_canonical_pipeline_purist_correct_of_rendered=581, llm_only_direct_labeler_purist_correct_of_rendered=564, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, the fact that evidence-trace metrics are NOT uniform across architectures: four report evidence_valid (free-text substring presence), llm_only_canonical_pipeline reports the deliberately distinct evidence_text_contained, and hybrid reports a formal CandidateSet source-id validity rate. The report footnotes and per-architecture metric table make this explicit.
- Claim language: Phase 2 de-overfitting iteration 1 comparison report synthesis (validation750 only; gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4). No test450 read, no holdout-facing or benchmark-comparable claim. Compares six PipelineArchitecture configs; deterministic and deterministic_canonical_pipeline are from Phase 2 runs (GAN_SHORTHAND de-overfitted); hybrid, llm_only_direct_labeler, hybrid_structured_events, llm_only_canonical_pipeline are from the Phase 1 gpt-4.1-mini pass (unchanged). Key finding: expected and intentional 14-row regression on deterministic architectures (674 vs 688 purist-correct); validates that the removed rules were GAN-dataset-specific and not genuinely generalizable clinical patterns.
- Artifacts: `experiments/gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09.md`.

### `gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase2_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis -- reads Phase 2 iteration 2 deterministic/deterministic_canonical_pipeline artifacts and Phase 1 LLM-architecture artifacts; assembles a shared comparison table plus a hybrid-only routing-taxonomy appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=673, deterministic_purist_correct_of_rendered=673, hybrid_purist_correct_of_rendered=500, hybrid_structured_events_purist_correct_of_rendered=661, llm_only_canonical_pipeline_purist_correct_of_rendered=581, llm_only_direct_labeler_purist_correct_of_rendered=564, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, the fact that evidence-trace metrics are NOT uniform across architectures: four report evidence_valid (free-text substring presence), llm_only_canonical_pipeline reports the deliberately distinct evidence_text_contained, and hybrid reports a formal CandidateSet source-id validity rate.
- Claim language: Phase 2 de-overfitting iteration 2 comparison report synthesis (validation750 only; gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4). No test450 read, no holdout-facing or benchmark-comparable claim. Compares six PipelineArchitecture configs; deterministic and deterministic_canonical_pipeline are from Phase 2 iteration 2 runs (GAN_SHORTHAND + CLUSTER_ARITHMETIC + DIARY_LOG_AGGREGATION de-overfitted); hybrid, llm_only_direct_labeler, hybrid_structured_events, llm_only_canonical_pipeline are from the Phase 1 gpt-4.1-mini pass (unchanged). Key finding: expected and intentional total regression of 15 rows across both de-overfitting iterations (688 -> 673 purist-correct); validates that the removed rules depended on GAN-dataset-specific notation.
- Artifacts: `experiments/gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09.md`.

### `gan2026_three_way_comparison_validation750_llm_only_direct_labeler_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_direct_labeler`; mode `live`; replay `live`.
- Model role: LLM-only direct labeler -- single DSPy call renders the final label directly from the note; no deterministic CandidateSet. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Primary metrics: call_failures=0, evidence_valid_rate=0.941, evidence_valid_rows=706, null_rows=0, parse_or_validation_failures=0, pragmatic_accuracy=0.781, pragmatic_correct=586, purist_accuracy=0.744, purist_correct=558, rendered_rows=750.
- Evidence validity: 706/750 rows (94.1%) carry an evidence_valid substring-presence trace. This architecture structurally cannot produce a null/unrendered row.
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_direct_labeler_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_direct_labeler_deepseek_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_canonical_pipeline`; mode `live`; replay `live`.
- Model role: LLM-only canonical pipeline -- single DSPy call collapses extract/select/normalize/project/render into one pass; no deterministic CandidateSet or projection stage; model `openai/gpt-4.1-mini`.
- Primary metrics: evidence_text_contained_rows=700, null_rows=0, pragmatic_correct_of_rendered=626, purist_correct_of_rendered=581, rendered_rows=750.
- Evidence validity: 700/750 rows (93.3%) carry an evidence_text_contained free-text trace -- a metric this architecture reports in place of (and deliberately distinct from) the evidence_valid substring-presence metric the other five architectures report; do not compare the two as one accuracy number (see Phase 1 report footnote).
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands. Newest of the six architectures -- the 'purest form' fully-LLM comparator with the deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_canonical_pipeline`; mode `live`; replay `live`.
- Model role: LLM-only canonical pipeline -- single DSPy call collapses extract/select/normalize/project/render into one pass; no deterministic CandidateSet or projection stage. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Primary metrics: call_failures=0, evidence_text_contained_rate=0.925, evidence_text_contained_rows=694, null_rows=0, parse_or_validation_failures=0, pragmatic_accuracy=0.781, pragmatic_correct=586, purist_accuracy=0.753, purist_correct=565, rendered_rows=750.
- Evidence validity: 694/750 rows (92.5%) carry an evidence_text_contained free-text trace -- a metric this architecture reports in place of (and deliberately distinct from) the evidence_valid substring-presence metric other architectures report; do not compare directly across architectures.
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: LLM-only structured-events extractor and selector -- slim source-near event schema; deterministic code limited to Gan normalization, evidence validation, and scoring; model `openai/gpt-4.1-mini`.
- Primary metrics: evidence_valid_rows=691, null_rows=2, pragmatic_correct_of_rendered=679, purist_correct_of_rendered=661, rendered_rows=748.
- Evidence validity: 691/750 rows (92.1%) carry an evidence_valid substring-presence trace; the 2 null rows are rare parse failures, not a structural give-up signal -- see the Phase 1 report's per-architecture rendered/null derivation footnote.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands. Restarted after fixing a schema_repair.py _ASSERTION_ALIASES bug that remapped the already-valid assertion_status value 'unknown' to the invalid 'unclear'; confirmed clean via re-pilot validation25 (0 failures, 100% accuracy) before this full run (see run markdown header).
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: LLM-only structured-events extractor and selector -- slim source-near event schema; deterministic code limited to Gan normalization, evidence validation, and scoring. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Primary metrics: call_failures=0, evidence_valid_rate=0.957, evidence_valid_rows=718, null_rows=8, parse_or_validation_failures=8, pragmatic_accuracy=0.845, pragmatic_correct=634, purist_accuracy=0.812, purist_correct=609, rendered_rows=742.
- Evidence validity: 718/750 rows (95.7%) carry an evidence_valid substring-presence trace. 8 parse_or_validation_failures (~1%) -- within accepted noise for this architecture.
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid`; mode `live`; replay `live`.
- Model role: Hybrid -- deterministic CandidateSet extraction + LLM-extracted CandidateSet union (both generated live, per row, replicating the static _v2_high_recall artifact's own build methodology) feeding a clinical-assessment probe; shared-table numbers below come from a deep-replay of those rows through projection_render -> score -> verification_route -> verification_decision, not from the probe's raw run_split output (the probe reports schema-fit diagnostics only and has no rendered/null/purist/routed numbers of its own).; model `openai/gpt-4.1-mini`.
- Primary metrics: evidence_trace_valid_rows=734, null_rows=149, pragmatic_correct_of_rendered=536, purist_correct_of_rendered=511, rendered_rows=600, routed_rows=42.
- Evidence validity: 734/750 rows (0.979) carry a valid candidate_set_source_id_status -- a formal CandidateSet source-id validity rate, NOT the evidence_valid substring-presence metric the other five architectures report (see the Phase 1 report's evidence-trace-metric-by-architecture table; these numbers are not directly comparable).
- Supersedes: `gan2026_three_way_comparison_validation750_hybrid_gpt41mini_2026-06-07`.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis. This run replaces the prior 250-row-scoped hybrid run (gan2026_three_way_comparison_validation750_hybrid_gpt41mini_2026-06-07, kept for the historical record of what that scoping looked like): run_split's fallback CandidateSet path was rewired from a static 250-row precomputed artifact (which emitted candidate_set_missing placeholders for the other 500 rows) to live per-row generation that replicates the static artifact's own deterministic+LLM-extraction union methodology, so this run finally covers the full 750-row validation surface like the other five architectures (missing_candidate_set_rows: 0, call_failures: 0, parse_or_validation_failures: 1). Launched as a fully OS-detached process (harness silently kills long-running background bash tasks at ~9 minutes; PowerShell Start-Process survives past that window) and resumed via --resume-existing after an earlier interruption -- see run markdown header for the resume provenance.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid`; mode `live`; replay `live`.
- Model role: Hybrid -- deterministic CandidateSet extraction + LLM-extracted CandidateSet union (both generated live, per row) feeding a clinical-assessment probe; shared-table numbers come from a deep-replay of those rows through projection_render -> score -> verification_route -> verification_decision. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Primary metrics: evidence_trace_valid_rate=0.985, evidence_trace_valid_rows=739, null_rows=146, pragmatic_correct_of_rendered=520, pragmatic_correct_rate_of_rendered=0.861, purist_correct_of_rendered=490, purist_correct_rate_of_rendered=0.811, rendered_rows=604, routed_rows=123.
- Evidence validity: 739/750 rows (98.5%) carry a valid candidate_set_source_id_status -- a formal CandidateSet source-id validity rate from the deep-replay (NOT the evidence_valid substring-presence metric other architectures report; these numbers are not directly comparable across architecture types).
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08.md`.

### `gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase1_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis -- reads six already-completed gpt-4.1-mini validation750 architecture-comparison artifacts (deterministic, deterministic_canonical_pipeline, hybrid, llm_only_direct_labeler, hybrid_structured_events, llm_only_canonical_pipeline) and assembles a shared comparison table plus a hybrid-only routing-taxonomy appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=688, deterministic_purist_correct_of_rendered=688, hybrid_purist_correct_of_rendered=511, hybrid_structured_events_purist_correct_of_rendered=661, llm_only_canonical_pipeline_purist_correct_of_rendered=581, llm_only_direct_labeler_purist_correct_of_rendered=564, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, the fact that evidence-trace metrics are NOT uniform across architectures: four report evidence_valid (free-text substring presence), llm_only_canonical_pipeline reports the deliberately distinct evidence_text_contained, and hybrid reports a formal CandidateSet source-id validity rate. The report's footnotes and per-architecture metric table make this explicit so readers do not compare these as one accuracy number.
- Claim language: Phase 1 three-way architecture comparison synthesis (gpt-4.1-mini pass, validation750 only; gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 and gan2026_three_way_comparison_phase1_report_design_2026-06-07). No test450 read, no holdout-facing or benchmark-comparable claim -- compares six PipelineArchitecture configs on universally meaningful axes (rendered/null disposition, Purist/Pragmatic-correct of rendered rows, evidence-trace validity, final-answer distribution); hybrid additionally carries a routing-taxonomy appendix with no analogous surface in the other five. hybrid's shared-table row is sourced from build_unified_pipeline_artifact deep-replay (using the live-generated CandidateSets the now-fixed hybrid run embeds in its own output rows), not raw run_split output -- this asymmetry is the architectural fact under comparison, not a methodology artifact, and the report's footnotes say so explicitly. A notable finding surfaced here: deterministic and deterministic_canonical_pipeline produce IDENTICAL purist/pragmatic/distribution numbers, i.e. the staged canonical-pipeline wrapper converges on the same rendered answers as the unstaged baseline on this pass.
- Artifacts: `experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.json`, `experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_llm_only_direct_labeler_gpt41mini_2026-06-07`
- Date/split: `2026-06-07`; `validation`; `750` rows.
- Pipeline: `llm_only_direct_labeler`; mode `live`; replay `live`.
- Model role: LLM-only direct labeler -- single DSPy call renders the final label directly from the note; no deterministic CandidateSet; model `openai/gpt-4.1-mini`.
- Primary metrics: evidence_valid_rows=711, null_rows=0, pragmatic_correct_of_rendered=599, purist_correct_of_rendered=564, rendered_rows=750.
- Evidence validity: 711/750 rows (94.8%) carry an evidence_valid substring-presence trace. This architecture structurally cannot produce a null/unrendered row -- see the Phase 1 report's footnote on the rendered-disposition asymmetry between single-shot LLM-only and deterministic-routed architectures.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands. Restarted mid-effort after fixing an answer_kind prompt/schema mismatch bug; confirmed clean via re-pilot validation25 (0 failures, 100% accuracy) before this full run (see run markdown header).
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_direct_labeler_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_direct_labeler_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_deterministic_gpt41mini_2026-06-07`
- Date/split: `2026-06-07`; `validation`; `750` rows.
- Pipeline: `deterministic`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator -- rules-only candidate extraction, normalization, and projection; no model calls; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=695, purist_correct_of_rendered=688, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace (this architecture's reported evidence-trace metric); formal CandidateSet source-id validity is not computed for single-shot architectures.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_deterministic_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07`
- Date/split: `2026-06-07`; `validation`; `750` rows.
- Pipeline: `deterministic_canonical_pipeline`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator routed through the staged canonical-pipeline architecture -- rules-only; no model calls; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=695, purist_correct_of_rendered=688, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace; identical to the `deterministic` architecture's numbers and final-label distribution on this split -- the staged canonical-pipeline wrapper converges on the same rendered answers as the unstaged baseline (see Phase 1 report).
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07.md`.

### `gan2026_llm_only_typed_operations_reasoner_v3_max4800_validation25_live_2026-06-03`
- Date/split: `2026-06-03`; `validation`; `25` rows.
- Pipeline: `llm_only_typed_operations_reasoner`; mode `live validation25 typed-operations evidence-copy, graph-projection, and max4800 smoke`; replay `cache_first`.
- Model role: LLM-only typed operation extraction, operation selection, model-owned final rendering, and graph-overlay sidecar; model `openai/gpt-4.1-mini`.
- Repair mode/config: `source-checked evidence-copy repair for escaped inequality artifacts; selected current/recent operation graph projection; selected-evidence arithmetic graph fallback; max_tokens=4800`.
- Primary metrics: call_failures=0, event_evidence_total=37, event_evidence_valid=34, format_only_purist_correct=20, max_tokens=4800, parse_failures=0, raw_llm_purist_correct=15, raw_llm_scorable=15, row_count=25, selected_evidence_arithmetic_purist_correct=25, selected_evidence_valid=22, selected_operation_trace_mismatches=0, structured_records=25, truncation_warnings=0, typed_graph_raw_correct_to_wrong=1, typed_graph_raw_wrong_to_correct=9, typed_operation_graph_projection_purist_correct=23, typed_operation_graph_projection_scorable=25.
- Evidence validity: Selected evidence exact 22/25; event evidence exact 34/37; selected-operation trace mismatches 0/25. Remaining typed-graph misses are row 446 invalid selected evidence and row 467 operand-to-graph rendering.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse. The CLI default max token budget for this pipeline is now 4800.
- Superseded by: `gan2026_llm_only_typed_operations_reasoner_v3_max4800_no_call_replay_2026-06-03`.
- Claim language: Validation25 development smoke only. The 4800-token budget removed truncation warnings. This live artifact is superseded for deterministic replay interpretation by the no-call replay after generalized evidence-artifact cleanup and graph-label precedence repair.
- Artifacts: `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.jsonl`, `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.md`.

### `gan2026_llm_only_typed_operations_reasoner_v3_max4800_no_call_replay_2026-06-03`
- Date/split: `2026-06-03`; `validation`; `25` rows.
- Pipeline: `llm_only_typed_operations_reasoner`; mode `saved-output no-call replay after evidence artifact and graph-label precedence repair`; replay `saved_output_replay`.
- Model role: analysis-only replay of LLM-only typed operation extraction, selection, final rendering, and graph-overlay sidecar; model `none; saved openai/gpt-4.1-mini max4800 outputs`.
- Repair mode/config: `No-call replay using generalized semantically-neutral evidence artifact cleanup, source-note mojibake cleanup, typed graph label precedence fix, and typed_operation_graph_projection semantic repair metadata.`.
- Primary metrics: event_evidence_total=37, event_evidence_valid=37, format_only_purist_correct=20, parse_failures=0, raw_llm_purist_correct=15, raw_llm_scorable=15, row_count=25, selected_evidence_arithmetic_purist_correct=25, selected_evidence_valid=25, selected_operation_trace_mismatches=0, structured_records=25, typed_operation_graph_projection_pragmatic_correct=25, typed_operation_graph_projection_purist_correct=24, typed_operation_graph_projection_scorable=25.
- Evidence validity: Selected evidence exact 25/25; event evidence exact 37/37; selected-operation trace mismatches 0/25.
- Cache/reuse source: experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.jsonl.
- Supersedes: `gan2026_llm_only_typed_operations_reasoner_v3_max4800_validation25_live_2026-06-03`.
- Claim language: Saved-output replay only: no hosted calls, prompt changes, scorer changes, split changes, or holdout behavior changes. Row 446 and row 467 deterministic replay bugs are fixed; row 598 remains a Purist graph-rendering miss, so revise before validation50.
- Artifacts: `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_max4800_no_call_replay_2026-06-03.jsonl`, `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_max4800_no_call_replay_2026-06-03.md`.

### `gan2026_llm_heavy_evidence_selection_decision0007_validation25_contract_triage_2026-06-03`
- Date/split: `2026-06-03`; `validation`; `25` rows.
- Pipeline: `llm_heavy_evidence_selection_with_deterministic_adapters`; mode `saved-output Decision 0007 validation25 contract triage`; replay `analysis_only`.
- Model role: analysis-only reviewer for selected evidence, operand completeness, raw parser-label grammar, and cluster-axis failure slices; model `none; saved outputs only`.
- Repair mode/config: `analysis only; proposed v1 prompt/schema contract without scorer, split, adapter, or gate changes`.
- Primary metrics: adapted_miss_rows=10,128,187,190,280,446, exact_evidence_failure_rows=10,40,79,103,409,446, missing_operand_rows=128, raw_parser_label_scorable=0, row_count=25, wrong_fact_or_operand_rows=187,190,280.
- Evidence validity: Identified exact-evidence escaping failures on rows 10, 40, 79, 103, 409, and 446; later v1 reduced these to rows 10, 40, and 446.
- Cache/reuse source: Saved-output row review of the v0 Decision 0007 validation25 smoke; no hosted calls.
- Superseded by: `gan2026_llm_heavy_evidence_selection_decision0007_v1_validation25_live_2026-06-03`.
- Claim language: Analysis-only triage predeclared a v1 prompt/schema revision. It did not change scorer, split, adapter, gate, or holdout behavior.
- Artifacts: `experiments/gan2026_llm_heavy_decision0007_validation25_contract_triage_2026-06-03.md`.

### `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `gated month-bucket duration-selection projection ablation v1`; replay `analysis_only`.
- Model role: diagnostic gated month-bucket duration projection replay over enriched target graphs plus validation hard-slice regression panel; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `gated diagnostic month_bucket_duration_selection_v1 projection variant only; no scorer, graph-builder, production projection-policy, or holdout change`.
- Primary metrics: all_rows_changed_labels=22, already_correct_regressions=0, frequency_with_seizure_free_node_changes=0, regression_changed_labels=4, regression_rows=232, target_exact_duration_corrections=18, target_exact_duration_regressions=0, target_rows=18, unknown_no_reference_boundary_changes=1.
- Evidence validity: Selected-node evidence was exact-offset valid for 18/18 target rows and 232/232 regression rows.
- Cache/reuse source: Saved seizure-free duration node replay JSONL and validation hard-slice state-graph diagnostics; no hosted calls.
- Supersedes: `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02`.
- Claim language: Diagnostic validation-cycle projection ablation. Gating preserves the 18/18 target corrections while removing v0 already-correct and frequency-with-seizure-free regressions; four wrong-to-wrong regression changes remain, so this is the best revise-only seed, not production policy.
- Artifacts: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02.jsonl`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02.json`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02.md`.

### `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `month-bucket duration-selection projection ablation v0`; replay `analysis_only`.
- Model role: diagnostic month-bucket duration projection replay over enriched target graphs plus validation hard-slice regression panel; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `diagnostic month_bucket_duration_selection projection variant only; no scorer, graph-builder, production projection-policy, or holdout change`.
- Primary metrics: all_rows_changed_labels=55, already_correct_regressions=27, frequency_with_seizure_free_node_changes=19, regression_changed_labels=37, regression_rows=232, target_exact_duration_corrections=18, target_exact_duration_regressions=0, target_rows=18, unknown_no_reference_boundary_changes=2.
- Evidence validity: Selected-node evidence was exact-offset valid for 18/18 target rows and 232/232 regression rows.
- Cache/reuse source: Saved seizure-free duration node replay JSONL and validation hard-slice state-graph diagnostics; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_month_bucket_duration_selection_decision_2026-06-02`.
- Claim language: Diagnostic validation-cycle projection ablation. It fixes the intended 18-row duration surface but causes 27 already-correct validation hard-slice regressions, so it is not promoted as a production projection policy; next work should design a gated/narrow policy.
- Artifacts: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.jsonl`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.json`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.md`.

### `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `graph-gated month-bucket duration-selection broad regression panel`; replay `analysis_only`.
- Model role: diagnostic graph-metadata-gated month-bucket duration projection replay; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `graph_gated_v2 diagnostic month_bucket_duration_selection projection variant plus graph metadata gate; no scorer, graph-builder, production projection-policy, or holdout change`.
- Primary metrics: all_rows_changed_labels=18, already_correct_regressions=0, frequency_with_seizure_free_node_changes=0, graph_gate_active_boundary_state_node_rows=6, graph_gate_blocked_rows=46, graph_gate_selected_rule_not_duration_normalization_v0_rows=46, regression_changed_labels=0, regression_rows=232, target_exact_duration_corrections=18, target_exact_duration_regressions=0, target_rows=18, unknown_no_reference_boundary_changes=0.
- Evidence validity: Selected-node evidence was exact-offset valid for 18/18 target rows and 232/232 regression rows; graph gate blocked 46 month-bucket replacements using graph metadata.
- Cache/reuse source: Saved seizure-free duration node replay JSONL and validation hard-slice state-graph diagnostics; no hosted calls.
- Supersedes: `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02`.
- Claim language: Diagnostic validation-cycle graph-metadata gate replay. The gate preserves 18/18 enriched duration corrections and blocks all broad-regression label changes by requiring selected month-bucket nodes to come from seizure_free_duration_node_normalization_v0 and by refusing active boundary-state graphs; no production projection policy is promoted.
- Artifacts: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.jsonl`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.json`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.md`.

### `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `gated month-bucket duration-selection broad regression panel`; replay `analysis_only`.
- Model role: diagnostic gated month-bucket duration projection replay with hard-slice family regression accounting; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `gated diagnostic month_bucket_duration_selection_v1 projection variant plus hidden-family regression tags; no scorer, graph-builder, production projection-policy, or holdout change`.
- Primary metrics: all_rows_changed_labels=22, already_correct_regressions=0, cluster_or_diary_changed_labels=4, frequency_with_seizure_free_node_changes=0, regression_changed_labels=4, regression_rows=232, seizure_free_overreach_changed_labels=3, target_exact_duration_corrections=18, target_exact_duration_regressions=0, target_rows=18, temporal_conflict_changed_labels=4, unknown_no_reference_boundary_changes=1.
- Evidence validity: Selected-node evidence was exact-offset valid for 18/18 target rows and 232/232 regression rows.
- Cache/reuse source: Saved seizure-free duration node replay JSONL and validation hard-slice state-graph diagnostics; no hosted calls.
- Supersedes: `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02`.
- Claim language: Diagnostic validation-cycle broad-regression replay. Gated v1 preserves 18/18 enriched duration corrections, adds hidden-family regression accounting, and leaves four wrong-to-wrong regression changes concentrated in cluster/diary plus temporal-conflict rows, including one unknown-boundary row; no production policy is promoted.
- Artifacts: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.jsonl`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.json`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.md`.

### `gan2026_llm_replacement_postprocessing_ablation_validation250_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `250` rows.
- Pipeline: `llm_replacement_postprocessing_ablation`; mode `saved-output no-call post-processing replacement ablation`; replay `saved_output_replay`.
- Model role: analysis-only deterministic post-processing replacement replay; model `none; saved outputs only`.
- Repair mode/config: `raw_llm + format_only + selected_evidence_arithmetic + benchmark_aligned`.
- Primary metrics: benchmark_aligned_adapter_purist_correct=204, condition_rows=1000, format_only_repair_purist_correct=188, raw_model_selected_label_purist_correct=188, reused_raw_output_rows=50, row_count=250, selected_evidence_arithmetic_only_purist_correct=219.
- Evidence validity: Reports selected-evidence exactness, event/node evidence validity, and selected-event trace mismatches for each replacement condition.
- Cache/reuse source: experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.jsonl.
- Supersedes: `gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02`.
- Claim language: Diagnostic saved-output replay only. No hosted calls, prompt changes, scorer changes, production projection policy changes, or holdout behavior changes are made.
- Artifacts: `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.jsonl`, `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.json`, `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.md`.

### `gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices_planned`; `250` rows.
- Pipeline: `llm_replacement_postprocessing_ablation`; mode `LLM-replacement deterministic post-processing ablation design`; replay `analysis_only`.
- Model role: analysis-only replacement-ablation planner for deterministic post-processing ownership; model `none`.
- Repair mode/config: `planning only; no scorer, projection, graph-builder, prompt, or holdout change`.
- Primary metrics: planned_conditions=11, replacement_targets=6, required_report_families=6, validation_surface_max_rows=250.
- Evidence validity: Design requires every replay to report selected-evidence exactness, event/node evidence exactness, selected-event trace mismatches, selected-node source, and rows dropped for non-exact evidence.
- Cache/reuse source: No hosted calls; design derived from project retrospective, LLM-heavy v1 validation250 failure families, state-graph diagnostics, and existing repair-attribution conventions.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation250_live_2026-06-02`, `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02`.
- Claim language: Diagnostic design only. Predeclares replacement ablations for deterministic post-processing modules before LLM-heavy v2 prompt work; no scorer, prompt, production projection policy, or holdout behavior changed.
- Artifacts: `experiments/gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation250_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `250` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation250 diagnostic scale-up after validation50 gate`; replay `cache_first`.
- Model role: LLM-heavy extraction, clinical selection, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v1 prompt/schema plus non-semantic enum/unit alias repair; benchmark-aligned layer remains side-car and selected-evidence arithmetic remains diagnostic attribution only`.
- Primary metrics: benchmark_aligned_purist_correct=204, call_failures=0, event_evidence_total=535, event_evidence_valid=508, format_only_purist_correct=188, parse_failures=13, raw_llm_pragmatic_correct=195, raw_llm_purist_correct=188, raw_llm_scorable=213, row_count=250, selected_event_trace_mismatches=9, selected_evidence_arithmetic_pragmatic_correct=225, selected_evidence_arithmetic_purist_correct=219, selected_evidence_valid=230, structured_records=237.
- Evidence validity: Selected evidence exact 230/250; event evidence exact 508/535; nine selected-event trace mismatches and 13 parse/schema failures remain.
- Cache/reuse source: Reused validation50 v1 raw outputs for the first 50 rows and ran rows 51-250 live with DSPy cache enabled.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation50_live_2026-06-02`.
- Claim language: Validation250 rejects promotion of v1 as an LLM-heavy final-label candidate: raw/format-only Purist is 188/250 and the stronger 219/250 selected-evidence arithmetic layer is attribution-diagnostic, not LLM-heavy success.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_schema_smoke_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation25 followed by saved-output schema replay after scalar-list shape repair`; replay `schema_replay`.
- Model role: LLM-heavy extraction, clinical selection, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `raw_llm + format_only + selected_evidence_arithmetic + benchmark_aligned + oracle_format_upper_bound layers; scalar-list schema repair only`.
- Primary metrics: benchmark_aligned_purist_correct=13, format_only_purist_correct=10, raw_llm_scorable=0, row_count=25, schema_valid_rows=24, selected_event_trace_mismatches=0, selected_evidence_arithmetic_purist_correct=23, selected_evidence_valid=18.
- Evidence validity: Event evidence 42/47 exact; selected evidence 18/25 exact, below the Stage A 22/25 stop rule.
- Cache/reuse source: DSPy cache enabled for the initial live run; saved raw outputs replayed after non-semantic scalar-list schema repair.
- Supersedes: `gan2026_llm_heavy_extraction_protocol_2026-06-02`.
- Claim language: LLM-heavy validation development smoke only. Schema validity reaches the 24/25 minimum after shape replay, but selected evidence exactness and raw LLM scorer format fail the Stage A stop rule; revise prompt/schema before validation50.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.md`, `experiments/gan2026_llm_heavy_extraction_protocol_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `row-level error analysis of validation25 schema smoke`; replay `analysis_only`.
- Model role: LLM-heavy extraction, clinical selection, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `analysis over raw_llm, format_only, selected_evidence_arithmetic, benchmark_aligned, and oracle_format_upper_bound layers`.
- Primary metrics: benchmark_aligned_purist_correct=13, benchmark_regressions_vs_arithmetic=10, deterministic_v1_same_rows_purist_correct=25, event_evidence_total=47, event_evidence_valid=42, format_only_purist_correct=10, raw_llm_scorable=0, selected_evidence_arithmetic_purist_correct=23, selected_evidence_valid=18, structured_records=24.
- Evidence validity: Selected evidence exactness 18/25 and event evidence exactness 42/47; selected-event traces had 0 mismatches.
- Cache/reuse source: No new hosted calls; analysis uses saved validation25 JSONL and deterministic V1 same-row comparator.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_schema_smoke_2026-06-02`.
- Claim language: Full validation-development error analysis. High selected-evidence arithmetic score is diagnostic only because raw LLM labels are 0/25 scorable and the best layer depends on deterministic derivation over selected evidence; revise before validation50.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.csv`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.json`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`.

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

### `gan2026_qwen36_35b_ollama_chat_setup_smoke_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `1` rows.
- Pipeline: `llm_only_claim_table_selector`; mode `native Ollama chat setup smoke`; replay `live`.
- Model role: local LLM-only claim-table selector; model `ollama_chat/qwen3.6:35b`.
- Repair mode/config: `none; endpoint smoke before Qwen-specific schema repair`.
- Primary metrics: call_failures=0, parse_schema_failures=1, row_count=1, structured_rows=0.
- Evidence validity: No structured record; output-contract smoke only.
- Cache/reuse source: DSPy cache disabled; native Ollama /api/chat smoke used think=false.
- Claim language: Endpoint setup is unblocked through ollama_chat/qwen3.6:35b with think=false, but v5 is not ladder-ready for Qwen: validation1 returned a nonempty Python-style dict and final_selector shape, producing a schema parse failure. Do not treat this as model-quality evidence or start validation5/25 until prompt hardening or a named schema-repair ablation exists. Dedicated schema-contract risk note logged for future Qwen prompt/repair design.
- Artifacts: `experiments/gan2026_qwen36_35b_ollama_chat_setup_smoke_2026-06-01.md`, `docs/research/gan2026_qwen_schema_contract_risk_2026-06-01.md`, `experiments/gan2026_llm_only_claim_table_selector_validation1_prompt_only_v5_2026-06-01.jsonl`, `experiments/gan2026_llm_only_claim_table_selector_validation1_prompt_only_v5_2026-06-01.md`, `experiments/gan2026_llm_only_claim_table_selector_validation1_qwen36_35b_v5_ollama_chat_smoke_2026-06-01.jsonl`, `experiments/gan2026_llm_only_claim_table_selector_validation1_qwen36_35b_v5_ollama_chat_smoke_2026-06-01.md`.

### `gan2026_minimal_evidence_selector_validation25_gpt41mini_v0_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `25` rows.
- Pipeline: `llm_only_minimal_evidence_selector`; mode `live minimal answer plus supporting_facts contract`; replay `live`.
- Model role: hosted LLM-only minimal evidence selector baseline; model `openai/gpt-4.1-mini`.
- Repair mode/config: `minimal alias/shape repair available; strict_format + frozen_clean_scorer_facing scoring`.
- Primary metrics: answer_evidence_valid=24, call_failures=0, clean_pragmatic_correct=16, clean_purist_correct=16, derived_state_complete=25, invalid_json_failures=0, minimal_records=25, parse_schema_failures=0, raw_pragmatic_correct=2, raw_purist_correct=2, raw_scorable=2, review_projection_complete=25, row_count=25, strict_format_purist_correct=15, supporting_fact_evidence_total=50, supporting_fact_evidence_valid=49.
- Evidence validity: Answer evidence exact in 24/25 rows; supporting-fact evidence exact in 49/50 facts. Row 243 used a non-exact answer/supporting evidence substring.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs; first-device OpenAI/LiteLLM smoke passed from .env before run.
- Claim language: Hosted simplified-contract baseline is output-contract clean with no JSON/schema failures and no alias repairs, but raw source-near answers are mostly scorer-unparsable; frozen clean scorer-facing score is 16/25 Purist and Pragmatic. Use as matched GPT-4.1 mini transfer baseline for Qwen minimal-contract validation, not holdout evidence.
- Artifacts: `experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v0_2026-06-01.jsonl`, `experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v0_2026-06-01.md`.

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

### `gan2026_agentic_hard50_tool_self_consistency_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_tool_self_consistency`; mode `live`; replay `live`.
- Model role: E2 four-call boundary-guide-only tool self-consistency with deterministic normalized-label voting, compared against saved single_self_consistency_temperature hard50 condition.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair + deterministic normalized-label vote`.
- Primary metrics: call_failures=0, decision_records=200, gate_max_losses=2, gate_required_wins=5, holdout_authorized=no, losses_vs_single_self_consistency_temperature=2, model_calls_attempted=200, parse_or_validation_failures=0, pragmatic_correct=35, purist_correct=34, rows=50, wins_vs_single_self_consistency_temperature=4.
- Evidence validity: Prediction-bearing validation hard50 development run: 200/200 decision records, 0 call failures, 0 parse/schema/label failures. Evidence substring metric not computed for this ablation artifact.
- Supersedes: `gan2026_agentic_hard50_tool_context_ablation_2026-06-12`.
- Claim language: Validation-development hard-slice result only. E2 missed the promotion gate by one rescue (4 wins, 2 losses; gate required at least 5 wins and at most 2 losses), so E3 and E4 were not run under the predeclared stop rule.
- Artifacts: `experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl`, `experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.md`.

### `gan2026_agentic_hard50_selective_fallback_replay_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_selective_fallback_replay`; mode `no_call_replay`; replay `saved_output_replay`.
- Model role: No-call selective fallback replay over saved hard50 matched-budget agentic traces, using single_self_consistency_temperature as fallback comparator.; model `none`.
- Repair mode/config: `saved-output policy replay; no scorer or label repair changes`.
- Primary metrics: all_agree_multi_accept_net_purist_gain=-6, all_agree_tool_accept_net_purist_gain=-12, boundary_coordinator_agree_net_purist_gain=-3, diagnostic_policy_count=1, holdout_authorized=no, promoted_policy_count=0, raw_repair_disagreement_fallback_net_purist_gain=-6, rows=50.
- Evidence validity: No new prediction evidence. Replay uses saved validation hard50 condition traces, final labels, role labels, normalized votes, and manifest slice tags for validation-only analysis.
- Cache/reuse source: experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.jsonl.
- Claim language: Validation-development replay only. No promotable selective fallback policy produced any wrong-to-correct changes; all eligible policies were reject signals, so the branch moved to E1 tool-context ablation rather than new live multi-agent calls.
- Artifacts: `experiments/gan2026_agentic_hard50_selective_fallback_replay_2026-06-12.jsonl`, `experiments/gan2026_agentic_hard50_selective_fallback_replay_2026-06-12.md`.

### `gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_boundary_audit_prompt_v2`; mode `live`; replay `live`.
- Model role: D1 one-call boundary-audit prompt v2 over the fixed validation hard50 slice; fixed boundary-guide context only, parser candidates disabled.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `format-only audit-field shape repair plus existing label/evidence repair; parser candidates disabled as prompt context`.
- Primary metrics: boundary_demotion_count=1, call_failures=0, changed_label_precision=0.3636, changed_labels_vs_reference=22, evidence_exact_substrings=35, hard50_gate=reject_or_revise, holdout_authorized=no, losses_vs_single_self_consistency_temperature=2, parse_or_validation_failures=0, pragmatic_correct=38, purist_correct=38, rows=50, schema_or_label_repair_rows=44, wins_vs_single_self_consistency_temperature=8.
- Evidence validity: 35/50 exact evidence substrings. Prediction-bearing hard50 run had 50/50 decision records, 0 call failures, and 0 parse/schema/label failures after format-only audit repair.
- Supersedes: `gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12`.
- Claim language: Validation hard-slice development result only. Despite 8 rescues, D1 missed the hard50 gate because it caused 2 regressions and changed-label precision was 0.3636; do not escalate D1 to validation250, D3, or holdout.
- Artifacts: `experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.jsonl`, `experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.md`.

### `gan2026_llm_heavy_evidence_selection_decision0007_v1_validation25_live_2026-06-03`
- Date/split: `2026-06-03`; `validation`; `25` rows.
- Pipeline: `llm_heavy_evidence_selection_with_deterministic_adapters`; mode `live validation25 Decision 0007 v1 selected-fact and operand contract smoke`; replay `live`.
- Model role: LLM-owned clinical fact, evidence, temporal state, raw parser label, and operands; deterministic code mechanically renders selected operands; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v1 prompt/schema-only contract: exact Unicode evidence copying, clinical-kind/operand consistency, vague-count guidance, and parser-ready raw-label grammar; scorer, split, adapter, and gate unchanged`.
- Primary metrics: adapter_parse_failures=0, benchmark_convention_adapter_purist_correct=23, call_failures=0, format_only_repair_purist_correct=25, mechanical_adapter_label_pragmatic_correct=24, mechanical_adapter_label_purist_correct=23, mechanical_adapter_raw_correct_to_wrong=2, mechanical_adapter_raw_wrong_to_correct=0, operand_complete_rows=25, raw_model_parser_label_purist_correct=25, raw_model_parser_label_scorable=25, row_count=25, selected_evidence_valid=22, selected_fact_trace_mismatches=0, structured_records=25.
- Evidence validity: Selected evidence exact 22/25; selected fact trace mismatches 0/25. Remaining failures are special-character evidence escaping on rows 10, 40, and 446.
- Cache/reuse source: DSPy cache disabled for the live v1 smoke; no saved raw-output reuse.
- Supersedes: `gan2026_llm_heavy_evidence_selection_decision0007_validation25_contract_triage_2026-06-03`.
- Claim language: Decision 0007 validation25 development smoke only. V1 fixes raw parser-label grammar and operand completeness, but promotion remains rejected because selected evidence exactness is 22/25 and the mechanical adapter regresses two raw-correct cluster-cadence rows.
- Artifacts: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_2026-06-03.jsonl`, `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_2026-06-03.md`.

### `gan2026_llm_only_typed_adapter_reasoner_v0_validation50_diagnostic_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `50` rows.
- Pipeline: `llm_only_typed_adapter_reasoner`; mode `live validation50 typed DSPy JSONAdapter diagnostic plus saved-output row-level error analysis`; replay `cache_first`.
- Model role: LLM-only typed DSPy event extraction, clinical selection, and parser-ready final-label renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `typed DSPy JSONAdapter outputs with raw_llm, format_only, selected_evidence_arithmetic, benchmark_aligned, and oracle_format_upper_bound layers; deterministic arithmetic and benchmark alignment remain side-cars`.
- Primary metrics: adapter_parse_failures=0, arithmetic_trace_present=38, benchmark_aligned_purist_correct=43, call_failures=0, event_evidence_total=85, event_evidence_valid=79, format_only_purist_correct=45, parse_failures=0, raw_llm_pragmatic_correct=42, raw_llm_purist_correct=42, raw_llm_scorable=45, rendering_operands_present=49, row_count=50, selected_event_trace_mismatches=0, selected_evidence_arithmetic_pragmatic_correct=49, selected_evidence_arithmetic_purist_correct=49, selected_evidence_arithmetic_raw_wrong_to_correct=7, selected_evidence_valid=45, structured_records=50.
- Evidence validity: Selected evidence exact 45/50; event evidence exact 79/85; selected-event trace mismatches 0/50.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse for the validation50 diagnostic. Error analysis reuses the saved validation50 JSONL only.
- Supersedes: `gan2026_llm_only_typed_adapter_reasoner_v0_validation25_live_2026-06-02`.
- Claim language: User-approved validation50 diagnostic after failed validation25 gate. Reject promotion: typed JSONAdapter/schema reliability is strong, but raw model-owned labels, exact selected evidence, and arithmetic traces are not clean enough; selected-evidence arithmetic is a deterministic side-car, not LLM-only success.
- Artifacts: `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_gpt41mini_v0_diagnostic_2026-06-02.jsonl`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_gpt41mini_v0_diagnostic_2026-06-02.md`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_error_analysis_2026-06-02.csv`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_error_analysis_2026-06-02.json`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_error_analysis_2026-06-02.md`.

### `gan2026_llm_only_typed_adapter_reasoner_v0_validation25_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_only_typed_adapter_reasoner`; mode `live validation25 typed DSPy JSONAdapter architecture smoke`; replay `cache_first`.
- Model role: LLM-only typed DSPy event extraction, clinical selection, and parser-ready final-label renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `typed DSPy JSONAdapter outputs with raw_llm, format_only, selected_evidence_arithmetic, benchmark_aligned, and oracle_format_upper_bound layers; deterministic arithmetic and benchmark alignment are side-cars`.
- Primary metrics: adapter_parse_failures=0, arithmetic_trace_present=17, benchmark_aligned_purist_correct=22, call_failures=0, event_evidence_total=38, event_evidence_valid=31, format_only_purist_correct=24, parse_failures=0, raw_llm_pragmatic_correct=22, raw_llm_purist_correct=22, raw_llm_scorable=22, rendering_operands_present=25, row_count=25, selected_event_trace_mismatches=0, selected_evidence_arithmetic_pragmatic_correct=25, selected_evidence_arithmetic_purist_correct=25, selected_evidence_arithmetic_raw_wrong_to_correct=3, selected_evidence_valid=19, structured_records=25.
- Evidence validity: Selected evidence exact 19/25; event evidence exact 31/38; selected-event trace mismatches 0/25.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse for this typed JSONAdapter smoke.
- Supersedes: `gan2026_dspy_adapter_architecture_report_2026-06-02`.
- Claim language: Typed-adapter LLM-only architecture smoke only. The scoped JSONAdapter and typed DSPy outputs produced 25/25 structured records with no adapter parse failures, but selected evidence exactness, parser-ready raw label rendering, and arithmetic traces miss the validation25 gate; selected-evidence arithmetic remains a deterministic side-car, not LLM-only success.
- Artifacts: `experiments/gan2026_dspy_adapter_architecture_report_2026-06-02.md`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation25 decision-0006 selected-evidence arithmetic/rendering smoke`; replay `cache_first`.
- Model role: LLM-heavy extraction, selected evidence, model-owned arithmetic/rendering, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v2 prompt/schema with model-owned rendering_operands and arithmetic_trace; deterministic selected-evidence arithmetic remains side-car only`.
- Primary metrics: arithmetic_trace_present=22, benchmark_aligned_purist_correct=21, deterministic_arithmetic_raw_wrong_to_correct=0, event_evidence_total=53, event_evidence_valid=51, format_only_purist_correct=21, parse_failures=3, raw_llm_pragmatic_correct=22, raw_llm_purist_correct=21, raw_llm_scorable=22, rendering_operands_present=22, row_count=25, selected_event_trace_mismatches=0, selected_evidence_arithmetic_pragmatic_correct=22, selected_evidence_arithmetic_purist_correct=21, selected_evidence_valid=22, structured_records=22.
- Evidence validity: Selected evidence exact 22/25; event evidence exact 51/53; selected-event trace mismatches 0/25.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse for this v2 prompt run.
- Supersedes: `gan2026_llm_replacement_postprocessing_ablation_validation250_2026-06-02`, `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation250_live_2026-06-02`.
- Claim language: Validation25 development smoke rejects validation50 escalation under decision 0006: raw model-owned Purist is 21/25 with zero deterministic arithmetic gap, but structured/scorable labels, selected evidence exactness, rendering operands, and arithmetic traces are only 22/25.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `saved-output row-level error analysis of decision-0006 validation25 smoke`; replay `analysis_only`.
- Model role: analysis-only row-level reviewer for v2 validation25 output-contract and label failures; model `none; saved openai/gpt-4.1-mini outputs only`.
- Repair mode/config: `analysis only over raw_llm, format_only, selected_evidence_arithmetic, and benchmark_aligned layers; no scorer/parser/prompt change`.
- Primary metrics: analysis_rows=6, invalid_json_truncation=1, missing_required_final_answer_field=2, nonselected_event_evidence_not_exact=2, raw_llm_purist_correct=21, selected_event_trace_mismatches=0, selected_evidence_arithmetic_purist_correct=21, wrong_selected_fact_or_cluster_semantics=1.
- Evidence validity: Classifies 2 invalid non-selected event-evidence rows; selected-answer evidence failures are attributable to the 3 blocking parse/schema rows.
- Cache/reuse source: experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.jsonl.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_live_2026-06-02`.
- Claim language: Analysis confirms no validation50 escalation: failure is mainly compactness/output contract, with one true cluster-cadence selected-fact/semantics error and zero deterministic-arithmetic rescue gap.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.csv`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.json`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact_validation25_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation25 compact decision-0006 selected-evidence arithmetic/rendering smoke`; replay `cache_first`.
- Model role: LLM-heavy extraction, selected evidence, compact model-owned arithmetic/rendering, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v2_compact prompt/schema with compact final_answer and model-owned rendering_operands/arithmetic_trace; deterministic selected-evidence arithmetic remains side-car only`.
- Primary metrics: arithmetic_trace_present=24, benchmark_aligned_purist_correct=23, deterministic_arithmetic_raw_wrong_to_correct=3, event_evidence_total=37, event_evidence_valid=35, format_only_purist_correct=22, parse_failures=0, raw_llm_pragmatic_correct=23, raw_llm_purist_correct=22, raw_llm_scorable=23, rendering_operands_present=24, row_count=25, selected_event_trace_mismatches=0, selected_evidence_arithmetic_pragmatic_correct=25, selected_evidence_arithmetic_purist_correct=25, selected_evidence_valid=22, structured_records=25.
- Evidence validity: Selected evidence exact 22/25; event evidence exact 35/37; selected-event trace mismatches 0/25.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse for this compact v2 prompt run.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02`.
- Claim language: Validation25 development smoke rejects validation50 escalation under decision 0006. Compact schema fixed the prior truncation/missing-selected-event-id failures with 25/25 structured records, but raw parser compatibility, selected evidence exactness, and model-owned rendering remain below stop rules; selected-evidence arithmetic is a deterministic side-car, not LLM-heavy success.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact_validation25_predeclaration_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.md`.

### `gan2026_llm_structured_v05_full_validation_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `750` rows.
- Pipeline: `llm_structured_events`; mode `live/cache-first structured v0.5 full-validation completion`; replay `cache_first`.
- Model role: LLM-first structured event extractor and clinical selector; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v0.5 structured-event selector plus large deterministic post-LLM repair stack`.
- Primary metrics: call_failures=0, deterministic_repair_notes=481, exact_selection_evidence_substrings=714, parse_schema_label_issues=0, pragmatic_correct=690, purist_correct=675, row_count=750, structured_records=750.
- Evidence validity: Exact selection evidence substrings 714/750; evidence exactness does not establish final repaired-label attribution.
- Cache/reuse source: Reused 720 raw model outputs from the validation ladder; live calls only for rows 721-750.
- Supersedes: `gan2026_llm_first_direct_extractor_validation750_2026-06-01`.
- Claim language: Reached 675/750 Purist on validation, but retrospective/audit reject it as a clean LLM-first result because deterministic semantic repair became prediction-bearing.
- Artifacts: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.jsonl`, `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.md`, `experiments/gan2026_llm_structured_decision_retrospective_2026-06-01.md`.

### `gan2026_llm_first_direct_extractor_validation750_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `750` rows.
- Pipeline: `llm_first_direct_extractor`; mode `live direct extraction validation ladder through rare full validation`; replay `cache_first`.
- Model role: LLM-first note-to-label extractor; model `openai/gpt-4.1-mini`.
- Repair mode/config: `deterministic code limited to label repair, evidence validation, and scoring`.
- Primary metrics: decision_records=709, exact_evidence_substrings=670, parse_schema_label_issues=41, pragmatic_correct=544, purist_correct=505, row_count=750.
- Evidence validity: Exact evidence substrings 670/750; 41 parse/schema/label issues.
- Cache/reuse source: DSPy cache; full validation reused 610 raw model outputs.
- Claim language: Validation development result only. Full validation reached 505/750 Purist, rejecting direct note-to-label extraction as the active LLM-first path.
- Artifacts: `experiments/gan2026_llm_first_validation25_gpt41mini_2026-05-31.jsonl`, `experiments/gan2026_llm_first_validation25_gpt41mini_2026-05-31.md`, `experiments/gan2026_llm_first_validation25_gpt41mini_v02_2026-05-31.jsonl`, `experiments/gan2026_llm_first_validation25_gpt41mini_v02_2026-05-31.md`, `experiments/gan2026_llm_first_validation250_gpt41mini_v01_2026-05-31.jsonl`, `experiments/gan2026_llm_first_validation250_gpt41mini_v01_2026-05-31.md`, `experiments/gan2026_llm_first_validation750_gpt41mini_v01_2026-06-01.jsonl`, `experiments/gan2026_llm_first_validation750_gpt41mini_v01_2026-06-01.md`.

### `gan2026_claim_table_v5_validation250_test450_generalization_audit_2026-06-01`
- Date/split: `2026-06-01`; `validation+test`; `700` rows.
- Pipeline: `llm_only_claim_table_selector`; mode `v5 max-token validation250 followed by frozen locked-test generalization audit`; replay `cache_first`.
- Model role: LLM-only direct-labeler claim extractor and final query selector; model `openai/gpt-4.1-mini`.
- Repair mode/config: `strict_schema_repair + frozen clean scorer-facing policy; no deterministic candidates before prediction`.
- Primary metrics: test_clean_pragmatic_correct=320, test_clean_purist_correct=301, test_exact_selected_final_evidence=418, test_parse_failures=5, test_raw_purist_correct=293, test_row_count=450, test_strict_purist_correct=294, test_structured_records=445.
- Evidence validity: Locked-test audit reports 1145/1188 exact claim evidence substrings and 418/450 exact selected-final evidence substrings; do not tune from test rows.
- Cache/reuse source: DSPy cache enabled; test450 resumed from 150 saved raw outputs.
- Supersedes: `gan2026_claim_table_v4_validation750_2026-06-01`.
- Claim language: Frozen generalization audit for claim-table v5. Test clean Purist was 301/450, so the path remains a comparator/failure-analysis artifact, not an active promoted candidate.
- Artifacts: `experiments/gan2026_llm_only_claim_table_selector_validation250_gpt41mini_v5_max2400_2026-06-01.jsonl`, `experiments/gan2026_llm_only_claim_table_selector_validation250_gpt41mini_v5_max2400_2026-06-01.md`, `experiments/gan2026_llm_only_claim_table_selector_validation250_v5_max2400_component_ablation_2026-06-01.json`, `experiments/gan2026_llm_only_claim_table_selector_validation250_v5_max2400_component_ablation_2026-06-01.md`, `experiments/gan2026_llm_only_claim_table_selector_test450_gpt41mini_v5_max2400_2026-06-01.jsonl`, `experiments/gan2026_llm_only_claim_table_selector_test450_gpt41mini_v5_max2400_2026-06-01.md`.

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

## Inform Phase7

### `exectv2_llm_only_all_entities_dev140_gpt41mini_20260612`
- Date/split: `2026-06-12`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_all_entities`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only all-entity single-pass extractor (one call per letter, all nine entities).; model `openai/gpt-4.1-mini`.
- Primary metrics: benchmark_per_item_f1=0.0, benchmark_per_letter_f1=0.0, call_failures=0, evidence_validity_rate=0.9418, mentions_scored=988, mentions_total=1049, parse_failures=0, phrase_only_per_item_f1=0.143, phrase_only_per_letter_f1=0.346, prompt_version=exectv2_llm_only_all_entities_v0.1, semantic_per_item_f1=0.087, semantic_per_letter_f1=0.236.
- Evidence validity: evidence_is_substring; 988/1049 valid, 61 dropped.
- Claim language: ExECTv2 Phase 6 LLM-only all-9 dev140 gpt-4.1-mini. Contract-clean (0 call/parse failures), evidence validity 94.18%, but low semantic overall F1 0.087/0.236 and benchmark with-CUI 0.000/0.000; suitable as locked all-entity LLM-only baseline for the authorized overall audit, not a competitive result.
- Artifacts: `experiments/exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl`, `experiments/exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.md`.

## Phase4 Complete

### `gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10`
- Date/split: `2026-06-10`; `test`; `450` rows.
- Pipeline: `phase4_test450_frozen_audit_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis: reads the four Phase 4 test450 frozen-audit artifacts (DCP, hybrid v5 with deep-replay via build_unified_pipeline_artifact, SE v0.5, CP v0.5); assembles the shared comparison table plus the hybrid-only routing appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=4, deterministic_canonical_pipeline_purist_correct_of_rendered=329, deterministic_canonical_pipeline_purist_rate=0.731, deterministic_canonical_pipeline_rendered_rows=450, hybrid_null_rows=116, hybrid_purist_correct_of_rendered=269, hybrid_purist_rate=0.805, hybrid_rendered_rows=334, hybrid_routed_rows=30, hybrid_structured_events_purist_correct_of_rendered=364, hybrid_structured_events_purist_rate=0.812, hybrid_structured_events_rendered_rows=448, llm_only_canonical_pipeline_purist_correct_of_rendered=326, llm_only_canonical_pipeline_purist_rate=0.724, llm_only_canonical_pipeline_rendered_rows=450, rows_per_architecture=450.
- Evidence validity: Surfaces, but does not collapse, that evidence-trace metrics are NOT uniform across architectures: DCP and SE report evidence_valid (substring presence), llm_only_canonical_pipeline reports evidence_text_contained, hybrid reports a CandidateSet source-id validity rate from deep-replay.
- Claim language: Phase 4 frozen test450 aggregate audit report (authorized 2026-06-09, plan Section 6): one-shot frozen aggregate read of the locked test450 split for deterministic_canonical_pipeline, hybrid (v5 prompt, deep-replayed), hybrid_structured_events (v0.5), and llm_only_canonical_pipeline (v0.5); deterministic and llm_only_direct_labeler intentionally excluded (Section 6 rationale). Of-rendered purist/pragmatic accuracy: DCP 0.731/0.758 (450/450 rendered), hybrid 0.805/0.841 (334/450 rendered, 30 routed all abstained), SE 0.812/0.850 (448/450 rendered), CP 0.724/0.769 (450/450 rendered). SE leads on both purist and pragmatic of-rendered accuracy; hybrid is second on accuracy of-rendered but renders the fewest rows (116 null/unscored of 450). No row-level holdout tuning; no re-runs based on these results.
- Artifacts: `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.jsonl`, `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.json`, `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md`.

### `gan2026_test450_phase4_frozen_audit_llm_only_canonical_pipeline_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `test`; `450` rows.
- Pipeline: `llm_only_canonical_pipeline`; mode `live`; replay `native_run_split`.
- Model role: fully-LLM canonical-pipeline labeler (v0.5): single LLM call -> decision_record with rule-taxonomy self-report.; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, evidence_text_contained=415, evidence_text_contained_rate=0.9222, parse_or_validation_failures=0, pragmatic_accuracy=0.7689, pragmatic_correct=346, prompt_version=gan2026_llm_only_canonical_pipeline_v0.5, purist_accuracy=0.7244, purist_correct=326, repair_notes=227, rows=450.
- Evidence validity: evidence_text_contained reported per row (deliberately distinct from evidence_valid).
- Claim language: Phase 4 frozen test450 aggregate audit (authorized 2026-06-09, plan Section 6) -- llm_only_canonical_pipeline v0.5 prompt (gan2026_llm_only_canonical_pipeline_v0.5) over the locked test450 split. 450/450 decision records, 0 call failures, 0 parse/schema/label issues, 227 deterministic repair notes, evidence_text_contained 415/450 (0.9222). Purist accuracy 0.7244 (326/450), Pragmatic accuracy 0.7689 (346/450).
- Artifacts: `experiments/gan2026_test450_phase4_frozen_audit_llm_only_canonical_pipeline_gpt41mini_2026-06-09.jsonl`, `experiments/gan2026_test450_phase4_frozen_audit_llm_only_canonical_pipeline_gpt41mini_2026-06-09.md`, `experiments/gan2026_test450_phase4_cp_gpt41mini_2026-06-09_stdout.txt`, `experiments/gan2026_test450_phase4_cp_gpt41mini_2026-06-09_stderr.txt`.

### `gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `test`; `450` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `native_run_split`.
- Model role: structured-events extraction (v0.5): raw note text -> structured events; deterministic normalize/project/render/score/route downstream.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `hybrid_full_stack`.
- Primary metrics: call_failures=0, evidence_valid=418, evidence_valid_rate=0.929, parse_or_validation_failures=2, pragmatic_accuracy=0.8467, pragmatic_correct=381, prompt_version=gan2026_hybrid_structured_events_v0.5, purist_accuracy=0.8089, purist_correct=364, repair_notes=306, rows=450, structured_records=448.
- Evidence validity: evidence_valid (free-text substring presence) reported per row.
- Claim language: Phase 4 frozen test450 aggregate audit (authorized 2026-06-09, plan Section 6) -- hybrid_structured_events v0.5 prompt (gan2026_hybrid_structured_events_v0.5) over the locked test450 split, repair_mode hybrid_full_stack. Structured records 448/450, 0 call failures, 2 parse/schema/label issues, 306 deterministic repair notes, evidence_valid 418/450 (0.929). Purist accuracy 0.8089 (364/450), Pragmatic accuracy 0.8467 (381/450).
- Artifacts: `experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl`, `experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.md`, `experiments/gan2026_test450_phase4_se_gpt41mini_2026-06-09_stdout.txt`, `experiments/gan2026_test450_phase4_se_gpt41mini_2026-06-09_stderr.txt`.

### `gan2026_test450_phase4_frozen_audit_hybrid_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `test`; `450` rows.
- Pipeline: `hybrid`; mode `live`; replay `assessment_stage_only`.
- Model role: hybrid clinical assessment probe (v5): CandidateSet -> clinical assessment schema; deterministic downstream (normalize/project/render/score/route) applied in deep-replay.; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, missing_candidate_set_rows=0, parse_or_validation_failures=0, prompt_version=gan2026_candidate_set_clinical_assessment_probe_v5, rows=450.
- Evidence validity: Assessment-stage probe only -- CandidateSet source-id validity rate computed in deep-replay during report build, not in this artifact directly.
- Claim language: Phase 4 frozen test450 aggregate audit (authorized 2026-06-09, plan Section 6) -- hybrid v5 prompt (gan2026_candidate_set_clinical_assessment_probe_v5) clinical-assessment probe over the locked test450 split, live-generated CandidateSets embedded per row. 450/450 rows, 0 call failures, 0 parse/validation failures, 0 missing candidate sets. Assessment-stage probe only -- no rendered/null/purist/routed numbers of its own; those are produced via deep-replay in gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.
- Artifacts: `experiments/gan2026_test450_phase4_frozen_audit_hybrid_gpt41mini_2026-06-09.jsonl`, `experiments/gan2026_test450_phase4_frozen_audit_hybrid_gpt41mini_2026-06-09.md`, `experiments/gan2026_test450_phase4_hybrid_gpt41mini_2026-06-09_stdout.txt`, `experiments/gan2026_test450_phase4_hybrid_gpt41mini_2026-06-09_stderr.txt`.

### `gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `test`; `450` rows.
- Pipeline: `deterministic_canonical_pipeline`; mode `deterministic`; replay `native_run_split`.
- Model role: Deterministic canonical-pipeline baseline; no model calls.; model `none`.
- Primary metrics: pragmatic_accuracy=0.7578, pragmatic_correct=341, purist_accuracy=0.7311, purist_correct=329, rows=450.
- Evidence validity: evidence_valid (free-text substring presence) reported per row.
- Claim language: Phase 4 frozen test450 aggregate audit (authorized 2026-06-09, plan Section 6) -- deterministic_canonical_pipeline over the locked test450 split. Fully deterministic pipeline, no live model calls (gpt41mini in the filename reflects the comparison cohort label, not a model dependency). One-shot frozen aggregate read; no row-level tuning, no re-runs based on results.
- Artifacts: `experiments/gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_gpt41mini_2026-06-09.jsonl`, `experiments/gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_gpt41mini_2026-06-09.md`.

## Inform Phase4

### `exectv2_hybrid_dev140_qwen3635b_20260611`
- Date/split: `2026-06-11`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 hybrid candidate-set + clinical-assessment extractor (deterministic candidates -> LLM keep/route/attribute -> deterministic normalize, SeizureFrequency only).; model `ollama_chat/qwen3.6:35b`.
- Primary metrics: call_failures=0, candidates_offered=639, mentions_kept=313, mentions_routed=45, mentions_scored=235, parse_failures=1, phrase_only_per_item_f1=0.498, phrase_only_per_letter_f1=0.73, prompt_version=exectv2_hybrid_candidate_assessment_v0.2, sf_benchmark_per_item_f1=0.228, sf_benchmark_per_letter_f1=0.451, sf_semantic_per_item_f1=0.228, sf_semantic_per_letter_f1=0.451.
- Evidence validity: evidence_is_substring (exact source-text substring check); routing taxonomy {no_frequency_attributes:25, bare_nonzero_count:13, empty_evidence:5, evidence_not_substring:2}.
- Supersedes: `exectv2_hybrid_dev50partial_qwen3635b_20260611`.
- Claim language: ExECTv2 Phase 4 - hybrid (candidate + assessment) full dev run (140 letters, D16 gold, SeizureFrequency only), qwen3.6:35b. Completed by RESUMING from a 50/140 checkpoint after a power interruption (core.run_resume; n_resumed=50) - no work re-spent. phrase_only per-item F1 0.498, per-letter 0.730 - below gpt-4.1-mini hybrid (0.585/0.781) but above the deterministic baseline per-letter (0.604) and the qwen LLM-only per_entity (0.642). sf_semantic == sf_benchmark per-item 0.228, per-letter 0.451 - below gpt hybrid (0.327/0.578) and deterministic (0.362/0.575), far above qwen LLM-only (0.036/0.104). 639 candidates offered, 313 kept by LLM, 235 scored, 45 routed; 0 call failures, 1 parse failure (one max_tokens=3000 truncation). gpt-4.1-mini > qwen on hybrid, mirroring the LLM-only result.
- Artifacts: `experiments/exectv2_hybrid_v02_dev140_qwen3635b_20260611.jsonl`, `experiments/exectv2_hybrid_v02_dev140_qwen3635b_20260611.md`.

### `exectv2_hybrid_dev140_gpt41mini_20260611`
- Date/split: `2026-06-11`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 hybrid candidate-set + clinical-assessment extractor (deterministic candidates -> LLM keep/route/attribute -> deterministic normalize, SeizureFrequency only).; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, candidates_offered=639, mentions_kept=288, mentions_routed=37, mentions_scored=247, parse_failures=0, phrase_only_per_item_f1=0.585, phrase_only_per_letter_f1=0.781, prompt_version=exectv2_hybrid_candidate_assessment_v0.2, sf_benchmark_per_item_f1=0.327, sf_benchmark_per_letter_f1=0.578, sf_semantic_per_item_f1=0.327, sf_semantic_per_letter_f1=0.578.
- Evidence validity: evidence_is_substring (exact source-text substring check); routing taxonomy {no_frequency_attributes:7, bare_nonzero_count:29, evidence_not_substring:1}.
- Claim language: ExECTv2 Phase 4 - hybrid (candidate + assessment) full dev run (140 letters, D16 gold, SeizureFrequency only). phrase_only per-item F1 0.585, per-letter 0.781 - best phrase recall of any family and the only architecture whose per-letter clears the SF benchmark target 0.68. sf_semantic == sf_benchmark per-item 0.327, per-letter 0.578 - best attribute-aware per-letter of any architecture (above deterministic 0.575 and far above LLM-only), marginally below deterministic on per-item (0.362). 639 candidates offered, 288 kept by LLM, 247 scored, 37 routed; 0 call/parse failures.
- Artifacts: `experiments/exectv2_hybrid_v02_dev140_gpt41mini_20260611.jsonl`, `experiments/exectv2_hybrid_v02_dev140_gpt41mini_20260611.md`.

### `exectv2_llm_only_single_pass_dev140_qwen3635b_20260610`
- Date/split: `2026-06-10`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_single_pass`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only single-pass extractor (one call per letter, all SF mentions + attributes + evidence).; model `ollama_chat/qwen3.6:35b`.
- Primary metrics: call_failures=0, evidence_validity_rate=0.945, mentions_scored=189, mentions_total=200, parse_failures=2, phrase_only_per_item_f1=0.383, phrase_only_per_letter_f1=0.623, prompt_version=exectv2_llm_only_single_pass_v0.2, sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.09, sf_semantic_per_letter_f1=0.213.
- Evidence validity: evidence_is_substring; 189/200 valid, 11 dropped.
- Claim language: ExECTv2 Phase 3 — qwen3.6:35b single_pass dev140. phrase_only per-letter 0.623 (below gpt-4.1-mini 0.701 by 11%). sf_semantic per-letter 0.213 (above gpt-4.1-mini 0.197 by 8%). 2 parse failures. 94.5% evidence validity. sf_benchmark 0.000 (CUI D3).
- Artifacts: `experiments/exectv2_llm_only_single_pass_dev140_qwen3635b_20260610.jsonl`, `experiments/exectv2_llm_only_single_pass_dev140_qwen3635b_20260610.md`.

### `exectv2_llm_only_single_pass_dev140_gpt41mini_20260610`
- Date/split: `2026-06-10`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_single_pass`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only single-pass extractor (one call per letter, all SF mentions + attributes + evidence).; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, evidence_validity_rate=0.9749, mentions_scored=195, mentions_total=199, parse_failures=0, phrase_only_per_item_f1=0.466, phrase_only_per_letter_f1=0.701, prompt_version=exectv2_llm_only_single_pass_v0.2, sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.094, sf_semantic_per_letter_f1=0.197.
- Evidence validity: evidence_is_substring (exact source-text substring check); 195/199 valid, 4 dropped.
- Claim language: ExECTv2 Phase 3 — LLM-only single-pass full dev run (140 letters, D16 gold, SeizureFrequency only). phrase_only per-item F1 0.466, per-letter 0.701 (exceeds SF benchmark target 0.68). sf_semantic near-zero (attribute-convention mismatch). sf_benchmark 0.000 (CUI lookup is shared post-step D3). Deterministic baseline: phrase_only 0.382/0.604.
- Artifacts: `experiments/exectv2_llm_only_single_pass_dev140_gpt41mini_20260610.jsonl`, `experiments/exectv2_llm_only_single_pass_dev140_gpt41mini_20260610.md`.

### `exectv2_llm_only_per_entity_dev140_qwen3635b_20260610`
- Date/split: `2026-06-10`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_per_entity`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only per-entity extractor (one focused call per entity type per letter, SF only).; model `ollama_chat/qwen3.6:35b`.
- Primary metrics: call_failures=0, evidence_validity_rate=0.961, mentions_scored=197, mentions_total=205, parse_failures=0, phrase_only_per_item_f1=0.401, phrase_only_per_letter_f1=0.642, prompt_version=exectv2_llm_only_per_entity_v0.2, sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.036, sf_semantic_per_letter_f1=0.104.
- Evidence validity: evidence_is_substring; 197/205 valid, 8 dropped.
- Claim language: ExECTv2 Phase 3 — qwen3.6:35b per_entity dev140. phrase_only per-letter 0.642 (below gpt-4.1-mini 0.698 by 8%). sf_semantic per-item 0.036, per-letter 0.104 — dramatically worse than gpt-4.1-mini per_entity (0.135/0.264). Unlike gpt-4.1-mini, qwen does NOT benefit from focused per_entity prompt for attributes; sf_semantic is even worse than qwen single_pass (0.090/0.213). 0 parse failures, 96.1% evidence validity. sf_benchmark 0.000 (CUI D3).
- Artifacts: `experiments/exectv2_llm_only_per_entity_dev140_qwen3635b_20260610.jsonl`, `experiments/exectv2_llm_only_per_entity_dev140_qwen3635b_20260610.md`.

### `exectv2_llm_only_per_entity_dev140_gpt41mini_20260610`
- Date/split: `2026-06-10`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_per_entity`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only per-entity extractor (one focused call per entity type per letter, SF only).; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, evidence_validity_rate=0.9632, mentions_scored=183, mentions_total=190, parse_failures=0, phrase_only_per_item_f1=0.486, phrase_only_per_letter_f1=0.698, prompt_version=exectv2_llm_only_per_entity_v0.1, sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.135, sf_semantic_per_letter_f1=0.264.
- Evidence validity: evidence_is_substring (exact source-text substring check); 183/190 valid, 7 dropped.
- Claim language: ExECTv2 Phase 3 — LLM-only per-entity full dev run (140 letters, D16 gold, SeizureFrequency only). phrase_only per-item F1 0.486, per-letter 0.698 (exceeds SF benchmark target 0.68). sf_semantic 0.135/0.264 — 44% better than single_pass per-item (0.094), 34% better per-letter (0.197). sf_benchmark 0.000 (CUI D3). Best LLM-only config for attribute matching. Deterministic baseline: phrase_only 0.382/0.604.
- Artifacts: `experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260610.jsonl`, `experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260610.md`.

## Phase3 Complete Gpt41Mini

### `gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase3_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis: reads Phase 2 deterministic/DCP artifacts, Phase 3 hybrid v5 artifact (with deep-replay for rendered/null/purist/routed numbers), Phase 3 DL v0.5 / CP v0.5 artifacts, Phase 1 SE artifact; assembles shared comparison table plus hybrid-only routing appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=673, deterministic_purist_correct_of_rendered=673, hybrid_purist_correct_of_rendered=526, hybrid_purist_rate=0.881, hybrid_rendered_rows=597, hybrid_structured_events_purist_correct_of_rendered=661, llm_only_canonical_pipeline_purist_correct_of_rendered=582, llm_only_direct_labeler_purist_correct_of_rendered=575, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, that evidence-trace metrics are NOT uniform across architectures: four report evidence_valid (substring presence), llm_only_canonical_pipeline reports evidence_text_contained, hybrid reports CandidateSet source-id validity rate.
- Supersedes: `gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09`.
- Claim language: Phase 3 three-way architecture comparison report (validation750, gpt-4.1-mini). Deterministic/DCP from Phase 2 iteration 2 (digit-only de-overfitting); hybrid from v5 run (FM-2/FM-5b/FM-6 prompt fixes); DL v0.5 / CP v0.5 from Phase 3 LLM-only runs; SE from Phase 1 (no SE-specific Phase 3 changes). Key Phase 3 vs Phase 2 delta for hybrid (gpt-4.1-mini): 597 rendered vs 589 (+8 more rendered), 526/597 purist = 88.1% vs 500/589 = 84.9% (+3.2pp); 545/597 pragmatic = 91.3%. hybrid_structured_events leads purist at 661/748=88.4%. deterministic/DCP ceiling: 673/741=90.8%. No test450 read; no holdout-facing claim.
- Artifacts: `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.md`.

## Inform Phase3

### `gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase1_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis -- reads completed validation750 run artifacts; assembles shared comparison table plus hybrid-only routing appendix; makes no hosted LLM calls.; model `ollama_chat/qwen3.6:35b`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=688, deterministic_purist_correct_of_rendered=688, hybrid_purist_correct_of_rendered=291, hybrid_rendered_rows=400, hybrid_structured_events_purist_correct_of_rendered=624, llm_only_canonical_pipeline_purist_correct_of_rendered=544, llm_only_direct_labeler_purist_correct_of_rendered=550, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, the fact that evidence-trace metrics are NOT uniform across architectures.
- Supersedes: `gan2026_three_way_comparison_phase1_report_qwen3635b_validation750_2026-06-09`.
- Claim language: Phase 1 three-way architecture comparison, ollama_chat/qwen3.6:35b pass, validation750 only (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 3 + Section 8b). Full 750-row surface: hybrid now uses the live-wired candidate-set generation (section 8a) merged from the resume-part into the 2026-06-08 file; 0 candidate_set_missing rows. Supersedes the interim 250-row-scoped hybrid report (gan2026_three_way_comparison_phase1_report_qwen3635b_validation750_2026-06-09). Key findings: hybrid_structured_events leads at 624/746 (0.836); hybrid renders only 400/750 rows (much lower surface than gpt-4.1-mini 589/750 or deepseek 604/750), with 62 routed (15.5%); llm_only_direct_labeler and llm_only_canonical_pipeline nearly tied (550/749=0.734 vs 544/748=0.727). Closes Section 8b.
- Artifacts: `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.md`.

### `gan2026_phase3_error_analysis_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase3_error_analysis`; mode `analysis-only`; replay `analysis_only`.
- Model role: Error analysis and failure taxonomy for Phase 3 prompt engineering; model `none`.
- Primary metrics: architectures_analysed=4, cp_failures=169, cp_rule_fire_failure_rate_max=0.426, dl_failures=186, hybrid_failures=88, named_failure_modes=8, se_failures=89, universal_failures=20.
- Evidence validity: Analysis draws directly from Phase 1 validation750 JSONL artifacts; row-by-row tables verified against source prediction and gold records.
- Claim language: Phase 3 error analysis: row-by-row + thematic failure catalogue over Phase 1 validation750 results for four architectures (gpt-4.1-mini). Documents 8 named failure modes (FM-1 through FM-8) across 532 total failures. Critical finding: four highest-failure-rate CP rules (seizure_free_conflict 42.6%, same_window_additive_frequency 34.7%, denominator_window_mismatch 30.3%, concrete_frequency_precedence 27.8%) account for 143/169 CP failures where a rule was cited — model cites rule then violates it. 20 universal failures (all 4 architectures). Priority ranking: FM-2 seizure-free FP (97) > FM-1 denominator window (~66 LLM-improvable) > FM-3 unknown FP (132) > FM-6 highest-type selection (~25 universal). Input to Phase 3 prompt-engineering decisions.
- Artifacts: `docs/research/gan2026_phase3_error_analysis_2026-06-09.md`.

### `gan2026_cross_model_comparison_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `cross_model_comparison`; mode `analysis-only`; replay `analysis_only`.
- Model role: Cross-model synthesis document -- no model calls; reads existing Phase 1 artifacts and computed failure breakdowns.; model `none`.
- Primary metrics: architectures_compared=6, deepseek_dl_sf_false_pos=56, deepseek_hybrid_rendered=604, deepseek_se_purist_rate=0.821, gpt41mini_dl_unknown_false_pos=59, gpt41mini_hybrid_rendered=589, gpt41mini_se_purist_rate=0.884, models_compared=3, qwen_dl_unknown_false_pos=91, qwen_hybrid_rendered=400, qwen_se_purist_rate=0.836.
- Evidence validity: Derived from Phase 1 per-row JSONL comparison fields for DL, CP, SE; aggregate numbers from Phase 1 report JSONLs for hybrid and all architectures.
- Claim language: Cross-model synthesis comparing all three Phase 1 models (gpt-4.1-mini, deepseek-v4-flash, qwen3.6-35b) across all six architecture configurations on validation750. Includes per-row failure category breakdowns for DL, CP, SE (hybrid row-level data not available for deepseek/qwen without deep-replay extraction). Key findings: (1) SE is consistently best across models but gpt-4.1-mini leads by 5-6pp; (2) qwen dominant failure is unknown_false_pos (91 DL vs 59 gpt-4.1-mini) -- reverse of deepseek (highest seizure_free_false_pos: 56 DL); (3) CP guidance block helps gpt-4.1-mini (+2.3pp) but harms qwen (-0.7pp); (4) FM-6 drop-attack selection is gpt-4.1-mini-specific -- qwen and deepseek already correct; (5) qwen hybrid renders only 400/750 rows vs 589/604 for gpt/deepseek; (6) deepseek hybrid routing dominated by rendered_label_supported_but_policy_sensitive (97/123) driven by its SF over-confidence.
- Artifacts: `docs/research/gan2026_cross_model_comparison_2026-06-09.md`.

## Historical

### `exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612`
- Date/split: `2026-06-12`; `full200_overall_audit`; `200` rows.
- Pipeline: `exectv2_llm_only_all_entities`; mode `live`; replay `live`.
- Model role: ExECTv2 Phase 7 frozen full-200 overall all-entity LLM-only audit.; model `openai/gpt-4.1-mini`.
- Primary metrics: authorization=full-200 overall read authorized by user 2026-06-12 (Phase 6/7), benchmark_per_item_ci=[0.0, 0.0], benchmark_per_item_f1=0.0, benchmark_per_letter_ci=[0.0, 0.0], benchmark_per_letter_f1=0.0, call_failures=0, evidence_validity_rate=0.9323, git_head=8d7ecfbc101f+dirty, mentions_raw=1492, mentions_scored=1391, parse_failures=0, phrase_only_per_item_f1=0.147, phrase_only_per_letter_f1=0.362, prompt_version=exectv2_llm_only_all_entities_v0.1, semantic_per_item_ci=[0.0711, 0.0985], semantic_per_item_f1=0.0844, semantic_per_letter_ci=[0.2007, 0.2632], semantic_per_letter_f1=0.2317.
- Evidence validity: frozen audit; exact substring evidence gate recorded in report.
- Claim language: Phase 7 frozen overall all-entity audit. Semantic overall F1 0.084/0.232; benchmark with-CUI F1 0.000/0.000; locked at git 8d7ecfbc101f+dirty.
- Artifacts: `experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl`, `experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.md`.

### `exectv2_audit_rules_full200_modelindependent_20260611`
- Date/split: `2026-06-11`; `full200_audit`; `200` rows.
- Pipeline: `exectv2_deterministic`; mode `deterministic`; replay `analysis_only`.
- Model role: ExECTv2 Phase 7 frozen full-200 SF audit (rules).; model `(model-independent)`.
- Primary metrics: authorization=full-200 read authorized by user 2026-06-11 (Phase 7), call_failures=0, git_head=ab0d8d5cb7aa, parse_failures=0, phrase_only_per_item_f1=0.4725, phrase_only_per_letter_f1=0.6756, prompt_version=n/a (deterministic rules), sf_benchmark_per_item_ci=[0.2538, 0.3879], sf_benchmark_per_item_f1=0.3211, sf_benchmark_per_letter_ci=[0.451, 0.6184], sf_benchmark_per_letter_f1=0.5392, sf_semantic_per_item_f1=0.3211, sf_semantic_per_letter_f1=0.5392.
- Evidence validity: frozen audit; gates recorded in the audit report.
- Claim language: Phase 7 frozen SF audit over all 200 letters (authorized 2026-06-11). Headline sf_benchmark per-item F1 0.321 (CI 0.254-0.388), per-letter F1 0.539 (CI 0.451-0.618) vs published 0.66/0.68. Immutable; locked at git ab0d8d5cb7aa.
- Artifacts: `experiments/exectv2_audit_rules_full200_modelindependent_20260611.md`, `experiments/exectv2_audit_rules_full200_modelindependent_20260611.jsonl`.

### `exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611`
- Date/split: `2026-06-11`; `full200_audit`; `200` rows.
- Pipeline: `exectv2_llm_only_per_entity`; mode `live`; replay `live`.
- Model role: ExECTv2 Phase 7 frozen full-200 SF audit (llm_only_per_entity/per_entity).; model `openai/gpt-4.1-mini`.
- Primary metrics: authorization=full-200 read authorized by user 2026-06-11 (Phase 7), call_failures=0, git_head=ab0d8d5cb7aa, parse_failures=0, phrase_only_per_item_f1=0.4627, phrase_only_per_letter_f1=0.6766, prompt_version=exectv2_llm_only_per_entity_v0.2, sf_benchmark_per_item_ci=[0.0, 0.0], sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_ci=[0.0, 0.0], sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.1216, sf_semantic_per_letter_f1=0.2463.
- Evidence validity: frozen audit; gates recorded in the audit report.
- Claim language: Phase 7 frozen SF audit over all 200 letters (authorized 2026-06-11). Headline sf_benchmark per-item F1 0.000 (CI 0.000-0.000), per-letter F1 0.000 (CI 0.000-0.000) vs published 0.66/0.68. Immutable; locked at git ab0d8d5cb7aa.
- Artifacts: `experiments/exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611.md`, `experiments/exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611.jsonl`.

### `exectv2_audit_hybrid_full200_gpt41mini_20260611`
- Date/split: `2026-06-11`; `full200_audit`; `200` rows.
- Pipeline: `exectv2_hybrid`; mode `live`; replay `live`.
- Model role: ExECTv2 Phase 7 frozen full-200 SF audit (hybrid).; model `openai/gpt-4.1-mini`.
- Primary metrics: authorization=full-200 read authorized by user 2026-06-11 (Phase 7), call_failures=0, git_head=ab0d8d5cb7aa, parse_failures=0, phrase_only_per_item_f1=0.5482, phrase_only_per_letter_f1=0.7778, prompt_version=exectv2_hybrid_candidate_assessment_v0.2, sf_benchmark_per_item_ci=[0.1924, 0.3008], sf_benchmark_per_item_f1=0.2458, sf_benchmark_per_letter_ci=[0.3874, 0.5462], sf_benchmark_per_letter_f1=0.4696, sf_semantic_per_item_f1=0.2458, sf_semantic_per_letter_f1=0.4696.
- Evidence validity: frozen audit; gates recorded in the audit report.
- Claim language: Phase 7 frozen SF audit over all 200 letters (authorized 2026-06-11). Headline sf_benchmark per-item F1 0.246 (CI 0.192-0.301), per-letter F1 0.470 (CI 0.387-0.546) vs published 0.66/0.68. Immutable; locked at git ab0d8d5cb7aa.
- Artifacts: `experiments/exectv2_audit_hybrid_full200_gpt41mini_20260611.md`, `experiments/exectv2_audit_hybrid_full200_gpt41mini_20260611.jsonl`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation50_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `50` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation50 output-contract gate with first 25 rows reused after alias repair`; replay `cache_first`.
- Model role: LLM-heavy extraction, clinical selection, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v1 prompt/schema plus non-semantic enum/unit alias repair; score layers raw_llm, format_only, selected_evidence_arithmetic, benchmark_aligned, oracle_format_upper_bound`.
- Primary metrics: benchmark_aligned_purist_correct=45, call_failures=0, event_evidence_total=125, event_evidence_valid=120, format_only_purist_correct=41, parse_failures=0, raw_llm_purist_correct=41, raw_llm_scorable=45, row_count=50, selected_event_trace_mismatches=1, selected_evidence_arithmetic_purist_correct=48, selected_evidence_valid=48, structured_records=50.
- Evidence validity: Selected evidence exact 48/50; event evidence exact 120/125; one selected-event trace mismatch.
- Cache/reuse source: Reused first 25 raw outputs from the interrupted validation50 checkpoint, then ran rows 26-50 live with DSPy cache enabled.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02`.
- Claim language: Validation50 passed the v1 output-contract gate, but raw/format-only Purist was only 41/50; escalation to validation250 was diagnostic, not promotional.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation50_gpt41mini_v1_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation50_gpt41mini_v1_2026-06-02.md`.

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

### `gan2026_llm_structured_v05_attribution_repair_ladder650_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `650` rows.
- Pipeline: `llm_structured_events`; mode `saved-output repair-family attribution ladder over structured v0.5 outputs`; replay `saved_output_replay`.
- Model role: analysis-only attribution and deterministic repair-family replay; model `none; saved openai/gpt-4.1-mini outputs only`.
- Repair mode/config: `raw_model_selection + strict_format + frozen_clean_policy + named deterministic semantic repair families`.
- Primary metrics: clean_policy_purist_correct=438, full_stack_pragmatic_correct=598, full_stack_purist_correct=588, raw_purist_correct=394, row_count=650, selected_evidence_repair_purist_correct=546, strict_format_purist_correct=413.
- Evidence validity: Saved-output replay keeps exact selection evidence at 619/650 from the audited source; repair-family attribution separates evidence validity from final-label ownership.
- Cache/reuse source: Saved raw output source: experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl.
- Supersedes: `gan2026_llm_structured_v05_full_validation_2026-06-01`.
- Claim language: Backfilled attribution ladder. Clean attribution ends at 438/650 Purist under frozen clean policy; full 588/650 stack is hybrid deterministic post-processing, not clean LLM-first success.
- Artifacts: `experiments/gan2026_llm_structured_validation750_v05_repair_audit_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_repair_ablation_2026-06-01.json`, `experiments/gan2026_llm_structured_validation750_v05_repair_ablation_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_basic_split_repair_ablation_2026-06-01.json`, `experiments/gan2026_llm_structured_validation750_v05_basic_split_repair_ablation_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.json`, `experiments/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.csv`, `experiments/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.md`, `experiments/gan2026_clean_policy_freeze_ladder650_v0_2026-06-01.json`, `experiments/gan2026_clean_policy_freeze_ladder650_v0_2026-06-01.md`, `experiments/gan2026_grouped_attribution_repair_ladder650_v0_2026-06-01.json`, `experiments/gan2026_grouped_attribution_repair_ladder650_v0_2026-06-01.md`, `experiments/gan2026_combined_attribution_repair_ladder650_v0_2026-06-01.json`, `experiments/gan2026_combined_attribution_repair_ladder650_v0_2026-06-01.md`.

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

### `gan2026_rules_only_v1_test_holdout_2026-05-31`
- Date/split: `2026-05-31`; `test`; `450` rows.
- Pipeline: `rules_only`; mode `locked-test holdout evaluation of frozen rules_only_v1`; replay `analysis_only`.
- Model role: deterministic comparator; model `none`.
- Repair mode/config: `deterministic_v1; no test-row tuning or row-level text inspection`.
- Primary metrics: rows=450, test_pragmatic_f1=0.7867, test_purist_f1=0.76, validation_purist_f1_context=0.9293.
- Evidence validity: Aggregate holdout report; no test row-level debugging allowed.
- Supersedes: `gan2026_rules_only_v1_baseline_2026-05-31`.
- Claim language: Final holdout result for frozen deterministic V1 only; useful as generalization context, not a benchmark-comparable paper claim or tuning surface.
- Artifacts: `experiments/gan2026_v1_test_holdout_2026-05-31.md`.

### `gan2026_rules_only_v1_baseline_2026-05-31`
- Date/split: `2026-05-31`; `validation+test`; `1200` rows.
- Pipeline: `rules_only`; mode `rules_only_v1`; replay `analysis_only`.
- Model role: deterministic comparator; model `none`.
- Repair mode/config: `deterministic_v1`.
- Primary metrics: test_pragmatic=0.7867, test_purist=0.76, validation_pragmatic=0.9387, validation_purist=0.9293.
- Evidence validity: Report-level deterministic evidence summary.
- Claim language: Frozen rules_only_v1 comparator; aggregate locked-test context is historical, not a tuning surface.
- Artifacts: `experiments/gan2026_v1_deterministic_baseline_2026-05-31.md`.

### `gan2026_dspy_adjudicator_devset_v04_2026-05-31`
- Date/split: `2026-05-31`; `validation_devset`; `16` rows.
- Pipeline: `dspy_final_selection_adjudicator`; mode `live validation-only dev-set adjudicator run`; replay `live`.
- Model role: final-selection adjudicator over deterministic V1 diagnostics; model `openai/gpt-4.1-mini`.
- Repair mode/config: `frozen deterministic V1 diagnostics; no scorer or split-policy change`.
- Primary metrics: call_failures=0, parse_failures=0, pragmatic_correct=12, purist_correct=9, row_count=16.
- Evidence validity: Uses deterministic V1 candidate diagnostics from validation-mined dev set; no locked-test row failures inspected.
- Claim language: Early validation-only DSPy adjudicator diagnostic. Kept as lineage for later hybrid adjudicator work; not a promoted candidate or benchmark result.
- Artifacts: `experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.jsonl`, `experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.md`, `experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_v04_2026-05-31.jsonl`, `experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_v04_2026-05-31.md`.
