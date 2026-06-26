# Gan 2026 Qwen v0.6 Repairfix Same-Raw Attribution

Date: 2026-06-21

Scope: validation development attribution over the completed Qwen v0.6 validation750 raw outputs. This is a no-call replay and a hybrid development artifact analysis, not a final holdout result.

- Source artifact: `experiments\gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl`
- JSON artifact: `experiments\gan2026_v06_validation750_qwen3635b_repairfix_attribution_2026-06-21.json`
- Split: `validation`, manifest `gan2026_split_v1`, 750 rows
- Model/raw-output source: `ollama_chat/qwen3.6:35b`, prompt `gan2026_hybrid_structured_events_v0.6`
- Inspection policy: validation row-level transitions only; no test450 rows inspected.

## Mode Scores

| Mode | Purist | Pragmatic | Structured | Parse issues | Repair notes |
| --- | ---: | ---: | ---: | ---: | ---: |
| `strict_json_raw_model` | 0.0000 (0/750) | 0.0000 (0/750) | 0 | 750 | 0 |
| `json_dialect_only` | 0.4920 (369/750) | 0.5213 (391/750) | 749 | 232 | 0 |
| `raw_model` | 0.4920 (369/750) | 0.5213 (391/750) | 749 | 232 | 0 |
| `strict_format` | 0.5360 (402/750) | 0.5667 (425/750) | 749 | 196 | 309 |
| `selected_evidence_derivation` | 0.8040 (603/750) | 0.8360 (627/750) | 749 | 1 | 472 |
| `hybrid_full_stack` | 0.8827 (662/750) | 0.9053 (679/750) | 749 | 1 | 508 |

## Full-Stack Versus Raw Model

- Changed final labels: 508
- Raw wrong -> full correct: 301
- Raw correct -> full wrong: 8
- Changed correct -> correct: 143
- Changed wrong -> wrong: 56
- Purist category changes: 346
- Pragmatic category changes: 326

Interpretation: the current threshold-clearing validation score is repair-dependent and should be claimed as a hybrid development artifact, not an LLM-first result.

## Raw-Wrong To Full-Correct Rows

