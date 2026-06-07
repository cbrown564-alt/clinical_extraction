# Gan 2026 Validation750 Null Reduction Proxy Slices Baseline

baseline validation-development null reduction proxy slices; no holdout use

## Summary of Slices

| Slice Family | Description | Total Rows | Rendered | Null | Purist Correct | Pragmatic Correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `cluster_cadence_values_incomplete` | Cluster frequency state extracted but required cadence or size operands were incomplete. | 13 | 0 | 13 | 0 | 0 |
| `cluster_frequency_values_unparsed` | Cluster frequency state extracted but cluster cadence/size operands remained unparsed. | 19 | 4 | 15 | 4 | 4 |
| `frequency_rate_values_incomplete` | Frequency rate facts extracted but required count/period operands were incomplete. | 58 | 0 | 58 | 0 | 0 |
| `frequency_rate_values_unparsed` | Frequency rate facts extracted but count/range/period operands remained unparsed. | 85 | 26 | 59 | 21 | 25 |
| `seizure_free_duration_required` | Seizure free state extracted but durational boundaries/anchors were missing. | 75 | 0 | 75 | 0 | 0 |
| `seizure_free_duration_unparsed` | Seizure free state extracted but durational values could not be parsed. | 37 | 10 | 27 | 8 | 8 |
| `vague_count` | Frequency count is vague (e.g. multiple) but Observation period is explicit. | 133 | 81 | 52 | 61 | 62 |

## Slice Details: `cluster_cadence_values_incomplete`

- **Description**: Cluster frequency state extracted but required cadence or size operands were incomplete.
- **Row count**: 13
- **Null count**: 13
- **Rendered count**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Purist Correct | Pragmatic Correct | Normalization Issues |
| ---: | --- | --- | --- | --- | --- | --- |
| 1706 | `cluster of short events on multiple days over the past month` | `multiple cluster per month, multiple per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `vague_count` |
| 6501 | `brief episodes occurring over 2–3 days` | `unknown` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 9879 | `brief clusters of events over the past three months` | `unknown` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 9937 | `periodic bursts roughly every few weeks` | `1 cluster per month, multiple per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 10434 | `on several mornings each week` | `multiple cluster per week, 2 to 3 per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `vague_count` |
| 10542 | `two to four absences per cluster over approximately 1 hour` | `unknown, 2 to 4 per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 10578 | `three to four focal impaired-awareness seizures per cluster` | `unknown, 3 to 4 per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 10630 | `several evenings per fortnight with roughly five short-lived spells per cluster` | `multiple cluster per 2 week, 5 per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `vague_count` |
| 15242 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 15 month, multiple per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 15262 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 13 month, multiple per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 16757 | `recent clusters of brief seizures` | `13 per 6 month` | `NULL` | False | False | `candidate_role_overlap_removed:supporting_candidate_ids:llm:16757:1:kept_primary_candidate_ids`, `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 16839 | `Clusters of 4 seizures in December and February` | `9 per 4 month` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 16907 | `run of six seizures within half an hour` | `9 per 6 month` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |

## Slice Details: `cluster_frequency_values_unparsed`

- **Description**: Cluster frequency state extracted but cluster cadence/size operands remained unparsed.
- **Row count**: 19
- **Null count**: 15
- **Rendered count**: 4

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Purist Correct | Pragmatic Correct | Normalization Issues |
| ---: | --- | --- | --- | --- | --- | --- |
| 1317 | `multiple short episodes within a single day consistent with typical events` | `unknown, multiple per cluster` | `unknown, multiple per cluster` | True | True | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` |
| 3468 | `perimenstrual only (days -2 to +2)` | `unknown` | `NULL` | False | False | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` |
| 3469 | `perimenstrual clustering` | `unknown` | `NULL` | False | False | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` |
| 3482 | `Seizures happen when perimenstrual only (days -3 to +3).` | `unknown` | `NULL` | False | False | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` |
| 3493 | `the attacks cluster around her period` | `unknown` | `NULL` | False | False | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` |
| 6501 | `brief episodes occurring over 2–3 days` | `unknown` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 7141 | `recurring mid‑cycle clustering of brief focal-aware episodes` | `unknown` | `unknown, multiple per cluster` | True | True | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` |
| 9879 | `brief clusters of events over the past three months` | `unknown` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 9937 | `periodic bursts roughly every few weeks` | `1 cluster per month, multiple per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 10189 | `Clusters occur sporadically; typically 3 or 4 events when they happen; several weeks seizure-free between clusters.` | `unknown, 3 to 4 per cluster` | `unknown, multiple per cluster` | True | True | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` |
| 10200 | `Clusters occur sporadically; typically two to four events when they happen.` | `unknown, 2 to 4 per cluster` | `unknown, multiple per cluster` | True | True | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` |
| 10509 | `clusters arising after nights of curtailed sleep` | `unknown` | `NULL` | False | False | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` |
| 10542 | `two to four absences per cluster over approximately 1 hour` | `unknown, 2 to 4 per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 10578 | `three to four focal impaired-awareness seizures per cluster` | `unknown, 3 to 4 per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |
| 15242 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 15 month, multiple per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` |

