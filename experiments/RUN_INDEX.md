# Gan 2026 Run Registry

Generated from `experiments/registry.jsonl`. The JSONL file remains the canonical machine-readable registry.

## Revise

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
- Evidence validity: Deterministic candidate evidence is carried from V1 diagnostics; raw/gated adjudicator evidence validity needs row-level review for schema-failing and boundary-demotion cases.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_saturated_surface_analysis_2026-06-01`.
- Claim language: Reviewed synthetic hard-case component stress is diagnostic/revise-only: raw adjudicator corrected five deterministic misses with no Purist regressions, but conservative gates kept only three corrections; candidate recall was only 42/56 and five schema/validation failures remain.
- Artifacts: `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.md`.

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
