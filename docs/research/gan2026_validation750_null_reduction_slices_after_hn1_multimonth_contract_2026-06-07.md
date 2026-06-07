# Gan 2026 Validation750 Null Reduction Proxy Slices Comparison

baseline validation-development null reduction proxy slices; no holdout use

## Summary of Slices

| Slice Family | Rows | Rendered | Null | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Valid Source IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cluster_cadence_values_incomplete` | 13 | 0 | 13 | 13 | 0 | 0 | 13 | 13 |
| `cluster_frequency_values_unparsed` | 19 | 4 | 15 | 14 | 4 | 4 | 19 | 19 |
| `frequency_rate_values_incomplete` | 53 | 0 | 53 | 3 | 0 | 0 | 53 | 52 |
| `frequency_rate_values_unparsed` | 85 | 31 | 54 | 1 | 27 | 30 | 85 | 84 |
| `seizure_free_duration_required` | 75 | 0 | 75 | 0 | 0 | 0 | 75 | 75 |
| `seizure_free_duration_unparsed` | 37 | 10 | 27 | 0 | 8 | 8 | 37 | 37 |
| `vague_count` | 133 | 81 | 52 | 3 | 61 | 62 | 133 | 133 |

## Slice Details: `cluster_cadence_values_incomplete`

- **Description**: Cluster frequency state extracted but required cadence or size operands were incomplete.
- **Row count**: 13
- **Null count**: 13
- **Rendered count**: 0
- **Routed count**: 13
- **Purist-correct count**: 0
- **Pragmatic-correct count**: 0
- **Exact-trace rows**: 13
- **Valid source-id rows**: 13
- **Trace or source-id gap rows**: 0

### Baseline Comparison

- **Baseline row count**: 18
- **Baseline rendered/null/routed**: 0 / 18 / 18
- **Shared rows**: 13
- **Current-only rows**: 0
- **Baseline-only rows**: 5
- **Wrong-to-correct**: 0
- **Correct-to-wrong**: 0
- **Newly rendered**: 0
- **Newly null**: 0
- **Newly routed**: 0
- **Newly unrouted**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1706 | `cluster of short events on multiple days over the past month` | `multiple cluster per month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `vague_count` | `cluster_axis_ambiguity` |
| 6501 | `brief episodes occurring over 2–3 days` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 9879 | `brief clusters of events over the past three months` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 9937 | `periodic bursts roughly every few weeks` | `1 cluster per month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10434 | `on several mornings each week` | `multiple cluster per week, 2 to 3 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `vague_count` | `cluster_axis_ambiguity` |
| 10542 | `two to four absences per cluster over approximately 1 hour` | `unknown, 2 to 4 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10578 | `three to four focal impaired-awareness seizures per cluster` | `unknown, 3 to 4 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10630 | `several evenings per fortnight with roughly five short-lived spells per cluster` | `multiple cluster per 2 week, 5 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `vague_count` | `cluster_axis_ambiguity` |
| 15242 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 15 month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 15262 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 13 month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 16757 | `recent clusters of brief seizures` | `13 per 6 month` | `NULL` | True | False | False | True | `valid` | `candidate_role_overlap_removed:supporting_candidate_ids:llm:16757:1:kept_primary_candidate_ids`, `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 16839 | `Clusters of 4 seizures in December and February` | `9 per 4 month` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 16907 | `run of six seizures within half an hour` | `9 per 6 month` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |

## Slice Details: `cluster_frequency_values_unparsed`

- **Description**: Cluster frequency state extracted but cluster cadence/size operands remained unparsed.
- **Row count**: 19
- **Null count**: 15
- **Rendered count**: 4
- **Routed count**: 14
- **Purist-correct count**: 4
- **Pragmatic-correct count**: 4
- **Exact-trace rows**: 19
- **Valid source-id rows**: 19
- **Trace or source-id gap rows**: 0

### Baseline Comparison

- **Baseline row count**: 19
- **Baseline rendered/null/routed**: 4 / 15 / 19
- **Shared rows**: 19
- **Current-only rows**: 0
- **Baseline-only rows**: 0
- **Wrong-to-correct**: 0
- **Correct-to-wrong**: 0
- **Newly rendered**: 0
- **Newly null**: 0
- **Newly routed**: 0
- **Newly unrouted**: 5

