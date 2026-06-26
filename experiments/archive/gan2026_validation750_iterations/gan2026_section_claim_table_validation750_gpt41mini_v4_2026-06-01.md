# Gan 2026 Section Claim Table V4

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Escalation reason: section-claim-table v4 schema replay cleared the 250-row metric and architecture gate enough to measure full-validation generalisation before any holdout use

## Model And Prompt Metadata

- Pipeline: `gan2026_section_claim_table_v4`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first claim extractor and final query selector
- Prompt/program version: `gan2026_section_claim_table_v4`
- Temperature: `0.0`
- Max tokens: `1400`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `250`
- Reuse source: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.jsonl`
- Optimizer: none
- Prompt policy taxonomy: `sct_v4.schema.scalar_enum_output`, `sct_v4.schema.strict_json_object`, `sct_v4.evidence.exact_substring`, `sct_v4.gan_label.parser_ready_surface`, `sct_v4.gan_label.interval_preservation`, `sct_v4.gan_label.cluster_dual_axis`, `sct_v4.selection.current_burden_precedence`, `sct_v4.selection.add_same_window_counts`, `sct_v4.boundary.unknown_no_reference_seizure_free`, `sct_v4.exclusion.proxy_or_conditional_frequency`, `sct_v4.gan_label.compact_interval_notation`, `sct_v4.gan_label.maximum_burden`
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `691903d`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 747 / 750
- Call failures: 0
- Parse/schema/label issues: 3
- Exact claim evidence substrings: 2021 / 2057
- Exact selected final evidence substrings: 723 / 750
- raw final-query score: Purist 0.6827 (512 / 750), Pragmatic 0.7453 (559 / 750)
- Strict-format score: Purist 0.6880 (516 / 750), Pragmatic 0.7520 (564 / 750)
- Frozen clean scorer-facing score: Purist 0.7040 (528 / 750), Pragmatic 0.7693 (577 / 750)
- Rows changed by downstream repair layers: 108

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 21 |
| claim_extraction | 54 |
| temporality_conflict | 7 |
| final_query | 27 |
| parse_schema | 3 |
| scorer_format | 44 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 182 | claim evidence not exact (c2: No use of rescue medication since the last appointment) |  |  |
| 763 | claim evidence not exact (c4: no clear myoclonic jerks or sustained tonic–clonic movements) |  |  |
| 891 | claim evidence not exact (c4: No witnessed generalised tonic–clonic seizures.) |  |  |
| 1317 |  | unparsable_label: 1 cluster per day (Unparsable cluster label: '1 cluster per day') |  |
| 2678 |  | unparsable_label: 1 per night (Unparsable label (raw: '1 per night' / normalized: '1 per night')) |  |
| 3468 | claim evidence not exact (c1: She observes a clear and consistent catamenial pattern: Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free.); selected evidence not exact (She observes a clear and consistent catamenial pattern: Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free.) |  |  |
| 3534 |  | unparsable_label: seizure_free for 6 month (Unparsable label (raw: 'seizure_free for 6 month' / normalized: 'seizure_free for 6 month')) |  |
| 3623 |  | unparsable_label: up to 7 per week (Unparsable label (raw: 'up to 7 per week' / normalized: 'up to 7 per week')) |  |
| 4368 | claim evidence not exact (c5: No family history of seizures reported.) |  |  |
| 4574 | claim evidence not exact (c3: No tongue biting or urinary incontinence reported) |  |  |
| 5210 | claim evidence not exact (c2: No episodes suggestive of absence, myoclonus, or nocturnal events) |  |  |
| 5551 |  | unparsable_label: several per day (Unparsable label (raw: 'several per day' / normalized: 'several per day')) |  |
| 5837 |  | unparsable_label: 1 cluster per 3 week, 1 per 3 week (Unparsable cluster label: '1 cluster per 3 week, 1 per 3 week') |  |
| 5974 | claim evidence not exact (c1: Seizures with missed ASM doses, typically occurring within 24–48 hours of a missed levetiracetam dose) |  |  |
| 5977 |  | unparsable_label: several per 6 week (Unparsable label (raw: 'several per 6 week' / normalized: 'several per 6 week')) |  |
| 6077 |  | unparsable_label: 1 per 1 (Unparsable label (raw: '1 per 1' / normalized: '1 per 1')) |  |
| 6153 | claim evidence not exact (c4: she feels that her seizures are clustering more often) |  |  |
| 6244 | claim evidence not exact (c2: she reports feeling unrefreshed on waking on approximately two mornings per week) |  |  |
| 6368 |  | unparsable_label: 3 to several per 6 week (Unparsable label (raw: '3 to several per 6 week' / normalized: '3 to several per 6 week')) |  |
| 6501 |  | unparsable_label: 1 cluster per 2 to 3 day (Unparsable cluster label: '1 cluster per 2 to 3 day') |  |
| 6738 |  | missing_final_label | schema_validation_error: Extra inputs are not permitted |
| 7141 |  | unparsable_label: 1 cluster per month (Unparsable cluster label: '1 cluster per month') |  |
| 7615 |  | unparsable_label: 3 to 6 per 1 cycle (Unparsable label (raw: '3 to 6 per 1 cycle' / normalized: '3 to 6 per 1 cycle')) |  |
| 7818 | claim evidence not exact (c1: he reports that since titration to levetiracetam 1000 mg twice daily in August 2023, there have been no further events suggestive of seizures); selected evidence not exact (he reports that since titration to levetiracetam 1000 mg twice daily in August 2023, there have been no further events suggestive of seizures) |  |  |
| 7859 | claim evidence not exact (c2: he describes continuing prodromal sensations on two occasions (a brief wave of queasiness and metallic taste, each <30 seconds) without progression to a collapse or witnessed convulsion) |  |  |
| 9103 |  | unparsable_label: infrequent over the past year (Unparsable label (raw: 'infrequent over the past year' / normalized: 'infrequent over the past year')) |  |
| 9344 |  | unparsable_label: several per 1 day (Unparsable label (raw: 'several per 1 day' / normalized: 'several per 1 day')) |  |
| 10003 |  | unparsable_label: 1 cluster per week (Unparsable cluster label: '1 cluster per week') |  |
| 10063 |  | unparsable_label: 1 cluster per 3 month (Unparsable cluster label: '1 cluster per 3 month') |  |
| 10260 | claim evidence not exact (c1: He describes occasional brief morning myoclonic jerks when sleep-deprived) |  |  |
| 10487 |  | unparsable_label: 1 cluster per month (Unparsable cluster label: '1 cluster per month') |  |
| 10630 | claim evidence not exact (c4: he believes the evening clustering of events has become more apparent during this period) |  |  |
| 10673 |  | unparsable_label: 1 cluster per month (Unparsable cluster label: '1 cluster per month') |  |
| 10807 |  | unparsable_label: 1 cluster per month (Unparsable cluster label: '1 cluster per month') |  |
| 10862 |  | unparsable_label: 1 cluster per week (Unparsable cluster label: '1 cluster per week') |  |
| 10865 |  | unparsable_label: 1 cluster per week (Unparsable cluster label: '1 cluster per week') |  |
| 10873 | claim evidence not exact (c7: The events tend to cluster rather than occur singly) | unparsable_label: 1 cluster per week, 6 or more per cluster (Unparsable cluster label: '1 cluster per week, 6 or more per cluster') |  |
| 10902 |  | unparsable_label: 1 cluster per week, 4 or more per cluster (Unparsable cluster label: '1 cluster per week, 4 or more per cluster') |  |
| 11109 |  | unparsable_label: 1 cluster per 2 week, 5 or more per cluster (Unparsable cluster label: '1 cluster per 2 week, 5 or more per cluster') |  |
| 11337 | claim evidence not exact (c2: No absence episodes noticed by the patient or their partner over the past eight weeks) |  |  |
| 11614 | selected evidence not exact (No seizure frequency information present in the note; only AIS preferences and administrative details.) |  |  |
| 11804 | selected evidence not exact (No seizure frequency reference found in the note text.) |  |  |
| 11824 | selected evidence not exact (No seizure frequency references found in the note.) |  |  |
| 11841 |  | missing_final_label | schema_validation_error: Field required |
| 12460 |  | unparsable_label: 1 per day, 2 per year (Unparsable label (raw: '1 per day, 2 per year' / normalized: '1 per day, 2 per year')) |  |
| 12468 |  | unparsable_label: 1 per day, 4 per year (Unparsable label (raw: '1 per day, 4 per year' / normalized: '1 per day, 4 per year')) |  |
| 12551 | claim evidence not exact (c7: rescue: Buccal midazolam 10 mg as required for prolonged convulsive seizures (not used in the last six months)) | unparsable_label: daily (Unparsable label (raw: 'daily' / normalized: 'daily')) |  |
| 12562 |  | unparsable_label: up to 4 per week (Unparsable label (raw: 'up to 4 per week' / normalized: 'up to 4 per week')) |  |
| 12667 |  | missing_final_label | schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 12676 | claim evidence not exact (c2: he has daily absences); selected evidence not exact (he has daily absences) | unparsable_label: daily (Unparsable label (raw: 'daily' / normalized: 'daily')) |  |
| 13114 | claim evidence not exact (c2: she had ... myoclonic jerks leading to a tonic seizure two Saturdays ago) |  |  |
| 13209 |  | unparsable_label: 1 cluster per 4 to 5 week (Unparsable cluster label: '1 cluster per 4 to 5 week') |  |
| 13267 | claim evidence not exact (c3: she had a run of brief myoclonic jerks over the preceding weekend) |  |  |
| 13290 | claim evidence not exact (c1: he did not have seizures for over 6 months, but then reported two generalised tonic-clonic seizures two Fridays ago); selected evidence not exact (he did not have seizures for over 6 months, but then reported two generalised tonic-clonic seizures two Fridays ago) |  |  |
| 13485 | claim evidence not exact (c2: he does not have epilepsy, c3: previous events recorded several years ago were reclassified as non-epileptic (likely stress-related episodes without electrographic correlate)) |  |  |
| 13595 | claim evidence not exact (c1: he is currently in long-term remission, having been seizure free for years); selected evidence not exact (he is currently in long-term remission, having been seizure free for years) |  |  |
| 13608 | claim evidence not exact (c1: he is currently in long-term remission, having been seizure free for years); selected evidence not exact (he is currently in long-term remission, having been seizure free for years) |  |  |
| 13922 | claim evidence not exact (c2: she has not required rescue medication and has not attended emergency services since the dose change) |  |  |
| 14317 | claim evidence not exact (c3: she has maintained seizure freedom since early April); selected evidence not exact (she has maintained seizure freedom since early April) |  |  |
| 14383 | claim evidence not exact (c3: patient to share confirming current seizure-free status since mid-January) |  |  |
| 14662 | selected evidence not exact (His first seizure occurred in May 2024 in Ireland, at night while asleep. The second and third event was in September 2024 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms.) |  |  |
| 15127 |  | unparsable_label: 4 per since last event (Unparsable label (raw: '4 per since last event' / normalized: '4 per since last event')) |  |
| 15168 | claim evidence not exact (c2: he continues to experience brief jumps from time to time) |  |  |
| 15497 | claim evidence not exact (c2: The most recent cluster began during a commercial flight and was preceded by marked travel-related anxiety) |  |  |
| 15503 | claim evidence not exact (c5: He has not required emergency treatment in the past year.) |  |  |
| 15672 |  | unparsable_label: 1 cluster per day (Unparsable cluster label: '1 cluster per day') |  |
| 16162 | claim evidence not exact (c3: Caregivers note occasional brief myoclonic-like jerks not followed by loss of awareness, though these are infrequent and not functionally impairing) |  |  |
| 16204 |  | unparsable_label: 1 in Sep, 1 in Aug, and 3 in Jul (Unparsable label (raw: '1 in sep, 1 in aug, and 3 in jul' / normalized: '1 in sep, 1 in aug, and 3 in jul')) |  |
| 16356 |  | unparsable_label: 1 cluster per 4 day (Unparsable cluster label: '1 cluster per 4 day') |  |
| 16394 |  | unparsable_label: 1 cluster per 2 to 4 day (Unparsable cluster label: '1 cluster per 2 to 4 day') |  |
| 16450 |  | unparsable_label: 1 per several day (Unparsable label (raw: '1 per several day' / normalized: '1 per several day')) |  |
| 16557 |  | unparsable_label: 1 cluster per 2 to 3 day (Unparsable cluster label: '1 cluster per 2 to 3 day') |  |
| 16574 |  | unparsable_label: 1 cluster per 4 day (Unparsable cluster label: '1 cluster per 4 day') |  |
| 16590 |  | unparsable_label: 1 cluster per 4 to 5 day (Unparsable cluster label: '1 cluster per 4 to 5 day') |  |
| 16618 |  | unparsable_label: 1 cluster per 5 day (Unparsable cluster label: '1 cluster per 5 day') |  |
| 16697 | claim evidence not exact (c3: In February another during physiotherapy.) |  |  |
| 16774 | claim evidence not exact (c5: this quarter rescue protocol ... has not been required) |  |  |
| 16839 | claim evidence not exact (c6: clobazam 10 mg at night (additional 10 mg PRN for clusters, used twice since January)) |  |  |
| 17135 |  | unparsable_label: 1 cluster per month (Unparsable cluster label: '1 cluster per month') |  |
| 17167 | claim evidence not exact (c3: No prolonged or status episodes since treatment escalation) |  |  |

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes |  |
| 103 | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per year | yes | yes |  |
| 128 | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | 1 per 7 day | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes | claim_extraction |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes |  |
| 190 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 198 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
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
| 743 | unknown | unknown | unknown | multiple per week | yes | yes |  |
| 744 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 763 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes | claim_extraction |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | yes |  |
| 816 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 849 | 1 per 12 month | 1 per 12 month | 1 per 12 month | 1 per year | yes | yes |  |
| 854 | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes | claim_extraction |
| 899 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 959 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 960 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 978 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 987 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 1030 | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | yes | yes |  |
| 1046 | 5 per month | 5 per month | 5 per month | 3 to 5 per month | no | no |  |
| 1070 | 3 to 4 per 1 week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | 3 to 5 per 1 week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes |  |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | yes |  |
| 1207 | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | yes | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 1281 | 5 to 7 per 1 year | 5 to 7 per year | 5 to 7 per year | 5 to 7 per year | yes | yes |  |
| 1317 | 1 cluster per day | 1 cluster per day | 1 per day | unknown, multiple per cluster |  | no | scorer_format |
| 1357 | 1 per 1 day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 1363 | 3 per 1 day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 1413 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 1454 | 7 per 1 week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 1486 | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 1573 | 11 per 1 week | 11 per week | 11 per week | 11 per week | yes | yes |  |
| 1591 | 11 per 1 month | 11 per month | 11 per month | 11 per month | yes | yes |  |
| 1596 | 12 per 1 week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1597 | 12 per 1 month | 12 per month | 12 per month | 12 per month | yes | yes |  |
| 1636 | 5 per 1 month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1640 | 5 per 1 week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 1687 | unknown | unknown | unknown | multiple per week | yes | yes |  |
| 1694 | 3 per 2 week | 3 per 2 week | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | yes |  |
| 1695 | unknown | unknown | unknown | multiple per month | yes | yes |  |
| 1706 | unknown | unknown | unknown | multiple cluster per month, multiple per cluster | no | no |  |
| 1707 | unknown | unknown | unknown | multiple per week | yes | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | 11 per 6 month | 11 per 6 month | yes | yes |  |
| 1773 | 11 per 3 month | 11 per 3 month | 11 per 3 month | 11 per 3 month | yes | yes |  |
| 1790 | 8 per 4 month | 8 per 4 month | 8 per 4 month | 8 per 4 month | yes | yes |  |
| 1794 | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1866 | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1880 | 7 per 2 month | 7 per 2 month | 7 per 2 month | 8 per 2 month | no | no |  |
| 1887 | 4 per 3 month | 4 per 3 month | 4 per 3 month | 4 per 3 month | yes | yes |  |
| 1914 | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1922 | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1923 | 7 per 6 month | 7 per 6 month | 7 per 6 month | 7 per 6 month | yes | yes |  |
| 1979 | 6 per 2 month | 6 per 2 month | 6 per 2 month | 6 per 2 month | yes | yes |  |
| 1980 | 6 per 3 month | 6 per 3 month | 6 per 3 month | 6 per 3 month | yes | yes |  |
| 2023 | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 2080 | unknown | unknown | unknown | multiple per month | yes | yes |  |
| 2094 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2114 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2149 | unknown | unknown | unknown | unknown | yes | yes |  |
| 2166 | unknown | unknown | unknown | unknown | yes | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | yes |  |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | yes |  |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | yes |  |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | yes | yes |  |
| 2366 | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per year | yes | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | yes | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | yes | yes |  |
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
| 2678 | 1 per night | 1 per day | 1 per day | 1 per day |  | yes | scorer_format |
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
| 2877 | 2 per 1 year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 2887 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 2932 | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | yes | yes |  |
| 2938 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 8 month | yes | yes |  |
| 2965 | seizure free for 1 year 4 month | seizure free for 1 year | seizure free for 1 year | seizure free for 16 month | yes | yes |  |
| 2992 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for 7 month | yes | yes |  |
| 3015 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 12 month | yes | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | yes | yes |  |
| 3095 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 3118 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 3137 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | yes |  |
| 3242 | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3261 | 1 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | no | no |  |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3281 | 8 per 30 day | 8 per 30 day | 8 per 30 day | 8 per month | yes | yes |  |
| 3297 | 6 per 30 day | 6 per 30 day | 6 per 30 day | 6 per month | yes | yes |  |
| 3325 | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 3356 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3371 | seizure free for 8 week | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 3436 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3468 | unknown | unknown | unknown | unknown | yes | yes | claim_extraction,final_query |
| 3469 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | unknown | no | no |  |
| 3482 | 1 per 7 day | 1 per 7 day | 1 per 7 day | unknown | no | no |  |
| 3493 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3507 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3512 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3528 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3532 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3534 | seizure_free for 6 month | seizure_free for 6 month | seizure_free for 6 month | unknown |  |  | scorer_format |
| 3600 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3623 | up to 7 per week | 7 per week | 7 per week | 7 per week |  | yes | scorer_format |
| 3643 | 1 cluster per week, up to 7 per cluster | 1 cluster per week, up to 7 per cluster | 1 cluster per week, up to 7 per cluster | 7 per week | yes | yes |  |
| 3681 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3682 | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3710 | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 3753 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 3766 | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3774 | 9 per 1 year | 9 per year | 9 per year | 9 per year | yes | yes |  |
| 3791 | 10 per 12 month | 10 per 12 month | 10 per 12 month | 10 per year | yes | yes |  |
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
| 4022 | 8 per 3 month | 8 per 3 month | 8 per 3 month | 8 per month | no | no |  |
| 4026 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4116 | 1 to 2 per day | 1 to 2 per day | 1 to 2 per day | 1 per 1 to 2 day | no | no |  |
| 4173 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 4243 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4258 | 4 per 7 day | 4 per 7 day | 4 per 7 day | 4 per week | yes | yes |  |
| 4337 | 3 per 3 month | 3 per 3 month | 3 per 3 month | 3 per 3 month | yes | yes |  |
| 4345 | 4 per 2 week | 4 per 2 week | 4 per 2 week | 4 per month | no | no |  |
| 4368 | 5 per 2 month | 5 per 2 month | 5 per 2 month | 5 per 2 month | yes | yes | claim_extraction |
| 4402 | 1 per month | 1 per month | 1 per month | 7 per 7 month | yes | yes |  |
| 4410 | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 4 per 7 month | yes | yes |  |
| 4478 | 19 per 1 week | 19 per week | 19 per week | 19 per week | yes | yes |  |
| 4480 | 3 to 5 per 1 week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | yes |  |
| 4562 | 1 per 6 week | 1 per 6 week | 1 per 6 week | 1 per 6 week | yes | yes |  |
| 4563 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 4574 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes | claim_extraction |
| 4592 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 4597 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 4624 | 2 per 1 month | 2 per month | 2 per month | 1 per 3 to 4 day | no | no |  |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | yes |  |
| 4690 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4694 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4700 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4709 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4731 | unknown | unknown | unknown | unknown | yes | yes |  |
| 4732 | unknown | unknown | unknown | unknown | yes | yes |  |
| 4771 | 2 per 6 week | 2 per 6 week | 2 per 6 week | unknown | no | no |  |
| 4839 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | seizure free for multiple month | yes | yes |  |
| 4842 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 4910 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes | segmentation_sectioning |
| 4919 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 4951 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 4956 | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 4992 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 11 month | yes | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 months | yes | yes |  |
| 5082 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5092 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5110 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 5121 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 5136 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5141 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | seizure free for multiple month | yes | yes |  |
| 5197 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5210 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes | claim_extraction |
| 5221 | seizure free for 1 year 9 month | seizure free for 1 year | seizure free for 1 year | seizure free for multiple month | yes | yes |  |
| 5248 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 5331 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 5345 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5351 | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 5379 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 5406 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | seizure free for multiple month | yes | yes |  |
| 5476 | 1 per month | 1 per month | 1 per month | unknown | no | no |  |
| 5490 | unknown | unknown | unknown | unknown | yes | yes | segmentation_sectioning |
| 5491 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5504 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5507 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5528 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per month | no | no |  |
| 5534 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per multiple month | no | no | segmentation_sectioning |
| 5551 | several per day | several per day | multiple per day | multiple per day |  | yes | scorer_format |
| 5567 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5584 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5624 | 1 per 10 day | 1 per 10 day | 1 per 10 day | 1 per 10 day | yes | yes |  |
| 5652 | 1 per 8 day | 1 per 8 day | 1 per 8 day | 1 per 8 day | yes | yes |  |
| 5682 | 2 to 4 per month | 2 to 4 per month | 2 to 4 per month | 2 to 4 per month | yes | yes |  |
| 5696 | 3 per 4 month | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 5763 | 2 per 3 month | 2 per 3 month | 2 per 3 month | 2 per month | no | no |  |
| 5767 | 1 per 1 to 2 week | 1 per 1 to 2 week | 1 per 1 to 2 week | 1 per 1 to 2 week | yes | yes |  |
| 5791 | 3 per 3 month | 3 per 3 month | 3 per 3 month | 1 per month | yes | yes |  |
| 5827 | 2 per 2 month | 2 per 2 month | 2 per 2 month | multiple per week | no | no |  |
| 5837 | 1 cluster per 3 week, 1 per 3 week | 1 cluster per 3 week, 1 per 3 week | 1 cluster per 3 week, 1 per 3 week | 2 cluster per 3 week, multiple per cluster |  |  | scorer_format |
| 5866 | 4 per 6 week | 4 per 6 week | 4 per 6 week | 4 per 6 week | yes | yes |  |
| 5873 | 3 per 6 week | 3 per 6 week | 3 per 6 week | multiple per week | no | no |  |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | yes |  |
| 5954 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 5974 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | unknown | no | no | claim_extraction |
| 5977 | several per 6 week | several per 6 week | several per 6 week | unknown |  |  | scorer_format |
| 5995 | 1 cluster per 1 day, 3 per cluster | 1 cluster per day, 3 per cluster | 1 cluster per day, 3 per cluster | 1 per 3 months | no | no |  |
| 5996 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6026 | 3 per 2 month | 3 per 2 month | 3 per 2 month | 3 per 2 month | yes | yes |  |
| 6029 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6034 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6065 | 5 to 7 per 3 month | 5 to 7 per 3 month | 5 to 7 per 3 month | 5 per month | no | no |  |
| 6077 | 1 per 1 | 1 per 1 | 1 per 1 | unknown |  |  | scorer_format |
| 6087 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6094 | 5 per month | 5 per month | 5 per month | 3 per month | no | no |  |
| 6112 | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 6131 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | unknown | no | no |  |
| 6137 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 week | yes | yes |  |
| 6153 | 9 per 4 week | 9 per 4 week | 9 per 4 week | 9 per month | yes | yes | claim_extraction |
| 6180 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 6192 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6204 | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 2 per month | yes | yes |  |
| 6209 | 1 per day | 1 per day | 1 per day | multiple per day | no | no |  |
| 6244 | unknown | unknown | unknown | unknown | yes | yes | claim_extraction |
| 6251 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 1 to 2 month | no | no |  |
| 6273 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6319 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 6321 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6331 | 2 per 6 week | 2 per 6 week | 2 per 6 week | 2 per 6 weeks | yes | yes |  |
| 6358 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for 15 to 16 months | yes | yes |  |
| 6368 | 3 to several per 6 week | 3 to several per 6 week | 3 to several per 6 week | unknown |  |  | scorer_format |
| 6395 | 1 to 2 per month | 1 to 2 per month | 1 to 2 per month | 1 to 2 per month | yes | yes |  |
| 6501 | 1 cluster per 2 to 3 day | 1 cluster per 2 to 3 day | 1 per 2 to 3 day | unknown |  | no | scorer_format |
| 6509 | 2 per 2 week | 2 per 2 week | 2 per 2 week | 1 per week | yes | yes |  |
| 6571 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | unknown | no | no |  |
| 6607 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6684 | 3 per 4 month | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 6701 | 4 per 3 week | 4 per 3 week | 4 per 3 week | 4 per 3 week | yes | yes |  |
| 6738 | None | None | None | 1 per 6 to 8 week |  |  | schema_validation_error: Extra inputs are not permitted; claim_extraction,final_query,parse_schema,scorer_format |
| 6852 | 4 to 6 per month | 4 to 6 per month | 4 to 6 per month | 4 to 6 per month | yes | yes |  |
| 6889 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 6952 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 6967 | unknown | unknown | unknown | unknown | yes | yes |  |
| 6987 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7093 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7126 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7141 | 1 cluster per month | 1 cluster per month | 1 per month | unknown |  | no | scorer_format |
| 7167 | 3 cluster per 6 week, 2 to 4 per cluster | 3 cluster per 6 week, 2 to 4 per cluster | 3 cluster per 6 week, 2 to 4 per cluster | 1 cluster per 2 weeks, 2 to 4 per cluster | yes | yes |  |
| 7168 | 2 per 12 month | 2 per 12 month | 2 per 12 month | unknown | no | no |  |
| 7192 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 7195 | 1 per month | 1 per month | 1 per month | unknown | no | no |  |
| 7196 | 6 per 6 week | 6 per 6 week | 6 per 6 week | 1 per week | yes | yes |  |
| 7198 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7275 | 3 per 12 week | 3 per 12 week | 3 per 12 week | 1 per month | yes | yes |  |
| 7290 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | 1 to 2 per month | 1 to 2 per month | yes | yes |  |
| 7389 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 7401 | 1 cluster per 6 week, 1 to 2 per cluster | 1 cluster per 6 week, 1 to 2 per cluster | 1 cluster per 6 week, 1 to 2 per cluster | 2 cluster per 6 week, 1 to 2 per cluster | no | no |  |
| 7409 | multiple per month | multiple per month | multiple per month | unknown | yes | yes |  |
| 7455 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7475 | 2 per 6 month | 2 per 6 month | 2 per 6 month | 2 per 6 month | yes | yes |  |
| 7491 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7506 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7573 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 7581 | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 7615 | 3 to 6 per 1 cycle | 3 to 6 per 1 cycle | 3 to 6 per 1 cycle | 3 to 7 per month |  |  | scorer_format |
| 7650 | unknown | unknown | unknown | unknown | yes | yes |  |
| 7738 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 7818 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 2 years | yes | yes | claim_extraction,final_query |
| 7834 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 7859 | seizure free for 6 week | seizure free for multiple year | seizure free for multiple year | unknown | no | no | claim_extraction |
| 7872 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7911 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 7961 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for multiple year | yes | yes |  |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | yes |  |
| 8006 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8079 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 18 month | yes | yes |  |
| 8089 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 16 month | yes | yes |  |
| 8124 | seizure free for 13 month | seizure free for 13 month | seizure free for 13 month | seizure free for 13 month | yes | yes |  |
| 8144 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8145 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for 6 month | yes | yes |  |
| 8160 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8180 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8188 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8203 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8224 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 8235 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8264 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | yes | yes |  |
| 8265 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 8354 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 8355 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for multiple year | yes | yes |  |
| 8400 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8419 | 1 to 2 per week | 1 to 2 per week | 1 to 2 per week | 1 to 2 per week | yes | yes |  |
| 8474 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8512 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 8564 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 8577 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8581 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 8593 | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 8596 | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | yes | yes |  |
| 8674 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8724 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 8730 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for 6 month | yes | yes |  |
| 8794 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 8802 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for 12 month | yes | yes |  |
| 8805 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 8808 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | yes | yes |  |
| 8820 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 7 month | yes | yes |  |
| 8835 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | yes | yes |  |
| 8854 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8893 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8922 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8924 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8938 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 10 month | yes | yes |  |
| 8949 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 8969 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9002 | 7 per year | 7 per year | 7 per year | 7 per year | yes | yes |  |
| 9063 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 8 month | yes | yes |  |
| 9103 | infrequent over the past year | infrequent over past year | infrequent over past year | unknown |  |  | scorer_format |
| 9163 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | seizure free for multiple month | yes | yes |  |
| 9190 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 9215 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 9238 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9250 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 9259 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for 1 year | yes | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes | temporality_conflict |
| 9299 | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 9344 | several per 1 day | several per day | multiple per day | multiple per day |  | yes | scorer_format |
| 9365 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 9368 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 9391 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 9397 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 9449 | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | 4 per 6 month | no | no |  |
| 9462 | multiple per month | multiple per month | multiple per month | 7 per 11 month | no | no |  |
| 9496 | 2 per 2 month | 2 per 2 month | 2 per 2 month | 6 per 12 month | no | no |  |
| 9547 | unknown | unknown | unknown | unknown | yes | yes |  |
| 9588 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 9704 | unknown | unknown | unknown | unknown | yes | yes |  |
| 9815 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 9877 | unknown | unknown | unknown | unknown | yes | yes |  |
| 9879 | unknown | unknown | unknown | unknown | yes | yes |  |
| 9888 | unknown | unknown | unknown | unknown | yes | yes |  |
| 9912 | unknown | unknown | unknown | unknown | yes | yes |  |
| 9937 | unknown | unknown | unknown | 1 cluster per month, multiple per cluster | no | no |  |
| 9943 | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | no |  |
| 9955 | 1 per month | 1 per month | 1 per month | 1 cluster per month, multiple per cluster | no | no |  |
| 10003 | 1 cluster per week | 1 cluster per week | 1 per week | 1 cluster per week, multiple per cluster |  | yes | scorer_format |
| 10047 | 2 per 3 month | 2 per 3 month | 2 per 3 month | 2 cluster per 3 month, multiple per cluster | no | no |  |
| 10063 | 1 cluster per 3 month | 1 cluster per 3 month | 1 per 3 month | 3 cluster per 3 month, multiple per cluster |  | no | scorer_format |
| 10097 | 3 per month | 3 per month | 3 per month | 3 cluster per month, multiple per cluster | no | no |  |
| 10147 | unknown | unknown | unknown | unknown | yes | yes |  |
| 10183 | unknown | unknown | unknown | unknown | yes | yes |  |
| 10189 | 1 cluster per unknown interval, 3 to 4 per cluster | 1 cluster per unknown interval, 3 to 4 per cluster | 1 cluster per unknown interval, 3 to 4 per cluster | unknown, 3 to 4 per cluster | yes | yes |  |
| 10200 | 1 cluster per month, 2 to 4 per cluster | 1 cluster per month, 2 to 4 per cluster | 1 cluster per month, 2 to 4 per cluster | unknown, 2 to 4 per cluster | no | no |  |
| 10237 | unknown | unknown | unknown | 4 cluster per month, multiple per cluster | no | no |  |
| 10245 | unknown | unknown | unknown | 3 cluster per month, multiple per cluster | no | no |  |
| 10260 | unknown | unknown | unknown | unknown | yes | yes | claim_extraction |
| 10264 | unknown | unknown | unknown | unknown | yes | yes |  |
| 10266 | unknown | unknown | unknown | unknown | yes | yes |  |
| 10268 | unknown | unknown | unknown | unknown | yes | yes |  |
| 10371 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple year | no | no |  |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | yes |  |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes | yes |  |
| 10434 | multiple per week | multiple per week | multiple per week | multiple cluster per week, 2 to 3 per cluster | no | no |  |
| 10481 | 4 cluster per month, 2 to 3 per cluster | 4 cluster per month, 2 to 3 per cluster | 4 cluster per month, 2 to 3 per cluster | 4 cluster per month, multiple per cluster | yes | yes |  |
| 10487 | 1 cluster per month | 1 cluster per month | 1 per month | 4 cluster per month, multiple per cluster |  | no | scorer_format |
| 10509 | unknown | unknown | unknown | unknown | yes | yes |  |
| 10517 | 1 per 2 to 3 day | 1 per 2 to 3 day | 1 per 2 to 3 day | 3 to 4 cluster per week, multiple per cluster | no | no |  |
| 10542 | 1 cluster per day, 2 to 4 per cluster | 1 cluster per day, 2 to 4 per cluster | 1 cluster per day, 2 to 4 per cluster | unknown, 2 to 4 per cluster | no | no |  |
| 10578 | unknown | unknown | unknown | unknown, 3 to 4 per cluster | yes | yes |  |
| 10583 | unknown | unknown | unknown | unknown, 2 to 3 per cluster | yes | yes |  |
| 10594 | unknown | unknown | unknown | unknown, 2 per cluster | yes | yes |  |
| 10618 | 4 to 6 per day | 4 to 6 per day | 4 to 6 per day | unknown, 4 to 6 per cluster | no | no |  |
| 10629 | unknown | unknown | unknown | unknown | yes | yes |  |
| 10630 | 1 cluster per 2 week, 5 per cluster | 1 cluster per 2 week, 5 per cluster | 1 cluster per 2 week, 5 per cluster | multiple cluster per 2 week, 5 per cluster | yes | yes | claim_extraction |
| 10673 | 1 cluster per month | 1 cluster per month | 1 per month | 1 cluster per month, multiple per cluster |  | no | scorer_format |
| 10677 | 1 per month | 1 per month | 1 per month | 1 cluster per month, multiple per cluster | no | no |  |
| 10753 | unknown | unknown | unknown | unknown | yes | yes |  |
| 10807 | 1 cluster per month | 1 cluster per month | 1 per month | 2 cluster per month, multiple per cluster |  | no | scorer_format |
| 10829 | unknown | unknown | unknown | 2 cluster per month, multiple per cluster | no | no |  |
| 10862 | 1 cluster per week | 1 cluster per week | 1 per week | 1 cluster per week, multiple per cluster |  | yes | scorer_format |
| 10865 | 1 cluster per week | 1 cluster per week | 1 per week | 1 cluster per week, multiple per cluster |  | yes | scorer_format |
| 10873 | 1 cluster per week, 6 or more per cluster | 1 cluster per week, 6 or more per cluster | 1 cluster per week, 6 or more per cluster | 1 cluster per week, 6 per cluster |  |  | claim_extraction,scorer_format |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | yes |  |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | yes |  |
| 10902 | 1 cluster per week, 4 or more per cluster | 1 cluster per week, 4 or more per cluster | 1 cluster per week, 4 or more per cluster | 1 cluster per week, 4 per cluster |  |  | scorer_format |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | yes |  |
| 10942 | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 10965 | 1 cluster per month, 4 to 5 per cluster | 1 cluster per month, 4 to 5 per cluster | 1 cluster per month, 4 to 5 per cluster | 2 cluster per month, 4 to 5 per cluster | yes | yes |  |
| 10967 | 1 cluster per month, 4 to 5 per cluster | 1 cluster per month, 4 to 5 per cluster | 1 cluster per month, 4 to 5 per cluster | 3 cluster per month, 4 to 5 per cluster | yes | yes |  |
| 10984 | 1 cluster per month, 3 to 4 per cluster | 1 cluster per month, 3 to 4 per cluster | 1 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | no | no |  |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | yes |  |
| 11002 | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | yes |  |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | yes |  |
| 11109 | 1 cluster per 2 week, 5 or more per cluster | 1 cluster per 2 week, 5 or more per cluster | 1 cluster per 2 week, 5 or more per cluster | 2 cluster per month, 5 per cluster |  |  | scorer_format |
| 11118 | 1 cluster per month, 6 per cluster | 1 cluster per month, 6 per cluster | 1 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | yes |  |
| 11131 | 1 cluster per 2 week, 3 to 4 per cluster | 1 cluster per 2 week, 3 to 4 per cluster | 1 cluster per 2 week, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | yes |  |
| 11197 | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | yes | yes |  |
| 11216 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | unknown | no | no |  |
| 11254 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | unknown | no | no |  |
| 11259 | unknown | unknown | unknown | unknown | yes | yes |  |
| 11262 | unknown | unknown | unknown | unknown | yes | yes |  |
| 11272 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | unknown | no | no |  |
| 11282 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | unknown | no | no |  |
| 11337 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes | claim_extraction |
| 11350 | multiple per week | multiple per week | multiple per week | unknown | yes | yes |  |
| 11380 | unknown | unknown | unknown | unknown | yes | yes |  |
| 11389 | unknown | unknown | unknown | unknown | yes | yes |  |
| 11400 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11405 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11408 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11409 | unknown | unknown | unknown | no seizure frequency reference | yes | yes |  |
| 11411 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11434 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11562 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11585 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11606 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11614 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11632 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11640 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11658 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11681 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11706 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11711 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11728 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11734 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | segmentation_sectioning |
| 11737 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11752 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11756 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11763 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11804 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11824 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction,final_query |
| 11841 | None | None | None | no seizure frequency reference |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 11852 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes | claim_extraction: no claim rows; segmentation_sectioning,claim_extraction |
| 12036 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12041 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12046 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12051 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12111 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12127 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12130 | 3 per 12 month | 3 per 12 month | 3 per 12 month | multiple per week | no | no |  |
| 12139 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12145 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12192 | multiple per day | multiple per day | multiple per day | 1 per day | no | no |  |
| 12218 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12236 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12246 | 1 to 2 per day | 1 to 2 per day | 1 to 2 per day | 1 to 2 per day | yes | yes |  |
| 12314 | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 12366 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12378 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12383 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12403 | multiple per day | multiple per day | multiple per day | 2 to 3 per day | no | no |  |
| 12412 | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 12422 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12438 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12456 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12460 | 1 per day, 2 per year | 1 per day, 2 per year | 1 per day, 2 per year | 1 per day |  |  | scorer_format |
| 12468 | 1 per day, 4 per year | 1 per day, 4 per year | 1 per day, 4 per year | 1 per day |  |  | scorer_format |
| 12484 | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | yes | yes |  |
| 12502 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12506 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12537 | 3 per week | 3 per week | 3 per week | 1 per day | no | no |  |
| 12548 | 1 per 1 year | 1 per year | 1 per year | 1 per day | no | no |  |
| 12551 | daily | 1 per day | 1 per day | 1 per day |  | yes | claim_extraction,scorer_format |
| 12556 | multiple per week | multiple per week | multiple per week | 1 per day | no | no |  |
| 12562 | up to 4 per week | 4 per week | 4 per week | 1 per day |  | no | scorer_format |
| 12573 | 2 per month | 2 per month | 2 per month | 1 per day | no | no | segmentation_sectioning |
| 12584 | 1 per 3 month | 1 per 3 month | 1 per 3 month | 1 per week | no | no |  |
| 12641 | 2 per week | 2 per week | 2 per week | 1 per day | no | no |  |
| 12665 | 2 per month | 2 per month | 2 per month | 1 per day | no | no |  |
| 12667 | None | None | None | 1 per day |  |  | schema_validation_error: Input should be 'low', 'medium' or 'high'; claim_extraction,final_query,parse_schema,scorer_format |
| 12676 | daily | 1 per day | 1 per day | 1 per day |  | yes | claim_extraction,final_query,scorer_format |
| 12679 | 2 per month | 2 per month | 2 per month | 1 per day | no | no |  |
| 12749 | multiple per day | multiple per day | multiple per day | 3 to 4 per day | no | no |  |
| 12751 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12788 | 6 per year | 6 per year | 6 per year | 6 per 4 month | no | no |  |
| 12810 | 5 per year | 5 per year | 5 per year | 5 per 2 month | no | no |  |
| 12823 | 9 per year | 9 per year | 9 per year | 9 per month | no | no |  |
| 12827 | 5 per year | 5 per year | 5 per year | 5 per 5 month | no | no |  |
| 12835 | unknown | unknown | unknown | 4 per month | no | no |  |
| 12877 | 10 per year | 10 per year | 10 per year | 10 per 4 month | no | no |  |
| 12882 | 7 per year | 7 per year | 7 per year | 7 per 4 month | no | no |  |
| 12901 | 8 per year | 8 per year | 8 per year | 8 per 5 month | no | no |  |
| 12949 | 9 per year | 9 per year | 9 per year | 9 per 6 month | no | no |  |
| 12950 | 7 per year | 7 per year | 7 per year | 7 per 3 month | no | no |  |
| 12963 | seizure free for 10 week | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 12979 | 3 per year | 3 per year | 3 per year | 3 per 4 month | yes | yes |  |
| 13008 | 4 per year | 4 per year | 4 per year | 4 per month | no | no |  |
| 13011 | 3 per year | 3 per year | 3 per year | 3 per 4 month | yes | yes |  |
| 13051 | seizure free for 8 month | seizure free for 8 month | seizure free for 8 month | 2 per 8 month | no | no | temporality_conflict |
| 13058 | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | 2 per 7 month | no | no | temporality_conflict |
| 13114 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | 1 per year | no | no | claim_extraction,temporality_conflict |
| 13122 | 3 per 7 day | 3 per 7 day | 3 per 7 day | 3 per year | no | no |  |
| 13149 | seizure free for 2 week | seizure free for multiple year | seizure free for multiple year | 3 per year | no | no |  |
| 13178 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | 1 per 6 month | no | no | temporality_conflict |
| 13190 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 5 month | no | no |  |
| 13209 | 1 cluster per 4 to 5 week | 1 cluster per 4 to 5 week | 1 per 4 to 5 week | 1 per 8 month |  | no | scorer_format |
| 13267 | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | 2 per 5 month | no | no | claim_extraction |
| 13290 | 2 per 1 week | 2 per week | 2 per week | 4 per 6 month | no | no | claim_extraction,final_query |
| 13327 | seizure free for several years | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | seizure free for 1.5 year | seizure free for 1.5 year | yes | yes |  |
| 13349 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for multiple year | yes | yes |  |
| 13385 | seizure free for 1.5 year | seizure free for 1.5 year | seizure free for 1.5 year | seizure free for 1.5 year | yes | yes |  |
| 13450 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 13471 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 5 year | yes | yes |  |
| 13478 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 13485 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year | yes | yes | claim_extraction |
| 13487 | seizure free for several year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13513 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 1.5 year | yes | yes |  |
| 13574 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year | yes | yes |  |
| 13595 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year | yes | yes | claim_extraction,final_query |
| 13598 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year | yes | yes |  |
| 13608 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year | yes | yes | claim_extraction,final_query |
| 13627 | multiple per month | multiple per month | multiple per month | 64 per 12 month | no | no |  |
| 13635 | multiple per month | multiple per month | multiple per month | 47 per 7 month | no | no |  |
| 13711 | multiple per month | multiple per month | multiple per month | 76 per 12 month | no | no |  |
| 13721 | unknown | unknown | unknown | 77 per 12 month | no | no |  |
| 13732 | unknown | unknown | unknown | 52 per 8 month | no | no |  |
| 13843 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 13858 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 13889 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 13893 | 2 per 1 year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 13922 | 2 per 3 month | 2 per 3 month | 2 per 3 month | unknown | no | no | claim_extraction |
| 14002 | unknown | unknown | unknown | unknown | yes | yes |  |
| 14025 | 2 per 6 week | 2 per 6 week | 2 per 6 week | unknown | no | no |  |
| 14029 | unknown | unknown | unknown | unknown | yes | yes |  |
| 14040 | unknown | unknown | unknown | unknown | yes | yes |  |
| 14076 | unknown | unknown | unknown | unknown | yes | yes |  |
| 14092 | 5 per 3 month | 5 per 3 month | 5 per 3 month | unknown | no | no |  |
| 14096 | 5 per 3 month | 5 per 3 month | 5 per 3 month | unknown | no | no |  |
| 14137 | 3 to 4 per 3 month | 3 to 4 per 3 month | 3 to 4 per 3 month | unknown | no | no |  |
| 14146 | 3 per 2 month | 3 per 2 month | 3 per 2 month | unknown | no | no |  |
| 14187 | seizure free | seizure free for multiple year | seizure free for multiple year | 2 to 3 per month | no | no |  |
| 14214 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | 2 to 4 per month | no | no |  |
| 14250 | seizure free for 3 week | seizure free for multiple year | seizure free for multiple year | 2 per month | no | no |  |
| 14282 | seizure free for 6 week | seizure free for multiple year | seizure free for multiple year | multiple per month | no | no |  |
| 14284 | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per month | no | no |  |
| 14317 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | 4 per 2 month | no | no | claim_extraction,final_query |
| 14332 | 5 per 1 month | 5 per month | 5 per month | 5 per 2 month | no | no |  |
| 14335 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | 3 to 4 per 2 month | no | no |  |
| 14383 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | 3 to 4 per 3 month | no | no | claim_extraction |
| 14454 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | 2 per 2 month | no | no |  |
| 14524 | unknown | unknown | unknown | 2 per 6 month | no | no |  |
| 14530 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 2 per 2 month | no | no |  |
| 14540 | seizure free | seizure free for multiple year | seizure free for multiple year | 2 per 8 month | no | no |  |
| 14562 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 3 per 6 month | no | no |  |
| 14567 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 3 per 3 month | no | no |  |
| 14581 | seizure free | seizure free for multiple year | seizure free for multiple year | 2 per 3 month | no | no |  |
| 14587 | 2 per 3 month | 2 per 3 month | 2 per 3 month | 2 per 3 month | yes | yes |  |
| 14592 | unknown | unknown | unknown | 3 per 5 month | no | no |  |
| 14611 | seizure free for 12 week | seizure free for multiple year | seizure free for multiple year | 2 per 4 month | no | no |  |
| 14628 | unknown | unknown | unknown | 2 per 2 month | no | no |  |
| 14635 | seizure free | seizure free for multiple year | seizure free for multiple year | 5 per 4 month | no | no |  |
| 14645 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | 2 per 6 month | no | no |  |
| 14662 | unknown | unknown | unknown | 3 per 4 month | no | no | final_query |
| 14672 | seizure free | seizure free for multiple year | seizure free for multiple year | 3 per 8 month | no | no |  |
| 14706 | 2 per 5 month | 2 per 5 month | 2 per 5 month | 2 per 5 month | yes | yes |  |
| 14765 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | 1 per month | no | no |  |
| 14806 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | 1 per 2 month | no | no |  |
| 14810 | seizure free for 4 week | seizure free for multiple year | seizure free for multiple year | 1 per month | no | no |  |
| 14821 | seizure free for 3 week | seizure free for multiple year | seizure free for multiple year | 1 per month | no | no |  |
| 14872 | seizure free for 2 week | seizure free for multiple year | seizure free for multiple year | 1 per month | no | no |  |
| 14943 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | 1 per 3 month | no | no |  |
| 14949 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 14965 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | 1 per 3 month | no | no |  |
| 14973 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | 1 per month | no | no |  |
| 15004 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | 1 per 3 month | no | no |  |
| 15012 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | 1 per 2 month | no | no |  |
| 15021 | 1 per 3 month | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 15029 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | 1 per 3 month | no | no |  |
| 15094 | 3 per 2 month | 3 per 2 month | 3 per 2 month | 4 per 13 month | no | no |  |
| 15108 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | 3 to 4 per 15 month | no | no |  |
| 15127 | 4 per since last event | 4 per since last | 4 per since last | 5 per 13 month |  |  | scorer_format |
| 15129 | unknown | unknown | unknown | 4 per 15 month | no | no |  |
| 15141 | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | 4 to 5 per 15 month | no | no |  |
| 15168 | unknown | unknown | unknown | multiple per 15 month | yes | yes | claim_extraction |
| 15193 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | multiple per 13 month | no | no |  |
| 15242 | unknown | unknown | unknown | multiple cluster per 15 month, multiple per cluster | no | no |  |
| 15262 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple cluster per 13 month, multiple per cluster | no | no | temporality_conflict |
| 15267 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | 3 per 14 month | no | no |  |
| 15306 | seizure free for 1 year 3 month | seizure free for 1 year | seizure free for 1 year | 2 to 3 per 15 month | no | no |  |
| 15317 | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | 2 to 3 per 15 month | no | no |  |
| 15376 | 4 to 6 per 1 day | 4 to 6 per day | 4 to 6 per day | 1 cluster per 2 week, 4 to 6 per cluster | no | no |  |
| 15404 | 1 cluster per day, 3 to 4 per cluster | 1 cluster per day, 3 to 4 per cluster | 1 cluster per day, 3 to 4 per cluster | 1 cluster per 4 month, 3 to 4 per cluster | no | no |  |
| 15429 | 1 cluster per day, 4 per cluster | 1 cluster per day, 4 per cluster | 1 cluster per day, 4 per cluster | 1 cluster per 2 month, 4 per cluster | no | no |  |
| 15431 | 1 cluster per day, 5 per cluster | 1 cluster per day, 5 per cluster | 1 cluster per day, 5 per cluster | 1 cluster per 4 month, 5 per cluster | no | no |  |
| 15442 | 2 per 1 day | 2 per day | 2 per day | 1 cluster per 4 day, 2 per cluster | no | no |  |
| 15470 | 2 per 3 month | 2 per 3 month | 2 per 3 month | 1 cluster per 5 day, multiple per cluster | no | no |  |
| 15479 | 1 per 4 to 5 day | 1 per 4 to 5 day | 1 per 4 to 5 day | 1 cluster per 4 to 5 day, 2 per cluster | yes | yes |  |
| 15497 | 1 cluster per 1 day, 5 per cluster | 1 cluster per day, 5 per cluster | 1 cluster per day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | yes | yes | claim_extraction |
| 15503 | 3 to 4 per 1 day | 3 to 4 per day | 3 to 4 per day | 1 cluster per 5 day, 3 to 4 per cluster | no | no | claim_extraction |
| 15513 | 2 to 3 per 1 day | 2 to 3 per day | 2 to 3 per day | 1 cluster per 4 to 5 day, 2 to 3 per cluster | no | no |  |
| 15519 | 1 cluster per 1 day, 3 per cluster | 1 cluster per day, 3 per cluster | 1 cluster per day, 3 per cluster | 1 cluster per 4 day, 3 per cluster | no | no |  |
| 15529 | 1 cluster per day, 4 per cluster | 1 cluster per day, 4 per cluster | 1 cluster per day, 4 per cluster | 1 cluster per 3 day, 4 per cluster | yes | yes |  |
| 15593 | 1 cluster per 6 day, 2 to 4 per cluster | 1 cluster per 6 day, 2 to 4 per cluster | 1 cluster per 6 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | yes |  |
| 15614 | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 15628 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 15639 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 15642 | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 15650 | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | yes | yes |  |
| 15672 | 1 cluster per day | 1 cluster per day | 1 per day | 1 per day |  | yes | scorer_format |
| 15697 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 15715 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 15745 | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 15766 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 15768 | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 15771 | unknown | unknown | unknown | 3 per week | no | no |  |
| 15772 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 15774 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 15783 | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 15802 | 7 per week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 15831 | 2 to 4 per day | 2 to 4 per day | 2 to 4 per day | 2 to 4 per day | yes | yes |  |
| 15834 | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 15964 | 11 per 2 month | 11 per 2 month | 11 per 2 month | 11 per 3 month | no | no |  |
| 15965 | 8 per 2 month | 8 per 2 month | 8 per 2 month | 13 per 2 month | no | no |  |
| 15966 | 5 per 2 month | 5 per 2 month | 5 per 2 month | 5 per 3 month | yes | yes |  |
| 15982 | 8 per 1 month | 8 per month | 8 per month | 9 per 2 month | yes | yes |  |
| 15986 | 5 to 5 per 1 month | 5 to 5 per month | 5 to 5 per month | 11 per 3 month | no | no |  |
| 15992 | 4 to 7 per month | 4 to 7 per month | 4 to 7 per month | 7 per 2 month | no | no |  |
| 15997 | unknown | unknown | unknown | 10 per 3 month | no | no |  |
| 16021 | 5 per month | 5 per month | 5 per month | 9 per 3 month | no | no |  |
| 16041 | 7 per 2 month | 7 per 2 month | 7 per 2 month | 9 per 3 month | yes | yes |  |
| 16084 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 8 per 4 month | no | no |  |
| 16091 | 2 per 1 month | 2 per month | 2 per month | 3 per 3 month | no | no |  |
| 16097 | 6 per month | 6 per month | 6 per month | 17 per 4 month | yes | yes |  |
| 16107 | 4 per month | 4 per month | 4 per month | 8 per 3 month | no | no |  |
| 16108 | 5 to 6 per 1 month | 5 to 6 per month | 5 to 6 per month | 12 per 4 month | no | no |  |
| 16132 | 7 per month | 7 per month | 7 per month | 15 per 3 month | yes | yes |  |
| 16133 | 6 per month | 6 per month | 6 per month | 18 per 4 month | yes | yes |  |
| 16161 | 7 per month | 7 per month | 7 per month | 18 per 3 month | yes | yes |  |
| 16162 | 6 per month | 6 per month | 6 per month | 11 per 3 month | no | no | claim_extraction |
| 16181 | 4 per month | 4 per month | 4 per month | 15 per 4 month | no | no |  |
| 16195 | 6 per month | 6 per month | 6 per month | 16 per 4 month | no | no |  |
| 16203 | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | 9 per 3 month | yes | yes |  |
| 16204 | 1 in Sep, 1 in Aug, and 3 in Jul | 1 in sep, 1 in aug, and 3 in jul | 1 in sep, 1 in aug, and 3 in jul | 5 per 3 month |  |  | scorer_format |
| 16220 | 4 per month | 4 per month | 4 per month | 11 per 4 month | no | no |  |
| 16324 | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | 10 per 3 month | yes | yes |  |
| 16335 | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 16356 | 1 cluster per 4 day | 1 cluster per 4 day | 1 per 4 day | 1 per 4 day |  | yes | scorer_format |
| 16394 | 1 cluster per 2 to 4 day | 1 cluster per 2 to 4 day | 1 per 2 to 4 day | 1 per 2 to 4 day |  | yes | scorer_format |
| 16408 | 1 per 3 day | 1 per 3 day | 1 per 3 day | 1 per 3 day | yes | yes |  |
| 16429 | 1 per 2 to 3 day | 1 per 2 to 3 day | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | yes |  |
| 16432 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 16450 | 1 per several day | 1 per several day | 1 per several day | 1 per multiple day |  |  | scorer_format |
| 16529 | 1 per 5 day | 1 per 5 day | 1 per 5 day | 1 per 5 day | yes | yes |  |
| 16557 | 1 cluster per 2 to 3 day | 1 cluster per 2 to 3 day | 1 per 2 to 3 day | 1 per 2 to 3 day |  | yes | scorer_format |
| 16574 | 1 cluster per 4 day | 1 cluster per 4 day | 1 per 4 day | 1 per 4 day |  | yes | scorer_format |
| 16590 | 1 cluster per 4 to 5 day | 1 cluster per 4 to 5 day | 1 per 4 to 5 day | 1 per 4 to 5 day |  | yes | scorer_format |
| 16618 | 1 cluster per 5 day | 1 cluster per 5 day | 1 per 5 day | 1 per 5 day |  | yes | scorer_format |
| 16645 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 5 per 7 month | no | no | final_query |
| 16674 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 7 per 6 month | no | no |  |
| 16685 | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | 10 per 3 month | yes | yes |  |
| 16697 | 3 per 6 month | 3 per 6 month | 3 per 6 month | 3 per 6 month | yes | yes | claim_extraction |
| 16704 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 9 per 6 month | no | no | temporality_conflict |
| 16714 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 5 per 6 month | no | no |  |
| 16717 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 5 per 6 month | no | no |  |
| 16719 | 1 per week | 1 per week | 1 per week | 7 per 6 month | no | no |  |
| 16728 | 2 per 3 month | 2 per 3 month | 2 per 3 month | 4 per 6 month | yes | yes |  |
| 16750 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | 6 per 7 month | no | no |  |
| 16757 | unknown | unknown | unknown | 13 per 6 month | no | no |  |
| 16758 | 9 per 3 month | 9 per 3 month | 9 per 3 month | 9 per 5 month | yes | yes |  |
| 16772 | 8 per 3 month | 8 per 3 month | 8 per 3 month | 9 per 5 month | yes | yes |  |
| 16774 | unknown | unknown | unknown | 19 per 7 month | no | no | claim_extraction |
| 16780 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 3 per 7 month | no | no |  |
| 16824 | 7 per 1 month | 7 per month | 7 per month | 11 per 5 month | no | no |  |
| 16833 | 5 per 1 month | 5 per month | 5 per month | 8 per 6 month | no | no |  |
| 16839 | unknown | unknown | unknown | 9 per 4 month | no | no | claim_extraction |
| 16867 | 6 per 6 month | 6 per 6 month | 6 per 6 month | 6 per 7 month | no | no |  |
| 16907 | unknown | unknown | unknown | 9 per 6 month | no | no |  |
| 16938 | 2 per 2 month | 2 per 2 month | 2 per 2 month | 2 per week | no | no |  |
| 16947 | 4 per 2 month | 4 per 2 month | 4 per 2 month | 2 per week | no | no |  |
| 16961 | 3 per 3 month | 3 per 3 month | 3 per 3 month | 2 per week | no | no |  |
| 16983 | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 16990 | 4 to 5 per week | 4 to 5 per week | 4 to 5 per week | 4 to 5 per week | yes | yes |  |
| 17001 | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 17003 | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | yes | yes |  |
| 17110 | 1 per 7 day | 1 per 7 day | 1 per 7 day | 4 to 5 cluster per week, multiple per cluster | no | no |  |
| 17135 | 1 cluster per month | 1 cluster per month | 1 per month | 5 cluster per month, multiple per cluster |  | no | scorer_format |
| 17146 | 1 per 6 month | 1 per 6 month | 1 per 6 month | 1 per day | no | no |  |
| 17167 | 1 per 6 month | 1 per 6 month | 1 per 6 month | 1 per week | no | no | claim_extraction |
| 17189 | 1 per 6 month | 1 per 6 month | 1 per 6 month | 1 per month | no | no |  |
| 17200 | 1 per 6 month | 1 per 6 month | 1 per 6 month | 1 per month | no | no |  |
| 17201 | 4 per month | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 17273 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | yes |  |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
