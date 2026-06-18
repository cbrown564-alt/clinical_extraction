# Gan 2026 Validation750 Null Reduction Proxy Slices Baseline

baseline validation-development null reduction proxy slices; no holdout use

## Summary of Slices

| Slice Family | Rows | Rendered | Null | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Valid Source IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cluster_cadence_values_incomplete` | 18 | 0 | 18 | 18 | 0 | 0 | 18 | 18 |
| `cluster_frequency_values_unparsed` | 19 | 4 | 15 | 19 | 4 | 4 | 19 | 19 |
| `frequency_rate_values_incomplete` | 75 | 0 | 75 | 33 | 0 | 0 | 75 | 73 |
| `frequency_rate_values_unparsed` | 71 | 24 | 47 | 6 | 23 | 23 | 71 | 70 |
| `seizure_free_duration_required` | 75 | 0 | 75 | 0 | 0 | 0 | 75 | 75 |
| `seizure_free_duration_unparsed` | 37 | 10 | 27 | 0 | 8 | 8 | 37 | 37 |
| `vague_count` | 133 | 77 | 56 | 7 | 48 | 58 | 133 | 133 |

## Slice Details: `cluster_cadence_values_incomplete`

- **Description**: Cluster frequency state extracted but required cadence or size operands were incomplete.
- **Row count**: 18
- **Null count**: 18
- **Rendered count**: 0
- **Routed count**: 18
- **Purist-correct count**: 0
- **Pragmatic-correct count**: 0
- **Exact-trace rows**: 18
- **Valid source-id rows**: 18
- **Trace or source-id gap rows**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1706 | `cluster of short events on multiple days over the past month` | `multiple cluster per month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `vague_count` | `cluster_axis_ambiguity` |
| 3468 | `perimenstrual only (days -2 to +2)` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 3469 | `perimenstrual clustering` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 3482 | `Seizures happen when perimenstrual only (days -3 to +3).` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 3493 | `the attacks cluster around her period` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 6501 | `brief episodes occurring over 2–3 days` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 9879 | `brief clusters of events over the past three months` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 9937 | `periodic bursts roughly every few weeks` | `1 cluster per month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10434 | `on several mornings each week` | `multiple cluster per week, 2 to 3 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `vague_count` | `cluster_axis_ambiguity` |
| 10509 | `clusters arising after nights of curtailed sleep` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 10542 | `two to four absences per cluster over approximately 1 hour` | `unknown, 2 to 4 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10578 | `three to four focal impaired-awareness seizures per cluster` | `unknown, 3 to 4 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10630 | `several evenings per fortnight with roughly five short-lived spells per cluster` | `multiple cluster per 2 week, 5 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `vague_count` | `cluster_axis_ambiguity` |
| 15242 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 15 month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 15262 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 13 month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |

## Slice Details: `cluster_frequency_values_unparsed`

- **Description**: Cluster frequency state extracted but cluster cadence/size operands remained unparsed.
- **Row count**: 19
- **Null count**: 15
- **Rendered count**: 4
- **Routed count**: 19
- **Purist-correct count**: 4
- **Pragmatic-correct count**: 4
- **Exact-trace rows**: 19
- **Valid source-id rows**: 19
- **Trace or source-id gap rows**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1317 | `multiple short episodes within a single day consistent with typical events` | `unknown, multiple per cluster` | `unknown, multiple per cluster` | True | True | True | True | `valid` | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` | `unresolved_cluster_cadence_with_per_cluster_burden` |
| 3468 | `perimenstrual only (days -2 to +2)` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 3469 | `perimenstrual clustering` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 3482 | `Seizures happen when perimenstrual only (days -3 to +3).` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 3493 | `the attacks cluster around her period` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 6501 | `brief episodes occurring over 2–3 days` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 7141 | `recurring mid‑cycle clustering of brief focal-aware episodes` | `unknown` | `unknown, multiple per cluster` | True | True | True | True | `valid` | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` | `unresolved_cluster_cadence_with_per_cluster_burden` |
| 9879 | `brief clusters of events over the past three months` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 9937 | `periodic bursts roughly every few weeks` | `1 cluster per month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10189 | `Clusters occur sporadically; typically 3 or 4 events when they happen; several weeks seizure-free between clusters.` | `unknown, 3 to 4 per cluster` | `unknown, multiple per cluster` | True | True | True | True | `valid` | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` | `unresolved_cluster_cadence_with_per_cluster_burden` |
| 10200 | `Clusters occur sporadically; typically two to four events when they happen.` | `unknown, 2 to 4 per cluster` | `unknown, multiple per cluster` | True | True | True | True | `valid` | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` | `unresolved_cluster_cadence_with_per_cluster_burden` |
| 10509 | `clusters arising after nights of curtailed sleep` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed`, `cyclic_window_without_event_count` | `cyclic_window_without_event_count` |
| 10542 | `two to four absences per cluster over approximately 1 hour` | `unknown, 2 to 4 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10578 | `three to four focal impaired-awareness seizures per cluster` | `unknown, 3 to 4 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 15242 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 15 month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |

## Slice Details: `frequency_rate_values_incomplete`

- **Description**: Frequency rate facts extracted but required count/period operands were incomplete.
- **Row count**: 75
- **Null count**: 75
- **Rendered count**: 0
- **Routed count**: 33
- **Purist-correct count**: 0
- **Pragmatic-correct count**: 0
- **Exact-trace rows**: 75
- **Valid source-id rows**: 73
- **Trace or source-id gap rows**: 2

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3356 | `brief generalised tonic–clonic seizures occurring exclusively after nights of curtailed sleep over the past three months` | `unknown` | `NULL` | True | False | False | True | `valid` | `conditional_only_trigger_without_baseline`, `frequency_rate_values_incomplete` | `conditional_only_trigger` |
| 3507 | `Frequency reduced by 0.3 after dose increase` | `unknown` | `NULL` | True | False | False | True | `valid` | `frequency_rate_values_incomplete`, `relative_change_without_current_baseline` | `relative_only_trend` |
| 3512 | `Frequency increased by approximately 20% after dose increase` | `unknown` | `NULL` | True | False | False | True | `valid` | `frequency_rate_values_incomplete`, `relative_change_without_current_baseline` | `relative_only_trend` |
| 3532 | `generalised tonic-clonic seizures predominantly from sleep with occasional brief absence episodes during the day` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5476 | `sporadic epileptic spasms this year` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5534 | `a very infrequent, short event a fortnight ago` | `1 per multiple month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5551 | `several episodes per day, predominantly focal events, with occasional generalised breakthroughs approximately once weekly` | `multiple per day` | `NULL` | True | False | False | True | `valid` | `additive_frequency_period_mismatch`, `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed`, `vague_count`, `vague_frequency_with_explicit_time_period` | `mixed_window_or_vague_addition` |
| 5791 | `two brief myoclonic jerks on awakening and one generalised tonic–clonic event over the past three months` | `1 per month` | `NULL` | True | False | False | True | `valid` | `additive_frequency_count_unparsed`, `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | `mixed_window_or_vague_addition` |
| 5974 | `Seizures with missed ASM doses, typically occurring within 24–48 hours of a missed levetiracetam dose` | `unknown` | `NULL` | True | False | False | True | `invalid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | `selected_source_id_invalid` |
| 5996 | `Recent breakthrough events predominantly following lapses in prescribed antiseizure medication` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 6029 | `Ongoing focal seizures less frequent between clusters but not absent` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 6077 | `one breakthrough seizure on 12/09/2025` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 6131 | `infrequent generalised seizures provoked by patterned or flickering visual stimuli` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 6209 | `daily brief events and 2–3 longer episodes per month` | `multiple per day` | `NULL` | True | False | False | True | `valid` | `additive_frequency_period_mismatch`, `frequency_rate_values_incomplete` | `mixed_window_or_vague_addition` |
| 6889 | `brief morning myoclonic jerks several times per week; three generalised tonic–clonic seizures in the past six months; once every 2–3 weeks` | `multiple per week` | `NULL` | True | False | False | True | `valid` | `additive_frequency_period_mismatch`, `frequency_rate_values_incomplete`, `vague_count`, `vague_frequency_with_explicit_time_period` | `mixed_window_or_vague_addition` |