## Slice Details: `frequency_rate_values_incomplete`

- **Description**: Frequency rate facts extracted but required count/period operands were incomplete.
- **Row count**: 58
- **Null count**: 58
- **Rendered count**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Purist Correct | Pragmatic Correct | Normalization Issues |
| ---: | --- | --- | --- | --- | --- | --- |
| 3507 | `frequency reduced by 0.3 after dose increase` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `relative_change_without_current_baseline` |
| 3512 | `frequency increased by approximately 20% after dose increase` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `relative_change_without_current_baseline` |
| 3532 | `generalised tonic to clonic seizures predominantly from sleep with occasional brief absence episodes during the day` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4337 | `3 seizure events on 06 to 03, 06 to 13, 09 to 23 as recorded in the patient’s diary` | `3 per 3 month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4345 | `4 generalised tonic to clonic seizures in july` | `4 per month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4368 | `5 seizure events documented recently` | `5 per 2 month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4562 | `median inter to seizure interval six weeks` | `1 per 6 week` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4563 | `median inter to seizure interval approximately four months` | `1 per 4 month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4574 | `median inter to seizure interval approximately four weeks` | `1 per 4 week` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4592 | `median inter to seizure interval approximately two months` | `1 per 2 month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4597 | `median inter to seizure interval approximately three weeks` | `1 per 3 week` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 5476 | `sporadic epileptic spasms this year` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 5534 | `a very infrequent, short event 2 weeks ago` | `1 per multiple month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 5974 | `seizures with missed asm doses, typically occurring within 24 to 48 hours of a missed levetiracetam dose` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 5996 | `recent breakthrough events predominantly following lapses in prescribed antiseizure medication` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |

## Slice Details: `frequency_rate_values_unparsed`

- **Description**: Frequency rate facts extracted but count/range/period operands remained unparsed.
- **Row count**: 85
- **Null count**: 59
- **Rendered count**: 26

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Purist Correct | Pragmatic Correct | Normalization Issues |
| ---: | --- | --- | --- | --- | --- | --- |
| 3532 | `generalised tonic to clonic seizures predominantly from sleep with occasional brief absence episodes during the day` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4337 | `3 seizure events on 06 to 03, 06 to 13, 09 to 23 as recorded in the patient’s diary` | `3 per 3 month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4345 | `4 generalised tonic to clonic seizures in july` | `4 per month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4368 | `5 seizure events documented recently` | `5 per 2 month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4562 | `median inter to seizure interval six weeks` | `1 per 6 week` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4563 | `median inter to seizure interval approximately four months` | `1 per 4 month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4574 | `median inter to seizure interval approximately four weeks` | `1 per 4 week` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4592 | `median inter to seizure interval approximately two months` | `1 per 2 month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 4597 | `median inter to seizure interval approximately three weeks` | `1 per 3 week` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 5476 | `sporadic epileptic spasms this year` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 5534 | `a very infrequent, short event 2 weeks ago` | `1 per multiple month` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 5551 | `frequency currently reported as several episodes per day, predominantly focal events, with occasional generalised breakthroughs (approximately once weekly).` | `multiple per day` | `multiple per day` | True | True | `additive_frequency_fallback_to_primary_candidate`, `additive_frequency_period_mismatch`, `frequency_rate_values_unparsed`, `vague_count`, `vague_frequency_with_explicit_time_period` |
| 5791 | `over the past three months they report two brief myoclonic jerks on awakening and one generalised tonic to clonic event at approximately 03:00 in early september, with full recovery by late morning and no injury.` | `1 per month` | `2 per 3 month` | False | True | `additive_frequency_count_unparsed`, `additive_frequency_fallback_to_primary_candidate`, `frequency_rate_values_unparsed` |
| 5974 | `seizures with missed asm doses, typically occurring within 24 to 48 hours of a missed levetiracetam dose` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |
| 5996 | `recent breakthrough events predominantly following lapses in prescribed antiseizure medication` | `unknown` | `NULL` | False | False | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` |

## Slice Details: `seizure_free_duration_required`