### Changed rows (first 15 shared rows)

| Row Index | Source Phrase | Gold Label | Baseline Rendered | Current Rendered | Baseline Purist | Current Purist | Baseline Routed | Current Routed |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 3468 | `perimenstrual only (days -2 to +2)` | `unknown` | `NULL` | `NULL` | False | False | True | False |
| 3469 | `perimenstrual clustering` | `unknown` | `NULL` | `NULL` | False | False | True | False |
| 3482 | `Seizures happen when perimenstrual only (days -3 to +3).` | `unknown` | `NULL` | `NULL` | False | False | True | False |
| 3493 | `the attacks cluster around her period` | `unknown` | `NULL` | `NULL` | False | False | True | False |
| 10509 | `clusters arising after nights of curtailed sleep` | `unknown` | `NULL` | `NULL` | False | False | True | False |

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1317 | `multiple short episodes within a single day consistent with typical events` | `unknown, multiple per cluster` | `unknown, multiple per cluster` | True | True | True | True | `valid` | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` | `unresolved_cluster_cadence_with_per_cluster_burden` |
| 3468 | `perimenstrual only (days -2 to +2)` | `unknown` | `NULL` | False | False | False | True | `valid` | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` | - |
| 3469 | `perimenstrual clustering` | `unknown` | `NULL` | False | False | False | True | `valid` | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` | - |
| 3482 | `Seizures happen when perimenstrual only (days -3 to +3).` | `unknown` | `NULL` | False | False | False | True | `valid` | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` | - |
| 3493 | `the attacks cluster around her period` | `unknown` | `NULL` | False | False | False | True | `valid` | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` | - |
| 6501 | `brief episodes occurring over 2–3 days` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 7141 | `recurring mid‑cycle clustering of brief focal-aware episodes` | `unknown` | `unknown, multiple per cluster` | True | True | True | True | `valid` | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` | `unresolved_cluster_cadence_with_per_cluster_burden` |
| 9879 | `brief clusters of events over the past three months` | `unknown` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 9937 | `periodic bursts roughly every few weeks` | `1 cluster per month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10189 | `Clusters occur sporadically; typically 3 or 4 events when they happen; several weeks seizure-free between clusters.` | `unknown, 3 to 4 per cluster` | `unknown, multiple per cluster` | True | True | True | True | `valid` | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` | `unresolved_cluster_cadence_with_per_cluster_burden` |
| 10200 | `Clusters occur sporadically; typically two to four events when they happen.` | `unknown, 2 to 4 per cluster` | `unknown, multiple per cluster` | True | True | True | True | `valid` | `cluster_cadence_unknown_with_per_cluster_burden`, `cluster_frequency_values_unparsed` | `unresolved_cluster_cadence_with_per_cluster_burden` |
| 10509 | `clusters arising after nights of curtailed sleep` | `unknown` | `NULL` | False | False | False | True | `valid` | `cluster_frequency_values_unparsed`, `cyclic_window_pattern_routed` | - |
| 10542 | `two to four absences per cluster over approximately 1 hour` | `unknown, 2 to 4 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 10578 | `three to four focal impaired-awareness seizures per cluster` | `unknown, 3 to 4 per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |
| 15242 | `occasional clusters of myoclonic jerks persisting` | `multiple cluster per 15 month, multiple per cluster` | `NULL` | True | False | False | True | `valid` | `cluster_cadence_values_incomplete`, `cluster_frequency_values_unparsed` | `cluster_axis_ambiguity` |

## Slice Details: `frequency_rate_values_incomplete`

- **Description**: Frequency rate facts extracted but required count/period operands were incomplete.
- **Row count**: 53
- **Null count**: 53
- **Rendered count**: 0
- **Routed count**: 3
- **Purist-correct count**: 0
- **Pragmatic-correct count**: 0
- **Exact-trace rows**: 53
- **Valid source-id rows**: 52
- **Trace or source-id gap rows**: 1

### Baseline Comparison

