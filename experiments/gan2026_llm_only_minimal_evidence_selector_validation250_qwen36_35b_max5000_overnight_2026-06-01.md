# Gan 2026 LLM-Only Minimal Evidence Selector V2

Date: 2026-06-02

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a minimal model-boundary schema can capture the clinically selected source-near answer and exact evidence while deterministic sidecars recover scorer labels and rich diagnostics.

Model task: produce `answer.answer_text` and exact selected evidence. Deterministic code validates structure and evidence, derives scorer-facing labels from the selected evidence, derives diagnostic state, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Escalation reason: not applicable for this run size.

## Model And Prompt Metadata

- Pipeline: `gan2026_llm_only_minimal_evidence_selector_v2`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only minimal evidence selector
- Prompt/program version: `gan2026_llm_only_minimal_evidence_selector_v2`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `False`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Prompt policy taxonomy: `mes_v2.schema.shallow_json_object`, `mes_v2.evidence.exact_answer_substring`, `mes_v2.answer.source_near_text`
- Schema contract: `minimal_source_near_answer_plus_selected_evidence_repair_v2`
- Deterministic rule configuration: none before prediction; deterministic code validates, performs strict/frozen clean scorer-facing repair, derives diagnostics, and scores.
- Git commit: `a11bedc`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_only_minimal_evidence_selector_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`

## Summary

- Minimal evidence records: 249 / 250
- Call failures: 0
- Invalid JSON failures: 0
- Schema failures: 1
- Parse/schema issues: 1
- Exact answer evidence substrings: 249 / 250
- Exact supporting-fact evidence substrings: 482 / 485
- Raw source-near answer score: Purist 0.0480 (12 / 250), Pragmatic 0.0480 (12 / 250)
- Strict-format score: Purist 0.2240 (56 / 250), Pragmatic 0.2280 (57 / 250)
- Frozen clean scorer-facing score: Purist 0.7720 (193 / 250), Pragmatic 0.7760 (194 / 250)
- Rows changed by downstream repair layers: 240
- Answer states: {'cluster_frequency': 17, 'frequency': 180, 'seizure_free': 43, 'unknown_frequency': 9}

## Contract And Evidence Issues

| Row | Contract issues | Evidence issues | Raw scorer-format issue |
| ---: | --- | --- | --- |
| 10 |  |  | unparsable_label: ≤ four per day (Unparsable label (raw: '≤ four per day' / normalized: '≤ four per day')) |
| 40 |  |  | unparsable_label: ≤ four seizures per week (Unparsable label (raw: '≤ four seizures per week' / normalized: '≤ four seizures per week')) |
| 79 |  |  | unparsable_label: ≤ 6 to 7 per year (Unparsable label (raw: '≤ 6 to 7 per year' / normalized: '≤ 6 to 7 per year')) |
| 103 |  |  | unparsable_label: ≤ two or four per year (Unparsable label (raw: '≤ two or four per year' / normalized: '≤ two or four per year')) |
| 156 |  |  | unparsable_label: seizures every 6 days (Unparsable label (raw: 'seizures every 6 days' / normalized: 'seizures every 6 days')) |
| 180 |  |  | unparsable_label: seizures every seven days (Unparsable label (raw: 'seizures every seven days' / normalized: 'seizures every seven days')) |
| 182 |  |  | unparsable_label: every 2 days (Unparsable label (raw: 'every 2 days' / normalized: 'every 2 days')) |
| 187 |  |  | unparsable_label: events tend to cluster every seven to nine days (Unparsable cluster label: 'events tend to cluster every seven to nine days') |
| 190 |  |  | unparsable_label: clusters of brief absence episodes every 4 weeks (Unparsable cluster label: 'clusters of brief absence episodes every 4 weeks') |
| 198 |  |  | unparsable_label: every 4 weeks (Unparsable label (raw: 'every 4 weeks' / normalized: 'every 4 weeks')) |
| 212 |  |  | unparsable_label: every 3 - 4 weeks (Unparsable label (raw: 'every 3 - 4 weeks' / normalized: 'every 3 to 4 weeks')) |
| 218 |  |  | unparsable_label: seizures every 3 weeks (Unparsable label (raw: 'seizures every 3 weeks' / normalized: 'seizures every 3 weeks')) |
| 243 |  |  | unparsable_label: every four months (Unparsable label (raw: 'every four months' / normalized: 'every four months')) |
| 278 |  |  | unparsable_label: multiple times in past week (Unparsable label (raw: 'multiple times in past week' / normalized: 'multiple times in past week')) |
| 280 | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'unknown_frequency', 'no_frequency_reference', 'last_event_only' or 'non_seizure_or_proxy' |  | missing_final_label |
| 338 |  |  | unparsable_label: many convulsions in past month (Unparsable label (raw: 'many convulsions in past month' / normalized: 'many convulsions in past month')) |
| 409 |  |  | unparsable_label: ≤ once per month (Unparsable label (raw: '≤ once per month' / normalized: '≤ once per month')) |
| 419 |  |  | unparsable_label: approximately twice per year (Unparsable label (raw: 'approximately twice per year' / normalized: 'approximately twice per year')) |
| 446 |  |  | unparsable_label: ≤ twice per week (Unparsable label (raw: '≤ twice per week' / normalized: '≤ twice per week')) |
| 466 |  |  | unparsable_label: 21 to 28 seizures per month (Unparsable label (raw: '21 to 28 seizures per month' / normalized: '21 to 28 seizures per month')) |
| 531 |  |  | unparsable_label: 12 to 30 per quarter (Unparsable label (raw: '12 to 30 per quarter' / normalized: '12 to 30 per quarter')) |
| 598 |  |  | unparsable_label: 1 per eight months (Unparsable label (raw: '1 per eight months' / normalized: '1 per eight months')) |
| 659 |  |  | unparsable_label: seizures twice every 4 days (Unparsable label (raw: 'seizures twice every 4 days' / normalized: 'seizures twice every 4 days')) |
| 665 |  |  | unparsable_label: twice every two weeks (Unparsable label (raw: 'twice every two weeks' / normalized: 'twice every two weeks')) |
| 678 |  |  | unparsable_label: twice every 4 months (Unparsable label (raw: 'twice every 4 months' / normalized: 'twice every 4 months')) |
| 694 |  |  | unparsable_label: once a week (Unparsable label (raw: 'once a week' / normalized: 'once a week')) |
| 704 |  |  | unparsable_label: twice a month (Unparsable label (raw: 'twice a month' / normalized: 'twice a month')) |
| 725 |  |  | unparsable_label: daily (Unparsable label (raw: 'daily' / normalized: 'daily')) |
| 731 |  |  | unparsable_label: daily (Unparsable label (raw: 'daily' / normalized: 'daily')) |
| 743 |  |  | unparsable_label: most shifts (Unparsable label (raw: 'most shifts' / normalized: 'most shifts')) |
| 744 |  |  | unparsable_label: brief absences occurring on most weekdays (Unparsable label (raw: 'brief absences occurring on most weekdays' / normalized: 'brief absences occurring on most weekdays')) |
| 763 |  |  | unparsable_label: weekly (Unparsable label (raw: 'weekly' / normalized: 'weekly')) |
| 790 |  |  | unparsable_label: roughly once every seven to ten days (Unparsable label (raw: 'roughly once every seven to ten days' / normalized: 'roughly once every seven to ten days')) |
| 816 |  |  | unparsable_label: monthly seizures (Unparsable label (raw: 'monthly seizures' / normalized: 'monthly seizures')) |
| 849 |  |  | unparsable_label: yearly seizures (Unparsable label (raw: 'yearly seizures' / normalized: 'yearly seizures')) |
| 854 |  |  | unparsable_label: roughly yearly (Unparsable label (raw: 'roughly yearly' / normalized: 'roughly yearly')) |
| 891 |  |  | unparsable_label: seizures every other day (Unparsable label (raw: 'seizures every other day' / normalized: 'seizures every other day')) |
| 899 |  |  | unparsable_label: seizures every other week (Unparsable label (raw: 'seizures every other week' / normalized: 'seizures every other week')) |
| 959 |  |  | unparsable_label: bimonthly on average (Unparsable label (raw: 'bimonthly on average' / normalized: 'bimonthly on average')) |
| 960 |  |  | unparsable_label: bimonthly seizures (Unparsable label (raw: 'bimonthly seizures' / normalized: 'bimonthly seizures')) |
| 978 |  |  | unparsable_label: every other month or so (Unparsable label (raw: 'every other month or so' / normalized: 'every other month or so')) |
| 987 |  |  | unparsable_label: bimonthly (Unparsable label (raw: 'bimonthly' / normalized: 'bimonthly')) |
| 1030 |  |  | unparsable_label: one or three seizures last month (Unparsable label (raw: 'one or three seizures last month' / normalized: 'one or three seizures last month')) |
| 1046 |  |  | unparsable_label: 3 or 5 seizures last month (Unparsable label (raw: '3 or 5 seizures last month' / normalized: '3 or 5 seizures last month')) |
| 1070 |  |  | unparsable_label: three or four seizures last week (Unparsable label (raw: 'three or four seizures last week' / normalized: 'three or four seizures last week')) |
| 1094 |  |  | unparsable_label: 3 to 5 seizures last week (Unparsable label (raw: '3 to 5 seizures last week' / normalized: '3 to 5 seizures last week')) |
| 1165 |  |  | unparsable_label: no further episodes for the last six weeks (Unparsable label (raw: 'no further episodes for the last six weeks' / normalized: 'no further episodes for the last six weeks')) |
| 1171 |  |  | unparsable_label: 7 to 9 focal onset seizures in three weeks (Unparsable label (raw: '7 to 9 focal onset seizures in three weeks' / normalized: '7 to 9 focal onset seizures in three weeks')) |
| 1207 |  |  | unparsable_label: 21 to 28 epileptic spasms in three months (Unparsable label (raw: '21 to 28 epileptic spasms in three months' / normalized: '21 to 28 epileptic spasms in three months')) |
| 1223 |  |  | unparsable_label: 3 or 4 focal impaired awareness seizures (Unparsable label (raw: '3 or 4 focal impaired awareness seizures' / normalized: '3 or 4 focal impaired awareness seizures')) |
| 1249 |  |  | unparsable_label: 2 or 4 focal impaired awareness seizures this week (Unparsable label (raw: '2 or 4 focal impaired awareness seizures this week' / normalized: '2 or 4 focal impaired awareness seizures this week')) |
| 1281 |  |  | unparsable_label: 5 or 7 epileptic spasms this year (Unparsable label (raw: '5 or 7 epileptic spasms this year' / normalized: '5 or 7 epileptic spasms this year')) |
| 1317 |  |  | unparsable_label: cluster of events over a single day (Unparsable cluster label: 'cluster of events over a single day') |
| 1357 |  |  | unparsable_label: 1 tonic-clonic seizures yesterday (Unparsable label (raw: '1 tonic-clonic seizures yesterday' / normalized: '1 tonic-clonic seizures yesterday')) |
| 1363 |  |  | unparsable_label: three tonic-clonic seizures yesterday (Unparsable label (raw: 'three tonic-clonic seizures yesterday' / normalized: 'three tonic-clonic seizures yesterday')) |
| 1413 |  |  | unparsable_label: nine events per month (Unparsable label (raw: 'nine events per month' / normalized: 'nine events per month')) |
| 1454 |  |  | unparsable_label: one tonic-clonic and six petit mal in last week (Unparsable label (raw: 'one tonic-clonic and six petit mal in last week' / normalized: 'one tonic-clonic and six petit mal in last week')) |
| 1486 |  |  | unparsable_label: two focal epileptic spasms and one focal non-motor in last month (Unparsable label (raw: 'two focal epileptic spasms and one focal non-motor in last month' / normalized: 'two focal epileptic spasms and one focal non-motor in last month')) |
| 1573 |  |  | unparsable_label: five focal cognitive and six focal non-motors in last week (Unparsable label (raw: 'five focal cognitive and six focal non-motors in last week' / normalized: 'five focal cognitive and six focal non-motors in last week')) |
| 1591 |  |  | unparsable_label: five focal onset seizures and six focal non-motors in last month (Unparsable label (raw: 'five focal onset seizures and six focal non-motors in last month' / normalized: 'five focal onset seizures and six focal non-motors in last month')) |
| 1596 |  |  | unparsable_label: five drop attacks and seven petit mal in last week (Unparsable label (raw: 'five drop attacks and seven petit mal in last week' / normalized: 'five drop attacks and seven petit mal in last week')) |
| 1597 |  |  | unparsable_label: five absence seizures and seven petit mal in last month (Unparsable label (raw: 'five absence seizures and seven petit mal in last month' / normalized: 'five absence seizures and seven petit mal in last month')) |
| 1636 |  |  | unparsable_label: two drop attacks and three petit mal in last month (Unparsable label (raw: 'two drop attacks and three petit mal in last month' / normalized: 'two drop attacks and three petit mal in last month')) |
| 1640 |  |  | unparsable_label: two absence seizures and three petit mal in last week (Unparsable label (raw: 'two absence seizures and three petit mal in last week' / normalized: 'two absence seizures and three petit mal in last week')) |
| 1687 |  |  | unparsable_label: several focal seizures last week (Unparsable label (raw: 'several focal seizures last week' / normalized: 'several focal seizures last week')) |
| 1694 |  |  | unparsable_label: three short episodes occurring on separate days (Unparsable label (raw: 'three short episodes occurring on separate days' / normalized: 'three short episodes occurring on separate days')) |
| 1695 |  |  | unparsable_label: no events have been recorded (Unparsable label (raw: 'no events have been recorded' / normalized: 'no events have been recorded')) |
| 1706 |  |  | unparsable_label: a cluster of short events on multiple days (Unparsable cluster label: 'a cluster of short events on multiple days') |
| 1707 |  |  | unparsable_label: a brief cluster of events occurring on multiple days within the past week (Unparsable cluster label: 'a brief cluster of events occurring on multiple days within the past week') |
| 1772 |  |  | unparsable_label: two drop attacks and nine absence seizures in the past six months (Unparsable label (raw: 'two drop attacks and nine absence seizures in the past six months' / normalized: 'two drop attacks and nine absence seizures in the past six months')) |
| 1773 |  |  | unparsable_label: two drop attacks and nine convulsions in the past three months (Unparsable label (raw: 'two drop attacks and nine convulsions in the past three months' / normalized: 'two drop attacks and nine convulsions in the past three months')) |
| 1790 |  |  | unparsable_label: six drop attacks and two epileptic spasms in the past four months (Unparsable label (raw: 'six drop attacks and two epileptic spasms in the past four months' / normalized: 'six drop attacks and two epileptic spasms in the past four months')) |
| 1794 |  |  | unparsable_label: six drop attacks and two absence seizures in the past two months (Unparsable label (raw: 'six drop attacks and two absence seizures in the past two months' / normalized: 'six drop attacks and two absence seizures in the past two months')) |
| 1866 |  |  | unparsable_label: one drop attacks and seven absence seizures in the past two months (Unparsable label (raw: 'one drop attacks and seven absence seizures in the past two months' / normalized: 'one drop attacks and seven absence seizures in the past two months')) |
| 1880 |  |  | unparsable_label: one drop attacks and seven convulsions in the past two months (Unparsable label (raw: 'one drop attacks and seven convulsions in the past two months' / normalized: 'one drop attacks and seven convulsions in the past two months')) |
| 1887 |  |  | unparsable_label: three drop attacks and one convulsion in the past three months (Unparsable label (raw: 'three drop attacks and one convulsion in the past three months' / normalized: 'three drop attacks and one convulsion in the past three months')) |
| 1914 |  |  | unparsable_label: two drop attacks and five tonic-clonic in the past three months (Unparsable label (raw: 'two drop attacks and five tonic-clonic in the past three months' / normalized: 'two drop attacks and five tonic-clonic in the past three months')) |
| 1922 |  |  | unparsable_label: two drop attacks and five convulsions in the past three months (Unparsable label (raw: 'two drop attacks and five convulsions in the past three months' / normalized: 'two drop attacks and five convulsions in the past three months')) |
| 1923 |  |  | unparsable_label: two drop attacks and five epileptic spasms in the past six months (Unparsable label (raw: 'two drop attacks and five epileptic spasms in the past six months' / normalized: 'two drop attacks and five epileptic spasms in the past six months')) |
| 1979 |  |  | unparsable_label: three focal onset seizures and three focal automatisms in the past two months (Unparsable label (raw: 'three focal onset seizures and three focal automatisms in the past two months' / normalized: 'three focal onset seizures and three focal automatisms in the past two months')) |
| 1980 |  |  | unparsable_label: three focal onset seizures and three focal epileptic spasms in the past three months (Unparsable label (raw: 'three focal onset seizures and three focal epileptic spasms in the past three months' / normalized: 'three focal onset seizures and three focal epileptic spasms in the past three months')) |
| 2023 |  |  | unparsable_label: four absence seizures and one myoclonic this month (Unparsable label (raw: 'four absence seizures and one myoclonic this month' / normalized: 'four absence seizures and one myoclonic this month')) |
| 2094 |  |  | unparsable_label: several absence seizures in the past month (Unparsable label (raw: 'several absence seizures in the past month' / normalized: 'several absence seizures in the past month')) |
| 2114 |  |  | unparsable_label: several myoclonic in the past month (Unparsable label (raw: 'several myoclonic in the past month' / normalized: 'several myoclonic in the past month')) |
| 2149 |  |  | unparsable_label: occasional tonic-clonic over last year (Unparsable label (raw: 'occasional tonic-clonic over last year' / normalized: 'occasional tonic-clonic over last year')) |
| 2166 |  |  | unparsable_label: frequent petit mal recently (Unparsable label (raw: 'frequent petit mal recently' / normalized: 'frequent petit mal recently')) |
| 2228 |  |  | unparsable_label: 3 or 5 seizures in the last two weeks (Unparsable label (raw: '3 or 5 seizures in the last two weeks' / normalized: '3 or 5 seizures in the last two weeks')) |
| 2233 |  |  | unparsable_label: about 6 or 7 seizures in the last two months (Unparsable label (raw: 'about 6 or 7 seizures in the last two months' / normalized: 'about 6 or 7 seizures in the last two months')) |
| 2245 |  |  | unparsable_label: about 7 to 8 seizures in the last three weeks (Unparsable label (raw: 'about 7 to 8 seizures in the last three weeks' / normalized: 'about 7 to 8 seizures in the last three weeks')) |
| 2259 |  |  | unparsable_label: about six or eight seizures in the last three months (Unparsable label (raw: 'about six or eight seizures in the last three months' / normalized: 'about six or eight seizures in the last three months')) |
| 2354 |  |  | unparsable_label: 6 to 7 myoclonic per week (Unparsable label (raw: '6 to 7 myoclonic per week' / normalized: '6 to 7 myoclonic per week')) |
| 2366 |  |  | unparsable_label: two or four seizures over the past year (Unparsable label (raw: 'two or four seizures over the past year' / normalized: 'two or four seizures over the past year')) |
| 2369 |  |  | unparsable_label: 3 to 4 seizures (Unparsable label (raw: '3 to 4 seizures' / normalized: '3 to 4 seizures')) |
| 2374 |  |  | unparsable_label: 7 to 9 seizures over the past month (Unparsable label (raw: '7 to 9 seizures over the past month' / normalized: '7 to 9 seizures over the past month')) |
| 2425 |  |  | unparsable_label: six or eight petit mal over the past month (Unparsable label (raw: 'six or eight petit mal over the past month' / normalized: 'six or eight petit mal over the past month')) |
| 2427 |  |  | unparsable_label: 3 or 5 tonic-clonic over the past month (Unparsable label (raw: '3 or 5 tonic-clonic over the past month' / normalized: '3 or 5 tonic-clonic over the past month')) |
| 2435 |  |  | unparsable_label: five to seven seizures during the last two weeks (Unparsable label (raw: 'five to seven seizures during the last two weeks' / normalized: 'five to seven seizures during the last two weeks')) |
| 2437 |  |  | unparsable_label: 2 to 3 seizures during the last two months (Unparsable label (raw: '2 to 3 seizures during the last two months' / normalized: '2 to 3 seizures during the last two months')) |
| 2440 |  |  | unparsable_label: five or seven seizures during the last two months (Unparsable label (raw: 'five or seven seizures during the last two months' / normalized: 'five or seven seizures during the last two months')) |
| 2456 |  |  | unparsable_label: six to seven seizures during the last two weeks (Unparsable label (raw: 'six to seven seizures during the last two weeks' / normalized: 'six to seven seizures during the last two weeks')) |
| 2459 |  |  | unparsable_label: seven to nine seizures during the last two weeks (Unparsable label (raw: 'seven to nine seizures during the last two weeks' / normalized: 'seven to nine seizures during the last two weeks')) |
| 2487 |  |  | unparsable_label: two to three seizures during the last three months (Unparsable label (raw: 'two to three seizures during the last three months' / normalized: 'two to three seizures during the last three months')) |
| 2513 |  |  | unparsable_label: 2 to 3 drop attacks during the last two weeks (Unparsable label (raw: '2 to 3 drop attacks during the last two weeks' / normalized: '2 to 3 drop attacks during the last two weeks')) |
| 2541 |  |  | unparsable_label: eight or nine drop attacks during the last two weeks (Unparsable label (raw: 'eight or nine drop attacks during the last two weeks' / normalized: 'eight or nine drop attacks during the last two weeks')) |
| 2548 |  |  | unparsable_label: five to six focal automatisms during the last two months (Unparsable label (raw: 'five to six focal automatisms during the last two months' / normalized: 'five to six focal automatisms during the last two months')) |
| 2554 |  |  | unparsable_label: 1 - 10 focal aware seizures during the last two months (Unparsable label (raw: '1 - 10 focal aware seizures during the last two months' / normalized: '1 to 10 focal aware seizures during the last two months')) |
| 2558 |  |  | unparsable_label: 3 to 4 focal impaired awareness seizures during the last two months (Unparsable label (raw: '3 to 4 focal impaired awareness seizures during the last two months' / normalized: '3 to 4 focal impaired awareness seizures during the last two months')) |
| 2609 |  |  | unparsable_label: once per night (Unparsable label (raw: 'once per night' / normalized: 'once per night')) |
| 2622 |  |  | unparsable_label: seizures every night (Unparsable label (raw: 'seizures every night' / normalized: 'seizures every night')) |
| 2628 |  |  | unparsable_label: seizures every night (Unparsable label (raw: 'seizures every night' / normalized: 'seizures every night')) |
| 2678 |  |  | unparsable_label: tonic-clonic every night (Unparsable label (raw: 'tonic-clonic every night' / normalized: 'tonic-clonic every night')) |
| 2681 |  |  | unparsable_label: an absence seizure every night (Unparsable label (raw: 'an absence seizure every night' / normalized: 'an absence seizure every night')) |
| 2698 |  |  | unparsable_label: myoclonic every other day (Unparsable label (raw: 'myoclonic every other day' / normalized: 'myoclonic every other day')) |
| 2731 |  |  | unparsable_label: every other week (Unparsable label (raw: 'every other week' / normalized: 'every other week')) |
| 2740 |  |  | unparsable_label: complex partial seizure monthly (Unparsable label (raw: 'complex partial seizure monthly' / normalized: 'complex partial seizure monthly')) |
| 2748 |  |  | unparsable_label: a focal seizure monthly (Unparsable label (raw: 'a focal seizure monthly' / normalized: 'a focal seizure monthly')) |
| 2759 |  |  | unparsable_label: monthly (Unparsable label (raw: 'monthly' / normalized: 'monthly')) |
| 2762 |  |  | unparsable_label: monthly (Unparsable label (raw: 'monthly' / normalized: 'monthly')) |
| 2765 |  |  | unparsable_label: a focal onset seizure monthly (Unparsable label (raw: 'a focal onset seizure monthly' / normalized: 'a focal onset seizure monthly')) |
| 2776 |  |  | unparsable_label: weekly (Unparsable label (raw: 'weekly' / normalized: 'weekly')) |
| 2789 |  |  | unparsable_label: convulsion weekly (Unparsable label (raw: 'convulsion weekly' / normalized: 'convulsion weekly')) |
| 2812 |  |  | unparsable_label: at least one drop attack daily (Unparsable label (raw: 'at least one drop attack daily' / normalized: 'at least one drop attack daily')) |
| 2822 |  |  | unparsable_label: daily (Unparsable label (raw: 'daily' / normalized: 'daily')) |
| 2824 |  |  | unparsable_label: tonic-clonic daily (Unparsable label (raw: 'tonic-clonic daily' / normalized: 'tonic-clonic daily')) |
| 2877 |  |  | unparsable_label: twice a year (Unparsable label (raw: 'twice a year' / normalized: 'twice a year')) |
| 2887 |  |  | unparsable_label: twice a week (Unparsable label (raw: 'twice a week' / normalized: 'twice a week')) |
| 2907 |  |  | unparsable_label: Seizure-free since 27 March 2024 (Unparsable label (raw: 'seizure-free since 27 march 2024' / normalized: 'seizure-free since 27 march 2024')) |
| 2932 |  |  | unparsable_label: seizure‑free since 29/09/2017 (Unparsable label (raw: 'seizure‑free since 29/09/2017' / normalized: 'seizure‑free since 29/09/2017')) |
| 2938 |  |  | unparsable_label: Seizure-free since 13-Nov-2015 (Unparsable label (raw: 'seizure-free since 13-nov-2015' / normalized: 'seizure-free since 13-nov-2015')) |
| 2965 |  |  | unparsable_label: no confirmed events (Unparsable label (raw: 'no confirmed events' / normalized: 'no confirmed events')) |
| 2992 |  |  | unparsable_label: no further events since that date (Unparsable label (raw: 'no further events since that date' / normalized: 'no further events since that date')) |
| 3015 |  |  | unparsable_label: no events over the last year (Unparsable label (raw: 'no events over the last year' / normalized: 'no events over the last year')) |
| 3048 |  |  | unparsable_label: No events for 16 months (Unparsable label (raw: 'no events for 16 months' / normalized: 'no events for 16 months')) |
| 3058 |  |  | unparsable_label: No events for twelve months (Unparsable label (raw: 'no events for twelve months' / normalized: 'no events for twelve months')) |
| 3082 |  |  | unparsable_label: No events for 10 months (Unparsable label (raw: 'no events for 10 months' / normalized: 'no events for 10 months')) |
| 3095 |  |  | unparsable_label: No events for twelve months (Unparsable label (raw: 'no events for twelve months' / normalized: 'no events for twelve months')) |
| 3113 |  |  | unparsable_label: No events for fourteen months (Unparsable label (raw: 'no events for fourteen months' / normalized: 'no events for fourteen months')) |
| 3118 |  |  | unparsable_label: No seizures since last visit (Unparsable label (raw: 'no seizures since last visit' / normalized: 'no seizures since last visit')) |
| 3137 |  |  | unparsable_label: no definite seizure events (Unparsable label (raw: 'no definite seizure events' / normalized: 'no definite seizure events')) |
| 3224 |  |  | unparsable_label: Monthly clusters, typically 6 to 7 seizures over 24 h (Unparsable cluster label: 'monthly clusters, typically 6 to 7 seizures over 24 h') |
| 3242 |  |  | unparsable_label: 2 clusters this month; each ≈five absences in the morning (Unparsable cluster label: '2 clusters this month; each ≈five absences in the morning') |
| 3261 |  |  | unparsable_label: two clusters this month; each ≈four absences in the morning (Unparsable cluster label: 'two clusters this month; each ≈four absences in the morning') |
| 3262 |  |  | unparsable_label: two clusters this month (Unparsable cluster label: 'two clusters this month') |
| 3281 |  |  | unparsable_label: 8/30 this month (Unparsable label (raw: '8/30 this month' / normalized: '8/30 this month')) |
| 3297 |  |  | unparsable_label: six/30 this month (Unparsable label (raw: 'six/30 this month' / normalized: 'six/30 this month')) |
| 3325 |  |  | unparsable_label: About three seizure days per week (Unparsable label (raw: 'about three seizure days per week' / normalized: 'about three seizure days per week')) |
| 3356 |  |  | unparsable_label: brief generalised tonic–clonic seizures occurring exclusively after nights of curtailed sleep, with no events reported when sleep has been adequate (Unparsable label (raw: 'brief generalised tonic–clonic seizures occurring exclusively after nights of curtailed sleep, with no events reported when sleep has been adequate' / normalized: 'brief generalised tonic–clonic seizures occurring exclusively after nights of curtailed sleep, with no events reported when sleep has been adequate')) |
| 3371 |  |  | unparsable_label: no events have occurred in the past eight weeks (Unparsable label (raw: 'no events have occurred in the past eight weeks' / normalized: 'no events have occurred in the past eight weeks')) |
| 3436 |  |  | unparsable_label: Events tend to cluster shortly after early-morning arousal (Unparsable cluster label: 'events tend to cluster shortly after early-morning arousal') |
| 3468 |  | supporting fact evidence not exact (f1: She reports focal aware auras... Importantly, she observes a clear and consistent catamenial pattern: Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free.) | unparsable_label: Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free. (Unparsable label (raw: 'seizures happen when perimenstrual only (days -2 to +2). outside this window she remains seizure-free.' / normalized: 'seizures happen when perimenstrual only (days -2 to +2). outside this window she remains seizure-free.')) |
| 3469 |  |  | unparsable_label: no events over the last six months (Unparsable label (raw: 'no events over the last six months' / normalized: 'no events over the last six months')) |
| 3482 |  |  | unparsable_label: Seizures happen when perimenstrual only (days -3 to +3) (Unparsable label (raw: 'seizures happen when perimenstrual only (days -3 to +3)' / normalized: 'seizures happen when perimenstrual only (days -3 to +3)')) |
| 3493 |  |  | unparsable_label: most episodes falling from roughly three days before the period up to three days afterwards (Unparsable label (raw: 'most episodes falling from roughly three days before the period up to three days afterwards' / normalized: 'most episodes falling from roughly three days before the period up to three days afterwards')) |
| 3528 |  |  | unparsable_label: no witnessed generalised tonic–clonic seizures since 2018 (Unparsable label (raw: 'no witnessed generalised tonic–clonic seizures since 2018' / normalized: 'no witnessed generalised tonic–clonic seizures since 2018')) |
| 3534 |  |  | unparsable_label: no seizures for six months (Unparsable label (raw: 'no seizures for six months' / normalized: 'no seizures for six months')) |
| 3623 |  |  | unparsable_label: up to seven in bad weeks (Unparsable label (raw: 'up to seven in bad weeks' / normalized: 'up to seven in bad weeks')) |
| 3643 |  | supporting fact evidence not exact (f2: There has been a clear deterioration in his seizure control over recent months.) | unparsable_label: clusters up to 7 in bad weeks (Unparsable cluster label: 'clusters up to 7 in bad weeks') |
| 3681 |  |  | unparsable_label: nine/mo (Unparsable label (raw: 'nine/mo' / normalized: 'nine/mo')) |
| 3682 |  |  | unparsable_label: six/mo (Unparsable label (raw: 'six/mo' / normalized: 'six/mo')) |
| 3710 |  |  | unparsable_label: TC *5/wk (Unparsable label (raw: 'tc *5/wk' / normalized: 'tc *5/wk')) |
| 3753 |  |  | unparsable_label: daily (Unparsable label (raw: 'daily' / normalized: 'daily')) |
| 3766 |  |  | unparsable_label: TC X8/yr (Unparsable label (raw: 'tc x8/yr' / normalized: 'tc x8/yr')) |
| 3774 |  |  | unparsable_label: nine/yr (Unparsable label (raw: 'nine/yr' / normalized: 'nine/yr')) |
| 3791 |  |  | unparsable_label: TC ×ten/yr (Unparsable label (raw: 'tc ×ten/yr' / normalized: 'tc ×ten/yr')) |
| 3801 |  |  | unparsable_label: sz ×nine/mo (Unparsable label (raw: 'sz ×nine/mo' / normalized: 'sz ×nine/mo')) |
| 3806 |  |  | unparsable_label: six/mo (Unparsable label (raw: 'six/mo' / normalized: 'six/mo')) |
| 3827 |  |  | unparsable_label: average of sz X7/mo (Unparsable label (raw: 'average of sz x7/mo' / normalized: 'average of sz x7/mo')) |
| 3846 |  |  | unparsable_label: sz X2/d (Unparsable label (raw: 'sz x2/d' / normalized: 'sz x2/d')) |
| 3849 |  |  | unparsable_label: sz x3/d (Unparsable label (raw: 'sz x3/d' / normalized: 'sz x3/d')) |
| 3889 |  |  | unparsable_label: sz xeight/yr (Unparsable label (raw: 'sz xeight/yr' / normalized: 'sz xeight/yr')) |
| 3892 |  |  | unparsable_label: sz x3/yr (Unparsable label (raw: 'sz x3/yr' / normalized: 'sz x3/yr')) |
| 3940 |  |  | unparsable_label: sz xfour/wk (Unparsable label (raw: 'sz xfour/wk' / normalized: 'sz xfour/wk')) |
| 3949 |  |  | unparsable_label: sz Xfour/wk (Unparsable label (raw: 'sz xfour/wk' / normalized: 'sz xfour/wk')) |
| 3988 |  |  | unparsable_label: several times per week (Unparsable label (raw: 'several times per week' / normalized: 'several times per week')) |
| 3995 |  |  | unparsable_label: abs monthly (Unparsable label (raw: 'abs monthly' / normalized: 'abs monthly')) |
| 3999 |  |  | unparsable_label: abs monthly (Unparsable label (raw: 'abs monthly' / normalized: 'abs monthly')) |
| 4022 |  |  | unparsable_label: 8 monthly (Unparsable label (raw: '8 monthly' / normalized: '8 monthly')) |
| 4026 |  |  | unparsable_label: roughly one brief absence episode in a typical month (Unparsable label (raw: 'roughly one brief absence episode in a typical month' / normalized: 'roughly one brief absence episode in a typical month')) |
| 4092 |  |  | unparsable_label: qtwo - threewk (Unparsable label (raw: 'qtwo - threewk' / normalized: 'qtwo - threewk')) |
| 4100 |  |  | unparsable_label: q2 - 3wk (Unparsable label (raw: 'q2 - 3wk' / normalized: 'q2 to 3wk')) |
| 4110 |  |  | unparsable_label: q1 - 2d (Unparsable label (raw: 'q1 - 2d' / normalized: 'q1 to 2d')) |
| 4116 |  |  | unparsable_label: qone to twod on workdays (Unparsable label (raw: 'qone to twod on workdays' / normalized: 'qone to twod on workdays')) |
| 4173 |  |  | unparsable_label: roughly once in a fortnight (Unparsable label (raw: 'roughly once in a fortnight' / normalized: 'roughly once in a fortnight')) |
| 4243 |  |  | unparsable_label: every two to three weeks (Unparsable label (raw: 'every two to three weeks' / normalized: 'every two to three weeks')) |
| 4258 |  |  | unparsable_label: four events per week (Unparsable label (raw: 'four events per week' / normalized: 'four events per week')) |
| 4337 |  |  | unparsable_label: Seizure events on 06-03, 06-13, 09-23 (Unparsable label (raw: 'seizure events on 06-03, 06-13, 09-23' / normalized: 'seizure events on 06 to 03, 06 to 13, 09 to 23')) |
| 4345 |  |  | unparsable_label: four seizures in July (Unparsable label (raw: 'four seizures in july' / normalized: 'four seizures in july')) |
| 4368 |  |  | unparsable_label: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24 (Unparsable label (raw: 'seizure events on 03-07, 03-27, 05-15, 05-19, 05-24' / normalized: 'seizure events on 03 to 07, 03 to 27, 05 to 15, 05 to 19, 05 to 24')) |
| 4402 |  |  | unparsable_label: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1 (Unparsable label (raw: 'jan x1, feb x0, mar x1, apr x2, may x1, jun x1, jul x1' / normalized: 'jan x1, feb x0, mar x1, apr x2, may x1, jun x1, jul x1')) |
| 4410 |  |  | unparsable_label: May x1, Jun x1, Jul x0, Aug x1, Sep x0, Oct x1, Nov x0 (Unparsable label (raw: 'may x1, jun x1, jul x0, aug x1, sep x0, oct x1, nov x0' / normalized: 'may x1, jun x1, jul x0, aug x1, sep x0, oct x1, nov x0')) |
| 4478 |  |  | unparsable_label: nineteen episode of status epilepticus in the past week (Unparsable label (raw: 'nineteen episode of status epilepticus in the past week' / normalized: 'nineteen episode of status epilepticus in the past week')) |
| 4480 |  |  | unparsable_label: three - five episode of status epilepticus in the past week (Unparsable label (raw: 'three - five episode of status epilepticus in the past week' / normalized: 'three - five episode of status epilepticus in the past week')) |
| 4496 |  |  | unparsable_label: seven to eight absence seizures this quarter (Unparsable label (raw: 'seven to eight absence seizures this quarter' / normalized: 'seven to eight absence seizures this quarter')) |
| 4562 |  |  | unparsable_label: median inter-seizure interval ≈ six weeks (Unparsable label (raw: 'median inter-seizure interval ≈ six weeks' / normalized: 'median inter-seizure interval ≈ six weeks')) |
| 4563 |  |  | unparsable_label: Median inter-seizure interval ≈ four months (Unparsable label (raw: 'median inter-seizure interval ≈ four months' / normalized: 'median inter-seizure interval ≈ four months')) |
| 4574 |  |  | unparsable_label: Median inter-seizure interval ≈ four weeks (Unparsable label (raw: 'median inter-seizure interval ≈ four weeks' / normalized: 'median inter-seizure interval ≈ four weeks')) |
| 4592 |  |  | unparsable_label: median inter-seizure interval ≈ two months (Unparsable label (raw: 'median inter-seizure interval ≈ two months' / normalized: 'median inter-seizure interval ≈ two months')) |
| 4597 |  |  | unparsable_label: Median inter-seizure interval ≈ three weeks (Unparsable label (raw: 'median inter-seizure interval ≈ three weeks' / normalized: 'median inter-seizure interval ≈ three weeks')) |
| 4624 |  |  | unparsable_label: intervals ranging three - four days between focal aware seizures (Unparsable label (raw: 'intervals ranging three - four days between focal aware seizures' / normalized: 'intervals ranging three - four days between focal aware seizures')) |
| 4631 |  |  | unparsable_label: intervals ranging 14 - 21 days (Unparsable label (raw: 'intervals ranging 14 - 21 days' / normalized: 'intervals ranging 14 to 21 days')) |
| 4694 |  |  | unparsable_label: ~9/h (Unparsable label (raw: '~9/h' / normalized: '~9/h')) |
| 4700 |  |  | unparsable_label: ~4/h (Unparsable label (raw: '~4/h' / normalized: '~4/h')) |
| 4709 |  |  | unparsable_label: frequent on EEG (~6/h) (Unparsable label (raw: 'frequent on eeg (~6/h)' / normalized: 'frequent on eeg (~6/h)')) |
| 4731 |  |  | unparsable_label: seizures happen rare (Unparsable label (raw: 'seizures happen rare' / normalized: 'seizures happen rare')) |
| 4732 |  |  | unparsable_label: seizures happen occasional, often clustering around travel days or after disrupted sleep (Unparsable cluster label: 'seizures happen occasional, often clustering around travel days or after disrupted sleep') |
| 4771 |  |  | unparsable_label: increased seizure activity (Unparsable label (raw: 'increased seizure activity' / normalized: 'increased seizure activity')) |
| 4839 |  |  | unparsable_label: no recorded events or auras since (Unparsable label (raw: 'no recorded events or auras since' / normalized: 'no recorded events or auras since')) |
| 4842 |  |  | unparsable_label: not experienced any seizures (Unparsable label (raw: 'not experienced any seizures' / normalized: 'not experienced any seizures')) |
| 4910 |  |  | unparsable_label: free of seizures for 2 year (Unparsable label (raw: 'free of seizures for 2 year' / normalized: 'free of seizures for 2 year')) |
| 4919 |  |  | unparsable_label: Free of seizures for 2 year (Unparsable label (raw: 'free of seizures for 2 year' / normalized: 'free of seizures for 2 year')) |
| 4926 |  |  | unparsable_label: Free of seizures for one year (Unparsable label (raw: 'free of seizures for one year' / normalized: 'free of seizures for one year')) |
| 4951 |  |  | unparsable_label: no events for many months (Unparsable label (raw: 'no events for many months' / normalized: 'no events for many months')) |
| 4956 |  |  | unparsable_label: free of events for the past seven months (Unparsable label (raw: 'free of events for the past seven months' / normalized: 'free of events for the past seven months')) |
| 4992 |  |  | unparsable_label: Seizure-free interval since 12-Sep-2018 (Unparsable label (raw: 'seizure-free interval since 12-sep-2018' / normalized: 'seizure-free interval since 12-sep-2018')) |
| 4994 |  |  | unparsable_label: seizure-free interval since 25/06/2021 (Unparsable label (raw: 'seizure-free interval since 25/06/2021' / normalized: 'seizure-free interval since 25/06/2021')) |
| 5040 |  |  | unparsable_label: no further episodes suggestive of seizures (Unparsable label (raw: 'no further episodes suggestive of seizures' / normalized: 'no further episodes suggestive of seizures')) |
| 5082 |  | supporting fact evidence not exact (f3: prior to this improvement she experienced her first seizure in February 2017... A second event occurred in June 2017) | unparsable_label: sustained period without any recurrence of her typical events (Unparsable label (raw: 'sustained period without any recurrence of her typical events' / normalized: 'sustained period without any recurrence of her typical events')) |
| 5092 |  |  | unparsable_label: No clinical seizures observed (Unparsable label (raw: 'no clinical seizures observed' / normalized: 'no clinical seizures observed')) |
| 5110 |  |  | unparsable_label: no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represent clinical seizures (Unparsable label (raw: 'no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represent clinical seizures' / normalized: 'no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represent clinical seizures')) |
| 5121 |  |  | unparsable_label: no events suggestive of seizures (Unparsable label (raw: 'no events suggestive of seizures' / normalized: 'no events suggestive of seizures')) |
| 5136 |  |  | unparsable_label: No recurrence (Unparsable label (raw: 'no recurrence' / normalized: 'no recurrence')) |
| 5141 |  |  | unparsable_label: no further events suggestive of seizures (Unparsable label (raw: 'no further events suggestive of seizures' / normalized: 'no further events suggestive of seizures')) |
| 5197 |  |  | unparsable_label: seizure-free (Unparsable label (raw: 'seizure-free' / normalized: 'seizure-free')) |
| 5221 |  |  | unparsable_label: no seizures for six months (Unparsable label (raw: 'no seizures for six months' / normalized: 'no seizures for six months')) |
| 5248 |  |  | unparsable_label: complete seizure control (Unparsable label (raw: 'complete seizure control' / normalized: 'complete seizure control')) |
| 5331 |  |  | unparsable_label: no events, warnings, or episodes suggestive of seizures over the past 12 months (Unparsable label (raw: 'no events, warnings, or episodes suggestive of seizures over the past 12 months' / normalized: 'no events, warnings, or episodes suggestive of seizures over the past 12 months')) |
| 5345 |  |  | unparsable_label: free of events for several months (Unparsable label (raw: 'free of events for several months' / normalized: 'free of events for several months')) |
| 5351 |  |  | unparsable_label: no events, warnings, or auras for over 18 months (Unparsable label (raw: 'no events, warnings, or auras for over 18 months' / normalized: 'no events, warnings, or auras for over 18 months')) |
| 5379 |  |  | unparsable_label: no recent epileptic seizures (Unparsable label (raw: 'no recent epileptic seizures' / normalized: 'no recent epileptic seizures')) |
| 5406 |  |  | unparsable_label: no definite epileptic events documented in this interval (Unparsable label (raw: 'no definite epileptic events documented in this interval' / normalized: 'no definite epileptic events documented in this interval')) |
| 5476 |  |  | unparsable_label: sporadic epileptic spasms this year (Unparsable label (raw: 'sporadic epileptic spasms this year' / normalized: 'sporadic epileptic spasms this year')) |
| 5504 |  |  | unparsable_label: Sporadic jerks this year (Unparsable label (raw: 'sporadic jerks this year' / normalized: 'sporadic jerks this year')) |
| 5507 |  |  | unparsable_label: scattered sudden falls over the past months, clustered around busy evening service (Unparsable cluster label: 'scattered sudden falls over the past months, clustered around busy evening service') |
| 5528 |  |  | unparsable_label: single very brief event last month (Unparsable label (raw: 'single very brief event last month' / normalized: 'single very brief event last month')) |
| 5534 |  |  | unparsable_label: very infrequent (Unparsable label (raw: 'very infrequent' / normalized: 'very infrequent')) |
| 5551 |  |  | unparsable_label: several episodes per day (Unparsable label (raw: 'several episodes per day' / normalized: 'several episodes per day')) |
| 5567 |  |  | unparsable_label: Several episodes per week (Unparsable label (raw: 'several episodes per week' / normalized: 'several episodes per week')) |
| 5584 |  |  | unparsable_label: several episodes per week (Unparsable label (raw: 'several episodes per week' / normalized: 'several episodes per week')) |

## Rows

| Row | State | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | frequency | ≤ four per day | 4 per day | 4 per day | 4 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 40 | frequency | ≤ four seizures per week | ≤ 4 per week | 4 per week | 4 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 79 | frequency | ≤ 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 103 | frequency | ≤ two or four per year | ≤ 2 or 4 per year | 2 to 4 per year | 2 to 4 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 128 | frequency | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 156 | frequency | seizures every 6 days | 1 per 6 day | 1 per 6 day | 1 per 6 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 180 | frequency | seizures every seven days | 1 per 7 day | 1 per 7 day | 1 per 7 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 182 | frequency | every 2 days | 1 per 2 day | 1 per 2 day | 1 per 2 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 187 | cluster_frequency | events tend to cluster every seven to nine days | tend to cluster every 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 190 | cluster_frequency | clusters of brief absence episodes every 4 weeks | clusters brief absence 1 per 4 week | 1 per 4 week | 1 per 4 week |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 198 | frequency | every 4 weeks | 1 per 4 week | 1 per 4 week | 1 per 4 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 212 | frequency | every 3 - 4 weeks | every 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 218 | frequency | seizures every 3 weeks | 1 per 3 week | 1 per 3 week | 1 per 3 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 243 | frequency | every four months | 1 per 4 month | 1 per 4 month | 1 per 4 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 278 | frequency | multiple times in past week | multiple times in past week | no seizure frequency reference | multiple per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 280 |  | None | None | None | multiple per day |  |  | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'unknown_frequency', 'no_frequency_reference', 'last_event_only' or 'non_seizure_or_proxy' |
| 338 | frequency | many convulsions in past month | many convulsions in past month | no seizure frequency reference | multiple per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 409 | frequency | ≤ once per month | 1 per month | 1 per month | 1 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 419 | frequency | approximately twice per year | 2 per year | 2 per year | 2 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 446 | frequency | ≤ twice per week | 2 per week | 2 per week | 2 per week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 466 | frequency | 21 to 28 seizures per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 467 | frequency | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 531 | frequency | 12 to 30 per quarter | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 598 | frequency | 1 per eight months | 1 per 8 month | 1 per 8 month | 1 per 8 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 659 | frequency | seizures twice every 4 days | 1 per 4 day | 2 per 4 day | 2 per 4 day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 665 | frequency | twice every two weeks | 1 per 2 week | 2 per 2 week | 2 per 2 week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 678 | frequency | twice every 4 months | 1 per 4 month | 2 per 4 month | 2 per 4 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 694 | frequency | once a week | 1 week | 1 per week | 1 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 704 | frequency | twice a month | 2 month | 2 per month | 2 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 725 | frequency | daily | 1 per day | 1 per day | 1 per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 731 | frequency | daily | 1 per day | 1 per day | 1 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 743 | frequency | most shifts | most shifts | no seizure frequency reference | multiple per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 744 | frequency | brief absences occurring on most weekdays | brief absences occurring on most weekdays | no seizure frequency reference | multiple per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 763 | frequency | weekly | 1 per week | 1 per week | 1 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 790 | frequency | roughly once every seven to ten days | roughly 1 every 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 816 | frequency | monthly seizures | 1 per month | 1 per month | 1 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 849 | frequency | yearly seizures | 1 per year | 1 per year | 1 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 854 | frequency | roughly yearly | roughly 1 per year | 1 per year | 1 per year |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 869 | unknown_frequency | unknown | unknown | multiple per day | multiple per month | yes | yes | cluster_axis=vague_cluster; boundary_state=unknown_frequency |
| 891 | frequency | seizures every other day | 1 per 2 day | 1 per 2 day | 1 per 2 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 899 | frequency | seizures every other week | 1 per 2 week | 1 per 2 week | 1 per 2 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 959 | frequency | bimonthly on average | 1 per 2 month on average | 1 per 2 month | 1 per 2 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 960 | frequency | bimonthly seizures | 1 per 2 month | 1 per 2 month | 1 per 2 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 978 | frequency | every other month or so | 1 per 2 month or so | 1 per 2 month | 1 per 2 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 987 | frequency | bimonthly | 1 per 2 month | 1 per 2 month | 1 per 2 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1030 | frequency | one or three seizures last month | 1 or 3 last month | 1 per month | 1 to 3 per month |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 1046 | frequency | 3 or 5 seizures last month | 3 or 5 last month | no seizure frequency reference | 3 to 5 per month |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 1070 | frequency | three or four seizures last week | 3 or 4 last week | no seizure frequency reference | 3 to 4 per week |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 1094 | frequency | 3 to 5 seizures last week | 3 to 5 last week | no seizure frequency reference | 3 to 5 per week |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 1165 | seizure_free | no further episodes for the last six weeks | no further for last 6 week | no seizure frequency reference | 5 to 7 per 3 week |  | no | cluster_axis=vague_cluster; boundary_state=seizure_free_interval |
| 1171 | frequency | 7 to 9 focal onset seizures in three weeks | 7 to 9 focal onset in 3 week | 9 per 3 week | 7 to 9 per 3 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1207 | frequency | 21 to 28 epileptic spasms in three months | 21 to 28 epileptic spasms in 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1223 | frequency | 3 or 4 focal impaired awareness seizures | 3 or 4 focal impaired awareness | no seizure frequency reference | 3 to 4 per week |  | no | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 1249 | frequency | 2 or 4 focal impaired awareness seizures this week | 2 or 4 focal impaired awareness this week | 2 to 4 per week | 2 to 4 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1281 | frequency | 5 or 7 epileptic spasms this year | 5 or 7 epileptic spasms this year | 5 to 7 per 10 month | 5 to 7 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1317 | cluster_frequency | cluster of events over a single day | cluster over single day | unknown | unknown, multiple per cluster |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 1357 | frequency | 1 tonic-clonic seizures yesterday | 1 tonic-clonic yesterday | 1 per day | 1 per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1363 | frequency | three tonic-clonic seizures yesterday | 3 tonic-clonic yesterday | 1 per day | 3 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 1413 | frequency | nine events per month | 9 per month | 9 per month | 9 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1454 | frequency | one tonic-clonic and six petit mal in last week | 1 tonic-clonic and 6 petit mal in last week | 7 per week | 7 per week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 1486 | frequency | two focal epileptic spasms and one focal non-motor in last month | 2 focal epileptic spasms and 1 focal non-motor in last month | 2 per month | 3 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1573 | frequency | five focal cognitive and six focal non-motors in last week | 5 focal cognitive and 6 focal non-motors in last week | no seizure frequency reference | 11 per week |  | no | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 1591 | frequency | five focal onset seizures and six focal non-motors in last month | 5 focal onset and 6 focal non-motors in last month | 5 per month | 11 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1596 | frequency | five drop attacks and seven petit mal in last week | 5 drop and 7 petit mal in last week | 12 per week | 12 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1597 | frequency | five absence seizures and seven petit mal in last month | 5 absence and 7 petit mal in last month | 12 per month | 12 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1636 | frequency | two drop attacks and three petit mal in last month | 2 drop and 3 petit mal in last month | 5 per month | 5 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1640 | frequency | two absence seizures and three petit mal in last week | 2 absence and 3 petit mal in last week | 5 per week | 5 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1687 | frequency | several focal seizures last week | several focal last week | multiple per day | multiple per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1694 | cluster_frequency | three short episodes occurring on separate days | 3 short occurring on separate day | 3 per 2 week | 1 cluster per 2 week, 3 per cluster |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 1695 | seizure_free | no events have been recorded | no have been recorded | no seizure frequency reference | multiple per month |  | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 1706 | cluster_frequency | a cluster of short events on multiple days | cluster short on multiple day | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 1707 | cluster_frequency | a brief cluster of events occurring on multiple days within the past week | brief cluster occurring on multiple day within past week | unknown | multiple per week |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 1772 | frequency | two drop attacks and nine absence seizures in the past six months | 2 drop and 9 absence in past 6 month | 11 per 6 month | 11 per 6 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 1773 | frequency | two drop attacks and nine convulsions in the past three months | 2 drop and 9 convulsions in past 3 month | 11 per 3 month | 11 per 3 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1790 | frequency | six drop attacks and two epileptic spasms in the past four months | 6 drop and 2 epileptic spasms in past 4 month | 8 per 4 month | 8 per 4 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1794 | frequency | six drop attacks and two absence seizures in the past two months | 6 drop and 2 absence in past 2 month | 8 per 2 month | 8 per 2 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1866 | frequency | one drop attacks and seven absence seizures in the past two months | 1 drop and 7 absence in past 2 month | 8 per 2 month | 8 per 2 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1880 | frequency | one drop attacks and seven convulsions in the past two months | 1 drop and 7 convulsions in past 2 month | 8 per 2 month | 8 per 2 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 1887 | frequency | three drop attacks and one convulsion in the past three months | 3 drop and 1 convulsion in past 3 month | 4 per 3 month | 4 per 3 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1914 | frequency | two drop attacks and five tonic-clonic in the past three months | 2 drop and 5 tonic-clonic in past 3 month | 7 per 3 month | 7 per 3 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1922 | frequency | two drop attacks and five convulsions in the past three months | 2 drop and 5 convulsions in past 3 month | 7 per 3 month | 7 per 3 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1923 | frequency | two drop attacks and five epileptic spasms in the past six months | 2 drop and 5 epileptic spasms in past 6 month | 7 per 6 month | 7 per 6 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 1979 | frequency | three focal onset seizures and three focal automatisms in the past two months | 3 focal onset and 3 focal automatisms in past 2 month | 3 per 2 month | 6 per 2 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 1980 | frequency | three focal onset seizures and three focal epileptic spasms in the past three months | 3 focal onset and 3 focal epileptic spasms in past 3 month | 6 per 3 month | 6 per 3 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2023 | frequency | four absence seizures and one myoclonic this month | 4 absence and 1 myoclonic this month | no seizure frequency reference | 5 per month |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 2080 | unknown_frequency | unknown | unknown | multiple per day | multiple per month | yes | yes | cluster_axis=none; boundary_state=unknown_frequency |
| 2094 | frequency | several absence seizures in the past month | several absence in past month | multiple per day | multiple per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2114 | frequency | several myoclonic in the past month | several myoclonic in past month | no seizure frequency reference | multiple per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2149 | frequency | occasional tonic-clonic over last year | occasional tonic-clonic over last year | no seizure frequency reference | unknown |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2166 | frequency | frequent petit mal recently | frequent petit mal recently | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2228 | frequency | 3 or 5 seizures in the last two weeks | 3 or 5 in last 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2233 | frequency | about 6 or 7 seizures in the last two months | 6 or 7 in last 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2245 | frequency | about 7 to 8 seizures in the last three weeks | 7 to 8 in last 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2259 | frequency | about six or eight seizures in the last three months | 6 or 8 in last 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2354 | frequency | 6 to 7 myoclonic per week | 6 to 7 myoclonic per week | no seizure frequency reference | 6 to 7 per week |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 2366 | frequency | two or four seizures over the past year | 2 or 4 over past year | 2 to 4 per year | 2 to 4 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2369 | frequency | 3 to 4 seizures | 3 to 4 | 3 to 4 per month | 3 to 4 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2374 | frequency | 7 to 9 seizures over the past month | 7 to 9 over past month | 7 to 9 per month | 7 to 9 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2425 | frequency | six or eight petit mal over the past month | 6 or 8 petit mal over past month | 6 to 8 per month | 6 to 8 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2427 | frequency | 3 or 5 tonic-clonic over the past month | 3 or 5 tonic-clonic over past month | 3 to 5 per month | 3 to 5 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2435 | frequency | five to seven seizures during the last two weeks | 5 to 7 during last 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2437 | frequency | 2 to 3 seizures during the last two months | 2 to 3 during last 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2440 | frequency | five or seven seizures during the last two months | 5 or 7 during last 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2456 | frequency | six to seven seizures during the last two weeks | 6 to 7 during last 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2459 | frequency | seven to nine seizures during the last two weeks | 7 to 9 during last 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2487 | frequency | two to three seizures during the last three months | 2 to 3 during last 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2513 | frequency | 2 to 3 drop attacks during the last two weeks | 2 to 3 drop during last 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2541 | frequency | eight or nine drop attacks during the last two weeks | 8 or 9 drop during last 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2548 | frequency | five to six focal automatisms during the last two months | 5 to 6 focal automatisms during last 2 month | no seizure frequency reference | 5 to 6 per 2 month |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 2554 | frequency | 1 - 10 focal aware seizures during the last two months | 1 to 10 focal aware during last 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2558 | frequency | 3 to 4 focal impaired awareness seizures during the last two months | 3 to 4 focal impaired awareness during last 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2609 | frequency | once per night | 1 per day | 1 per day | 1 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2622 | frequency | seizures every night | every night | 1 per day | 1 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2628 | frequency | seizures every night | every night | 1 per day | 1 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2678 | frequency | tonic-clonic every night | tonic-clonic every night | 1 per day | 1 per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2681 | frequency | an absence seizure every night | absence every night | 1 per day | 1 per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2698 | frequency | myoclonic every other day | myoclonic 1 per 2 day | 1 per 2 day | 1 per 2 day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2731 | frequency | every other week | 1 per 2 week | 1 per 2 week | 1 per 2 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2740 | frequency | complex partial seizure monthly | complex partial seizure1 per month | 1 per month | 1 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2748 | frequency | a focal seizure monthly | focal seizure1 per month | 1 per month | 1 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2759 | frequency | monthly | 1 per month | 1 per month | 1 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2762 | frequency | monthly | 1 per month | 1 per month | 1 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2765 | frequency | a focal onset seizure monthly | focal onset seizure1 per month | 1 per month | 1 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2776 | frequency | weekly | 1 per week | 1 per week | 1 per week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2789 | frequency | convulsion weekly | convulsion1 per week | 1 per week | 1 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2812 | frequency | at least one drop attack daily | at least 1 drop attack1 per day | 1 per day | 1 per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2822 | frequency | daily | 1 per day | 1 per day | 1 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 2824 | frequency | tonic-clonic daily | tonic-clonic1 per day | 1 per day | 1 per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2877 | frequency | twice a year | 2 year | 2 per year | 2 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2887 | frequency | twice a week | 2 week | 2 per week | 2 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 2907 | seizure_free | Seizure-free since 27 March 2024 | seizure free for multiple year | seizure free for multiple year | seizure free for 6 month |  | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 2932 | seizure_free | seizure‑free since 29/09/2017 | ‑free since 29/09/2017 | no seizure frequency reference | seizure free for 9 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 2938 | seizure_free | Seizure-free since 13-Nov-2015 | seizure free for multiple year | seizure free for multiple year | seizure free for 8 month |  | yes | cluster_axis=vague_cluster; boundary_state=seizure_free_interval |
| 2965 | seizure_free | no confirmed events | no confirmed | no seizure frequency reference | seizure free for 16 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 2992 | seizure_free | no further events since that date | no further since that date | no seizure frequency reference | seizure free for 7 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3015 | seizure_free | no events over the last year | no over last year | no seizure frequency reference | seizure free for 12 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3048 | seizure_free | No events for 16 months | no for 16 month | no seizure frequency reference | seizure free for 16 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3058 | seizure_free | No events for twelve months | no for 12 month | no seizure frequency reference | seizure free for 12 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3082 | seizure_free | No events for 10 months | no for 10 month | no seizure frequency reference | seizure free for 10 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3095 | seizure_free | No events for twelve months | no for 12 month | no seizure frequency reference | seizure free for 12 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3113 | seizure_free | No events for fourteen months | no for fourteen month | no seizure frequency reference | seizure free for 14 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3118 | seizure_free | No seizures since last visit | no since last visit | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3137 | seizure_free | no definite seizure events | no definite | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 3224 | cluster_frequency | Monthly clusters, typically 6 to 7 seizures over 24 h | 1 per month clusters, typically 6 to 7 over 24 h | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 3242 | cluster_frequency | 2 clusters this month; each ≈five absences in the morning | 2 clusters this month; each ≈5 absences in morning | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster |  | yes | cluster_axis=cadence_and_burden; boundary_state=ordinary_frequency |
| 3261 | cluster_frequency | two clusters this month; each ≈four absences in the morning | 2 clusters this month; each ≈4 absences in morning | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 3262 | cluster_frequency | two clusters this month | 2 clusters this month | 2 cluster per month, multiple per cluster | 2 cluster per month, 5 per cluster |  | no | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 3281 | frequency | 8/30 this month | 8/30 this month | 8 per month | 8 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3297 | frequency | six/30 this month | 6/30 this month | 6 per month | 6 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 3325 | frequency | About three seizure days per week | 3 day per week | no seizure frequency reference | 3 per week |  | no | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 3356 | frequency | brief generalised tonic–clonic seizures occurring exclusively after nights of curtailed sleep, with no events reported when sleep has been adequate | brief generalised tonic–clonic occurring exclusively after nights curtailed sleep, with no reported when sleep has been adequate | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3371 | seizure_free | no events have occurred in the past eight weeks | no have occurred in past 8 week | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 3436 | cluster_frequency | Events tend to cluster shortly after early-morning arousal | tend to cluster shortly after early-morning arousal | unknown | unknown |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 3468 | cluster_frequency | Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free. | seizure free for multiple year | seizure free for multiple year | unknown |  | no | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 3469 | seizure_free | no events over the last six months | no over last 6 month | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 3482 | frequency | Seizures happen when perimenstrual only (days -3 to +3) | happen when perimenstrual only (day -3 to +3) | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3493 | cluster_frequency | most episodes falling from roughly three days before the period up to three days afterwards | most falling from roughly 3 day before period up to 3 day afterwards | no seizure frequency reference | unknown |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 3507 | unknown_frequency | unknown | unknown | unknown | unknown | yes | yes | cluster_axis=none; boundary_state=unknown_frequency |
| 3512 | unknown_frequency | unknown | unknown | unknown | unknown | yes | yes | cluster_axis=none; boundary_state=unknown_frequency |
| 3528 | frequency | no witnessed generalised tonic–clonic seizures since 2018 | no witnessed generalised tonic–clonic since 2018 | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3532 | unknown_frequency | unknown | unknown | unknown | unknown | yes | yes | cluster_axis=none; boundary_state=unknown_frequency |
| 3534 | seizure_free | no seizures for six months | no for 6 month | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 3600 | unknown_frequency | unknown | unknown | unknown | unknown | yes | yes | cluster_axis=none; boundary_state=unknown_frequency |
| 3623 | cluster_frequency | up to seven in bad weeks | up to 7 in bad week | 7 per week | 7 per week |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 3643 | cluster_frequency | clusters up to 7 in bad weeks | clusters up to 7 in bad week | 7 per week | 7 per week |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 3681 | frequency | nine/mo | 9 per month | 9 per month | 9 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3682 | frequency | six/mo | 6 per month | 6 per month | 6 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3710 | frequency | TC *5/wk | tc *5 per week | 5 per week | 5 per week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 3753 | frequency | daily | 1 per day | multiple per day | 1 per day |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 3766 | frequency | TC X8/yr | tc x8 per year | 8 per year | 8 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3774 | frequency | nine/yr | 9 per year | 9 per year | 9 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3791 | frequency | TC ×ten/yr | tc ×10 per year | 10 per year | 10 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3801 | frequency | sz ×nine/mo | ×9 per month | 9 per month | 9 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3806 | frequency | six/mo | 6 per month | 6 per month | 6 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3827 | frequency | average of sz X7/mo | average x7 per month | 7 per month | 7 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 3846 | frequency | sz X2/d | x2 per day | 2 per day | 2 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 3849 | frequency | sz x3/d | x3 per day | 3 per day | 3 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 3889 | frequency | sz xeight/yr | xeight/year | no seizure frequency reference | 8 per year |  | no | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 3892 | frequency | sz x3/yr | x3 per year | 3 per year | 3 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3940 | frequency | sz xfour/wk | xfour/week | no seizure frequency reference | 4 per week |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 3949 | frequency | sz Xfour/wk | xfour/week | no seizure frequency reference | 4 per week |  | no | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 3988 | frequency | several times per week | several per week | multiple per week | multiple per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3995 | frequency | abs monthly | abs1 per month | 1 per month | 1 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 3999 | frequency | abs monthly | abs1 per month | 1 per month | 1 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 4022 | frequency | 8 monthly | 8 per month | 8 per month | 8 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 4026 | frequency | roughly one brief absence episode in a typical month | roughly 1 brief absence in typical month | no seizure frequency reference | 1 per month |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 4092 | frequency | qtwo - threewk | qtwo - threewk | 1 per 2 to 3 week | 1 per 2 to 3 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4100 | frequency | q2 - 3wk | q2 to 3wk | 1 per 2 to 3 week | 1 per 2 to 3 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4110 | frequency | q1 - 2d | q1 to 2d | 1 per 1 to 2 day | 1 per 1 to 2 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4116 | frequency | qone to twod on workdays | qone to twod on workdays | 1 per 1 to 2 day | 1 per 1 to 2 day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 4173 | frequency | roughly once in a fortnight | roughly 1 in fortnight | no seizure frequency reference | 1 per 2 week |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 4243 | frequency | every two to three weeks | every 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 4258 | frequency | four events per week | 4 per week | 4 per week | 4 per week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4337 | frequency | Seizure events on 06-03, 06-13, 09-23 | on 06 to 03, 06 to 13, 09 to 23 | no seizure frequency reference | 3 per 3 month |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 4345 | frequency | four seizures in July | 4 in july | no seizure frequency reference | 4 per month |  | no | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 4368 | frequency | Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24 | on 03 to 07, 03 to 27, 05 to 15, 05 to 19, 05 to 24 | no seizure frequency reference | 5 per 2 month |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 4402 | frequency | Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1 | jan x1, feb x0, mar x1, apr x2, may x1, jun x1, jul x1 | 7 per 7 month | 7 per 7 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4410 | frequency | May x1, Jun x1, Jul x0, Aug x1, Sep x0, Oct x1, Nov x0 | may x1, jun x1, jul x0, aug x1, sep x0, oct x1, nov x0 | 4 per 7 month | 4 per 7 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4478 | frequency | nineteen episode of status epilepticus in the past week | nineteen status epilepticus in past week | no seizure frequency reference | 19 per week |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 4480 | frequency | three - five episode of status epilepticus in the past week | 3 to 5 status epilepticus in past week | no seizure frequency reference | 3 to 5 per week |  | no | cluster_axis=none; boundary_state=ordinary_frequency |
| 4496 | frequency | seven to eight absence seizures this quarter | 7 to 8 absence this quarter | 7 to 8 per 3 month | 7 to 8 per 3 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 4562 | frequency | median inter-seizure interval ≈ six weeks | median inter- interval ≈ 6 week | 1 per 6 week | 1 per 6 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4563 | frequency | Median inter-seizure interval ≈ four months | median inter- interval ≈ 4 month | 1 per 4 month | 1 per 4 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4574 | frequency | Median inter-seizure interval ≈ four weeks | median inter- interval ≈ 4 week | 1 per 4 week | 1 per 4 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4592 | frequency | median inter-seizure interval ≈ two months | median inter- interval ≈ 2 month | 1 per 2 month | 1 per 2 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 4597 | frequency | Median inter-seizure interval ≈ three weeks | median inter- interval ≈ 3 week | 1 per 3 week | 1 per 3 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4624 | frequency | intervals ranging three - four days between focal aware seizures | intervals ranging 3 to 4 day between focal aware | 1 per 3 to 4 day | 1 per 3 to 4 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4631 | frequency | intervals ranging 14 - 21 days | intervals ranging 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4690 | unknown_frequency | unknown | unknown | unknown | multiple per day | yes | yes | cluster_axis=none; boundary_state=unknown_frequency |
| 4694 | frequency | ~9/h | ~9/h | no seizure frequency reference | multiple per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4700 | frequency | ~4/h | ~4/h | no seizure frequency reference | multiple per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4709 | frequency | frequent on EEG (~6/h) | frequent on eeg (~6/h) | no seizure frequency reference | multiple per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4731 | frequency | seizures happen rare | happen rare | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4732 | cluster_frequency | seizures happen occasional, often clustering around travel days or after disrupted sleep | happen occasional, often clustering travel day or after disrupted sleep | unknown | unknown |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 4771 | frequency | increased seizure activity | increased activity | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 4839 | seizure_free | no recorded events or auras since | no recorded or auras since | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 4842 | seizure_free | not experienced any seizures | not experienced any | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 4910 | seizure_free | free of seizures for 2 year | free for 2 year | no seizure frequency reference | seizure free for 2 year |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 4919 | seizure_free | Free of seizures for 2 year | free for 2 year | no seizure frequency reference | seizure free for 2 year |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 4926 | seizure_free | Free of seizures for one year | free for 1 year | no seizure frequency reference | seizure free for 1 year |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 4951 | seizure_free | no events for many months | no for many month | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 4956 | seizure_free | free of events for the past seven months | free for past 7 month | no seizure frequency reference | seizure free for 7 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 4992 | seizure_free | Seizure-free interval since 12-Sep-2018 | seizure free for multiple year | seizure free for multiple year | seizure free for 11 month |  | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 4994 | seizure_free | seizure-free interval since 25/06/2021 | seizure free for multiple year | seizure free for multiple year | seizure free for 6 month |  | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 5040 | seizure_free | no further episodes suggestive of seizures | no further suggestive | no seizure frequency reference | seizure free for 6 months |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5082 | seizure_free | sustained period without any recurrence of her typical events | sustained period without any recurrence her typical | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5092 | seizure_free | No clinical seizures observed | no clinical observed | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5110 | seizure_free | no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represent clinical seizures | no witnessed convulsive recorded by him or observers, nor any he felt were likely to represent clinical | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5121 | seizure_free | no events suggestive of seizures | no suggestive | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5136 | seizure_free | No recurrence | no recurrence | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5141 | seizure_free | no further events suggestive of seizures | no further suggestive | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5197 | seizure_free | seizure-free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month |  | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 5210 | seizure_free | Seizure freedom continues | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes | cluster_axis=none; boundary_state=seizure_free_interval |
| 5221 | seizure_free | no seizures for six months | no for 6 month | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5248 | seizure_free | complete seizure control | complete control | no seizure frequency reference | seizure free for multiple year |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5331 | seizure_free | no events, warnings, or episodes suggestive of seizures over the past 12 months | no, warnings, or suggestive over past 12 month | no seizure frequency reference | seizure free for 12 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5345 | seizure_free | free of events for several months | free for several month | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5351 | seizure_free | no events, warnings, or auras for over 18 months | no, warnings, or auras for over 18 month | no seizure frequency reference | seizure free for 18 month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5379 | seizure_free | no recent epileptic seizures | no recent epileptic | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5406 | seizure_free | no definite epileptic events documented in this interval | no definite epileptic documented in this interval | no seizure frequency reference | seizure free for multiple month |  | no | cluster_axis=none; boundary_state=seizure_free_interval |
| 5476 | frequency | sporadic epileptic spasms this year | sporadic epileptic spasms this year | no seizure frequency reference | unknown |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 5490 | unknown_frequency | unknown | unknown | unknown | unknown | yes | yes | cluster_axis=none; boundary_state=unknown_frequency |
| 5491 | unknown_frequency | unknown | unknown | unknown | unknown | yes | yes | cluster_axis=none; boundary_state=unknown_frequency |
| 5504 | frequency | Sporadic jerks this year | sporadic jerks this year | no seizure frequency reference | unknown |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 5507 | cluster_frequency | scattered sudden falls over the past months, clustered around busy evening service | scattered sudden falls over past month, clustered busy evening service | unknown | unknown |  | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 5528 | frequency | single very brief event last month | single very brief last month | 1 per month | 1 per month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 5534 | frequency | very infrequent | very infrequent | no seizure frequency reference | 1 per multiple month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 5551 | frequency | several episodes per day | several per day | multiple per day | multiple per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 5567 | frequency | Several episodes per week | several per week | multiple per week | multiple per week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 5584 | frequency | several episodes per week | several per week | multiple per week | multiple per week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
