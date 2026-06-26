# Gan 2026 Architecture Component Ablation

This is a development attribution artifact, not a held-out benchmark claim.

- Split: `validation`
- Split manifest: `gan2026_split_v1`

## Condition Summary

| Architecture | Condition | Role | Rows | Purist | Pragmatic | Evidence | Issues | Changed | Improved | Regressed |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deterministic_only | deterministic_all_rules | deterministic_extractor | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_only | deterministic_disable_date_duration_utilities | deterministic_extractor | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_only | deterministic_disable_portable_rate_expressions | deterministic_extractor | 50 | 0.4200 | 0.4400 | 1.0000 | 0 | 31 | 0 | 29 |
| deterministic_only | deterministic_disable_seizure_free_no_event_assertions | deterministic_extractor | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_only | deterministic_disable_cluster_arithmetic | deterministic_extractor | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_only | deterministic_disable_diary_log_aggregation | deterministic_extractor | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_only | deterministic_disable_temporal_selection | deterministic_extractor | 50 | 0.9000 | 0.9000 | 1.0000 | 0 | 5 | 0 | 5 |
| deterministic_only | deterministic_disable_gan_shorthand | deterministic_extractor | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_only | deterministic_disable_benchmark_repair | deterministic_extractor | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_only | deterministic_disable_gold_normalization_policy | deterministic_extractor | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_then_llm | deterministic_candidate_generator_top | candidate_generator_topline | 50 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 |
| deterministic_then_llm | raw_llm_adjudicator_final | prediction_bearing_adjudicator | 50 | 0.9600 | 0.9800 |  | 1 | 3 | 0 | 2 |
| deterministic_then_llm | conservative_llm_adjudicator_final | gated_prediction_bearing_adjudicator | 50 | 0.9600 | 0.9800 |  | 1 | 3 | 0 | 2 |

## Component Map

### deterministic_all_rules

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, portable_rate_expressions, seizure_free_no_event_assertions, cluster_arithmetic, diary_log_aggregation, temporal_selection, gan_shorthand, benchmark_repair, gold_normalization_policy
- Disabled: none
- Artifact: `generated in-process`

### deterministic_disable_date_duration_utilities

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: portable_rate_expressions, seizure_free_no_event_assertions, cluster_arithmetic, diary_log_aggregation, temporal_selection, gan_shorthand, benchmark_repair, gold_normalization_policy
- Disabled: date_duration_utilities
- Artifact: `generated in-process`

### deterministic_disable_portable_rate_expressions

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, seizure_free_no_event_assertions, cluster_arithmetic, diary_log_aggregation, temporal_selection, gan_shorthand, benchmark_repair, gold_normalization_policy
- Disabled: portable_rate_expressions
- Artifact: `generated in-process`

### deterministic_disable_seizure_free_no_event_assertions

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, portable_rate_expressions, cluster_arithmetic, diary_log_aggregation, temporal_selection, gan_shorthand, benchmark_repair, gold_normalization_policy
- Disabled: seizure_free_no_event_assertions
- Artifact: `generated in-process`

### deterministic_disable_cluster_arithmetic

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, portable_rate_expressions, seizure_free_no_event_assertions, diary_log_aggregation, temporal_selection, gan_shorthand, benchmark_repair, gold_normalization_policy
- Disabled: cluster_arithmetic
- Artifact: `generated in-process`

### deterministic_disable_diary_log_aggregation

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, portable_rate_expressions, seizure_free_no_event_assertions, cluster_arithmetic, temporal_selection, gan_shorthand, benchmark_repair, gold_normalization_policy
- Disabled: diary_log_aggregation
- Artifact: `generated in-process`

### deterministic_disable_temporal_selection

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, portable_rate_expressions, seizure_free_no_event_assertions, cluster_arithmetic, diary_log_aggregation, gan_shorthand, benchmark_repair, gold_normalization_policy
- Disabled: temporal_selection
- Artifact: `generated in-process`

### deterministic_disable_gan_shorthand

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, portable_rate_expressions, seizure_free_no_event_assertions, cluster_arithmetic, diary_log_aggregation, temporal_selection, benchmark_repair, gold_normalization_policy
- Disabled: gan_shorthand
- Artifact: `generated in-process`

### deterministic_disable_benchmark_repair

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, portable_rate_expressions, seizure_free_no_event_assertions, cluster_arithmetic, diary_log_aggregation, temporal_selection, gan_shorthand, gold_normalization_policy
- Disabled: benchmark_repair
- Artifact: `generated in-process`

### deterministic_disable_gold_normalization_policy

- Architecture: `deterministic_only`
- Prediction source: `Gan2026PipelineV1`
- Enabled: date_duration_utilities, portable_rate_expressions, seizure_free_no_event_assertions, cluster_arithmetic, diary_log_aggregation, temporal_selection, gan_shorthand, benchmark_repair
- Disabled: gold_normalization_policy
- Artifact: `generated in-process`

### deterministic_candidate_generator_top

- Architecture: `deterministic_then_llm`
- Prediction source: `hybrid rules-candidates LLM adjudicator deterministic diagnostics`
- Enabled: deterministic candidate generator
- Disabled: LLM adjudicator
- Artifact: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.jsonl`

### raw_llm_adjudicator_final

- Architecture: `deterministic_then_llm`
- Prediction source: `hybrid rules-candidates LLM adjudicator saved adjudicator output`
- Enabled: deterministic candidate generator, LLM adjudicator
- Disabled: conservative overreach gates, deterministic fallback
- Artifact: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.jsonl`

### conservative_llm_adjudicator_final

- Architecture: `deterministic_then_llm`
- Prediction source: `hybrid rules-candidates LLM adjudicator after named overreach gates`
- Enabled: deterministic candidate generator, LLM adjudicator, conservative overreach gates, deterministic fallback
- Disabled: none
- Artifact: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.jsonl`