| Row | Raw | Full | Gold | Repair notes |
| ---: | --- | --- | --- | --- |
| 10 | ≤ 4 per day | 4 per day | 4 per day | final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 40 | ≤ 4 per week | 4 per week | 4 per week | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | ≤ 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | ≤ 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | final_label_repaired: '≤ 2 to 4 per year' -> '2 to 4 per year' |
| 182 | 1 per day | 1 per 2 day | 1 per 2 day | final_label_repaired: '1 per day' -> '1 per 2 day' |
| 187 | multiple per week | 1 per 7 to 9 day | 1 per 7 to 9 day | final_label_repaired: 'multiple per week' -> '1 per 7 to 9 day' |
| 190 | 1 cluster per month | 1 per 4 week | 1 per 4 week | final_label_repaired: '1 cluster per month' -> '1 per 4 week' |
| 338 | many per month | multiple per month | multiple per month | final_label_repaired: 'many per month' -> 'multiple per month' |
| 409 | ≤ 1 per month | 1 per month | 1 per month | final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 446 | ≤ 2 per week | 15 per 3 month | 2 per week | final_label_repaired: '≤ 2 per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 531 | 12 to 30 per quarter | 12 to 30 per 3 month | 12 to 30 per 3 month | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per eight months | 1 per 8 month | 1 per 8 month | final_label_repaired: '1 per eight months' -> '1 per 8 month' |
| 725 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 731 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 763 | weekly | 1 per week | 1 per week | final_label_repaired: 'weekly' -> '1 per week' |
| 790 | 1 per week to 10 days | 1 per 7 to 10 day | 1 per 7 to 10 day | final_label_repaired: '1 per week to 10 days' -> '1 per 7 to 10 day' |
| 869 | several per month | multiple per month | multiple per month | final_label_repaired: 'several per month' -> 'multiple per month' |
| 891 | every other day | 1 per 2 day | 1 per 2 day | final_label_repaired: 'every other day' -> '1 per 2 day' |
| 959 | bimonthly | 1 per 2 month | 1 per 2 month | final_label_repaired: 'bimonthly' -> '1 per 2 month' |
| 960 | 2 per month | 1 per 2 month | 1 per 2 month | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 987 | 2 per month | 1 per 2 month | 1 per 2 month | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 1165 | multiple per week | 5 to 7 per 6 week | 5 to 7 per 3 week | final_label_repaired: 'multiple per week' -> '5 to 7 per 6 week' |
| 1171 | multiple per week | 9 per 3 week | 7 to 9 per 3 week | final_label_repaired: 'multiple per week' -> '9 per 3 week' |
| 1317 | multiple per day (cluster) | unknown | unknown, multiple per cluster | final_label_repaired: 'multiple per day (cluster)' -> 'unknown' |
| 1363 | multiple per week (including 3 tonic-clonic seizures yesterday) | 1 per day | 3 per day | final_label_repaired: 'multiple per week (including 3 tonic-clonic seizures yesterday)' -> '1 per day' |
| 1573 | 11 seizures per week | 11 per week | 11 per week | final_label_repaired: '11 seizures per week' -> '11 per week' |
| 1596 | 12 seizures per week | 12 per week | 12 per week | final_label_repaired: '12 seizures per week' -> '12 per week' |
| 1695 | a handful per month | no seizure frequency reference | multiple per month | final_label_repaired: 'a handful per month' -> 'no seizure frequency reference' |
| 1706 | multiple clusters per week | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | final_label_repaired: 'multiple clusters per week' -> 'multiple cluster per month, multiple per cluster' |
| 1772 | 11 events in 6 months | 11 per 6 month | 11 per 6 month | final_label_repaired: '11 events in 6 months' -> '11 per 6 month' |
| 1773 | 11 seizures in 3 months | 11 per 3 month | 11 per 3 month | final_label_repaired: '11 seizures in 3 months' -> '11 per 3 month' |
| 1790 | 8 seizures in 4 months | 8 per 4 month | 8 per 4 month | final_label_repaired: '8 seizures in 4 months' -> '8 per 4 month' |
| 1794 | 8 events in 2 months | 8 per 2 month | 8 per 2 month | final_label_repaired: '8 events in 2 months' -> '8 per 2 month' |
| 1887 | 4 seizures in 3 months | 4 per 3 month | 4 per 3 month | final_label_repaired: '4 seizures in 3 months' -> '4 per 3 month' |
| 1914 | 7 seizures in 3 months | 7 per 3 month | 7 per 3 month | final_label_repaired: '7 seizures in 3 months' -> '7 per 3 month' |
| 1922 | 7 seizures in 3 months | 7 per 3 month | 7 per 3 month | final_label_repaired: '7 seizures in 3 months' -> '7 per 3 month' |
| 1923 | 7 seizures in 6 months | 7 per 6 month | 7 per 6 month | final_label_repaired: '7 seizures in 6 months' -> '7 per 6 month' |
| 1979 | 6 events in 2 months | 3 per 2 month | 6 per 2 month | final_label_repaired: '6 events in 2 months' -> '3 per 2 month' |
| 2080 | few per month | multiple per month | multiple per month | final_label_repaired: 'few per month' -> 'multiple per month' |
| 2094 | several per month | multiple per month | multiple per month | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 | several per month | multiple per month | multiple per month | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2166 | frequent | multiple per day | unknown | final_label_repaired: 'frequent' -> 'multiple per day' |
| 2245 | about 7 to 8 per 3 weeks | 7 to 8 per 3 week | 7 to 8 per 3 week | final_label_repaired: 'about 7 to 8 per 3 weeks' -> '7 to 8 per 3 week' |
| 2609 | 1 per night | 1 per day | 1 per day | final_label_repaired: '1 per night' -> '1 per day' |
| 2622 | multiple per day | 1 per day | 1 per day | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2628 | 1 per day (nocturnal) | 1 per day | 1 per day | final_label_repaired: '1 per day (nocturnal)' -> '1 per day' |
| 2678 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 2822 | daily with occasional clusters | 1 per day | 1 per day | final_label_repaired: 'daily with occasional clusters' -> '1 per day' |
| 3242 | 2 clusters per month, ~5 seizures per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | final_label_repaired: '2 clusters per month, ~5 seizures per cluster' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 clusters per month, approx 4 seizures per cluster | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | final_label_repaired: '2 clusters per month, approx 4 seizures per cluster' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 clusters per month, ~5 events per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | final_label_repaired: '2 clusters per month, ~5 events per cluster' -> '2 cluster per month, 5 per cluster' |
| 3356 | unclear frequency (triggered by sleep deprivation) | no seizure frequency reference | unknown | final_label_repaired: 'unclear frequency (triggered by sleep deprivation)' -> 'no seizure frequency reference' |
| 3468 | perimenstrual cluster (days -2 to +2) | unknown | unknown | final_label_repaired: 'perimenstrual cluster (days -2 to +2)' -> 'unknown' |
| 3469 | perimenstrual cluster | unknown | unknown | final_label_repaired: 'perimenstrual cluster' -> 'unknown' |
| 3482 | perimenstrual only | no seizure frequency reference | unknown | final_label_repaired: 'perimenstrual only' -> 'no seizure frequency reference' |
| 3493 | cluster frequency around menstruation | unknown | unknown | final_label_repaired: 'cluster frequency around menstruation' -> 'unknown' |
| 3512 | increased frequency (~20%) | no seizure frequency reference | unknown | final_label_repaired: 'increased frequency (~20%)' -> 'no seizure frequency reference' |
| 3528 | increased frequency (relative) | no seizure frequency reference | unknown | final_label_repaired: 'increased frequency (relative)' -> 'no seizure frequency reference' |
| 3532 | increased frequency (approx 20% increase over 3 weeks) | no seizure frequency reference | unknown | final_label_repaired: 'increased frequency (approx 20% increase over 3 weeks)' -> 'no seizure frequency reference' |
| 3623 | up to 7 per week | 7 per week | 7 per week | final_label_repaired: 'up to 7 per week' -> '7 per week' |
| 3643 | up to 7 clusters per week | 7 per week | 7 per week | final_label_repaired: 'up to 7 clusters per week' -> '7 per week' |
| 3988 | several times per week | multiple per week | multiple per week | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 4092 | 2 to 3 per week | 1 per 2 to 3 week | 1 per 2 to 3 week | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 every 2 to 3 weeks | 1 per 2 to 3 week | 1 per 2 to 3 week | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4110 | 1 to 2 per day | 1 per 1 to 2 day | 1 per 1 to 2 day | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4116 | multiple per week | 1 per 1 to 2 day | 1 per 1 to 2 day | final_label_repaired: 'multiple per week' -> '1 per 1 to 2 day' |
| 4337 | 3 events in recent months | 3 per 3 month | 3 per 3 month | final_label_repaired: '3 events in recent months' -> '3 per 3 month' |
| 4368 | multiple per month | 5 per 2 month | 5 per 2 month | final_label_repaired: 'multiple per month' -> '5 per 2 month' |
| 4410 | multiple per month | 8 per 14 month | 4 per 7 month | final_label_repaired: 'multiple per month' -> '4 per 7 month'; final_label_repaired: '4 per 7 month' -> '8 per 14 month' |
| 4496 | 7-8 per quarter | 7 to 8 per 6 month | 7 to 8 per 3 month | final_label_repaired: '7-8 per quarter' -> '7 to 8 per 6 month' |
| 4624 | every 3-4 days | 1 per 3 to 4 day | 1 per 3 to 4 day | final_label_repaired: 'every 3-4 days' -> '1 per 3 to 4 day' |
| 4690 | ~10 per hour | multiple per day | multiple per day | final_label_repaired: '~10 per hour' -> 'multiple per day' |
| 4694 | ~9 per hour | multiple per day | multiple per day | final_label_repaired: '~9 per hour' -> 'multiple per day' |
| 4700 | ~4 per hour | multiple per day | multiple per day | final_label_repaired: '~4 per hour' -> 'multiple per day' |
| 4709 | ~6 per hour | multiple per day | multiple per day | final_label_repaired: '~6 per hour' -> 'multiple per day' |
| 4732 | occasional clusters | unknown | unknown | final_label_repaired: 'occasional clusters' -> 'unknown' |
| 5476 | sporadic / approximately 1 cluster per month | unknown | unknown | final_label_repaired: 'sporadic / approximately 1 cluster per month' -> 'unknown' |
| 5491 | increased frequency | no seizure frequency reference | unknown | final_label_repaired: 'increased frequency' -> 'no seizure frequency reference' |
| 5534 | very infrequent | no seizure frequency reference | 1 per multiple month | final_label_repaired: 'very infrequent' -> 'no seizure frequency reference' |
| 5551 | several per day | multiple per day | multiple per day | final_label_repaired: 'several per day' -> 'multiple per day' |
| 5567 | several per week | multiple per week | multiple per week | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | several per week | multiple per week | multiple per week | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5652 | 1 per week | 1 per 8 day | 1 per 8 day | final_label_repaired: '1 per week' -> '1 per 8 day' |
| 5791 | 3 seizures in 3 months | 3 per 3 month | 1 per month | final_label_repaired: '3 seizures in 3 months' -> '3 per 3 month' |
| 5866 | 4 in 6 weeks | 4 per 6 week | 4 per 6 week | final_label_repaired: '4 in 6 weeks' -> '4 per 6 week' |
| 5873 | most nights per week | no seizure frequency reference | multiple per week | final_label_repaired: 'most nights per week' -> 'no seizure frequency reference' |
| 5974 | seizures associated with missed medication doses | no seizure frequency reference | unknown | final_label_repaired: 'seizures associated with missed medication doses' -> 'no seizure frequency reference' |
| 5995 | infrequent | 3 per 7 month | 1 per 3 months | final_label_repaired: 'infrequent' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 7 month' |
| 5996 | 2 to 3 clusters per week | unknown | unknown | final_label_repaired: '2 to 3 clusters per week' -> 'unknown' |
| 6029 | multiple per week (clustering) | unknown | unknown | final_label_repaired: 'multiple per week (clustering)' -> 'unknown' |
| 6034 | clusters during disrupted routine | unknown | unknown | final_label_repaired: 'clusters during disrupted routine' -> 'unknown' |
| 6094 | 5 recent events (3 in Sept, 2 in Oct) | 4 per 2 month | 3 per month | final_label_repaired: '5 recent events (3 in Sept, 2 in Oct)' -> '5 per 2 month'; final_label_repaired: '5 per 2 month' -> '4 per 2 month' |
| 6153 | 9 seizures in 4 weeks (3 generalised/nocturnal, 6 focal) | 9 per 4 week | 9 per month | final_label_repaired: '9 seizures in 4 weeks (3 generalised/nocturnal, 6 focal)' -> '9 per 4 week' |
| 6180 | several per week | multiple per week | multiple per week | final_label_repaired: 'several per week' -> 'multiple per week' |
| 6209 | daily | multiple per day | multiple per day | final_label_repaired: 'daily' -> 'multiple per day' |
| 6251 | rare | 1 per 4 month | 1 per 1 to 2 month | final_label_repaired: 'rare' -> 'multiple per year'; final_label_repaired: 'multiple per year' -> '1 per 4 month' |
| 6319 | roughly weekly | 1 per week | 1 per week | final_label_repaired: 'roughly weekly' -> '1 per week' |
| 6501 | clusters every few weeks | unknown | unknown | final_label_repaired: 'clusters every few weeks' -> 'unknown' |
| 6607 | multiple per week (clusters) and occasional prolonged events | unknown | unknown | final_label_repaired: 'multiple per week (clusters) and occasional prolonged events' -> 'unknown' |
| 7126 | increased peri-mid-cycle; infrequent otherwise | no seizure frequency reference | unknown | final_label_repaired: 'increased peri-mid-cycle; infrequent otherwise' -> 'no seizure frequency reference' |
| 7141 | multiple per week (mid-cycle clustering) with recent convulsions | unknown | unknown | final_label_repaired: 'multiple per week (mid-cycle clustering) with recent convulsions' -> 'unknown' |
| 7192 | several times per week | multiple per week | multiple per week | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 7196 | 6 events in 6 weeks | 6 per 6 week | 1 per week | final_label_repaired: '6 events in 6 weeks' -> '6 per 6 week' |
| 7275 | 3 events in 3 months | 3 per 12 week | 1 per month | final_label_repaired: '3 events in 3 months' -> '3 per 12 week' |
| 7409 | most weeks | multiple per week | unknown | final_label_repaired: 'most weeks' -> 'multiple per week' |
| 7491 | clusters per week | unknown | unknown | final_label_repaired: 'clusters per week' -> 'unknown' |
| 9103 | infrequent | no seizure frequency reference | unknown | final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 9344 | several per day | multiple per day | multiple per day | final_label_repaired: 'several per day' -> 'multiple per day' |
| 9496 | seizure free for focal seizures in July 2020; no GTCS since March 2018 | 6 per 13 month | 6 per 12 month | final_label_repaired: 'seizure free for focal seizures in July 2020; no GTCS since March 2018' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '6 per 13 month' |
| 9815 | ~9 per hour | multiple per day | multiple per day | final_label_repaired: '~9 per hour' -> 'multiple per day' |
| 9879 | multiple per week (clusters) | unknown | unknown | final_label_repaired: 'multiple per week (clusters)' -> 'unknown' |
| 9955 | 1 cluster per month with several seizures per cluster | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | final_label_repaired: '1 cluster per month with several seizures per cluster' -> '1 cluster per month, multiple per cluster' |
| 10003 | weekly clusters | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | final_label_repaired: 'weekly clusters' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 clusters per quarter | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | final_label_repaired: '2 clusters per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 per quarter | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | final_label_repaired: '3 per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10189 | multiple per week (clustered) | multiple per week | unknown, 3 to 4 per cluster | final_label_repaired: 'multiple per week (clustered)' -> 'multiple per week' |
| 10200 | 2 to 4 per cluster | no seizure frequency reference | unknown, 2 to 4 per cluster | final_label_repaired: '2 to 4 per cluster' -> 'no seizure frequency reference' |
| 10383 | 5 per week (in clusters) | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | final_label_repaired: '5 per week (in clusters)' -> '1 cluster per week, 5 per cluster' |
| 10386 | 1 cluster per week (2-3 seizures) | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | final_label_repaired: '1 cluster per week (2-3 seizures)' -> '1 cluster per week, 2 to 3 per cluster' |
| 10481 | 4 clusters per month | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 clusters per month | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | clusters per night | unknown | unknown | final_label_repaired: 'clusters per night' -> 'unknown' |
| 10517 | 3-4 times per week | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | final_label_repaired: '3-4 times per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10618 | 4 to 6 per cluster | no seizure frequency reference | unknown, 4 to 6 per cluster | final_label_repaired: '4 to 6 per cluster' -> 'no seizure frequency reference' |
| 10677 | 1 per month | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | occasional with travel-related clusters | unknown | unknown | final_label_repaired: 'occasional with travel-related clusters' -> 'unknown' |
| 10807 | 2 clusters per month | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | final_label_repaired: '2 clusters per month' -> '2 cluster per month, multiple per cluster' |
| 10829 | 2 clusters per month | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | final_label_repaired: '2 clusters per month' -> '2 cluster per month, multiple per cluster' |
| 10862 | 1 cluster per week | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | multiple per week (clusters of 6+) | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | final_label_repaired: 'multiple per week (clusters of 6+)' -> '1 cluster per week, 6 per cluster' |
| 10894 | weekly clusters of 4 seizures | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | final_label_repaired: 'weekly clusters of 4 seizures' -> '1 cluster per week, 4 per cluster' |
| 10896 | weekly clusters of 3-4 seizures | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | final_label_repaired: 'weekly clusters of 3-4 seizures' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | weekly clusters of 4+ seizures | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | final_label_repaired: 'weekly clusters of 4+ seizures' -> '1 cluster per week, 4 per cluster' |
| 10942 | 2 clusters per month (approx. 10 seizures) | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | final_label_repaired: '2 clusters per month (approx. 10 seizures)' -> '2 cluster per month, 5 per cluster' |
| 10965 | 2 clusters per month, 4-5 events per cluster | 2 cluster per month, 4 to 5 per cluster | 2 cluster per month, 4 to 5 per cluster | final_label_repaired: '2 clusters per month, 4-5 events per cluster' -> '2 cluster per month, 4 to 5 per cluster' |
| 10984 | 3 per month | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | final_label_repaired: '3 per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 per month | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | final_label_repaired: '1 to 2 per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 per month | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | final_label_repaired: '2 to 4 per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per quarter | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | final_label_repaired: '1 cluster per quarter' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | multiple per week (with clusters of 5+ daily) | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | final_label_repaired: 'multiple per week (with clusters of 5+ daily)' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 clusters per month, ~6 seizures per cluster day | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | final_label_repaired: '2 clusters per month, ~6 seizures per cluster day' -> '2 cluster per month, 6 per cluster' |
| 11131 | 3 to 4 per day | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | final_label_repaired: '3 to 4 per day' -> '2 cluster per month, 3 to 4 per cluster' |
| 11409 | occasional clusters | unknown | no seizure frequency reference | final_label_repaired: 'occasional clusters' -> 'unknown' |
| 12046 | near-daily / dozens per day | multiple per day | multiple per day | final_label_repaired: 'near-daily / dozens per day' -> 'multiple per day' |
| 12051 | near-daily / dozens per day | multiple per day | multiple per day | final_label_repaired: 'near-daily / dozens per day' -> 'multiple per day' |
| 12111 | several times per week | multiple per week | multiple per week | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12127 | several per week | multiple per week | multiple per week | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12130 | several per week | multiple per week | multiple per week | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12139 | several per week | multiple per week | multiple per week | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12145 | several per week | multiple per week | multiple per week | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12192 | multiple seizure types with daily to weekly frequency | 1 per day | 1 per day | final_label_repaired: 'multiple seizure types with daily to weekly frequency' -> '1 per day' |
| 12218 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12236 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12314 | multiple per week | 3 per week | 3 per week | final_label_repaired: 'multiple per week' -> '3 per week' |
| 12366 | multiple seizure types with high frequency (4/day, clusters, 2/month) | 4 per day | 4 per day | final_label_repaired: 'multiple seizure types with high frequency (4/day, clusters, 2/month)' -> '4 per day' |
| 12378 | multiple per day | 4 per day | 4 per day | final_label_repaired: 'multiple per day' -> '4 per day' |
| 12383 | multiple seizure types with high frequency (focal: 4/day; drop attacks: clusters; tonic-clonic: 2/month) | 4 per day | 4 per day | final_label_repaired: 'multiple seizure types with high frequency (focal: 4/day; drop attacks: clusters; tonic-clonic: 2/month)' -> '4 per day' |
| 12403 | multiple per day | 2 to 3 per day | 2 to 3 per day | final_label_repaired: 'multiple per day' -> '2 to 3 per day' |
| 12412 | multiple seizure types with varying frequencies (2/day, clusters, 2/month) | 2 per day | 2 per day | final_label_repaired: 'multiple seizure types with varying frequencies (2/day, clusters, 2/month)' -> '2 per day' |
| 12422 | nightly | 1 per day | 1 per day | final_label_repaired: 'nightly' -> '1 per day' |
| 12438 | nightly | 1 per day | 1 per day | final_label_repaired: 'nightly' -> '1 per day' |
| 12456 | nightly | 1 per day | 1 per day | final_label_repaired: 'nightly' -> '1 per day' |
| 12460 | nightly | 1 per day | 1 per day | final_label_repaired: 'nightly' -> '1 per day' |
| 12468 | nightly | 1 per day | 1 per day | final_label_repaired: 'nightly' -> '1 per day' |
| 12506 | multiple per day | 4 per day | 4 per day | final_label_repaired: 'multiple per day' -> '4 per day' |
| 12537 | multiple per day | 1 per day | 1 per day | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12548 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12551 | multiple per day | 1 per day | 1 per day | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12556 | multiple seizure types with high burden (daily drop attacks, up to 2-3 GTCS/week) | 1 per day | 1 per day | final_label_repaired: 'multiple seizure types with high burden (daily drop attacks, up to 2-3 GTCS/week)' -> '1 per day' |
| 12562 | multiple per day/week | 1 per day | 1 per day | final_label_repaired: 'multiple per day/week' -> '1 per day' |
| 12573 | multiple seizure types: GTCs up to 2/month, daily drop attacks, FIAS every 4-6 weeks | 1 per day | 1 per day | final_label_repaired: 'multiple seizure types: GTCs up to 2/month, daily drop attacks, FIAS every 4-6 weeks' -> '1 per day' |
| 12584 | weekly | 1 per week | 1 per week | final_label_repaired: 'weekly' -> '1 per week' |
| 12641 | multiple per day | 1 per day | 1 per day | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12665 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12667 | multiple seizure types: 1-2 GTC/month, daily absence, focal clonic q3-4wks, drop attacks | 1 per day | 1 per day | final_label_repaired: 'multiple seizure types: 1-2 GTC/month, daily absence, focal clonic q3-4wks, drop attacks' -> '1 per day' |
| 12676 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12679 | multiple seizure types: 1-2 GTCS/month, daily absences, focal non-motor every 3-4 weeks, drop attacks | 1 per day | 1 per day | final_label_repaired: 'multiple seizure types: 1-2 GTCS/month, daily absences, focal non-motor every 3-4 weeks, drop attacks' -> '1 per day' |
| 12749 | multiple per day | 3 to 4 per day | 3 to 4 per day | final_label_repaired: 'multiple per day' -> '3 to 4 per day' |
| 12751 | multiple per day | 4 per day | 4 per day | final_label_repaired: 'multiple per day' -> '4 per day' |
| 12788 | 6 per year | 6 per 4 month | 6 per 4 month | final_label_repaired: '6 per year' -> '6 per 4 month' |
| 12810 | 5 per year | 5 per 2 month | 5 per 2 month | final_label_repaired: '5 per year' -> '5 per 2 month' |
| 12823 | 9 per year (generalised tonic-clonic); 1 per 3-4 weeks (focal impaired-awareness) | 9 per month | 9 per month | final_label_repaired: '9 per year (generalised tonic-clonic); 1 per 3-4 weeks (focal impaired-awareness)' -> '9 per month' |
| 12827 | 5 per year | 5 per 5 month | 5 per 5 month | final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12835 | 4 in 2015 so far | 4 per month | 4 per month | final_label_repaired: '4 in 2015 so far' -> '4 per month' |
| 12882 | 7 per year (GTC), 1-2 per month (focal) | 1 to 2 per month | 7 per 4 month | final_label_repaired: '7 per year (GTC), 1-2 per month (focal)' -> '1 to 2 per month' |
| 12901 | 8 per year (so far) | 8 per 5 month | 8 per 5 month | final_label_repaired: '8 per year (so far)' -> '8 per 5 month' |
| 12949 | 9 per year | 9 per 6 month | 9 per 6 month | final_label_repaired: '9 per year' -> '9 per 6 month' |
| 12950 | multiple per week | 7 per 3 month | 7 per 3 month | final_label_repaired: 'multiple per week' -> '7 per 3 month' |
| 12963 | few seizures per year | multiple per year | unknown | final_label_repaired: 'few seizures per year' -> 'multiple per year' |
| 13008 | 4 per year | 4 per month | 4 per month | final_label_repaired: '4 per year' -> '4 per month' |
| 13122 | 1 cluster (3 seizures) in the recent past | 3 per 1 year | 3 per year | final_label_repaired: '1 cluster (3 seizures) in the recent past' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 1 year' |
| 13178 | 1 event (breakthrough) | 1 per 6 month | 1 per 6 month | final_label_repaired: '1 event (breakthrough)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 6 month' |
| 13627 | multiple per week | 20 per 3 month | 64 per 12 month | final_label_repaired: 'multiple per week' -> '64 per 12 month'; final_label_repaired: '64 per 12 month' -> '20 per 3 month' |
| 13635 | multiple per week | 30 per 5 month | 47 per 7 month | final_label_repaired: 'multiple per week' -> '47 per 7 month'; final_label_repaired: '47 per 7 month' -> '30 per 5 month' |
| 13711 | multiple per week | 28 per 6 month | 76 per 12 month | final_label_repaired: 'multiple per week' -> '76 per 12 month'; final_label_repaired: '76 per 12 month' -> '28 per 6 month' |
| 13721 | multiple per week | 26 per 6 month | 77 per 12 month | final_label_repaired: 'multiple per week' -> '77 per 12 month'; final_label_repaired: '77 per 12 month' -> '26 per 6 month' |
| 13732 | multiple per week | 16 per 3 month | 52 per 8 month | final_label_repaired: 'multiple per week' -> '52 per 8 month'; final_label_repaired: '52 per 8 month' -> '16 per 3 month' |
| 13889 | unknown | seizure free for multiple year | seizure free for multiple month | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13922 | 2 total since medication increase | no seizure frequency reference | unknown | final_label_repaired: '2 total since medication increase' -> 'no seizure frequency reference' |
| 14002 | several | no seizure frequency reference | unknown | final_label_repaired: 'several' -> 'no seizure frequency reference' |
| 14029 | several per month | multiple per month | unknown | final_label_repaired: 'several per month' -> 'multiple per month' |
| 14092 | 5 events since last review | no seizure frequency reference | unknown | final_label_repaired: '5 events since last review' -> 'no seizure frequency reference' |
| 14096 | 5 since last clinic appointment | no seizure frequency reference | unknown | final_label_repaired: '5 since last clinic appointment' -> 'no seizure frequency reference' |
| 14146 | 3 total | no seizure frequency reference | unknown | final_label_repaired: '3 total' -> 'no seizure frequency reference' |
| 14187 | seizure free | 2 to 3 per 1 month | 2 to 3 per month | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 to 3 per 1 month' |
| 14214 | seizure free | 2 to 4 per 1 month | 2 to 4 per month | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 to 4 per 1 month' |
| 14250 | seizure free for 1 month | 2 per 1 month | 2 per month | final_label_repaired: 'seizure free for 1 month' -> '2 per 1 month' |
| 14284 | 2 to 3 per week | 2 to 3 per 1 month | 2 to 3 per month | final_label_repaired: '2 to 3 per week' -> '2 to 3 per 1 month' |
| 14317 | seizure free for 2 month | 4 per 2 month | 4 per 2 month | final_label_repaired: 'seizure free for 2 month' -> '4 per 2 month' |
| 14332 | seizure free for 2 month | 5 per 2 month | 5 per 2 month | final_label_repaired: 'seizure free for 2 month' -> '5 per 2 month' |
| 14335 | seizure free for 8 weeks | 3 to 4 per 8 week | 3 to 4 per 2 month | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 8 week' |
| 14383 | seizure free since 13-Jan-2019 | 3 to 4 per 3 month | 3 to 4 per 3 month | final_label_repaired: 'seizure free since 13-Jan-2019' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 3 month' |
| 14454 | seizure free for 2 months | 2 per 2 month | 2 per 2 month | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '2 per 2 month' |
| 14524 | occasional clusters | 2 per 3 month | 2 per 6 month | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 3 month' |
| 14530 | seizure free since May 2019 | 2 per 2 month | 2 per 2 month | final_label_repaired: 'seizure free since May 2019' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 2 month' |
| 14540 | seizure free since August 2018 | 2 per 8 month | 2 per 8 month | final_label_repaired: 'seizure free since August 2018' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 8 month' |
| 14562 | seizure free since July 2021 | 3 per 6 month | 3 per 6 month | final_label_repaired: 'seizure free since July 2021' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '0 per 1 month'; final_label_repaired: '0 per 1 month' -> '3 per 6 month' |
| 14567 | unknown | 3 per 3 month | 3 per 3 month | final_label_repaired: 'unknown' -> '3 per 3 month' |
| 14581 | seizure free | 2 per 3 month | 2 per 3 month | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month' |
| 14611 | seizure free since May 2020 | 2 per 4 month | 2 per 4 month | final_label_repaired: 'seizure free since May 2020' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 4 month' |
| 14628 | 2 events in recent months | 2 per 2 month | 2 per 2 month | final_label_repaired: '2 events in recent months' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 per 2 month' |
| 14645 | seizure free | 2 per 6 month | 2 per 6 month | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 6 month' |
| 14662 | 3 events since May 2024 | 3 per 4 month | 3 per 4 month | final_label_repaired: '3 events since May 2024' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 4 month' |
| 14672 | seizure free | 3 per 8 month | 3 per 8 month | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 8 month' |
| 14765 | seizure free for 1 month | 1 per 1 month | 1 per month | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14806 | seizure free for 1 month | 1 per 2 month | 1 per 2 month | final_label_repaired: 'seizure free for 1 month' -> '1 per 2 month' |
| 14810 | seizure free for 4 weeks | 1 per 1 month | 1 per month | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14821 | seizure free since 24 Jul | 1 per 1 month | 1 per month | final_label_repaired: 'seizure free since 24 Jul' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14872 | seizure free for 2 weeks | 1 per 1 month | 1 per month | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14943 | seizure free since 21 Feb | 1 per 3 month | 1 per 3 month | final_label_repaired: 'seizure free since 21 Feb' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14965 | seizure free since 20/May | 1 per 3 month | 1 per 3 month | final_label_repaired: 'seizure free since 20/May' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14973 | seizure free since 06 February | 1 per 1 month | 1 per month | final_label_repaired: 'seizure free since 06 February' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 15004 | seizure free for 3 month | 1 per 3 month | 1 per 3 month | final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 15012 | seizure free since 31-May-2017 | 1 per 2 month | 1 per 2 month | final_label_repaired: 'seizure free since 31-May-2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 15029 | seizure free for 3 month | 1 per 3 month | 1 per 3 month | final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 15094 | seizure free for 1 year | 3 per 13 month | 4 per 13 month | final_label_repaired: 'seizure free for 1 year' -> '2022 per 1 year'; final_label_repaired: '2022 per 1 year' -> '3 per 13 month' |
| 15127 | 4 since Feb 2020 | 4 per 13 month | 5 per 13 month | final_label_repaired: '4 since Feb 2020' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 13 month' |
| 15129 | 4 events since 3/2015 | 4 per 15 month | 4 per 15 month | final_label_repaired: '4 events since 3/2015' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 15 month' |
| 15141 | rare (3-4 events over >1 year) | 3 to 4 per 15 month | 4 to 5 per 15 month | final_label_repaired: 'rare (3-4 events over >1 year)' -> 'multiple per year'; final_label_repaired: 'multiple per year' -> '3 to 4 per 15 month' |
| 15168 | occasional | multiple per month | multiple per 15 month | final_label_repaired: 'occasional' -> 'multiple per month' |
| 15242 | occasional clusters | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15262 | occasional clusters | multiple cluster per 13 month, multiple per cluster | multiple cluster per 13 month, multiple per cluster | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 13 month, multiple per cluster' |
| 15306 | 2 to 3 per month | 2 to 3 per 15 month | 2 to 3 per 15 month | final_label_repaired: '2 to 3 per month' -> '2 to 3 per 15 month' |
| 15404 | 3 to 4 per day (in clusters) | 3 to 4 per 4 month | 1 cluster per 4 month, 3 to 4 per cluster | final_label_repaired: '3 to 4 per day (in clusters)' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 4 per 4 month' |
| 15429 | 4 per day (in clusters) | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | final_label_repaired: '4 per day (in clusters)' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15442 | multiple per week (cluster) | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | final_label_repaired: 'multiple per week (cluster)' -> '1 cluster per 4 day, 2 per cluster' |
| 15479 | multiple per week (clustered) | 1 cluster per 4 to 5 day, 2 per cluster | 1 cluster per 4 to 5 day, 2 per cluster | final_label_repaired: 'multiple per week (clustered)' -> '1 cluster per 4 to 5 day, 2 per cluster' |
| 15497 | 1 cluster per week (approx) | 1 cluster per 5 day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | final_label_repaired: '1 cluster per week (approx)' -> '1 cluster per 5 day, 5 per cluster' |
| 15513 | 2 to 3 per day (in clusters) | 1 cluster per 5 day, 2 to 3 per cluster | 1 cluster per 4 to 5 day, 2 to 3 per cluster | final_label_repaired: '2 to 3 per day (in clusters)' -> '1 cluster per 5 day, 2 to 3 per cluster' |
| 15519 | 3 per day (in clusters) | 1 cluster per 4 day, 3 per cluster | 1 cluster per 4 day, 3 per cluster | final_label_repaired: '3 per day (in clusters)' -> '1 cluster per 4 day, 3 per cluster' |
| 15529 | 1 cluster per week (approx) | 1 cluster per 3 day, 4 per cluster | 1 cluster per 3 day, 4 per cluster | final_label_repaired: '1 cluster per week (approx)' -> '1 cluster per 3 day, 4 per cluster' |
| 15593 | 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | final_label_repaired: '2 to 4 per cluster' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15628 | several times per week | multiple per week | multiple per week | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 15672 | daily clusters | 1 per day | 1 per day | final_label_repaired: 'daily clusters' -> '1 per day' |
| 15697 | almost 1 per day | 1 per day | 1 per day | final_label_repaired: 'almost 1 per day' -> '1 per day' |
| 15715 | almost 1 per day | 1 per day | 1 per day | final_label_repaired: 'almost 1 per day' -> '1 per day' |
| 15964 | 6 per month | 11 per 3 month | 11 per 3 month | final_label_repaired: '6 per month' -> '11 per 3 month' |
| 15986 | ongoing breakthrough seizures | 11 per 3 month | 11 per 3 month | final_label_repaired: 'ongoing breakthrough seizures' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '11 per 3 month' |
| 15997 | 6 per month | 10 per 3 month | 10 per 3 month | final_label_repaired: '6 per month' -> '10 per 3 month' |
| 16021 | 5 per month | 9 per 3 month | 9 per 3 month | final_label_repaired: '5 per month' -> '9 per 3 month' |
| 16041 | 4 per month | 9 per 3 month | 9 per 3 month | final_label_repaired: '4 per month' -> '9 per 3 month' |
| 16084 | 8 per quarter | 8 per 4 month | 8 per 4 month | final_label_repaired: '8 per quarter' -> '8 per 4 month' |
| 16097 | multiple per week | 17 per 4 month | 17 per 4 month | final_label_repaired: 'multiple per week' -> '17 per 4 month' |
| 16107 | 4 per month | 9 per 3 month | 8 per 3 month | final_label_repaired: '4 per month' -> '8 per 3 month'; final_label_repaired: '8 per 3 month' -> '9 per 3 month' |
| 16108 | 12 seizures in the last 3 months | 12 per 4 month | 12 per 4 month | final_label_repaired: '12 seizures in the last 3 months' -> '12 per 4 month' |
| 16132 | multiple per week | 13 per 2 month | 15 per 3 month | final_label_repaired: 'multiple per week' -> '13 per 2 month' |
| 16133 | multiple per week | 18 per 4 month | 18 per 4 month | final_label_repaired: 'multiple per week' -> '18 per 4 month' |
| 16162 | 6 per month | 11 per 3 month | 11 per 3 month | final_label_repaired: '6 per month' -> '11 per 3 month' |
| 16181 | multiple per week | 15 per 4 month | 15 per 4 month | final_label_repaired: 'multiple per week' -> '15 per 4 month' |
| 16195 | multiple per week | 16 per 4 month | 16 per 4 month | final_label_repaired: 'multiple per week' -> '16 per 4 month' |
| 16204 | 5 seizures in 3 months | 4 per 2 month | 5 per 3 month | final_label_repaired: '5 seizures in 3 months' -> '5 per 3 month'; final_label_repaired: '5 per 3 month' -> '4 per 2 month' |
| 16324 | 10 per quarter (approx. 2-3 per month) | 7 per 2 month | 10 per 3 month | final_label_repaired: '10 per quarter (approx. 2-3 per month)' -> '7 per 2 month' |
| 16335 | 7 seizures over 3 months | 7 per 3 month | 7 per 3 month | final_label_repaired: '7 seizures over 3 months' -> '7 per 3 month' |
| 16356 | 1 cluster every 4 days | 1 per 4 day | 1 per 4 day | final_label_repaired: '1 cluster every 4 days' -> '1 per 4 day' |
| 16394 | 1 cluster every 2 to 4 days | 1 per 2 to 4 day | 1 per 2 to 4 day | final_label_repaired: '1 cluster every 2 to 4 days' -> '1 per 2 to 4 day' |
| 16408 | 1 per 3 days (up to daily) | 1 per 3 day | 1 per 3 day | final_label_repaired: '1 per 3 days (up to daily)' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 3 day' |
| 16429 | multiple per day | 1 per 2 to 3 day | 1 per 2 to 3 day | final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 to 3 day' |
| 16432 | 1 per 2 days to daily | 1 per 2 day | 1 per 2 day | final_label_repaired: '1 per 2 days to daily' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 day' |
| 16529 | 1 cluster every 5 days | 1 per 5 day | 1 per 5 day | final_label_repaired: '1 cluster every 5 days' -> '1 per 5 day' |
| 16557 | 1 cluster every 2 to 3 days | 1 per 2 to 3 day | 1 per 2 to 3 day | final_label_repaired: '1 cluster every 2 to 3 days' -> '1 per 2 to 3 day' |
| 16574 | multiple per week (clusters every 4 days) | 1 per 4 day | 1 per 4 day | final_label_repaired: 'multiple per week (clusters every 4 days)' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 4 day' |
| 16590 | multiple per week (clusters every 4-5 days) | 1 per 4 to 5 day | 1 per 4 to 5 day | final_label_repaired: 'multiple per week (clusters every 4-5 days)' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 4 to 5 day' |
| 16618 | multiple per week (clusters every 5 days) with occasional daily bursts | 1 per 5 day | 1 per 5 day | final_label_repaired: 'multiple per week (clusters every 5 days) with occasional daily bursts' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 5 day' |
| 16674 | fewer events per month | 6 per 4 month | 7 per 6 month | final_label_repaired: 'fewer events per month' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '6 per 4 month' |
| 16685 | multiple per month | 10 per 3 month | 10 per 3 month | final_label_repaired: 'multiple per month' -> '10 per 3 month' |
| 16697 | 3 seizures in 6 months | 2 per 3 month | 3 per 6 month | final_label_repaired: '3 seizures in 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '2 per 3 month' |
| 16704 | 7 per month | 9 per 6 month | 9 per 6 month | final_label_repaired: '7 per month' -> '9 per 6 month' |
| 16717 | multiple per month | 5 per 6 month | 5 per 6 month | final_label_repaired: 'multiple per month' -> '5 per 6 month' |
| 16719 | 1 per week | 7 per 4 month | 7 per 6 month | final_label_repaired: '1 per week' -> '7 per 4 month' |
| 16750 | seizure free since late August 2010 | 6 per 7 month | 6 per 7 month | final_label_repaired: 'seizure free since late August 2010' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '6 per 7 month' |
| 16758 | multiple per month | 8 per 4 month | 9 per 5 month | final_label_repaired: 'multiple per month' -> '8 per 4 month' |
| 16780 | unknown | 3 per 7 month | 3 per 7 month | final_label_repaired: 'unknown' -> '3 per 7 month' |
| 16824 | 1 per month | 11 per 3 month | 11 per 5 month | final_label_repaired: '1 per month' -> '11 per 3 month' |
| 16833 | multiple per month | 8 per 6 month | 8 per 6 month | final_label_repaired: 'multiple per month' -> '8 per 6 month' |
| 16839 | multiple per month | 9 per 3 month | 9 per 4 month | final_label_repaired: 'multiple per month' -> '9 per 3 month' |
| 16907 | multiple per month | 8 per 4 month | 9 per 6 month | final_label_repaired: 'multiple per month' -> '8 per 4 month' |
| 16938 | 2 per 2 months (GTC), up to 2 per week (Absence) | 2 per week | 2 per week | final_label_repaired: '2 per 2 months (GTC), up to 2 per week (Absence)' -> '2 per week' |
| 16947 | 4 per 2 months (GTC), up to 2 per week (absence) | 2 per week | 2 per week | final_label_repaired: '4 per 2 months (GTC), up to 2 per week (absence)' -> '2 per week' |
| 16961 | multiple per week | 2 per week | 2 per week | final_label_repaired: 'multiple per week' -> '2 per week' |
| 17189 | 1 per 6 months (GTC), 1 per month (myoclonic) | 1 per month | 1 per month | final_label_repaired: '1 per 6 months (GTC), 1 per month (myoclonic)' -> '1 per month' |

