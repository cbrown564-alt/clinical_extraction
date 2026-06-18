# Gan 2026 Hidden-Family And First-Failure Atlas

Diagnostic validation-cycle artifact. This summarizes saved experiment rows; it does not change scoring, prompts, rules, projection policy, or holdout claims.

- Rows: 1000
- Purist correct: 911/1000
- Pragmatic correct: 922/1000
- CSV: `experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.csv`
- Summary JSON: `experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.json`

## Artifacts

| Artifact | Rows |
| --- | ---: |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 750 |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 250 |

## First Failure Owners

| Owner | Incorrect rows |
| --- | ---: |
| `candidate_generation` | 44 |
| `llm_clinical_selection` | 22 |
| `projection` | 9 |
| `operand_exposure` | 8 |
| `deterministic_adapter` | 3 |
| `final_projection` | 2 |
| `schema_or_parse` | 1 |

## Hidden Families On Incorrect Rows

| Family | Rows |
| --- | ---: |
| `current_vs_historical` | 46 |
| `uncertainty_or_ambiguity` | 40 |
| `competing_semiologies` | 39 |
| `unknown_boundary` | 35 |
| `seizure_free_duration` | 33 |
| `rate_bucket_or_denominator` | 31 |
| `cluster_burden` | 21 |
| `benchmark_format_convention` | 20 |
| `diary_or_log_aggregation` | 9 |
| `unclassified` | 3 |

## Family By First Failure

| Family | First failure owner | Incorrect rows |
| --- | --- | ---: |
| `benchmark_format_convention` | `candidate_generation` | 9 |
| `benchmark_format_convention` | `llm_clinical_selection` | 5 |
| `benchmark_format_convention` | `deterministic_adapter` | 2 |
| `benchmark_format_convention` | `operand_exposure` | 2 |
| `benchmark_format_convention` | `projection` | 1 |
| `benchmark_format_convention` | `schema_or_parse` | 1 |
| `cluster_burden` | `candidate_generation` | 10 |
| `cluster_burden` | `llm_clinical_selection` | 4 |
| `cluster_burden` | `operand_exposure` | 3 |
| `cluster_burden` | `deterministic_adapter` | 2 |
| `cluster_burden` | `projection` | 1 |
| `cluster_burden` | `schema_or_parse` | 1 |
| `competing_semiologies` | `candidate_generation` | 21 |
| `competing_semiologies` | `llm_clinical_selection` | 8 |
| `competing_semiologies` | `projection` | 4 |
| `competing_semiologies` | `operand_exposure` | 3 |
| `competing_semiologies` | `deterministic_adapter` | 2 |
| `competing_semiologies` | `final_projection` | 1 |
| `current_vs_historical` | `candidate_generation` | 20 |
| `current_vs_historical` | `llm_clinical_selection` | 13 |
| `current_vs_historical` | `operand_exposure` | 5 |
| `current_vs_historical` | `projection` | 5 |
| `current_vs_historical` | `deterministic_adapter` | 2 |
| `current_vs_historical` | `schema_or_parse` | 1 |
| `diary_or_log_aggregation` | `llm_clinical_selection` | 4 |
| `diary_or_log_aggregation` | `candidate_generation` | 3 |
| `diary_or_log_aggregation` | `final_projection` | 1 |
| `diary_or_log_aggregation` | `schema_or_parse` | 1 |
| `rate_bucket_or_denominator` | `candidate_generation` | 16 |
| `rate_bucket_or_denominator` | `llm_clinical_selection` | 6 |
| `rate_bucket_or_denominator` | `projection` | 3 |
| `rate_bucket_or_denominator` | `deterministic_adapter` | 2 |
| `rate_bucket_or_denominator` | `operand_exposure` | 2 |
| `rate_bucket_or_denominator` | `final_projection` | 1 |
| `rate_bucket_or_denominator` | `schema_or_parse` | 1 |
| `seizure_free_duration` | `candidate_generation` | 22 |
| `seizure_free_duration` | `llm_clinical_selection` | 6 |
| `seizure_free_duration` | `projection` | 5 |
| `uncertainty_or_ambiguity` | `candidate_generation` | 20 |
| `uncertainty_or_ambiguity` | `llm_clinical_selection` | 10 |
| `uncertainty_or_ambiguity` | `operand_exposure` | 5 |
| `uncertainty_or_ambiguity` | `projection` | 4 |
| `uncertainty_or_ambiguity` | `deterministic_adapter` | 1 |
| `unclassified` | `candidate_generation` | 1 |
| `unclassified` | `llm_clinical_selection` | 1 |
| `unclassified` | `projection` | 1 |
| `unknown_boundary` | `candidate_generation` | 16 |
| `unknown_boundary` | `llm_clinical_selection` | 10 |
| `unknown_boundary` | `operand_exposure` | 5 |
| `unknown_boundary` | `projection` | 4 |

