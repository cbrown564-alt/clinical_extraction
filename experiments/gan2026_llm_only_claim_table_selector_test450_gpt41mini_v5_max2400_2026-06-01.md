# Gan 2026 LLM-Only Claim Table Selector V5

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `test` split, `gan2026_split_v1`, 240 rows.
Escalation reason: Frozen test generalization audit after validation250 v5; candidate, prompt, model, scorer, split manifest, and repair layers fixed before test run. Inspect aggregate and predeclared scoring layers only; do not tune from test rows. Resumed from partial 150-row artifact by reusing saved raw outputs.

## Model And Prompt Metadata

- Pipeline: `gan2026_llm_only_claim_table_selector_v5`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only direct-labeler claim extractor and final query selector
- Prompt/program version: `gan2026_llm_only_claim_table_selector_v5`
- Temperature: `0.0`
- Max tokens: `2400`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `150`
- Reuse source: `experiments/gan2026_llm_only_claim_table_selector_test450_gpt41mini_v5_max2400_2026-06-01.jsonl`
- Optimizer: none
- Prompt policy taxonomy: `sct_v5.schema.scalar_enum_output`, `sct_v5.schema.strict_json_object`, `sct_v5.evidence.exact_substring`, `sct_v5.gan_label.parser_ready_surface`, `sct_v5.gan_label.interval_preservation`, `sct_v5.gan_label.cluster_dual_axis`, `sct_v5.schema.cluster_axis_state`, `sct_v5.selection.current_burden_precedence`, `sct_v5.selection.add_same_window_counts`, `sct_v5.boundary.unknown_no_reference_seizure_free`, `sct_v5.schema.boundary_state`, `sct_v5.exclusion.proxy_or_conditional_frequency`, `sct_v5.gan_label.compact_interval_notation`, `sct_v5.gan_label.maximum_burden`, `sct_v5.selection.constrained_selector`
- Required ablations before 25/50/250 ladder runs: `raw_model_claim_table`, `strict_schema_repair`, `constrained_selector_state`, `clean_scorer_facing_policy`
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `0d4770d`
- Working tree note: `clean`
- JSONL artifact: `experiments/gan2026_llm_only_claim_table_selector_test450_gpt41mini_v5_max2400_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 240 / 240
- Call failures: 0
- Parse/schema/label issues: 0
- Exact claim evidence substrings: 600 / 625
- Exact selected final evidence substrings: 229 / 240
- raw final-query score: Purist 0.8125 (195 / 240), Pragmatic 0.8125 (195 / 240)
- Strict-format score: Purist 0.8167 (196 / 240), Pragmatic 0.8167 (196 / 240)
- Frozen clean scorer-facing score: Purist 0.8208 (197 / 240), Pragmatic 0.8208 (197 / 240)
- Rows changed by downstream repair layers: 38

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 11 |
| claim_extraction | 23 |
| temporality_conflict | 4 |
| final_query | 11 |
| parse_schema | 0 |
| scorer_format | 13 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 51 | claim evidence not exact (c3: They report that clusters tend to occur on workdays, often mid-afternoon.) |  |  |
| 892 | claim evidence not exact (c2: Over the past two months he reports ... generalised tonic–clonic seizures roughly twice per fortnight); selected evidence not exact (Over the past two months he reports ... generalised tonic–clonic seizures roughly twice per fortnight) |  |  |
| 1378 |  | unparsable_label: 1 per month, 4 per month (Unparsable label (raw: '1 per month, 4 per month' / normalized: '1 per month, 4 per month')) |  |
| 1705 |  | unparsable_label: 1 cluster per month (Unparsable cluster label: '1 cluster per month') |  |
| 1868 | claim evidence not exact (c2: Over the past two months he describes ... seven tonic-clonic in the past two months) |  |  |
| 1883 | claim evidence not exact (c2: over the past three months he reports ... one petit mal in the past three months) |  |  |
| 1889 | claim evidence not exact (c2: over the past six months, records ... one petit mal in the past six months) |  |  |
| 1934 | claim evidence not exact (c1: she reports that, over the past two months, she has experienced two drop attacks and five myoclonic in the past two months); selected evidence not exact (she reports that, over the past two months, she has experienced two drop attacks and five myoclonic in the past two months) |  |  |
| 1938 | claim evidence not exact (c2: Over the past four months he reports ... four epileptic spasms in the past four months) |  |  |
| 2262 | claim evidence not exact (c1: they report that over the past three weeks she has experienced about seven to nine seizures in the last three weeks); selected evidence not exact (they report that over the past three weeks she has experienced about seven to nine seizures in the last three weeks) |  |  |
| 2596 |  | unparsable_label: 2 per night (Unparsable label (raw: '2 per night' / normalized: '2 per night')) |  |
| 2597 |  | unparsable_label: 1 cluster per night, 2 per night (Unparsable cluster label: '1 cluster per night, 2 per night') |  |
| 3340 | claim evidence not exact (c1: he reports ongoing events with a pattern of fluctuation but, on balance, about 2 - 3 seizure days per month); selected evidence not exact (he reports ongoing events with a pattern of fluctuation but, on balance, about 2 - 3 seizure days per month) |  |  |
| 3514 | claim evidence not exact (c3: No focal warning symptoms) |  |  |
| 3747 |  | unparsable_label: 1 cluster per 5 to 7 day, 3 per day (Unparsable cluster label: '1 cluster per 5 to 7 day, 3 per day') |  |
| 3888 | claim evidence not exact (c1: Over the past 12 months, the seizure frequency has settled at sz Øeight/yr); selected evidence not exact (Over the past 12 months, the seizure frequency has settled at sz Øeight/yr) |  |  |
| 4679 |  | unparsable_label: 1 per hour (Unparsable label (raw: '1 per hour' / normalized: '1 per hour')) |  |
| 4809 |  | unparsable_label: 1 cluster per illness period (Unparsable cluster label: '1 cluster per illness period') |  |
| 5540 | claim evidence not exact (c2: On balance, given the near-absent recent activity (·virtually no events apart from the brief spell), I have not altered therapy today.) |  |  |
| 5555 |  | unparsable_label: several per week (Unparsable label (raw: 'several per week' / normalized: 'several per week')) |  |
| 5684 |  | unparsable_label: 1 cluster per 1 to 2 day (Unparsable cluster label: '1 cluster per 1 to 2 day') |  |
| 6025 |  | unparsable_label: conditional_or_window_limited (Unparsable label (raw: 'conditional_or_window_limited' / normalized: 'conditional_or_window_limited')) |  |
| 6387 |  | unparsable_label: 2 per travel event (Unparsable label (raw: '2 per travel event' / normalized: '2 per travel event')) |  |
| 6909 |  | unparsable_label: 1 per 2 to 3 week, 3 per 3 month (Unparsable label (raw: '1 per 2 to 3 week, 3 per 3 month' / normalized: '1 per 2 to 3 week, 3 per 3 month')) |  |
| 6979 | claim evidence not exact (c1: she has not kept a seizure diary recently and could not confidently recall the timing of her most recent episode, stating that it "might have been a while" but she wasn’t certain); selected evidence not exact (she has not kept a seizure diary recently and could not confidently recall the timing of her most recent episode, stating that it "might have been a while" but she wasn’t certain) |  |  |
| 7005 | claim evidence not exact (c1: he believes there were two brief episodes in the last six months characterised by a sudden blank spell with loss of awareness for under a minute, c2: No emergency call activations logged on the device); selected evidence not exact (he believes there were two brief episodes in the last six months characterised by a sudden blank spell with loss of awareness for under a minute) |  |  |
| 7328 |  | unparsable_label: occasional (Unparsable label (raw: 'occasional' / normalized: 'occasional')) |  |
| 7386 | claim evidence not exact (c2: Over the past eight weeks, the patient reports ... two focal seizures with secondary impairment of awareness) |  |  |
| 7783 | claim evidence not exact (c1: he reports that over the past three months there have been no witnessed events suggestive of attacks); selected evidence not exact (he reports that over the past three months there have been no witnessed events suggestive of attacks) |  |  |
| 7892 | claim evidence not exact (c2: the carer keeps a diary and has noted several brief episodes of uncertainty about awareness that resolved spontaneously without escalation) |  |  |
| 8135 | claim evidence not exact (c4: From the app logs and her diary: ... Jun: dose increase 07/06, thereafter 0; Jul: 0; Aug: 0; Sep: 0.) |  |  |
| 8540 | claim evidence not exact (c1: he has been keeping a seizure diary and, over this interval, there have been no recorded or witnessed events suggestive of epileptic activity, c3: he has not described any blackouts, tongue biting, or unwitnessed nocturnal events); selected evidence not exact (he has been keeping a seizure diary and, over this interval, there have been no recorded or witnessed events suggestive of epileptic activity) |  |  |
| 8624 | claim evidence not exact (c3: No auras, blackouts or witnessed episodes since) |  |  |
| 8813 | claim evidence not exact (c1: the device dashboard from the past 90 days indicates no detected convulsive activity, summarised by the platform as “0% seizure activity recorded,” and his partner’s diary entries show no witnessed episodes in that period); selected evidence not exact (the device dashboard from the past 90 days indicates no detected convulsive activity, summarised by the platform as “0% seizure activity recorded,” and his partner’s diary entries show no witnessed episodes in that period) |  |  |
| 8979 | claim evidence not exact (c1: seizure control has been stable since resection with no clinical events reported in the community, consistent with a sustained post-surgical absence of seizures) |  |  |
| 9212 | claim evidence not exact (c1: he reports that since our last contact three months ago there have not been any episodes seen by others or described by himself suggestive of seizures); selected evidence not exact (he reports that since our last contact three months ago there have not been any episodes seen by others or described by himself suggestive of seizures) |  |  |

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 31 | 1 per day | 1 per day | 1 per day | 4 per day | yes | yes |  |
| 51 | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes | claim_extraction |
| 61 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 115 | 7 to 8 per month | 7 to 8 per month | 7 to 8 per month | 7 to 8 per month | yes | yes |  |
| 136 | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | yes | yes |  |
| 174 | 1 per 1 to 3 day | 1 per 1 to 3 day | 1 per 1 to 3 day | 1 per 1 to 3 day | yes | yes |  |
| 176 | 1 per 6 to 7 day | 1 per 6 to 7 day | 1 per 6 to 7 day | 1 per 6 to 7 day | yes | yes |  |
| 234 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 240 | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | yes |  |
| 364 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | 1 per week | yes | yes |  |
| 493 | 11 per month | 11 per month | 11 per month | 11 per month | yes | yes |  |
| 503 | 11 to 28 per 3 month | 11 to 28 per 3 month | 11 to 28 per 3 month | 11 to 28 per 3 month | yes | yes | segmentation_sectioning |
| 538 | 1 per 4 day | 1 per 4 day | 1 per 4 day | 1 per 4 day | yes | yes |  |
| 610 | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | yes |  |
| 632 | 1 per 1 to 2 month | 1 per 1 to 2 month | 1 per 1 to 2 month | 1 per 1 to 2 month | yes | yes |  |
| 666 | 2 per 2 to 3 month | 2 per 2 to 3 month | 2 per 2 to 3 month | 2 per 2 to 3 month | yes | yes |  |
| 685 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 714 | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 722 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 735 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 739 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 748 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | 1 per 2 month | no | no |  |
| 750 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 803 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 804 | 2 cluster per month, 2 per cluster | 2 cluster per month, 2 per cluster | 2 cluster per month, 2 per cluster | 1 per month | no | no | segmentation_sectioning,temporality_conflict |
| 824 | 1 per 1 month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 836 | 1 per 12 month | 1 per 12 month | 1 per 12 month | 1 per year | yes | yes |  |
| 841 | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 892 | 2 per 2 week | 2 per 2 week | 2 per 2 week | 1 per 2 day | yes | yes | claim_extraction,final_query |
| 934 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 938 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 1005 | 1 per 3 month | 1 per 3 month | 1 per 3 month | multiple per 3 month | no | no |  |
| 1017 | 1 per 3 month | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 1060 | 6 to 7 per 1 month | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | yes | yes |  |
| 1182 | 6 to 14 per 3 month | 6 to 14 per 3 month | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | yes |  |
| 1184 | 6 to 14 per 3 month | 6 to 14 per 3 month | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | yes | temporality_conflict |
| 1250 | 2 to 4 per 1 week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 1289 | 5 to 6 per year | 5 to 6 per year | 5 to 6 per year | 5 to 6 per year | yes | yes |  |
| 1290 | 8 to 9 per year | 8 to 9 per year | 8 to 9 per year | 8 to 9 per year | yes | yes | segmentation_sectioning |
| 1326 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 1378 | 1 per month, 4 per month | 1 per month, 4 per month | 1 per month, 4 per month | 5 per month |  |  | scorer_format |
| 1422 | 9 per 1 week | 9 per week | 9 per week | 9 per week | yes | yes |  |
| 1433 | 4 per 1 month | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 1460 | 7 per 1 month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 1497 | 3 per 1 month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 1511 | 7 per 1 month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 1534 | 9 per 1 month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 1624 | 12 per 1 week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1629 | 12 per 1 month | 12 per month | 12 per month | 12 per month | yes | yes |  |
| 1633 | 12 per 1 week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1656 | 5 per 1 month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1683 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 1705 | 1 cluster per month | 1 cluster per month | 1 per month | 1 cluster per month, multiple per cluster |  | no | scorer_format |
| 1722 | 3 per 2 month | 3 per 2 month | 3 per 2 month | 3 per 2 month | yes | yes |  |
| 1736 | 4 per 6 month | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes |  |
| 1812 | 12 per 3 month | 12 per 3 month | 12 per 3 month | 12 per 3 month | yes | yes |  |
| 1868 | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes | claim_extraction |
| 1883 | 4 per 3 month | 4 per 3 month | 4 per 3 month | 4 per 3 month | yes | yes | claim_extraction |
| 1889 | 4 per 6 month | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes | claim_extraction |
| 1898 | 4 per 6 month | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes |  |
| 1911 | 7 per 2 month | 7 per 2 month | 7 per 2 month | 7 per 2 month | yes | yes |  |
| 1934 | 7 per 2 month | 7 per 2 month | 7 per 2 month | 7 per 2 month | yes | yes | claim_extraction,final_query |
| 1938 | 1 to 5 per 4 month | 1 to 5 per 4 month | 1 to 5 per 4 month | 5 per 4 month | no | no | claim_extraction |
| 2071 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 2112 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 2135 | unknown | unknown | unknown | unknown | yes | yes |  |
| 2220 | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | yes |  |
| 2226 | 3 to 10 per 2 week | 3 to 10 per 2 week | 3 to 10 per 2 week | 3 to 10 per 2 week | yes | yes |  |
| 2246 | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | yes |  |
| 2262 | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | yes | claim_extraction,final_query |
| 2306 | 8 to 9 per month | 8 to 9 per month | 8 to 9 per month | 8 to 9 per month | yes | yes |  |
| 2311 | 5 to 7 per month | 5 to 7 per month | 5 to 7 per month | 5 to 7 per month | yes | yes |  |
| 2356 | 6 to 7 per 1 week | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | yes | yes |  |
| 2404 | 6 to 7 per 1 month | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | yes | yes |  |
| 2486 | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | yes |  |
| 2543 | 2 to 4 per 2 week | 2 to 4 per 2 week | 2 to 4 per 2 week | 2 to 4 per 2 week | yes | yes |  |
| 2564 | 3 to 5 per 2 month | 3 to 5 per 2 month | 3 to 5 per 2 month | 3 to 5 per 2 month | yes | yes |  |
| 2596 | 2 per night | 2 per day | 2 per day | 2 per day |  | yes | scorer_format |
| 2597 | 1 cluster per night, 2 per night | 1 cluster per day, 2 per day | 1 cluster per day, 2 per day | 2 per day |  |  | scorer_format |
| 2652 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2684 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2725 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 2749 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2781 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2795 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2854 | 2 per month | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 2879 | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 2978 | 1 cluster per month, 3 to 4 per cluster | 1 cluster per month, 3 to 4 per cluster | 1 cluster per month, 3 to 4 per cluster | seizure free for 9 month | no | no | temporality_conflict |
| 3054 | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 3102 | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 3214 | 1 cluster per month, 5 to 7 per cluster | 1 cluster per month, 5 to 7 per cluster | 1 cluster per month, 5 to 7 per cluster | 1 cluster per month, 5 to 7 per cluster | yes | yes |  |
| 3225 | 1 cluster per month, 3 to 10 per cluster | 1 cluster per month, 3 to 10 per cluster | 1 cluster per month, 3 to 10 per cluster | 1 cluster per month, 3 to 10 per cluster | yes | yes |  |
| 3237 | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | yes | yes |  |
| 3246 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | yes |  |
| 3291 | 9 per 30 day | 9 per 30 day | 9 per 30 day | 9 per month | yes | yes |  |
| 3293 | 8 per 30 day | 8 per 30 day | 8 per 30 day | 8 per month | yes | yes |  |
| 3300 | 9 per 30 day | 9 per 30 day | 9 per 30 day | 9 per month | yes | yes |  |
| 3327 | 5 to 6 per 1 year | 5 to 6 per year | 5 to 6 per year | 5 to 6 per year | yes | yes |  |
| 3329 | 2 to 3 per day | 2 to 3 per day | 2 to 3 per day | 2 to 3 per day | yes | yes |  |
| 3340 | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | yes | yes | claim_extraction,final_query |
| 3353 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3355 | 2 per 6 month | 2 per 6 month | 2 per 6 month | 1 per 3 month | yes | yes |  |
| 3407 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 3452 | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | yes | yes |  |
| 3514 | unknown | unknown | unknown | unknown | yes | yes | claim_extraction |
| 3630 | 7 per week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 3638 | 1 cluster per week, 3 per cluster | 1 cluster per week, 3 per cluster | 1 cluster per week, 3 per cluster | 3 per week | yes | yes |  |
| 3675 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 3706 | 6 per week | 6 per week | 6 per week | 6 per week | yes | yes |  |
| 3747 | 1 cluster per 5 to 7 day, 3 per day | 1 cluster per 5 to 7 day, 3 per day | 1 cluster per 5 to 7 day, 3 per day | 3 per day |  |  | scorer_format |
| 3831 | 7 per month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 3864 | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes | segmentation_sectioning |
| 3867 | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 3888 | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes | claim_extraction,final_query |
| 3906 | 4 per year | 4 per year | 4 per year | 4 per year | yes | yes |  |
| 3918 | 9 per week | 9 per week | 9 per week | 9 per week | yes | yes |  |
| 3934 | 9 per week | 9 per week | 9 per week | 9 per week | yes | yes | segmentation_sectioning |
| 4003 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4004 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4073 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4076 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4197 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 4217 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 4239 | unknown | unknown | unknown | unknown | yes | yes |  |
| 4342 | 1 per month | 1 per month | 1 per month | 5 per 3 month | no | no |  |
| 4352 | 5 per 3 month | 5 per 3 month | 5 per 3 month | 5 per 3 month | yes | yes |  |
| 4424 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | 3 per 6 month | no | no | segmentation_sectioning |
| 4679 | 1 per hour | 1 per hour | 1 per hour | multiple per day |  |  | scorer_format |
| 4707 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 4809 | 1 cluster per illness period | 1 cluster per illness period | 1 cluster per illness period | unknown |  |  | scorer_format |
| 4831 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 4892 | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | yes | yes |  |
| 4903 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 4967 | unknown | unknown | unknown | seizure free for multiple month | no | no |  |
| 4996 | seizure free for 1 year 4 month | seizure free for 1 year | seizure free for 1 year | seizure free for 16 month | yes | yes |  |
| 5088 | seizure free for recent months | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5174 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5213 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5385 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 1 year | no | no |  |
| 5395 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 6 month | no | no |  |
| 5505 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5527 | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 5540 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 4 to 5 month | no | no | claim_extraction |
| 5555 | several per week | several per week | multiple per week | multiple per week |  | yes | scorer_format |
| 5627 | 1 per 5 day | 1 per 5 day | 1 per 5 day | 1 per 5 day | yes | yes |  |
| 5653 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 5684 | 1 cluster per 1 to 2 day | 1 cluster per 1 to 2 day | 1 per 1 to 2 day | unknown |  | no | scorer_format |
| 5708 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5764 | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 5766 | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | multiple per week | no | no |  |
| 5976 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6025 | conditional_or_window_limited | conditional_or_window_limited | conditional_or_window_limited | unknown |  |  | scorer_format |
| 6028 | unknown | unknown | unknown | 1 per 3 months | no | no |  |
| 6063 | 3 per 2 week | 3 per 2 week | 3 per 2 week | unknown | no | no | segmentation_sectioning |
| 6073 | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 weeks | yes | yes |  |
| 6164 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6216 | 5 per 6 week | 5 per 6 week | 5 per 6 week | 4 per 6 week | yes | yes |  |
| 6252 | 2 to 4 per month | 2 to 4 per month | 2 to 4 per month | 2 to 4 per month | yes | yes |  |
| 6288 | 2 per 10 week | 2 per 10 week | 2 per 10 week | 2 per 10 week | yes | yes |  |
| 6296 | 3 per 4 month | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 6303 | unknown | unknown | unknown | unknown | yes | yes | segmentation_sectioning |
| 6330 | 2 per 3 month | 2 per 3 month | 2 per 3 month | multiple per month | no | no |  |
| 6365 | 1 to 2 per day | 1 to 2 per day | 1 to 2 per day | unknown, 1 to 2 per cluster | no | no |  |
| 6380 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6387 | 2 per travel event | 2 per travel | 2 per travel | unknown |  |  | scorer_format |
| 6408 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6592 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6661 | 3 per 6 week | 3 per 6 week | 3 per 6 week | 0.5 per week | yes | yes |  |
| 6763 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes | segmentation_sectioning |
| 6775 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | 1 per 5 month | no | no |  |
| 6787 | 8 per 6 week | 8 per 6 week | 8 per 6 week | 8 per 6 week | yes | yes |  |
| 6909 | 1 per 2 to 3 week, 3 per 3 month | 1 per 2 to 3 week, 3 per 3 month | 1 per 2 to 3 week, 3 per 3 month | 1 per 2 to 3 weeks |  |  | scorer_format |
| 6929 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 6930 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6976 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6979 | unknown | unknown | unknown | unknown | yes | yes | claim_extraction,final_query |
| 6986 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7005 | 2 per 6 month | 2 per 6 month | 2 per 6 month | 2 per 6 month | yes | yes | claim_extraction,final_query |
| 7047 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7061 | unknown | unknown | unknown | 2 per 6 week | no | no |  |
| 7232 | 1 per 6 to 8 day | 1 per 6 to 8 day | 1 per 6 to 8 day | 6 to 8 cluster per month, multiple per cluster | yes | yes |  |
| 7280 | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 7318 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 7327 | 2 per 4 month | 2 per 4 month | 2 per 4 month | 2 per 4 months | yes | yes |  |
| 7328 | occasional | occasional | occasional | unknown |  |  | scorer_format |
| 7341 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7386 | 5 to 7 per 8 week | 5 to 7 per 8 week | 5 to 7 per 8 week | 7 per 8 week | yes | yes | claim_extraction |
| 7393 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | unknown | no | no |  |
| 7405 | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per multiple months | no | no |  |
| 7431 | 2 per 8 week | 2 per 8 week | 2 per 8 week | 1 per month | yes | yes |  |
| 7670 | 1 per day | 1 per day | 1 per day | multiple per week | no | no |  |
| 7688 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 1 year | no | no |  |
| 7708 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 7712 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | 2 per 3 month | no | no |  |
| 7719 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | seizure free for multiple month | yes | yes |  |
| 7783 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes | claim_extraction,final_query |
| 7816 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | seizure free for multiple month | yes | yes |  |
| 7863 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | seizure free for multiple month | yes | yes |  |
| 7884 | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for multiple month | yes | yes | segmentation_sectioning |
| 7892 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | seizure free for multiple month | yes | yes | claim_extraction |
| 7935 | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | seizure free for multiple month | no | no |  |
| 7958 | seizure free for 3 year | seizure free for 3 year | seizure free for 3 year | seizure free for multiple year | yes | yes |  |
| 7987 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7993 | 2 to 3 per 2 day | 2 to 3 per 2 day | 2 to 3 per 2 day | unknown, 2 to 3 per cluster | no | no |  |
| 8109 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 8116 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 8127 | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 8135 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes | claim_extraction |
| 8169 | seizure free for several month | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8221 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 8222 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 8244 | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for multiple month | yes | yes |  |
| 8286 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 8342 | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | yes | yes |  |
| 8346 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8423 | seizure free for 10 week | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8432 | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | yes | segmentation_sectioning |
| 8488 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8540 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes | claim_extraction,final_query |
| 8624 | seizure free for 13 month | seizure free for 13 month | seizure free for 13 month | seizure free for 13 month | yes | yes | claim_extraction |
| 8645 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 8723 | seizure free for several week | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8790 | seizure free for 8 week | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8791 | seizure free for 6 week | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8799 | seizure free | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 8813 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes | claim_extraction,final_query |
| 8852 | seizure free for 8 month | seizure free for 8 month | seizure free for 8 month | seizure free for 8 month | yes | yes |  |
| 8858 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8954 | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | seizure free for 8 month | yes | yes |  |
| 8957 | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for 8 month | yes | yes |  |
| 8979 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes | claim_extraction |
| 9014 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 11 month | yes | yes | temporality_conflict |
| 9065 | seizure free for 1 year 1 month | seizure free for 1 year | seizure free for 1 year | seizure free for 13 month | yes | yes |  |
| 9109 | unknown | unknown | unknown | unknown | yes | yes |  |
| 9114 | 1 per 4 to 6 week | 1 per 4 to 6 week | 1 per 4 to 6 week | 1 per 4 to 6 week | yes | yes |  |
| 9147 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 9179 | seizure free for 1 per 2 month | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9189 | seizure free for an extended interval | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9202 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 9212 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 3 months | no | no | claim_extraction,final_query |
