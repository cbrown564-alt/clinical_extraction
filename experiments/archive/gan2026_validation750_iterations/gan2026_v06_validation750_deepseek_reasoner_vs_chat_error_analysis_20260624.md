# Gan 2026 v0.6 DeepSeek Reasoner vs Chat Validation750 Error Analysis

Date: 2026-06-24

This is a validation-only development analysis on `gan2026_split_v1`. It was created because the frozen test450 aggregate showed the DeepSeek reasoner/thinking condition underperforming the non-reasoning DeepSeek chat condition, but test row-level inspection remains out of bounds for development.

## Compared Artifacts

- Reasoner/thinking validation750: `experiments\gan2026_v06_validation750_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260624.jsonl`
- Non-reasoning chat validation750 comparator: `experiments\gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.jsonl`
- Transition ledger: `experiments\gan2026_v06_validation750_deepseek_reasoner_vs_chat_transition_ledger_20260624.csv`
- Machine-readable summary: `experiments\gan2026_v06_validation750_deepseek_reasoner_vs_chat_error_analysis_20260624.json`

The reasoner validation750 artifact was resumed from the completed validation250 prefix. The first 250 rows are the 2026-06-23 validation250 artifact; rows 251-750 were newly run on 2026-06-24.

## Aggregate Readout

| Run | Rows | Structured | Parse issues | Evidence exact | Rows repaired | Purist | Pragmatic |
| --- | --- | --- | --- | --- | --- | --- | --- |
| non-reasoning chat validation750 | 750 | 745/750 | 5 | 719/750 | 500 | 622/750 (0.829) | 646/750 (0.861) |
| reasoner thinking validation750 | 750 | 745/750 | 5 | 731/750 | 415 | 616/750 (0.821) | 649/750 (0.865) |
| non-reasoning chat test450 aggregate | 450 | 446/450 | 4 | 440/450 | 307 | 354/450 (0.787) | 368/450 (0.818) |
| reasoner thinking test450 aggregate | 450 | 447/450 | 3 | 441/450 | 257 | 345/450 (0.767) | 365/450 (0.811) |

Validation mirrors the holdout direction but not a dramatic collapse: reasoner is 616/750 Purist-correct versus chat 622/750, a net -6 rows. On the locked test aggregate only, reasoner is 345/450 versus chat 354/450, a net -9 rows. Row-level explanation below uses validation only.

## Side-by-Side Transition Accounting

| Transition | Rows | Interpretation |
| --- | --- | --- |
| C->C | 558 | both correct |
| C->W | 64 | reasoner regression |
| W->C | 58 | reasoner rescue |
| W->W | 70 | both wrong |

The reasoner changed the final normalized label on 249/750 rows and changed the final semantic kind on 103/750 rows. The score difference is small because the changes nearly cancel: 64 chat-correct rows became wrong, while 58 chat-wrong rows became correct.

## Main Finding

The reasoner does not fail because of transport, schema validity, evidence validity, or a uniformly worse parser interaction. It produces slightly more exact evidence (731/750 vs 719/750), fewer repaired rows (415 vs 500), and the same number of structured records (745/750). The deficit is semantic selection churn: the thinking model often chooses a different abstraction for the same note, especially demoting frequency-like cluster/range evidence to `unknown`, while also rescuing some seizure-free boundary cases that chat mishandles.

## Slices

### By Validation Order

| Slice | C->C | C->W | W->C | W->W | Net reasoner |
| --- | --- | --- | --- | --- | --- |
| 001-250 | 225 | 12 | 7 | 6 | -5 |
| 251-500 | 186 | 15 | 17 | 32 | 2 |
| 501-750 | 147 | 37 | 34 | 32 | -3 |

### By Gold Label Kind

| Slice | C->C | C->W | W->C | W->W | Net reasoner |
| --- | --- | --- | --- | --- | --- |
| frequency | 330 | 49 | 38 | 51 | -11 |
| no_reference | 17 | 4 | 4 | 2 | 0 |
| seizure_free | 92 | 5 | 11 | 4 | 6 |
| unknown | 78 | 5 | 4 | 13 | -1 |
| unresolved_multiple | 41 | 1 | 1 | 0 | 0 |

### By row_ok Flag

| Slice | C->C | C->W | W->C | W->W | Net reasoner |
| --- | --- | --- | --- | --- | --- |
| False | 19 | 7 | 4 | 2 | -3 |
| True | 539 | 57 | 54 | 68 | -3 |

## Failure-Family Tags

Tags are heuristic and overlapping; they are meant to locate the failure pressure, not replace row review.

