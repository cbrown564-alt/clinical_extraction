# Gan 2026 Frozen Component-Projection Follow-Up Panel

Frozen validation-development replay over saved RQ2/RQ4 artifacts. The panel applies the interpretation policy by propagating hidden-family tags, assigning first-failure owner labels, and separating gated projection targets from regression panels. It is not a benchmark or locked-holdout claim.

- Date: `2026-06-04`
- Split manifest: `gan2026_split_v1`
- Panel rows: 654
- Source rows represented: 371
- JSONL artifact: `experiments/gan2026_component_projection_followup_panel_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_component_projection_followup_panel_2026-06-04.json`

## Panel Roles

| Role | Rows |
| --- | ---: |
| `changed_row` | 166 |
| `context` | 56 |
| `gated_projection_regression` | 232 |
| `gated_projection_target` | 18 |
| `schema_near_or_projection_miss` | 160 |
| `typed_operand_incomplete` | 22 |

## First-Failure Owners

| Owner | Rows |
| --- | ---: |
| `candidate_generation` | 78 |
| `deterministic_adapter` | 1 |
| `evidence_selection` | 1 |
| `llm_clinical_selection` | 36 |
| `none` | 239 |
| `operand_exposure` | 18 |
| `projection` | 19 |
| `projection_policy` | 152 |
| `schema_or_parse` | 1 |
| `typed_state_representation` | 109 |

## Component Outcomes

| Component | Rows | W->C | C->W | Exact evidence |
| --- | ---: | ---: | ---: | ---: |
| `boundary_state_priority` | 17 | 17 | 0 | 17 |
| `claim_table_final_query` | 38 | 0 | 0 | 38 |
| `competing_frequency_uncertainty` | 1 | 1 | 0 | 1 |
| `graph_gated_month_bucket_duration` | 250 | 18 | 0 | 250 |
| `hybrid_adjudicator_raw` | 61 | 0 | 8 | 61 |
| `llm_candidate_selector_raw` | 61 | 7 | 49 | 61 |
| `llm_heavy_selected_fact` | 95 | 0 | 0 | 94 |
| `state_graph_projection` | 131 | 0 | 84 | 125 |

## Gated Projection Panels

| Gate | Target rows | Regression rows | W->C | C->W | Changed regression rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `graph_gated_month_bucket_duration` | 18 | 232 | 18 | 0 | 0 |

## Predeclared Projection Slices

| Slice | Rows | Component focus | Primary metric |
| --- | ---: | --- | --- |
| `candidate_generation_rescue` | 44 | candidate generation | Candidate-recall rescue rate before final-label promotion; final policy keeps the deterministic safety floor unless a rescue is predeclared and ablated. |
| `candidate_generation_unknown_seizure_free_boundary` | 26 | candidate generation | Boundary-state recall without converting uncertain seizure-free language into a prediction-bearing deterministic repair. |
| `projection_arbitration` | 11 | graph/final projection | Projection-variant correction precision, mechanical-correct to projected-wrong regressions, and selected-evidence/source trace validity. |
| `projection_unknown_seizure_free_arbitration` | 6 | graph/final projection | Unknown/seizure-free/current-vs-historical arbitration precision with no broad validation retuning. |

## Hidden Family By First-Failure Owner