## Full-Stack Regressions From Raw

| Row | Raw | Full | Gold | Repair notes |
| ---: | --- | --- | --- | --- |
| 2459 | 7 to 9 per 2 weeks | 5 per 5 month | 7 to 9 per 2 week | final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2932 | seizure free since 29/09/2017 | 13 per 2 month | seizure free for 9 month | final_label_repaired: 'seizure free since 29/09/2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '13 per 2 month' |
| 4402 | 1 per month | 7 per 4 month | 7 per 7 month | final_label_repaired: '1 per month' -> '7 per 7 month'; final_label_repaired: '7 per 7 month' -> '7 per 4 month' |
| 6273 | unknown | 2 per 9 month | unknown | final_label_repaired: 'unknown' -> '2 per 9 month' |
| 8581 | seizure free since 12th June 2025 | 1 per 4 month | seizure free for multiple month | final_label_repaired: 'seizure free since 12th June 2025' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 4 month' |
| 10542 | unknown | 2 to 4 per 3 month | unknown, 2 to 4 per cluster | final_label_repaired: 'unknown' -> '2 to 4 per 3 month' |
| 12484 | 3 to 4 per day | 1 cluster per month, multiple per cluster | 3 to 4 per day | final_label_repaired: '3 to 4 per day' -> '1 cluster per month, multiple per cluster' |
| 16774 | 3 per month | 19 per 4 month | 19 per 7 month | final_label_repaired: '3 per month' -> '19 per 4 month' |