| Outcome | cluster | seizure-free | unknown/no-ref | range/multiple | rate/window | semantic kind shift |
| --- | --- | --- | --- | --- | --- | --- |
| C->W | 29 | 52 | 42 | 42 | 56 | 21 |
| W->C | 26 | 42 | 31 | 44 | 48 | 16 |
| W->W | 50 | 63 | 49 | 62 | 65 | 16 |

The most important asymmetry is by gold kind: ordinary `frequency` rows are net -11 for the reasoner (49 regressions, 38 rescues), while `seizure_free` rows are net +6 (5 regressions, 11 rescues). So the reasoning model appears better at some remission/date-boundary cases but worse at preserving countable frequency evidence, especially when cluster or interval language is awkward.

## Final-Kind Shifts

Top changed-kind transitions, including outcome:

| Chat kind | Reasoner kind | Outcome | Rows |
| --- | --- | --- | --- |
| frequency | unknown | C->C | 45 |
| frequency | unknown | C->W | 9 |
| seizure_free | frequency | W->W | 7 |
| no_reference | seizure_free | W->C | 5 |
| no_reference |  | C->W | 4 |
| frequency | unknown | W->C | 3 |
| frequency | unknown | W->W | 3 |
| seizure_free | unknown | W->C | 2 |
| seizure_free | unknown | C->W | 2 |
| unresolved_multiple | frequency | W->W | 2 |
|  | no_reference | W->C | 2 |
| no_reference | unknown | C->C | 2 |
| frequency | seizure_free | C->W | 2 |
| seizure_free | frequency | W->C | 2 |
| seizure_free | frequency | C->C | 2 |

The dominant shift is `frequency -> unknown` (60 rows overall across outcomes). This is the strongest validation explanation for the holdout surprise: thinking seems more conservative about whether a structured event supports a countable frequency, but that conservatism is not selectively calibrated enough to improve Purist F1.

## Confidence Is Not A Useful Gate Here

| Outcome | High | Medium | Low | Blank |
| --- | --- | --- | --- | --- |
| C->C | 481 | 75 | 2 | 0 |
| C->W | 51 | 9 | 0 | 4 |
| W->C | 54 | 3 | 1 | 0 |
| W->W | 52 | 17 | 0 | 1 |

Reasoner regressions are usually high confidence (51/64), and rescues are also usually high confidence (54/58). The in-pass confidence field does not separate helpful from harmful changes.

## Representative Reasoner Regressions (Validation Only)

| Row | Gold | Chat | Reasoner | Outcome | Tags | Reasoner evidence/rationale |
| --- | --- | --- | --- | --- | --- | --- |
| 14567 | 3 per 3 month | 3 per 3 month | unknown | C->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | Her second and third seizure was in January 2018 / The note describes three past seizures but does not provide a current or recent seizure frequency. |
| 14806 | 1 per 2 month | 1 per 2 month | no seizure frequency reference | C->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | recent short-lived cluster of aura-like events / Recent cluster event indicates active seizure activity; adjacent seizure-free period of 2 months doe... |
| 16645 | 5 per 7 month | 5 per 7 month | 5 per 4 month | C->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | He had a cluster of three seizures in August (short, not full convulsions, fluctuating awareness, self-terminating). In November he had a nocturnal s... |
| 16780 | 3 per 7 month | 3 per 7 month | unknown | C->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | A prolonged event occurred in Jan (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously). In Apr she h... |
| 12751 | 4 per day | 4 per day | seizure free for multiple year | C->W | cluster_or_cluster_burden;seizure_free_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | No seizures have been noted since her previous review / The note explicitly states no seizures since last review, which is the most current status; b... |
| 10542 | unknown, 2 to 4 per cluster | unknown | 2 per 3 month | C->W | cluster_or_cluster_burden;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | frequency not tracked / The note explicitly states that the frequency of absence clusters is not tracked, and no overall seizure count is provided. A... |
| 8144 | seizure free for multiple month | seizure free for multiple year | unknown | C->W | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | occasional brief déjà vu sensations / Patient has ongoing mild auras with unknown frequency while disabling seizures are absent. Since other current ... |
| 11405 | no seizure frequency reference | no seizure frequency reference |  | C->W | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;semantic_kind_shift;label_changed;parse_schema_issue;evidence_validity_shift | / |
| 14092 | unknown | no seizure frequency reference | 1 per 3 month | C->W | seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | the last reported on 7 April / The most recent seizure event was a myoclonic jerk on 7 April 2017; no tonic–clonic events occurred, and no current se... |
| 14562 | 3 per 6 month | 3 per 6 month | unknown | C->W | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | Her second and third seizure was in July 2021 / Two seizures in July 2021 with a short seizure-free interval (approximately one month) do not represe... |
| 14587 | 2 per 3 month | 2 per 3 month | unknown | C->W | seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | Two nocturnal events within three months / The note describes two isolated seizures within three months but no ongoing seizure frequency. Therefore t... |
| 14592 | 3 per 5 month | 3 per 5 month | unknown | C->W | seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | The second and third event was in June 2024 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms. / No explicit se... |
| 14965 | 1 per 3 month | 1 per 3 month | unknown | C->W | seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | The last such episode occurred on 20/May and she has been stable since. / Last focal aware seizure on 20/May 2015; patient stable since; no current f... |
| 15129 | 4 per 15 month | 4 per 15 month | unknown | C->W | seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | only four brief morning jerks since 3/2015 as per diary. / Only four morning jerks since last tonic-clonic in 3/2015; frequency not specified as a ra... |