| Hidden family | First-failure owner | Rows |
| --- | --- | ---: |
| `already_projection_correct` | `none` | 181 |
| `benchmark_format_convention` | `candidate_generation` | 16 |
| `benchmark_format_convention` | `deterministic_adapter` | 1 |
| `benchmark_format_convention` | `evidence_selection` | 1 |
| `benchmark_format_convention` | `llm_clinical_selection` | 6 |
| `benchmark_format_convention` | `none` | 24 |
| `benchmark_format_convention` | `operand_exposure` | 6 |
| `benchmark_format_convention` | `projection` | 3 |
| `benchmark_format_convention` | `projection_policy` | 49 |
| `benchmark_format_convention` | `schema_or_parse` | 1 |
| `benchmark_format_convention` | `typed_state_representation` | 26 |
| `candidate_absent_or_weak` | `projection_policy` | 4 |
| `cluster_burden` | `candidate_generation` | 20 |
| `cluster_burden` | `deterministic_adapter` | 1 |
| `cluster_burden` | `evidence_selection` | 1 |
| `cluster_burden` | `llm_clinical_selection` | 4 |
| `cluster_burden` | `none` | 48 |
| `cluster_burden` | `operand_exposure` | 6 |
| `cluster_burden` | `projection` | 1 |
| `cluster_burden` | `projection_policy` | 42 |
| `cluster_burden` | `schema_or_parse` | 1 |
| `cluster_burden` | `typed_state_representation` | 25 |
| `cluster_or_diary` | `none` | 161 |
| `cluster_or_diary` | `projection_policy` | 46 |
| `competing_semiologies` | `candidate_generation` | 39 |
| `competing_semiologies` | `llm_clinical_selection` | 19 |
| `competing_semiologies` | `none` | 86 |
| `competing_semiologies` | `operand_exposure` | 8 |
| `competing_semiologies` | `projection` | 9 |
| `competing_semiologies` | `projection_policy` | 74 |
| `competing_semiologies` | `typed_state_representation` | 67 |
| `current_vs_historical` | `candidate_generation` | 33 |
| `current_vs_historical` | `deterministic_adapter` | 1 |
| `current_vs_historical` | `evidence_selection` | 1 |
| `current_vs_historical` | `llm_clinical_selection` | 28 |
| `current_vs_historical` | `none` | 164 |
| `current_vs_historical` | `operand_exposure` | 17 |
| `current_vs_historical` | `projection` | 10 |
| `current_vs_historical` | `projection_policy` | 93 |
| `current_vs_historical` | `schema_or_parse` | 1 |
| `current_vs_historical` | `typed_state_representation` | 53 |
| `deterministic_miss` | `projection_policy` | 4 |
| `diary_or_log_aggregation` | `candidate_generation` | 5 |
| `diary_or_log_aggregation` | `deterministic_adapter` | 1 |
| `diary_or_log_aggregation` | `evidence_selection` | 1 |
| `diary_or_log_aggregation` | `llm_clinical_selection` | 12 |
| `diary_or_log_aggregation` | `none` | 35 |
| `diary_or_log_aggregation` | `operand_exposure` | 1 |
| `diary_or_log_aggregation` | `projection_policy` | 28 |
| `diary_or_log_aggregation` | `schema_or_parse` | 1 |
| `diary_or_log_aggregation` | `typed_state_representation` | 1 |
| `frequency_with_seizure_free_node` | `none` | 18 |
| `frequency_with_seizure_free_node` | `projection_policy` | 1 |
| `numeric_seizure_free_duration` | `none` | 13 |
| `numeric_seizure_free_duration` | `projection_policy` | 7 |
| `rate_bucket_or_denominator` | `candidate_generation` | 29 |
| `rate_bucket_or_denominator` | `deterministic_adapter` | 1 |
| `rate_bucket_or_denominator` | `evidence_selection` | 1 |
| `rate_bucket_or_denominator` | `llm_clinical_selection` | 5 |
| `rate_bucket_or_denominator` | `none` | 73 |
| `rate_bucket_or_denominator` | `operand_exposure` | 7 |
| `rate_bucket_or_denominator` | `projection` | 5 |
| `rate_bucket_or_denominator` | `projection_policy` | 55 |
| `rate_bucket_or_denominator` | `schema_or_parse` | 1 |
| `rate_bucket_or_denominator` | `typed_state_representation` | 42 |
| `seizure_free_duration` | `candidate_generation` | 35 |
| `seizure_free_duration` | `llm_clinical_selection` | 15 |
| `seizure_free_duration` | `none` | 50 |
| `seizure_free_duration` | `operand_exposure` | 10 |
| `seizure_free_duration` | `projection` | 11 |
| `seizure_free_duration` | `projection_policy` | 43 |
| `seizure_free_duration` | `typed_state_representation` | 30 |
| `seizure_free_overreach` | `none` | 15 |
| `seizure_free_overreach` | `projection_policy` | 38 |
| `shorthand_interval_range` | `none` | 40 |
| `shorthand_interval_range` | `projection_policy` | 11 |
| `temporal_conflict` | `none` | 157 |
| `temporal_conflict` | `projection_policy` | 39 |
| `uncertainty_or_ambiguity` | `candidate_generation` | 36 |
| `uncertainty_or_ambiguity` | `deterministic_adapter` | 1 |
| `uncertainty_or_ambiguity` | `llm_clinical_selection` | 15 |
| `uncertainty_or_ambiguity` | `none` | 20 |
| `uncertainty_or_ambiguity` | `operand_exposure` | 9 |
| `uncertainty_or_ambiguity` | `projection` | 9 |
| `uncertainty_or_ambiguity` | `projection_policy` | 41 |
| `uncertainty_or_ambiguity` | `typed_state_representation` | 2 |
| `unclassified` | `candidate_generation` | 2 |
| `unclassified` | `llm_clinical_selection` | 6 |
| `unclassified` | `none` | 41 |
| `unclassified` | `projection` | 3 |
| `unclassified` | `projection_policy` | 13 |
| `unclassified` | `typed_state_representation` | 18 |
| `unknown_boundary` | `candidate_generation` | 28 |
| `unknown_boundary` | `llm_clinical_selection` | 15 |
| `unknown_boundary` | `none` | 18 |
| `unknown_boundary` | `operand_exposure` | 9 |
| `unknown_boundary` | `projection` | 9 |
| `unknown_boundary` | `projection_policy` | 38 |
| `unknown_no_reference_boundary` | `none` | 6 |
| `unknown_no_reference_boundary` | `projection_policy` | 39 |