- **Baseline row count**: 75
- **Baseline rendered/null/routed**: 0 / 75 / 33
- **Shared rows**: 35
- **Current-only rows**: 18
- **Baseline-only rows**: 40
- **Wrong-to-correct**: 0
- **Correct-to-wrong**: 0
- **Newly rendered**: 0
- **Newly null**: 0
- **Newly routed**: 0
- **Newly unrouted**: 0

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3507 | `frequency reduced by 0.3 after dose increase` | `unknown` | `NULL` | True | False | False | True | `valid` | `frequency_rate_values_incomplete`, `relative_change_without_current_baseline` | `relative_only_trend` |
| 3512 | `frequency increased by approximately 20% after dose increase` | `unknown` | `NULL` | True | False | False | True | `valid` | `frequency_rate_values_incomplete`, `relative_change_without_current_baseline` | `relative_only_trend` |
| 3532 | `generalised tonic to clonic seizures predominantly from sleep with occasional brief absence episodes during the day` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4337 | `3 seizure events on 06 to 03, 06 to 13, 09 to 23 as recorded in the patient’s diary` | `3 per 3 month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4345 | `4 generalised tonic to clonic seizures in july` | `4 per month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4368 | `5 seizure events documented recently` | `5 per 2 month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4562 | `median inter to seizure interval six weeks` | `1 per 6 week` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4563 | `median inter to seizure interval approximately four months` | `1 per 4 month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4574 | `median inter to seizure interval approximately four weeks` | `1 per 4 week` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4592 | `median inter to seizure interval approximately two months` | `1 per 2 month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4597 | `median inter to seizure interval approximately three weeks` | `1 per 3 week` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5476 | `sporadic epileptic spasms this year` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5534 | `a very infrequent, short event 2 weeks ago` | `1 per multiple month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5974 | `seizures with missed asm doses, typically occurring within 24 to 48 hours of a missed levetiracetam dose` | `unknown` | `NULL` | True | False | False | True | `invalid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | `selected_source_id_invalid` |
| 5996 | `recent breakthrough events predominantly following lapses in prescribed antiseizure medication` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |

## Slice Details: `frequency_rate_values_unparsed`

- **Description**: Frequency rate facts extracted but count/range/period operands remained unparsed.
- **Row count**: 85
- **Null count**: 54
- **Rendered count**: 31
- **Routed count**: 1
- **Purist-correct count**: 27
- **Pragmatic-correct count**: 30
- **Exact-trace rows**: 85
- **Valid source-id rows**: 84
- **Trace or source-id gap rows**: 1

### Baseline Comparison

- **Baseline row count**: 71
- **Baseline rendered/null/routed**: 24 / 47 / 6
- **Shared rows**: 71
- **Current-only rows**: 14
- **Baseline-only rows**: 0
- **Wrong-to-correct**: 9
- **Correct-to-wrong**: 5
- **Newly rendered**: 11
- **Newly null**: 5
- **Newly routed**: 0
- **Newly unrouted**: 5

### Changed rows (first 15 shared rows)

| Row Index | Source Phrase | Gold Label | Baseline Rendered | Current Rendered | Baseline Purist | Current Purist | Baseline Routed | Current Routed |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 4345 | `4 generalised tonic to clonic seizures in july` | `4 per month` | `4 per month` | `NULL` | True | False | False | False |
| 4368 | `5 seizure events documented recently` | `5 per 2 month` | `5 per 2 month` | `NULL` | True | False | False | False |
| 5551 | `frequency currently reported as several episodes per day, predominantly focal events, with occasional generalised breakthroughs (approximately once weekly).` | `multiple per day` | `NULL` | `multiple per day` | False | True | True | False |
| 5791 | `over the past three months they report two brief myoclonic jerks on awakening and one generalised tonic to clonic event at approximately 03:00 in early september, with full recovery by late morning and no injury.` | `1 per month` | `NULL` | `2 per 3 month` | False | False | True | False |
| 12192 | `she continues to experience drop attack on a daily basis` | `1 per day` | `NULL` | `1 per day` | False | True | True | False |
| 12236 | `she continues to experience absence seizures on a daily basis` | `1 per day` | `NULL` | `1 per day` | False | True | True | False |
| 12751 | `she suffers generalised tonic to clonic seizures twice monthly` | `4 per day` | `NULL` | `2 per month` | False | False | True | False |
| 13051 | `one generalised tonic to clonic seizure 3 weeks ago after 8 months seizure to free on levetiracetam` | `2 per 8 month` | `2 per 8 month` | `NULL` | True | False | False | False |
| 13190 | `seizure to free for 5 months, then 1 focal impaired to awareness seizure` | `1 per 5 month` | `1 per 5 month` | `NULL` | True | False | False | False |
| 13209 | `focal impaired to awareness seizure 2 weeks ago after 8 months seizure to free` | `1 per 8 month` | `1 per 8 month` | `NULL` | True | False | False | False |
| 15129 | `only four brief morning jerks since 3/2015 as per diary` | `4 per 15 month` | `NULL` | `4 per 15 month` | False | True | False | False |
| 16674 | `four short absences in a cluster in april, two brief absences in july, and one in september` | `7 per 6 month` | `NULL` | `7 per 6 month` | False | True | False | False |
| 16697 | `three seizures recorded over six months: september, november, and february` | `3 per 6 month` | `NULL` | `3 per 6 month` | False | True | False | False |
| 16704 | `seven myoclonic jerks documented in september over three months` | `9 per 6 month` | `NULL` | `7 per 3 month` | False | True | False | False |
| 16758 | `3 brief absences in dec, 5 drop attacks in mar, and 1 tonic seizure in apr` | `9 per 5 month` | `NULL` | `9 per 5 month` | False | True | False | False |

### First 15 matching rows:

| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3532 | `generalised tonic to clonic seizures predominantly from sleep with occasional brief absence episodes during the day` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4337 | `3 seizure events on 06 to 03, 06 to 13, 09 to 23 as recorded in the patient’s diary` | `3 per 3 month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4345 | `4 generalised tonic to clonic seizures in july` | `4 per month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4368 | `5 seizure events documented recently` | `5 per 2 month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4562 | `median inter to seizure interval six weeks` | `1 per 6 week` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4563 | `median inter to seizure interval approximately four months` | `1 per 4 month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4574 | `median inter to seizure interval approximately four weeks` | `1 per 4 week` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4592 | `median inter to seizure interval approximately two months` | `1 per 2 month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 4597 | `median inter to seizure interval approximately three weeks` | `1 per 3 week` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5476 | `sporadic epileptic spasms this year` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5534 | `a very infrequent, short event 2 weeks ago` | `1 per multiple month` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |
| 5551 | `frequency currently reported as several episodes per day, predominantly focal events, with occasional generalised breakthroughs (approximately once weekly).` | `multiple per day` | `multiple per day` | False | True | True | True | `valid` | `additive_frequency_fallback_to_primary_candidate`, `additive_frequency_period_mismatch`, `frequency_rate_values_unparsed`, `vague_count`, `vague_frequency_with_explicit_time_period` | - |
| 5791 | `over the past three months they report two brief myoclonic jerks on awakening and one generalised tonic to clonic event at approximately 03:00 in early september, with full recovery by late morning and no injury.` | `1 per month` | `2 per 3 month` | False | False | True | True | `valid` | `additive_frequency_count_unparsed`, `additive_frequency_fallback_to_primary_candidate`, `frequency_rate_values_unparsed` | - |
| 5974 | `seizures with missed asm doses, typically occurring within 24 to 48 hours of a missed levetiracetam dose` | `unknown` | `NULL` | True | False | False | True | `invalid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | `selected_source_id_invalid` |
| 5996 | `recent breakthrough events predominantly following lapses in prescribed antiseizure medication` | `unknown` | `NULL` | False | False | False | True | `valid` | `frequency_rate_values_incomplete`, `frequency_rate_values_unparsed` | - |

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

### Baseline Comparison

- **Baseline row count**: 75
- **Baseline rendered/null/routed**: 0 / 75 / 0
- **Shared rows**: 75
- **Current-only rows**: 0
- **Baseline-only rows**: 0
- **Wrong-to-correct**: 0
- **Correct-to-wrong**: 0
- **Newly rendered**: 0
- **Newly null**: 0
- **Newly routed**: 0
- **Newly unrouted**: 0

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

### Baseline Comparison

- **Baseline row count**: 37
- **Baseline rendered/null/routed**: 10 / 27 / 0
- **Shared rows**: 37
- **Current-only rows**: 0
- **Baseline-only rows**: 0
- **Wrong-to-correct**: 0
- **Correct-to-wrong**: 0
- **Newly rendered**: 0
- **Newly null**: 0
- **Newly routed**: 0
- **Newly unrouted**: 0

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
- **Null count**: 52
- **Rendered count**: 81
- **Routed count**: 3
- **Purist-correct count**: 61
- **Pragmatic-correct count**: 62
- **Exact-trace rows**: 133
- **Valid source-id rows**: 133
- **Trace or source-id gap rows**: 0

### Baseline Comparison

- **Baseline row count**: 133
- **Baseline rendered/null/routed**: 77 / 56 / 7
- **Shared rows**: 133
- **Current-only rows**: 0
- **Baseline-only rows**: 0
- **Wrong-to-correct**: 13
- **Correct-to-wrong**: 0
- **Newly rendered**: 4
- **Newly null**: 0
- **Newly routed**: 0
- **Newly unrouted**: 4

### Changed rows (first 15 shared rows)

| Row Index | Source Phrase | Gold Label | Baseline Rendered | Current Rendered | Baseline Purist | Current Purist | Baseline Routed | Current Routed |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 5551 | `frequency currently reported as several episodes per day, predominantly focal events, with occasional generalised breakthroughs (approximately once weekly).` | `multiple per day` | `NULL` | `multiple per day` | False | True | True | False |
| 5837 | `two myoclonic clusters over the past three weeks` | `2 cluster per 3 week, multiple per cluster` | `2 per 3 week` | `2 cluster per 3 week, multiple per cluster` | False | True | False | False |
| 6889 | `three generalised tonic to clonic seizures in the past six months` | `multiple per week` | `NULL` | `3 per 6 month` | False | False | True | False |
| 10003 | `Weekly morning clusters reported` | `1 cluster per week, multiple per cluster` | `1 per week` | `1 cluster per week, multiple per cluster` | True | True | False | False |
| 10047 | `two clusters this quarter of brief focal aware seizures with left-hand paraesthesias and speech hesitation lasting 30–60 seconds` | `2 cluster per 3 month, multiple per cluster` | `2 per 3 month` | `2 cluster per 3 month, multiple per cluster` | False | True | False | False |
| 10063 | `three clusters this quarter, each lasting 1–2 days with several brief episodes` | `3 cluster per 3 month, multiple per cluster` | `3 per 3 month` | `3 cluster per 3 month, multiple per cluster` | False | True | False | False |
| 10097 | `nocturnal clusters 3×/month` | `3 cluster per month, multiple per cluster` | `3 per month` | `3 cluster per month, multiple per cluster` | False | True | False | False |
| 10237 | `last month ≈4 clusters` | `4 cluster per month, multiple per cluster` | `4 per month` | `4 cluster per month, multiple per cluster` | False | True | False | False |
| 10245 | `last month ≈three clusters` | `3 cluster per month, multiple per cluster` | `3 per month` | `3 cluster per month, multiple per cluster` | False | True | False | False |
| 10487 | `four clusters this month` | `4 cluster per month, multiple per cluster` | `4 per month` | `4 cluster per month, multiple per cluster` | False | True | False | False |
| 10517 | `3–4 nights per week` | `3 to 4 cluster per week, multiple per cluster` | `3 to 4 per week` | `3 to 4 cluster per week, multiple per cluster` | False | True | False | False |
| 10673 | `short bursts around the beginning of most months` | `1 cluster per month, multiple per cluster` | `1 per month` | `1 cluster per month, multiple per cluster` | False | True | False | False |
| 10807 | `two cluster days this month` | `2 cluster per month, multiple per cluster` | `2 per month` | `2 cluster per month, multiple per cluster` | False | True | False | False |
| 10829 | `2 cluster days this month` | `2 cluster per month, multiple per cluster` | `2 per month` | `2 cluster per month, multiple per cluster` | False | True | False | False |
| 10862 | `one cluster this week` | `1 cluster per week, multiple per cluster` | `1 per week` | `1 cluster per week, multiple per cluster` | True | True | False | False |

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
| 4690 | `electrographic seizures frequent on eeg (ten/h)` | `multiple per day` | `multiple per day` | False | True | True | True | `valid` | `vague_count` | - |