## Representative Reasoner Rescues (Validation Only)

| Row | Gold | Chat | Reasoner | Outcome | Tags | Reasoner evidence/rationale |
| --- | --- | --- | --- | --- | --- | --- |
| 8180 | seizure free for multiple month | no seizure frequency reference | seizure free for 6 month | W->C | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;semantic_kind_shift;label_changed | he has not described any further events suggestive of seizures / Patient reports no seizures since last review in April, and examination is normal. N... |
| 9250 | seizure free for multiple month | no seizure frequency reference | seizure free for multiple year | W->C | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;semantic_kind_shift;label_changed | there have been essentially no clear-cut events to suggest recent seizures / The patient reports no definitive seizures since last seen in January 20... |
| 10371 | seizure free for multiple year | no seizure frequency reference | seizure free for multiple year | W->C | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;semantic_kind_shift;label_changed | Prior cluster pattern resolved since 11 Aug 2023 / Patient has been seizure-free since August 2023 with no current seizure activity reported. |
| 13051 | 2 per 8 month | seizure free for multiple year | 2 per 8 month | W->C | cluster_or_cluster_burden;seizure_free_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | before experiencing a generalised tonic-clonic seizure 3 Tuesdays ago, preceded by a cluster of absences. / Recent breakthrough with one GTC and one ... |
| 14187 | 2 to 3 per month | 1 per 1 month | 2 to 3 per month | W->C | cluster_or_cluster_burden;seizure_free_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | 2 to 3 seizures / The patient recently had 2 to 3 seizures after discontinuing valproate. Although now seizure-free, the short interval does not over... |
| 3534 | unknown | seizure free for 7 month | unknown | W->C | seizure_free_boundary;unknown_or_no_reference_boundary;semantic_kind_shift;label_changed | she describes her seizure control as Better over the past seven months / No explicit seizure frequency is provided; the note mentions improved contro... |
| 5110 | seizure free for multiple month | no seizure frequency reference | seizure free for 3 month | W->C | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;semantic_kind_shift;label_changed | Across this interval, there have been no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represent ... |
| 5406 | seizure free for multiple month | no seizure frequency reference | seizure free for 2 month | W->C | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;semantic_kind_shift;label_changed | no definite epileptic events documented in this interval / The note explicitly states no definite epileptic events in the past two months, indicating... |
| 5534 | 1 per multiple month | 1 per 2 week | unknown | W->C | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | a very infrequent, short event a fortnight ago / The note reports a single brief absence-like seizure two weeks ago, with no clear frequency rate. Th... |
| 11337 | unknown | 1 per 6 month | unknown | W->C | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | one breakthrough event: the patient reported having a seizure on 06-Nov / One GTC seizure on 06-Nov is the most recent seizure; no ongoing frequency;... |
| 11389 | unknown | seizure free for 2 month | unknown | W->C | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;semantic_kind_shift;label_changed | single recent event and otherwise good control / Single seizure reported 2 months prior; frequency not explicitly quantified as a rate; described as ... |
| 13178 | 1 per 6 month | 1 per 2 week | 1 per 6 month | W->C | seizure_free_boundary;unknown_or_no_reference_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | until a focal impaired-awareness seizure occurred 2 Thursdays ago / Single recent seizure after a 6-month seizure-free period; no ongoing frequency p... |
| 16220 | 11 per 4 month | 11 per 2 month | 11 per 4 month | W->C | seizure_free_boundary;rate_denominator_or_window;semantic_kind_shift;label_changed | 4 in February / Selected the most recent non-zero frequency rate (February 2024) with 4 seizures, as it represents the highest recent seizure burden,... |
| 11606 | no seizure frequency reference |  | no seizure frequency reference | W->C | unknown_or_no_reference_boundary;semantic_kind_shift;label_changed;parse_schema_issue;evidence_validity_shift | Currently not driving by self-report. / Note contains no seizure frequency information; only non-seizure patient update. |

## Shared Misses (Validation Only)

