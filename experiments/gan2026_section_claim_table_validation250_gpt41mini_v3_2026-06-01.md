# Gan 2026 Section Claim Table V3

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Escalation reason: User accepted the v3 50-row rationale-repair replay as passing the documented decision gate; 250-row diagnostic will decide whether to promote, revise, or reject the section-claim-table v3 candidate.

## Model And Prompt Metadata

- Pipeline: `gan2026_section_claim_table_v3`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first claim extractor and final query selector
- Prompt/program version: `gan2026_section_claim_table_v3`
- Temperature: `0.0`
- Max tokens: `1400`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `50`
- Reuse source: `experiments/gan2026_section_claim_table_validation50_gpt41mini_v3_rationale_replay_2026-06-01.jsonl`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `b9ea9e8`
- Working tree note: `clean`
- JSONL artifact: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v3_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 248 / 250
- Call failures: 0
- Parse/schema/label issues: 2
- Exact claim evidence substrings: 760 / 771
- Exact selected final evidence substrings: 246 / 250
- raw final-query score: Purist 0.8680 (217 / 250), Pragmatic 0.8920 (223 / 250)
- Strict-format score: Purist 0.8680 (217 / 250), Pragmatic 0.8920 (223 / 250)
- Frozen clean scorer-facing score: Purist 0.8720 (218 / 250), Pragmatic 0.8960 (224 / 250)
- Rows changed by downstream repair layers: 19

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 0 |
| claim_extraction | 13 |
| temporality_conflict | 1 |
| final_query | 4 |
| parse_schema | 2 |
| scorer_format | 4 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 243 | claim evidence not exact (c2: he and his partner report that the seizures occur every four months); selected evidence not exact (he and his partner report that the seizures occur every four months) |  |  |
| 1223 | claim evidence not exact (c1: this week he has had 3 or 4 focal impaired awareness seizures, each lasting a few minutes with subsequent confusion and fatigue for up to an hour); selected evidence not exact (this week he has had 3 or 4 focal impaired awareness seizures, each lasting a few minutes with subsequent confusion and fatigue for up to an hour) |  |  |
| 1694 | claim evidence not exact (c2: She has been generally stable for several months prior to this cluster) |  |  |
| 2166 |  | unparsable_label: frequent petit mal recently (Unparsable label (raw: 'frequent petit mal recently' / normalized: 'frequent petit mal recently')) |  |
| 2228 | claim evidence not exact (c3: No tongue biting or urinary incontinence reported in recent episodes) |  |  |
| 3224 | claim evidence not exact (c3: She does not recall clear auras) |  |  |
| 3468 |  | missing_final_label | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event' |
| 4110 | claim evidence not exact (c3: seizure diary entries corroborating the reported frequency of q1 - 2d over the past six weeks) |  |  |
| 4173 | claim evidence not exact (c2: he feels this interval has been broadly stable over the past year) |  |  |
| 4345 | claim evidence not exact (c3: No absence spells or myoclonic clusters reported outside these dates) |  |  |
| 4480 |  | missing_final_label | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event' |
| 4592 | claim evidence not exact (c4: no new red-flag features were reported today) |  |  |
| 5406 | claim evidence not exact (c2: The patient describes fewer stress-related spells and improved sleep regularity. There have been no injuries, no tongue biting, and recovery is rapid when episodes occur, aligning with non-epileptic-like events rather than electroclinical seizures.) |  |  |
| 5528 | claim evidence not exact (c2: he has otherwise been well and there have been no additional episodes) |  |  |
| 5551 |  | unparsable_label: several per day (Unparsable label (raw: 'several per day' / normalized: 'several per day')) |  |

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 128 | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | 1 per 7 day | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes |  |
| 190 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 198 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes | claim_extraction,final_query |
| 278 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 409 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 419 | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes |  |
| 598 | 1 per 8 month | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes |  |
| 659 | 2 per 4 day | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
| 665 | 2 per 2 week | 2 per 2 week | 2 per 2 week | 2 per 2 week | yes | yes |  |
| 678 | 2 per 4 month | 2 per 4 month | 2 per 4 month | 2 per 4 month | yes | yes |  |
| 694 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 704 | 2 per month | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 725 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 731 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 743 | multiple per month | multiple per month | multiple per month | multiple per week | yes | yes |  |
| 744 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 763 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | yes |  |
| 816 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 849 | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 854 | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 899 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 959 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 960 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 978 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 987 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 1030 | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | yes | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | 3 to 5 per 1 week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes |  |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | yes |  |
| 1207 | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | yes | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes | claim_extraction,final_query |
| 1249 | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 1281 | 5 to 7 per year | 5 to 7 per year | 5 to 7 per year | 5 to 7 per year | yes | yes |  |
| 1317 | 1 per 1 day | 1 per day | 1 per day | unknown, multiple per cluster | no | no |  |
| 1357 | 1 per 1 day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 1363 | 3 per 1 day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 1413 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 1454 | 7 per 1 week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 1486 | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 1573 | 11 per 1 week | 11 per week | 11 per week | 11 per week | yes | yes |  |
| 1591 | 11 per month | 11 per month | 11 per month | 11 per month | yes | yes |  |
| 1596 | 12 per 1 week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1597 | 5 to 7 per 1 month | 5 to 7 per month | 5 to 7 per month | 12 per month | yes | yes |  |
| 1636 | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1640 | 5 per 1 week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 1687 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 1694 | 3 per 2 week | 3 per 2 week | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | yes | claim_extraction |
| 1695 | unknown | unknown | unknown | multiple per month | yes | yes |  |
| 1706 | multiple per month | multiple per month | multiple per month | multiple cluster per month, multiple per cluster | no | no |  |
| 1707 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | 11 per 6 month | 11 per 6 month | yes | yes |  |
| 1773 | multiple per month | multiple per month | multiple per month | 11 per 3 month | no | no |  |
| 1790 | 6 per 4 month | 6 per 4 month | 6 per 4 month | 8 per 4 month | yes | yes |  |
| 1794 | 6 per 2 month | 6 per 2 month | 6 per 2 month | 8 per 2 month | no | no |  |
| 1866 | 1 to 4 per month | 1 to 4 per month | 1 to 4 per month | 8 per 2 month | no | no |  |
| 1880 | 7 per 2 month | 7 per 2 month | 7 per 2 month | 8 per 2 month | no | no |  |
| 1887 | 4 per 3 month | 4 per 3 month | 4 per 3 month | 4 per 3 month | yes | yes |  |
| 1914 | 5 to 7 per 3 month | 5 to 7 per 3 month | 5 to 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1922 | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | 7 per 3 month | no | no |  |
| 1923 | 7 per 6 month | 7 per 6 month | 7 per 6 month | 7 per 6 month | yes | yes |  |
| 1979 | 6 per 2 month | 6 per 2 month | 6 per 2 month | 6 per 2 month | yes | yes |  |
| 1980 | 3 per 3 month | 3 per 3 month | 3 per 3 month | 6 per 3 month | no | no |  |
| 2023 | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 2080 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2094 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2114 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2149 | unknown | unknown | unknown | unknown | yes | yes |  |
| 2166 | frequent petit mal recently | frequent petit mal recently | frequent petit mal recently | unknown |  |  | scorer_format |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | yes | claim_extraction |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | yes |  |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | yes |  |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | yes | yes |  |
| 2366 | 2 to 4 per 1 year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | yes | yes |  |
| 2374 | 7 to 9 per 1 month | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | yes | yes |  |
| 2425 | 6 to 8 per 1 month | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | yes | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | yes |  |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | yes |  |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | yes |  |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | yes |  |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | yes |  |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | yes |  |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | yes |  |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | yes |  |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | yes |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | yes |  |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | yes |  |
| 2609 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2622 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2628 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2678 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2681 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 2731 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 2740 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2748 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2759 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2762 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2765 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2776 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2789 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2812 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2822 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2824 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2877 | 2 per 12 month | 2 per 12 month | 2 per 12 month | 2 per year | yes | yes |  |
| 2887 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 2932 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 9 month | yes | yes |  |
| 2938 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 8 month | yes | yes |  |
| 2965 | seizure free for 1 year 4 month | seizure free for 1 year | seizure free for 1 year | seizure free for 16 month | yes | yes |  |
| 2992 | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 3015 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 12 month | yes | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | yes | yes |  |
| 3095 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 12 month | yes | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 3118 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 3137 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 3224 | 6 to 7 per 1 day | 6 to 7 per day | 6 to 7 per day | 1 cluster per month, 6 to 7 per cluster | no | no | claim_extraction |
| 3242 | multiple per month | multiple per month | multiple per month | 2 cluster per month, 5 per cluster | no | no |  |
| 3261 | multiple per month | multiple per month | multiple per month | 2 cluster per month, 4 per cluster | no | no |  |
| 3262 | 2 per month | 2 per month | 2 per month | 2 cluster per month, 5 per cluster | no | no |  |
| 3281 | 8 per 30 day | 8 per 30 day | 8 per 30 day | 8 per month | yes | yes |  |
| 3297 | 6 per 30 day | 6 per 30 day | 6 per 30 day | 6 per month | yes | yes |  |
| 3325 | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 3356 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3371 | seizure free for 8 week | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 3436 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3468 | None | None | None | unknown |  |  | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event'; claim_extraction,final_query,parse_schema,scorer_format |
| 3469 | 1 per 6 day | 1 per 6 day | 1 per 6 day | unknown | no | no |  |
| 3482 | 1 per 6 day | 1 per 6 day | 1 per 6 day | unknown | no | no |  |
| 3493 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3507 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3512 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3528 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3532 | 2 per 3 week | 2 per 3 week | 2 per 3 week | unknown | no | no |  |
| 3534 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | unknown | no | no |  |
| 3600 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3623 | multiple per week | multiple per week | multiple per week | 7 per week | no | no |  |
| 3643 | multiple per week | multiple per week | multiple per week | 7 per week | no | no |  |
| 3681 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3682 | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3710 | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 3753 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 3766 | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3774 | 9 per year | 9 per year | 9 per year | 9 per year | yes | yes |  |
| 3791 | 10 per year | 10 per year | 10 per year | 10 per year | yes | yes |  |
| 3801 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3806 | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3827 | 7 per month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 3846 | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 3849 | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 3889 | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3892 | 3 per year | 3 per year | 3 per year | 3 per year | yes | yes |  |
| 3940 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3949 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3988 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 3995 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 3999 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4022 | 8 per month | 8 per month | 8 per month | 8 per month | yes | yes |  |
| 4026 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4092 | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 1 per 2 to 3 week | no | no |  |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes | claim_extraction |
| 4116 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4173 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes | claim_extraction |
| 4243 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4258 | 4 per 7 day | 4 per 7 day | 4 per 7 day | 4 per week | yes | yes |  |
| 4337 | 3 per 3 month | 3 per 3 month | 3 per 3 month | 3 per 3 month | yes | yes |  |
| 4345 | 4 per month | 4 per month | 4 per month | 4 per month | yes | yes | claim_extraction |
| 4368 | 5 per 2 month | 5 per 2 month | 5 per 2 month | 5 per 2 month | yes | yes |  |
| 4402 | 1 per month | 1 per month | 1 per month | 7 per 7 month | yes | yes |  |
| 4410 | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 4 per 7 month | yes | yes |  |
| 4478 | 19 per week | 19 per week | 19 per week | 19 per week | yes | yes |  |
| 4480 | None | None | None | 3 to 5 per week |  |  | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event'; claim_extraction,final_query,parse_schema,scorer_format |
| 4496 | 5 to 8 per 3 month | 5 to 8 per 3 month | 5 to 8 per 3 month | 7 to 8 per 3 month | yes | yes |  |
| 4562 | 1 per 6 week | 1 per 6 week | 1 per 6 week | 1 per 6 week | yes | yes |  |
| 4563 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 4574 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 4592 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes | claim_extraction |
| 4597 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 4624 | 1 per 3 to 4 day | 1 per 3 to 4 day | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | yes |  |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | yes |  |
| 4690 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4694 | multiple per hour | multiple per hour | multiple per hour | multiple per day | yes | yes |  |
| 4700 | multiple per hour | multiple per hour | multiple per hour | multiple per day | yes | yes |  |
| 4709 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 4731 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 4732 | unknown | unknown | unknown | unknown | yes | yes |  |
| 4771 | 2 per 6 week | 2 per 6 week | 2 per 6 week | unknown | no | no |  |
| 4839 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | seizure free for multiple month | yes | yes |  |
| 4842 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 4910 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4926 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 1 year | yes | yes |  |
| 4951 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 4956 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 7 month | yes | yes |  |
| 4992 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 11 month | yes | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 months | yes | yes |  |
| 5082 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5092 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no | temporality_conflict |
| 5110 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 5121 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5136 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 5141 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5197 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5210 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5221 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for multiple month | yes | yes |  |
| 5248 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 5331 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 5345 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5351 | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 5379 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 5406 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no | claim_extraction |
| 5476 | 1 per month | 1 per month | 1 per month | unknown | no | no |  |
| 5490 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5491 | 2 per 6 week | 2 per 6 week | 2 per 6 week | unknown | no | no |  |
| 5504 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5507 | 3 per 4 month | 3 per 4 month | 3 per 4 month | unknown | no | no |  |
| 5528 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes | claim_extraction |
| 5534 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per multiple month | no | no |  |
| 5551 | several per day | several per day | multiple per day | multiple per day |  | yes | scorer_format |
| 5567 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5584 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
