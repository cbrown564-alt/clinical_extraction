# Gan 2026 LLM-Only Minimal Evidence Selector Qwen36 35B Validation250 Error Analysis

Date: 2026-06-02

This is validation-split development error analysis on `gan2026_split_v1`; it is not a final holdout result.

Run artifact: `experiments/gan2026_llm_only_minimal_evidence_selector_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`
Run report: `experiments/gan2026_llm_only_minimal_evidence_selector_validation250_qwen36_35b_max5000_overnight_2026-06-01.md`
Row audit CSV: `experiments/gan2026_llm_only_minimal_evidence_selector_validation250_qwen36_35b_max5000_overnight_2026-06-01_error_rows.csv`

## Executive Findings

- Qwen completed the minimal contract on 249 / 250 rows with no call failures and no invalid JSON failures. The only structural failure is row 280, an answer-state enum/schema issue.
- Exact evidence behavior is strong: answer evidence is exact on 249 / 250 rows, and supporting-fact evidence is exact on 482 / 485 facts. The main problem is not evidence retrieval.
- Raw source-near answers score very poorly, 12 / 250 Purist, because the minimal contract asks for note-near text. Strict repair raises this to 56 / 250; frozen clean scorer-facing repair raises it to 193 / 250.
- The clean-score residual error is concentrated in two places: seizure-free intervals collapsed to `no seizure frequency reference` and source-near counted-window/range/semiology expressions that the frozen repair cannot convert into parser-ready Gan labels.
- Clean Purist correctness overstates boundary correctness: 37 rows are scorer-correct semantic-boundary mismatches, mostly unknown/unresolved labels where the scorer category matches despite different state semantics.

## Score Layers

| Layer | Scorable | Purist correct | Pragmatic correct |
| --- | ---: | ---: | ---: |
| Raw source-near answer | 12 / 250 | 12 / 250 | 12 / 250 |
| Strict format repair | 58 / 250 | 56 / 250 | 57 / 250 |
| Frozen clean scorer-facing repair | 249 / 250 | 193 / 250 | 194 / 250 |

## Contract And Evidence

| Check | Count |
| --- | ---: |
| Rows | 250 |
| Minimal records parsed | 249 / 250 |
| Parse/schema failures | 1 |
| Exact answer evidence substrings | 249 / 250 |
| Exact supporting-fact evidence substrings | 482 / 485 |
| Rows changed by repair layers | 240 |

## Clean Error Families

| Family | Rows |
| --- | ---: |
| correct | 156 |
| wrong_frequency_bucket_or_normalization | 54 |
| scorer_correct_semantic_boundary_mismatch | 37 |
| parse_or_schema_failure | 1 |
| frequency_predicted_as_seizure_free | 1 |
| overpredicted_specific_frequency_for_unknown_gold | 1 |

## Residual Error Families Only

| Family | Rows |
| --- | ---: |
| wrong_frequency_bucket_or_normalization | 54 |
| parse_or_schema_failure | 1 |
| frequency_predicted_as_seizure_free | 1 |
| overpredicted_specific_frequency_for_unknown_gold | 1 |

## Residual Surface Families

| Surface family | Rows |
| --- | ---: |
| seizure_free_interval_collapsed_to_no_reference | 32 |
| count_over_recent_window_not_parser_ready | 11 |
| clean_repair_fell_back_to_unknown | 7 |
| abbreviation_or_vague_surface | 4 |
| schema_state_enum_alias | 1 |
| cluster_or_pattern_cadence_surface | 1 |
| interval_or_cadence_surface | 1 |

## Gold Kinds On Residual Clean Failures

| Gold kind | Rows |
| --- | ---: |
| seizure_free | 32 |
| frequency | 23 |
| unresolved_multiple | 1 |
| unknown | 1 |

## Answer States On Residual Clean Failures

| Answer state | Rows |
| --- | ---: |
| seizure_free | 33 |
| frequency | 21 |
| cluster_frequency | 2 |
|  | 1 |

## Top Residual Confusions

| Gold category -> prediction category | Rows |
| --- | ---: |
| ('currently_no_seizure', 'seizure_freq_unknown') | 32 |
| ('seizure_freq_more1week_less1day', 'seizure_freq_unknown') | 10 |
| ('seizure_freq_1ormore_daily', 'seizure_freq_unknown') | 3 |
| ('seizure_freq_more1mon_less1week', 'seizure_freq_unknown') | 3 |
| ('seizure_freq_1_per_week', 'seizure_freq_unknown') | 2 |
| ('seizure_freq_1_per_mon', 'seizure_freq_unknown') | 2 |
| ('seizure_freq_unknown', 'unscorable') | 1 |
| ('seizure_freq_more1mon_less1week', 'seizure_freq_1_per_mon') | 1 |
| ('seizure_freq_more1week_less1day', 'seizure_freq_1_per_week') | 1 |
| ('seizure_freq_unknown', 'currently_no_seizure') | 1 |
| ('seizure_freq_more1per6mon_less1mon', 'seizure_freq_unknown') | 1 |