## Slice Details: `frequency_rate_values_unparsed`

- **Description**: Frequency rate facts extracted but count/range/period operands remained unparsed.
- **Row count**: 71
- **Null count**: 47
- **Rendered count**: 24
- **Routed count**: 6
- **Purist-correct count**: 23
- **Pragmatic-correct count**: 23
- **Exact-trace rows**: 71
- **Valid source-id rows**: 70
- **Trace or source-id gap rows**: 1

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3532 | `generalised tonic-clonic seizures predominantly from sleep with occasional brief absence episodes during the day` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4345 | `Seizure events on 07-03, 07-07, 07-10, 07-18 were documented, each described as brief generalised tonic–clonic episodes lasting under 2 minutes, with post-ictal fatigue for several hours and no tongue biting reported on two of the dates.` | `4 per month` | `4 per month` | False | True | True | True | `valid` | `frequency_rate_values_repaired_from_primary_candidate`, `frequency_rate_values_unparsed` | - |
| 4368 | `Regarding recent frequency, the seizure diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.` | `5 per 2 month` | `5 per 2 month` | False | True | True | True | `valid` | `frequency_rate_values_repaired_from_primary_candidate`, `frequency_rate_values_unparsed` | - |
| 5476 | `sporadic epileptic spasms this year` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5534 | `a very infrequent, short event a fortnight ago` | `1 per multiple month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5551 | `several episodes per day, predominantly focal events, with occasional generalised breakthroughs approximately once weekly` | `multiple per day` | `NULL` | True | False | False | True | `valid` | `additive_frequency_period_mismatch`, `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed`, `vague_count`, `vague_frequency_with_explicit_time_period` | `mixed_window_or_vague_addition` |
| 5791 | `two brief myoclonic jerks on awakening and one generalised tonic–clonic event over the past three months` | `1 per month` | `NULL` | True | False | False | True | `valid` | `additive_frequency_count_unparsed`, `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | `mixed_window_or_vague_addition` |
| 5974 | `Seizures with missed ASM doses, typically occurring within 24–48 hours of a missed levetiracetam dose` | `unknown` | `NULL` | True | False | False | True | `invalid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | `selected_source_id_invalid` |
| 5996 | `Recent breakthrough events predominantly following lapses in prescribed antiseizure medication` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 6029 | `Ongoing focal seizures less frequent between clusters but not absent` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 6077 | `one breakthrough seizure on 12/09/2025` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 6131 | `infrequent generalised seizures provoked by patterned or flickering visual stimuli` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 6952 | `clips recorded on the family phone over the last eight weeks indicate brief generalised episodes occurring approximately twice weekly` | `2 per week` | `2 per week` | False | True | True | True | `valid` | `frequency_rate_values_repaired_from_primary_candidate`, `frequency_rate_values_unparsed` | - |
| 7126 | `recurring mid-cycle surge in episodes approximately 10–14 days after menses onset` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 7168 | `intermittent morning myoclonic jerks day-to-day` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |

## Slice Details: `seizure_free_duration_required`

- **Description**: Seizure free state extracted but durational boundaries/anchors were missing.
- **Row count**: 75
- **Null count**: 75
- **Rendered count**: 0
- **Routed count**: 0
- **Purist-correct count**: 0
- **Pragmatic-correct count**: 0
- **Exact-trace rows**: 75
- **Valid source-id rows**: 75
- **Trace or source-id gap rows**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1695 | `no events have been recorded in the current month to date` | `multiple per month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 3118 | `No seizures since last visit` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` | - |
| 3137 | `no definite seizure events` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `vague_count` | - |
| 3371 | `no events have occurred in the past eight weeks` | `unknown` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 4842 | `no seizures reported since last appointment` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` | - |
| 4951 | `no events for many months` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 5040 | `no further episodes suggestive of seizures` | `seizure free for 6 months` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `vague_count` | - |
| 5082 | `a sustained period without any recurrence of her typical events` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 5092 | `No clinical seizures observed since the initial referral` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` | - |
| 5110 | `no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represent clinical seizures` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `vague_count` | - |
| 5121 | `denies blackouts, convulsions, brief lapses, or nocturnal events` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 5136 | `No recurrence` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `vague_count` | - |
| 5197 | `remain seizure-free since the last consultation` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` | - |
| 5210 | `Seizure freedom continues` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `vague_count` | - |
| 5345 | `he has been free of events for several months` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `vague_count` | - |