## Highest-Signal Incorrect Rows

| Artifact | Row | Gold | Prediction | Families | First failure |
| --- | ---: | --- | --- | --- | --- |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 1165 | `5 to 7 per 3 week` | `1 per 3 week` | competing_semiologies | `deterministic_adapter` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 1317 | `unknown, multiple per cluster` | `1 per day` | cluster_burden;rate_bucket_or_denominator;current_vs_historical;uncertainty_or_ambiguity;benchmark_format_convention | `deterministic_adapter` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 1363 | `3 per day` | `1 to 2 per week` | rate_bucket_or_denominator;competing_semiologies | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 1695 | `multiple per month` | `3 to 5 per month` | diary_or_log_aggregation;current_vs_historical;competing_semiologies;benchmark_format_convention | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 1706 | `multiple cluster per month, multiple per cluster` | `1 per 1 month` | cluster_burden;current_vs_historical;competing_semiologies;benchmark_format_convention | `operand_exposure` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 1707 | `multiple per week` | `1 per 7 day` | cluster_burden;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention | `deterministic_adapter` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 2748 | `1 per month` | `7 per 10 month` | rate_bucket_or_denominator;competing_semiologies | `final_projection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3137 | `seizure free for multiple month` | `no seizure frequency reference` | seizure_free_duration;current_vs_historical | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3356 | `unknown` | `occasional per 3 month` | unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `operand_exposure` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3371 | `unknown` | `0 per 8 week` | unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3468 | `unknown` | `6 per 28 day` | unknown_boundary;seizure_free_duration;cluster_burden;current_vs_historical;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3469 | `unknown` | `1 per 7 day` | unknown_boundary;current_vs_historical;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3482 | `unknown` | `1 per 6 month` | unknown_boundary;diary_or_log_aggregation;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3493 | `unknown` | `1 per 6 day` | unknown_boundary;cluster_burden;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3528 | `unknown` | `frequent per unspecified unit` | unknown_boundary;competing_semiologies;uncertainty_or_ambiguity | `operand_exposure` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3534 | `unknown` | `seizure free for 7 month` | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3623 | `7 per week` | `up to 7 per 1 week` | cluster_burden;rate_bucket_or_denominator;current_vs_historical | `operand_exposure` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3988 | `multiple per week` | `3 to 7 per week` | cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention | `schema_or_parse` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 3995 | `1 per month` | `multiple per month` | rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4337 | `3 per 3 month` | `3 per 7 month` | diary_or_log_aggregation;competing_semiologies | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4368 | `5 per 2 month` | `no seizure frequency reference` | diary_or_log_aggregation | `final_projection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4690 | `multiple per day` | `frequent per day` | rate_bucket_or_denominator;benchmark_format_convention | `operand_exposure` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4694 | `multiple per day` | `9 per day` | rate_bucket_or_denominator;benchmark_format_convention | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4700 | `multiple per day` | `4 per day` | rate_bucket_or_denominator;benchmark_format_convention | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4709 | `multiple per day` | `6 per year` | rate_bucket_or_denominator;benchmark_format_convention | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4731 | `unknown` | `rare per unspecified unit` | unknown_boundary;current_vs_historical;uncertainty_or_ambiguity | `operand_exposure` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4732 | `unknown` | `occasional` | unknown_boundary;cluster_burden;current_vs_historical;uncertainty_or_ambiguity | `operand_exposure` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 4771 | `unknown` | `1 per month` | unknown_boundary;cluster_burden;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 5092 | `seizure free for multiple month` | `no seizure frequency reference` | seizure_free_duration;current_vs_historical | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 5110 | `seizure free for multiple month` | `no seizure frequency reference` | seizure_free_duration;diary_or_log_aggregation | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 5121 | `seizure free for multiple month` | `no seizure frequency reference` | seizure_free_duration;current_vs_historical;competing_semiologies | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 5476 | `unknown` | `1 per month` | unknown_boundary;cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 5491 | `unknown` | `2 per 6 week` | unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 5504 | `unknown` | `occasional per year` | unknown_boundary;uncertainty_or_ambiguity | `operand_exposure` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 5507 | `unknown` | `3 per 4 month` | unknown_boundary;current_vs_historical;uncertainty_or_ambiguity | `llm_clinical_selection` |
| `gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl` | 5534 | `1 per multiple month` | `1 per 14 day` | unclassified | `llm_clinical_selection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 3356 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 3528 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 4690 | `multiple per day` | `seizure free for multiple year` | seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 5534 | `1 per multiple month` | `seizure free for multiple year` | seizure_free_duration;current_vs_historical;competing_semiologies | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 5921 | `1 per 6 to 8 week` | `1 per day` | rate_bucket_or_denominator | `projection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 5974 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6077 | `unknown` | `seizure free for 8 month` | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6094 | `3 per month` | `3 per week` | rate_bucket_or_denominator | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6131 | `unknown` | `seizure free for 6 month` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6153 | `9 per month` | `1 per 1 to 2 week` | unclassified | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6209 | `multiple per day` | `1 per day` | rate_bucket_or_denominator;benchmark_format_convention | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6244 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6321 | `unknown` | `1 per day` | unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6368 | `unknown` | `1 per 1 to 2 week` | unknown_boundary;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6501 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;cluster_burden;competing_semiologies;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6571 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6889 | `multiple per week` | `1 per 2 to 3 week` | rate_bucket_or_denominator;benchmark_format_convention | `projection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 6987 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 7168 | `unknown` | `2 per year` | unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 7615 | `3 to 7 per month` | `2 per year` | competing_semiologies | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 9496 | `6 per 12 month` | `2 per week` | rate_bucket_or_denominator;competing_semiologies | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 9888 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 9937 | `1 cluster per month, multiple per cluster` | `1 per multiple week` | cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `1 per 4 to 5 week` | cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 9955 | `1 cluster per month, multiple per cluster` | `1 per month` | cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 10266 | `unknown` | `1 per 5 day` | unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 10386 | `1 cluster per week, 2 to 3 per cluster` | `1 per day` | cluster_burden;rate_bucket_or_denominator;current_vs_historical | `projection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 10618 | `unknown, 4 to 6 per cluster` | `seizure free for multiple year` | seizure_free_duration;cluster_burden;competing_semiologies;uncertainty_or_ambiguity | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 10677 | `1 cluster per month, multiple per cluster` | `1 per month` | cluster_burden;rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 10996 | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, multiple per cluster` | cluster_burden;benchmark_format_convention | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 11216 | `unknown` | `seizure free for 4 month` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `projection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 11254 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `projection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 11259 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | `projection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 11272 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `projection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 12422 | `1 per day` | `4 per year` | rate_bucket_or_denominator;competing_semiologies | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 12438 | `1 per day` | `2 to 3 per year` | rate_bucket_or_denominator;competing_semiologies | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 12456 | `1 per day` | `3 per year` | rate_bucket_or_denominator;competing_semiologies | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 12460 | `1 per day` | `2 per year` | rate_bucket_or_denominator;competing_semiologies | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 12468 | `1 per day` | `4 per year` | rate_bucket_or_denominator;competing_semiologies | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 13209 | `1 per 8 month` | `1 per 4 to 5 week` | seizure_free_duration;competing_semiologies | `projection` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 13843 | `seizure free for multiple month` | `no seizure frequency reference` | seizure_free_duration;diary_or_log_aggregation;current_vs_historical | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 13858 | `seizure free for multiple month` | `no seizure frequency reference` | seizure_free_duration;diary_or_log_aggregation;current_vs_historical | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 13889 | `seizure free for multiple month` | `no seizure frequency reference` | seizure_free_duration;current_vs_historical | `candidate_generation` |
| `gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 14025 | `unknown` | `seizure free for multiple year` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | `candidate_generation` |