## Top Repair Notes

- 24: `final_label_repaired: 'seizure free' -> 'seizure free for multiple year'`
- 8: `final_label_repaired: 'daily' -> '1 per day'`
- 7: `final_label_repaired: 'several per week' -> 'multiple per week'`
- 5: `final_label_repaired: 'multiple per day' -> '1 per day'`
- 5: `final_label_repaired: 'occasional clusters' -> 'unknown'`
- 5: `final_label_repaired: 'nightly' -> '1 per day'`
- 4: `final_label_repaired: 'several per month' -> 'multiple per month'`
- 4: `final_label_repaired: '1 per 2 weeks' -> '1 per 2 week'`
- 4: `final_label_repaired: '1 per 2 days' -> '1 per 2 day'`
- 4: `final_label_repaired: 'several times per week' -> 'multiple per week'`
- 4: `final_label_repaired: 'seizure free for >1 year' -> 'seizure free for multiple year'`
- 4: `final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month'`
- 4: `final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'`
- 4: `final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month'`
- 3: `final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year'`
- 3: `final_label_repaired: '1 per 6-8 weeks' -> '1 per 6 to 8 week'`
- 3: `final_label_repaired: 'infrequent' -> 'no seizure frequency reference'`
- 3: `final_label_repaired: 'multiple per day' -> '4 per day'`
- 2: `final_label_repaired: '1 per day' -> '1 per 2 day'`
- 2: `final_label_repaired: '1 per month' -> '1 per 4 week'`

## Next Decision

Run only a frozen aggregate test450 evaluation for this candidate. Do not inspect test row-level failures; if the aggregate fails the >0.8 target, return to validation hard-slice work using the remaining validation miss clusters.