## Slice Details: `seizure_free_duration_unparsed`

- **Description**: Seizure free state extracted but durational values could not be parsed.
- **Row count**: 37
- **Null count**: 27
- **Rendered count**: 10
- **Routed count**: 0
- **Purist-correct count**: 8
- **Pragmatic-correct count**: 8
- **Exact-trace rows**: 37
- **Valid source-id rows**: 37
- **Trace or source-id gap rows**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1695 | `no events have been recorded in the current month to date` | `multiple per month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 2965 | `Last seizure on 03-Sep-2017` | `seizure free for 16 month` | `seizure free for 16 month` | False | True | True | True | `valid` | `seizure_free_anchor_from_last_event_phrase`, `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` | - |
| 3015 | `no events over the last year` | `seizure free for 12 month` | `seizure free for 12 month` | False | True | True | True | `valid` | `seizure_free_anchor_from_last_event_phrase`, `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` | - |
| 3371 | `no events have occurred in the past eight weeks` | `unknown` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 4951 | `no events for many months` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 4992 | `Seizure-free interval since 12-Sep-2018` | `seizure free for 11 month` | `seizure free for 11 month` | False | True | True | True | `valid` | `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` | - |
| 4994 | `seizure-free interval since 25/06/2021` | `seizure free for 6 month` | `seizure free for 6 month` | False | True | True | True | `valid` | `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` | - |
| 5082 | `a sustained period without any recurrence of her typical events` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 5121 | `denies blackouts, convulsions, brief lapses, or nocturnal events` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 7834 | `No further seizure episodes.` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 7859 | `recent period with essentially no breakthrough events` | `unknown` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 7911 | `Seizures under sustained control` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 7961 | `a sustained period of seizure stability with no impairment of daily activities` | `seizure free for multiple year` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 8006 | `No seizures or breakthrough events over the past six months` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_duration_unparsed` | - |
| 8079 | `sustained remission since 25 Jan 2019` | `seizure free for 18 month` | `seizure free for 18 month` | False | True | True | True | `valid` | `candidate_role_overlap_removed:supporting_candidate_ids:llm:8079:2:kept_primary_candidate_ids`, `seizure_free_duration_instrumented_from_since_date`, `seizure_free_duration_unparsed` | - |