## Semantic-Boundary Mismatches That Still Score Correct

| Gold kind -> answer state -> clean label | Rows |
| --- | ---: |
| ('unresolved_multiple', 'frequency', 'no seizure frequency reference') | 9 |
| ('unknown', 'frequency', 'no seizure frequency reference') | 9 |
| ('unknown', 'cluster_frequency', 'unknown') | 4 |
| ('unresolved_multiple', 'frequency', 'multiple per day') | 3 |
| ('unknown', 'seizure_free', 'no seizure frequency reference') | 3 |
| ('unresolved_multiple', 'frequency', 'multiple per week') | 3 |
| ('unresolved_multiple', 'unknown_frequency', 'multiple per day') | 2 |
| ('unresolved_multiple', 'seizure_free', 'no seizure frequency reference') | 1 |
| ('unresolved_multiple', 'cluster_frequency', 'unknown') | 1 |
| ('unknown', 'cluster_frequency', 'no seizure frequency reference') | 1 |
| ('unresolved_multiple', 'unknown_frequency', 'unknown') | 1 |

## High-Value Residual Rows

| Row | Family | Gold | Answer text | Strict | Clean | Pred category | Surface |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 280 | parse_or_schema_failure | multiple per day |  |  |  | unscorable | schema_state_enum_alias |
| 1165 | frequency_predicted_as_seizure_free | 5 to 7 per 3 week | no further episodes for the last six weeks | no further for last 6 week | no seizure frequency reference | seizure_freq_unknown | clean_repair_fell_back_to_unknown |
| 1030 | wrong_frequency_bucket_or_normalization | 1 to 3 per month | one or three seizures last month | 1 or 3 last month | 1 per month | seizure_freq_1_per_mon | count_over_recent_window_not_parser_ready |
| 1046 | wrong_frequency_bucket_or_normalization | 3 to 5 per month | 3 or 5 seizures last month | 3 or 5 last month | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |
| 1070 | wrong_frequency_bucket_or_normalization | 3 to 4 per week | three or four seizures last week | 3 or 4 last week | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |
| 1094 | wrong_frequency_bucket_or_normalization | 3 to 5 per week | 3 to 5 seizures last week | 3 to 5 last week | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |
| 1223 | wrong_frequency_bucket_or_normalization | 3 to 4 per week | 3 or 4 focal impaired awareness seizures | 3 or 4 focal impaired awareness | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |
| 1573 | wrong_frequency_bucket_or_normalization | 11 per week | five focal cognitive and six focal non-motors in last... | 5 focal cognitive and 6 focal non-m... | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |
| 2023 | wrong_frequency_bucket_or_normalization | 5 per month | four absence seizures and one myoclonic this month | 4 absence and 1 myoclonic this month | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |
| 2354 | wrong_frequency_bucket_or_normalization | 6 to 7 per week | 6 to 7 myoclonic per week | 6 to 7 myoclonic per week | no seizure frequency reference | seizure_freq_unknown | clean_repair_fell_back_to_unknown |
| 2548 | wrong_frequency_bucket_or_normalization | 5 to 6 per 2 month | five to six focal automatisms during the last two mon... | 5 to 6 focal automatisms during las... | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |
| 2932 | wrong_frequency_bucket_or_normalization | seizure free for 9 month | seizure‑free since 29/09/2017 | ‑free since 29/09/2017 | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 2965 | wrong_frequency_bucket_or_normalization | seizure free for 16 month | no confirmed events | no confirmed | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 2992 | wrong_frequency_bucket_or_normalization | seizure free for 7 month | no further events since that date | no further since that date | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3015 | wrong_frequency_bucket_or_normalization | seizure free for 12 month | no events over the last year | no over last year | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3048 | wrong_frequency_bucket_or_normalization | seizure free for 16 month | No events for 16 months | no for 16 month | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3058 | wrong_frequency_bucket_or_normalization | seizure free for 12 month | No events for twelve months | no for 12 month | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3082 | wrong_frequency_bucket_or_normalization | seizure free for 10 month | No events for 10 months | no for 10 month | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3095 | wrong_frequency_bucket_or_normalization | seizure free for 12 month | No events for twelve months | no for 12 month | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3113 | wrong_frequency_bucket_or_normalization | seizure free for 14 month | No events for fourteen months | no for fourteen month | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3118 | wrong_frequency_bucket_or_normalization | seizure free for multiple month | No seizures since last visit | no since last visit | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3137 | wrong_frequency_bucket_or_normalization | seizure free for multiple month | no definite seizure events | no definite | no seizure frequency reference | seizure_freq_unknown | seizure_free_interval_collapsed_to_no_reference |
| 3262 | wrong_frequency_bucket_or_normalization | 2 cluster per month, 5 per clus... | two clusters this month | 2 clusters this month | 2 cluster per month, multiple per c... | seizure_freq_1_per_week | count_over_recent_window_not_parser_ready |
| 3325 | wrong_frequency_bucket_or_normalization | 3 per week | About three seizure days per week | 3 day per week | no seizure frequency reference | seizure_freq_unknown | clean_repair_fell_back_to_unknown |
| 3753 | wrong_frequency_bucket_or_normalization | 1 per day | daily | 1 per day | multiple per day | seizure_freq_unknown | clean_repair_fell_back_to_unknown |
| 3889 | wrong_frequency_bucket_or_normalization | 8 per year | sz xeight/yr | xeight/year | no seizure frequency reference | seizure_freq_unknown | abbreviation_or_vague_surface |
| 3940 | wrong_frequency_bucket_or_normalization | 4 per week | sz xfour/wk | xfour/week | no seizure frequency reference | seizure_freq_unknown | abbreviation_or_vague_surface |
| 3949 | wrong_frequency_bucket_or_normalization | 4 per week | sz Xfour/wk | xfour/week | no seizure frequency reference | seizure_freq_unknown | abbreviation_or_vague_surface |
| 4026 | wrong_frequency_bucket_or_normalization | 1 per month | roughly one brief absence episode in a typical month | roughly 1 brief absence in typical ... | no seizure frequency reference | seizure_freq_unknown | abbreviation_or_vague_surface |
| 4173 | wrong_frequency_bucket_or_normalization | 1 per 2 week | roughly once in a fortnight | roughly 1 in fortnight | no seizure frequency reference | seizure_freq_unknown | interval_or_cadence_surface |
| 4337 | wrong_frequency_bucket_or_normalization | 3 per 3 month | Seizure events on 06-03, 06-13, 09-23 | on 06 to 03, 06 to 13, 09 to 23 | no seizure frequency reference | seizure_freq_unknown | clean_repair_fell_back_to_unknown |
| 4345 | wrong_frequency_bucket_or_normalization | 4 per month | four seizures in July | 4 in july | no seizure frequency reference | seizure_freq_unknown | clean_repair_fell_back_to_unknown |
| 4368 | wrong_frequency_bucket_or_normalization | 5 per 2 month | Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24 | on 03 to 07, 03 to 27, 05 to 15, 05... | no seizure frequency reference | seizure_freq_unknown | clean_repair_fell_back_to_unknown |
| 4478 | wrong_frequency_bucket_or_normalization | 19 per week | nineteen episode of status epilepticus in the past we... | nineteen status epilepticus in past... | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |
| 4480 | wrong_frequency_bucket_or_normalization | 3 to 5 per week | three - five episode of status epilepticus in the pas... | 3 to 5 status epilepticus in past w... | no seizure frequency reference | seizure_freq_unknown | count_over_recent_window_not_parser_ready |