| Row | Gold | Chat | Reasoner | Outcome | Tags | Reasoner evidence/rationale |
| --- | --- | --- | --- | --- | --- | --- |
| 3371 | unknown | seizure free for multiple year | 1 per 8 week | W->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | The last event was on 10 September 2025 / The patient had one focal seizure in the past eight weeks, conditional on sleep deprivation, giving a low f... |
| 7195 | unknown | 1 per month | 1 per month | W->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift | only one possible brief event last month / Only a single possible event reported in the last month; no clear ongoing frequency. |
| 10237 | 4 cluster per month, multiple per cluster | no seizure frequency reference | unknown | W->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | last month ≈4 clusters / Highest recent seizure burden from last month's cluster frequency; current month frequency is unclear. |
| 14214 | 2 to 4 per month | 8 per 2 month | no seizure frequency reference | W->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | two to four seizures / Recent cluster of 2-4 seizures, followed by a short seizure-free period (<1 year). Per directives, the frequency event is sele... |
| 14530 | 2 per 2 month | no seizure frequency reference | unknown | W->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed;evidence_validity_shift | A second event occurred in Italy the following May 2019, once more during the night, lasting four minutes with similar semiology. / Only last event d... |
| 16714 | 5 per 6 month | 5 per 4 month | 5 per 4 month | W->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift | Since initial review by the GP, the pattern of episodes has been clarified as follows: / The note only provides historical seizure events (November c... |
| 16839 | 9 per 4 month | 12 per 3 month | 12 per 3 month | W->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;evidence_validity_shift | 4 further seizures at night / Recent highest burden of 4 seizures in one night in February indicates ongoing seizure activity; averaged over reported... |
| 16867 | 6 per 7 month | 5 per 4 month | 5 per 4 month | W->W | cluster_or_cluster_burden;seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift | if further events occur / The note documents three distinct clusters of seizures over the past 7-8 months (December, March, June) but provides no sta... |
| 14284 | 2 to 3 per month | 1 per 2 month | 2 to 3 per week | W->W | cluster_or_cluster_burden;seizure_free_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | two to three seizures / The note reports 2-3 seizures in the week after stopping medication, which is the most recent quantitative frequency. Althoug... |
| 14317 | 4 per 2 month | seizure free for multiple year | 4 per month | W->W | cluster_or_cluster_burden;seizure_free_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | Around that period, she had 4 seizures / The note reports 4 seizures around early April with subsequent seizure freedom of ~2 months. Per protocol, f... |
| 6077 | unknown | seizure free for 8 month | 1 per 8 month | W->W | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed;evidence_validity_shift | one breakthrough episode on 12/09/2025 / The most recent seizure event indicates active seizures; the preceding eight-month seizure-free interval is ... |
| 8400 | seizure free for multiple month | multiple per month | unknown | W->W | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | only occasional brief warning episodes / The only current seizure activity is occasional warning episodes with no specific rate; no convulsive events. |
| 14025 | unknown | 2 per 6 week | seizure free for multiple year | W->W | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | There have been no generalised tonic–clonic seizures reported since starting dietary therapy / The only current seizure-frequency statement is the ab... |
| 14454 | 2 per 2 month | seizure free for 2 month | unknown | W->W | seizure_free_boundary;unknown_or_no_reference_boundary;range_or_vague_multiple;rate_denominator_or_window;semantic_kind_shift;label_changed | she reported two seizures, one after a stressful day. / Two seizures occurred in February after topiramate discontinuation. The seizure-free interval... |

## Interpretation

1. The reasoner/thinking model is not globally worse at the task; it is a high-churn variant with near-balanced corrections and regressions.
2. Its net validation loss is concentrated in frequency-bearing rows. The largest recurrent mechanism is over-conservative or altered selection around cluster/range/window evidence, often moving from a countable frequency answer toward `unknown` or a narrower subtype/window.
3. It helps seizure-free/remission boundary cases, where non-reasoning chat sometimes converts seizure-free duration into an elapsed frequency or misses the remission state.
4. The higher exact-evidence rate does not translate to better selection. Evidence faithfulness is necessary but not sufficient for this pipeline.
5. The validation result explains why the holdout aggregate could be lower without needing to inspect holdout rows: the reasoner makes many confident semantic changes, and the harmful frequency regressions slightly outnumber the helpful boundary rescues.

## Recommendation

Do not promote `deepseek/deepseek-reasoner` thinking mode as the v0.6 structured-events default. Keep it as a diagnostic comparator for seizure-free boundary behavior. If used again, it needs a selective-action design rather than wholesale replacement: preserve chat or deterministic fallback for countable frequency/cluster rows, and test a narrow reasoner gate only for predeclared seizure-free/unknown boundary slices on validation.