## Highest-Signal Rows

| Subproblem | Role | Component | Source row | Gold | Candidate | Owner | Families |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 338 | `multiple per month` | `1 cluster per month, multiple per cluster` | `typed_state_representation` | `current_vs_historical;competing_semiologies;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 1046 | `3 to 5 per month` | `5 per month` | `typed_state_representation` | `cluster_burden;current_vs_historical;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 1317 | `unknown, multiple per cluster` | `1 cluster per 1 day, multiple per cluster` | `deterministic_adapter` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical;uncertainty_or_ambiguity;benchmark_format_convention;diary_or_log_aggregation` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 1695 | `multiple per month` | `seizure free for 1 month` | `llm_clinical_selection` | `diary_or_log_aggregation;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 1706 | `multiple cluster per month, multiple per cluster` | `unknown` | `operand_exposure` | `cluster_burden;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 1923 | `7 per 6 month` | `2 to 3 per 6 month` | `typed_state_representation` | `current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 3137 | `seizure free for multiple month` | `no seizure frequency reference` | `llm_clinical_selection` | `seizure_free_duration;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 3261 | `2 cluster per month, 4 per cluster` | `1 cluster per month, 4 per cluster` | `typed_state_representation` | `cluster_burden;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 3623 | `7 per week` | `unknown` | `operand_exposure` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 3988 | `multiple per week` | `1 per week` | `schema_or_parse` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 4337 | `3 per 3 month` | `3 per 4 month` | `llm_clinical_selection` | `diary_or_log_aggregation;competing_semiologies;unclassified` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 4402 | `7 per 7 month` | `1 to 2 per month` | `typed_state_representation` | `unclassified` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 4690 | `multiple per day` | `seizure free interval` | `operand_exposure` | `rate_bucket_or_denominator;benchmark_format_convention;seizure_free_duration;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 5092 | `seizure free for multiple month` | `no seizure frequency reference` | `llm_clinical_selection` | `seizure_free_duration;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 5110 | `seizure free for multiple month` | `no seizure frequency reference` | `llm_clinical_selection` | `seizure_free_duration;diary_or_log_aggregation` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 5121 | `seizure free for multiple month` | `no seizure frequency reference` | `llm_clinical_selection` | `seizure_free_duration;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 5491 | `unknown` | `2 per 6 week` | `llm_clinical_selection` | `unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 5528 | `1 per month` | `no seizure frequency reference` | `typed_state_representation` | `current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `claim_table_final_query` | 5534 | `1 per multiple month` | `1 per 2 week` | `llm_clinical_selection` | `unclassified;seizure_free_duration;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `hybrid_adjudicator_raw` | 190 | `1 per 4 week` | `unknown` | `typed_state_representation` | `cluster_burden;competing_semiologies` |
| `evidence_selection` | `changed_row` | `hybrid_adjudicator_raw` | 2822 | `1 per day` | `unknown` | `typed_state_representation` | `cluster_burden;rate_bucket_or_denominator;competing_semiologies` |
| `evidence_selection` | `changed_row` | `hybrid_adjudicator_raw` | 3623 | `7 per week` | `unknown` | `operand_exposure` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical` |
| `evidence_selection` | `changed_row` | `hybrid_adjudicator_raw` | 4116 | `1 per 1 to 2 day` | `1 per day` | `typed_state_representation` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 3356 | `unknown` | `seizure free for multiple year` | `operand_exposure` | `unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;seizure_free_duration` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 3528 | `unknown` | `seizure free for multiple year` | `operand_exposure` | `unknown_boundary;competing_semiologies;uncertainty_or_ambiguity;seizure_free_duration;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 4690 | `multiple per day` | `seizure free for multiple year` | `operand_exposure` | `rate_bucket_or_denominator;benchmark_format_convention;seizure_free_duration;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 5534 | `1 per multiple month` | `seizure free for multiple year` | `llm_clinical_selection` | `unclassified;seizure_free_duration;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 5921 | `1 per 6 to 8 week` | `1 per day` | `projection` | `rate_bucket_or_denominator` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 5974 | `unknown` | `seizure free for multiple year` | `candidate_generation` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6077 | `unknown` | `seizure free for 8 month` | `candidate_generation` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6094 | `3 per month` | `3 per week` | `candidate_generation` | `rate_bucket_or_denominator` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6131 | `unknown` | `seizure free for 6 month` | `candidate_generation` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6153 | `9 per month` | `1 per 1 to 2 week` | `candidate_generation` | `unclassified` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6209 | `multiple per day` | `1 per day` | `candidate_generation` | `rate_bucket_or_denominator;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6244 | `unknown` | `seizure free for multiple year` | `candidate_generation` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6321 | `unknown` | `1 per day` | `candidate_generation` | `unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6368 | `unknown` | `1 per 1 to 2 week` | `candidate_generation` | `unknown_boundary;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6501 | `unknown` | `seizure free for multiple year` | `candidate_generation` | `unknown_boundary;seizure_free_duration;cluster_burden;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6571 | `unknown` | `seizure free for multiple year` | `candidate_generation` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6889 | `multiple per week` | `1 per 2 to 3 week` | `projection` | `rate_bucket_or_denominator;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 6987 | `unknown` | `seizure free for multiple year` | `candidate_generation` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 7168 | `unknown` | `2 per year` | `candidate_generation` | `unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 7615 | `3 to 7 per month` | `2 per year` | `candidate_generation` | `competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 9496 | `6 per 12 month` | `2 per week` | `candidate_generation` | `rate_bucket_or_denominator;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 9888 | `unknown` | `seizure free for multiple year` | `candidate_generation` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 9937 | `1 cluster per month, multiple per cluster` | `1 per multiple week` | `candidate_generation` | `cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `1 per 4 to 5 week` | `candidate_generation` | `cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 9955 | `1 cluster per month, multiple per cluster` | `1 per month` | `candidate_generation` | `cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 10266 | `unknown` | `1 per 5 day` | `candidate_generation` | `unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 10386 | `1 cluster per week, 2 to 3 per cluster` | `1 per day` | `projection` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 10618 | `unknown, 4 to 6 per cluster` | `seizure free for multiple year` | `candidate_generation` | `seizure_free_duration;cluster_burden;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 10677 | `1 cluster per month, multiple per cluster` | `1 per month` | `candidate_generation` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 10996 | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, multiple per cluster` | `candidate_generation` | `cluster_burden;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 11216 | `unknown` | `seizure free for 4 month` | `projection` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 11254 | `unknown` | `seizure free for multiple year` | `projection` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 11259 | `unknown` | `seizure free for multiple year` | `projection` | `unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 11272 | `unknown` | `seizure free for multiple year` | `projection` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 12422 | `1 per day` | `4 per year` | `candidate_generation` | `rate_bucket_or_denominator;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 12438 | `1 per day` | `2 to 3 per year` | `candidate_generation` | `rate_bucket_or_denominator;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 12456 | `1 per day` | `3 per year` | `candidate_generation` | `rate_bucket_or_denominator;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 12460 | `1 per day` | `2 per year` | `candidate_generation` | `rate_bucket_or_denominator;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 12468 | `1 per day` | `4 per year` | `candidate_generation` | `rate_bucket_or_denominator;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 13209 | `1 per 8 month` | `1 per 4 to 5 week` | `projection` | `seizure_free_duration;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 13843 | `seizure free for multiple month` | `no seizure frequency reference` | `candidate_generation` | `seizure_free_duration;diary_or_log_aggregation;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 13858 | `seizure free for multiple month` | `no seizure frequency reference` | `candidate_generation` | `seizure_free_duration;diary_or_log_aggregation;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 13889 | `seizure free for multiple month` | `no seizure frequency reference` | `candidate_generation` | `seizure_free_duration;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 14025 | `unknown` | `seizure free for multiple year` | `candidate_generation` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 14076 | `unknown` | `seizure free for multiple year` | `candidate_generation` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 14810 | `1 per month` | `12 per month` | `candidate_generation` | `seizure_free_duration;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 14821 | `1 per month` | `17 per month` | `candidate_generation` | `seizure_free_duration;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 15168 | `multiple per 15 month` | `seizure free for multiple year` | `candidate_generation` | `seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 15193 | `multiple per 13 month` | `seizure free for multiple year` | `candidate_generation` | `seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `2 per 6 month` | `candidate_generation` | `cluster_burden;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 15672 | `1 per day` | `2 per 6 week` | `candidate_generation` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 15834 | `5 per week` | `1 per multiple month` | `candidate_generation` | `rate_bucket_or_denominator;current_vs_historical` |
| `evidence_selection` | `schema_near_or_projection_miss` | `hybrid_adjudicator_raw` | 15986 | `11 per 3 month` | `1 per 5 to 7 day` | `projection` | `unclassified` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 1695 | `multiple per month` | `seizure free` | `llm_clinical_selection` | `diary_or_log_aggregation;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 2992 | `seizure free for 7 month` | `unknown` | `typed_state_representation` | `seizure_free_duration;current_vs_historical` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 3356 | `unknown` | `unknown` | `none` | `unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;seizure_free_duration` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 5767 | `1 per 1 to 2 week` | `1-2 per week` | `typed_state_representation` | `unclassified` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 5791 | `1 per month` | `2-3 per 3 months` | `typed_state_representation` | `current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 6244 | `unknown` | `unknown` | `none` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 6321 | `unknown` | `unknown` | `none` | `unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 6738 | `1 per 6 to 8 week` | `unknown` | `typed_state_representation` | `competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 7275 | `1 per month` | `2-5 per month` | `typed_state_representation` | `unclassified` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 9449 | `4 per 6 month` | `1-2 per month` | `typed_state_representation` | `competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 10097 | `3 cluster per month, multiple per cluster` | `3 per month` | `typed_state_representation` | `cluster_burden;benchmark_format_convention` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 10245 | `3 cluster per month, multiple per cluster` | `unknown_frequency` | `typed_state_representation` | `cluster_burden;current_vs_historical;uncertainty_or_ambiguity;benchmark_format_convention` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 10266 | `unknown` | `unknown` | `none` | `unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 11259 | `unknown` | `unknown` | `none` | `unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12502 | `4 per day` | `1-2 per month` | `typed_state_representation` | `seizure_free_duration;cluster_burden;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12506 | `4 per day` | `1-2 per month` | `typed_state_representation` | `seizure_free_duration;cluster_burden;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12537 | `1 per day` | `3 per week` | `typed_state_representation` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12556 | `1 per day` | `2-3 per week` | `typed_state_representation` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12573 | `1 per day` | `2 per month` | `typed_state_representation` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12584 | `1 per week` | `1 per 3 months` | `typed_state_representation` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12641 | `1 per day` | `1-2 per week` | `typed_state_representation` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12665 | `1 per day` | `1-2 per month` | `typed_state_representation` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12667 | `1 per day` | `1-2 per month` | `typed_state_representation` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| `evidence_selection` | `changed_row` | `llm_candidate_selector_raw` | 12679 | `1 per day` | `1-2 per month` | `typed_state_representation` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |

## Interpretation

This panel keeps deterministic outputs as comparators and safety floors, not as eligible RQ1-RQ4 answers. Projection-compatible clinical phrases are assigned to projection/rendering policy rather than counted as LLM component failures; faithful ambiguous facts are kept visible for later policy-mediated projection.