## Evidence Exceptions

| Row | Issue | Answer text | Evidence |
| ---: | --- | --- | --- |
| 280 | parse/schema; answer evidence not exact |  |  |
| 3468 | 1 supporting evidence not exact | Seizures happen when perimenstrual only (days -2 to +2). Outside this... | Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains ... |
| 3643 | 1 supporting evidence not exact | clusters up to 7 in bad weeks | clusters up to 7 in bad weeks |
| 5082 | 1 supporting evidence not exact | sustained period without any recurrence of her typical events | she reports a sustained period without any recurrence of her typical events |

## Interpretation

The 250-row Qwen run supports the validation25 conclusion, but with clearer scale: the minimal selector is a good local-model JSON/evidence-transfer contract and a weak prediction boundary. Most failures are downstream representation failures caused by asking the model for source-near `answer_text` and then relying on conservative deterministic repair to infer Gan scorer labels.

The biggest repair gap is seizure-free text. Many rows correctly identify `no events`, `free of seizures`, or `no seizures for N months`, but the clean layer emits `no seizure frequency reference`, which is scorer-wrong against `currently_no_seizure`. This is distinct from the earlier inequality/range issue and is now the largest residual class.

For the next experiment, the smallest high-leverage change is to keep the minimal evidence schema but add a separate parser-ready field such as `answer.final_label`, while preserving `answer.answer_text` and exact evidence for audit. That would test whether Qwen can do the missing normalization without reintroducing the full claim-table surface.