## Slice Details: `vague_count`

- **Description**: Frequency count is vague (e.g. multiple) but Observation period is explicit.
- **Row count**: 133
- **Null count**: 56
- **Rendered count**: 77
- **Routed count**: 7
- **Purist-correct count**: 48
- **Pragmatic-correct count**: 58
- **Exact-trace rows**: 133
- **Valid source-id rows**: 133
- **Trace or source-id gap rows**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 278 | `multiple seizures in past week` | `multiple per week` | `multiple per week` | False | True | True | True | `valid` | `vague_count`, `vague_frequency_with_explicit_time_period` | - |
| 280 | `multiple seizures in past day` | `multiple per day` | `multiple per day` | False | True | True | True | `valid` | `vague_count`, `vague_frequency_with_explicit_time_period` | - |
| 338 | `many convulsions in past month` | `multiple per month` | `multiple per month` | False | True | True | True | `valid` | `vague_count`, `vague_frequency_with_explicit_time_period` | - |
| 869 | `several events spread across most months` | `multiple per month` | `multiple per day` | False | True | True | True | `valid` | `vague_count`, `vague_frequency_with_explicit_time_period` | - |
| 1687 | `several focal seizures last week` | `multiple per week` | `multiple per day` | False | True | True | True | `valid` | `vague_count`, `vague_frequency_with_explicit_time_period` | - |
| 1706 | `cluster of short events on multiple days over the past month` | `multiple cluster per month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `vague_count` | `cluster_axis_ambiguity` |
| 2094 | `several absence seizures in the past month` | `multiple per month` | `multiple per month` | False | True | True | True | `valid` | `vague_count`, `vague_frequency_with_explicit_time_period` | - |
| 2114 | `several myoclonic seizures in the past month` | `multiple per month` | `multiple per month` | False | True | True | True | `valid` | `vague_count`, `vague_frequency_with_explicit_time_period` | - |
| 2907 | `Seizure-free since 27 March 2024` | `seizure free for 6 month` | `seizure free for 6 month` | False | True | True | True | `valid` | `seizure_free_duration_instrumented_from_since_date`, `vague_count` | - |
| 2932 | `seizure-free since 29/09/2017` | `seizure free for 9 month` | `seizure free for 9 month` | False | True | True | True | `valid` | `seizure_free_duration_instrumented_from_since_date`, `vague_count` | - |
| 2938 | `Seizure-free since 13-Nov-2015` | `seizure free for 8 month` | `seizure free for 8 month` | False | True | True | True | `valid` | `seizure_free_duration_instrumented_from_since_date`, `vague_count` | - |
| 2992 | `no seizures since 19-May-2024` | `seizure free for 7 month` | `seizure free for 7 month` | False | True | True | True | `valid` | `seizure_free_duration_instrumented_from_since_date`, `vague_count` | - |
| 3118 | `No seizures since last visit` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `seizure_free_since_date_anchor_unparsed`, `vague_count` | - |
| 3137 | `no definite seizure events` | `seizure free for multiple month` | `NULL` | False | False | False | True | `valid` | `seizure_free_duration_required`, `vague_count` | - |
| 4690 | `Electrographic seizures frequent on EEG (~ten/h)` | `multiple per day` | `multiple per day` | False | True | True | True | `valid` | `vague_count` | - |