- **Description**: Seizure free state extracted but durational boundaries/anchors were missing.
- **Row count**: 75
- **Null count**: 75
- **Rendered count**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Purist Correct | Pragmatic Correct | Normalization Issues |
| ---: | --- | --- | --- | --- | --- | --- |
| 1695 | `no events have been recorded in the current month to date` | `multiple per month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 3118 | `No seizures since last visit` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` |
| 3137 | `no definite seizure events` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `vague_count` |
| 3371 | `no events have occurred in the past eight weeks` | `unknown` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 4842 | `no seizures reported since last appointment` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` |
| 4951 | `no events for many months` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 5040 | `no further episodes suggestive of seizures` | `seizure free for 6 months` | `NULL` | False | False | `seizure_free_duration_required`, `vague_count` |
| 5082 | `a sustained period without any recurrence of her typical events` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 5092 | `No clinical seizures observed since the initial referral` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` |
| 5110 | `no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represent clinical seizures` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `vague_count` |
| 5121 | `denies blackouts, convulsions, brief lapses, or nocturnal events` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 5136 | `No recurrence` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `vague_count` |
| 5197 | `remain seizure-free since the last consultation` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` |
| 5210 | `Seizure freedom continues` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `vague_count` |
| 5345 | `he has been free of events for several months` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `vague_count` |

## Slice Details: `seizure_free_duration_unparsed`

- **Description**: Seizure free state extracted but durational values could not be parsed.
- **Row count**: 37
- **Null count**: 27
- **Rendered count**: 10

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Purist Correct | Pragmatic Correct | Normalization Issues |
| ---: | --- | --- | --- | --- | --- | --- |
| 1695 | `no events have been recorded in the current month to date` | `multiple per month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 2965 | `Last seizure on 03-Sep-2017` | `seizure free for 16 month` | `seizure free for 16 month` | True | True | `seizure_free_anchor_from_last_event_phrase`, `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` |
| 3015 | `no events over the last year` | `seizure free for 12 month` | `seizure free for 12 month` | True | True | `seizure_free_anchor_from_last_event_phrase`, `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` |
| 3371 | `no events have occurred in the past eight weeks` | `unknown` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 4951 | `no events for many months` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 4992 | `Seizure-free interval since 12-Sep-2018` | `seizure free for 11 month` | `seizure free for 11 month` | True | True | `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` |
| 4994 | `seizure-free interval since 25/06/2021` | `seizure free for 6 month` | `seizure free for 6 month` | True | True | `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` |
| 5082 | `a sustained period without any recurrence of her typical events` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 5121 | `denies blackouts, convulsions, brief lapses, or nocturnal events` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 7834 | `No further seizure episodes.` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 7859 | `recent period with essentially no breakthrough events` | `unknown` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 7911 | `Seizures under sustained control` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 7961 | `a sustained period of seizure stability with no impairment of daily activities` | `seizure free for multiple year` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 8006 | `No seizures or breakthrough events over the past six months` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_duration_unparsed` |
| 8079 | `sustained remission since 25 Jan 2019` | `seizure free for 18 month` | `seizure free for 18 month` | True | True | `candidate_role_overlap_removed:supporting_candidate_ids:llm:8079:2:kept_primary_candidate_ids`, `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` |

## Slice Details: `vague_count`

- **Description**: Frequency count is vague (e.g. multiple) but Observation period is explicit.
- **Row count**: 133
- **Null count**: 52
- **Rendered count**: 81

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Purist Correct | Pragmatic Correct | Normalization Issues |
| ---: | --- | --- | --- | --- | --- | --- |
| 278 | `multiple seizures in past week` | `multiple per week` | `multiple per week` | True | True | `vague_count`, `vague_frequency_with_explicit_time_period` |
| 280 | `multiple seizures in past day` | `multiple per day` | `multiple per day` | True | True | `vague_count`, `vague_frequency_with_explicit_time_period` |
| 338 | `many convulsions in past month` | `multiple per month` | `multiple per month` | True | True | `vague_count`, `vague_frequency_with_explicit_time_period` |
| 869 | `several events spread across most months` | `multiple per month` | `multiple per day` | True | True | `vague_count`, `vague_frequency_with_explicit_time_period` |
| 1687 | `several focal seizures last week` | `multiple per week` | `multiple per day` | True | True | `vague_count`, `vague_frequency_with_explicit_time_period` |
| 1706 | `cluster of short events on multiple days over the past month` | `multiple cluster per month, multiple per cluster` | `NULL` | False | False | `cluster_cadence_values_incomplete`, `vague_count` |
| 2094 | `several absence seizures in the past month` | `multiple per month` | `multiple per month` | True | True | `vague_count`, `vague_frequency_with_explicit_time_period` |
| 2114 | `several myoclonic seizures in the past month` | `multiple per month` | `multiple per month` | True | True | `vague_count`, `vague_frequency_with_explicit_time_period` |
| 2907 | `Seizure-free since 27 March 2024` | `seizure free for 6 month` | `seizure free for 6 month` | True | True | `seizure_free_duration_instrumented_from_since_date`, `vague_count` |
| 2932 | `seizure-free since 29/09/2017` | `seizure free for 9 month` | `seizure free for 9 month` | True | True | `seizure_free_duration_instrumented_from_since_date`, `vague_count` |
| 2938 | `Seizure-free since 13-Nov-2015` | `seizure free for 8 month` | `seizure free for 8 month` | True | True | `seizure_free_duration_instrumented_from_since_date`, `vague_count` |
| 2992 | `no seizures since 19-May-2024` | `seizure free for 7 month` | `seizure free for 7 month` | True | True | `seizure_free_duration_instrumented_from_since_date`, `vague_count` |
| 3118 | `No seizures since last visit` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` |
| 3137 | `no definite seizure events` | `seizure free for multiple month` | `NULL` | False | False | `seizure_free_duration_required`, `vague_count` |
| 4690 | `electrographic seizures frequent on eeg (ten/h)` | `multiple per day` | `multiple per day` | True | True | `vague_count` |
