# Gan 2026 Run Registry

Generated from `experiments/registry.jsonl`. The JSONL file remains the canonical machine-readable registry.

## Revise

### `gan2026_three_way_comparison_validation750_llm_only_structured_events_gpt41mini_2026-06-07`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_structured_events`; mode `live`; replay `live`.
- Model role: LLM-only structured-events extractor and selector -- slim source-near event schema; deterministic code limited to Gan normalization, evidence validation, and scoring; model `openai/gpt-4.1-mini`.
- Primary metrics: evidence_valid_rows=691, null_rows=2, pragmatic_correct_of_rendered=679, purist_correct_of_rendered=661, rendered_rows=748.
- Evidence validity: 691/750 rows (92.1%) carry an evidence_valid substring-presence trace; the 2 null rows are rare parse failures, not a structural give-up signal -- see the Phase 1 report's per-architecture rendered/null derivation footnote.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands. Restarted after fixing a schema_repair.py _ASSERTION_ALIASES bug that remapped the already-valid assertion_status value 'unknown' to the invalid 'unclear'; confirmed clean via re-pilot validation25 (0 failures, 100% accuracy) before this full run (see run markdown header).
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_structured_events_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_structured_events_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_llm_only_structured_events_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_structured_events`; mode `live`; replay `live`.
- Model role: LLM-only structured-events extractor and selector -- slim source-near event schema; deterministic code limited to Gan normalization, evidence validation, and scoring. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Primary metrics: call_failures=0, evidence_valid_rate=0.957, evidence_valid_rows=718, null_rows=8, parse_or_validation_failures=8, pragmatic_accuracy=0.845, pragmatic_correct=634, purist_accuracy=0.812, purist_correct=609, rendered_rows=742.
- Evidence validity: 718/750 rows (95.7%) carry an evidence_valid substring-presence trace. 8 parse_or_validation_failures (~1%) -- within accepted noise for this architecture.
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_structured_events_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_structured_events_deepseek_2026-06-08.md`.

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
- Model role: Analysis-only synthesis -- reads six already-completed gpt-4.1-mini validation750 architecture-comparison artifacts (deterministic, deterministic_canonical_pipeline, hybrid, llm_only_direct_labeler, llm_only_structured_events, llm_only_canonical_pipeline) and assembles a shared comparison table plus a hybrid-only routing-taxonomy appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=688, deterministic_purist_correct_of_rendered=688, hybrid_purist_correct_of_rendered=511, llm_only_canonical_pipeline_purist_correct_of_rendered=581, llm_only_direct_labeler_purist_correct_of_rendered=564, llm_only_structured_events_purist_correct_of_rendered=661, rows_per_architecture=750.
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

## Historical

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
