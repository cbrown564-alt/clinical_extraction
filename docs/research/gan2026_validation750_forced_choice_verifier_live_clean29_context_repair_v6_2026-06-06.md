# Gan 2026 Validation750 Forced-Choice Verifier Live Run Clean29 V6

Validation-development forced-choice verifier run over the clean 56-row V6 surface.

## Metrics

| Metric | Value |
| --- | ---: |
| Total Rows | 56 |
| Agreement Rows | 8 |
| Disagreement Rows | 48 |
| Agreement Rate | 0.1429 |
| Affirm Rows | 40 |
| Reject Rows | 5 |
| Abstain Rows | 0 |
| Human Review Rows | 11 |

## Action Counts (Forced-Choice Equivalent)

| Action | Count |
| --- | ---: |
| `affirm` | 40 |
| `human_review` | 11 |
| `reject` | 5 |

## Choice Counts

| Choice | Count |
| --- | ---: |
| `det:10434:1` | 1 |
| `det:12127:3` | 1 |
| `det:15262:1` | 1 |
| `det:16839:1` | 1 |
| `det:1706:1` | 1 |
| `human_review` | 11 |
| `llm:10200:1` | 1 |
| `llm:10509:1` | 1 |
| `llm:10542:1` | 1 |
| `llm:10578:1` | 1 |
| `llm:10630:1` | 1 |
| `llm:12192:1` | 1 |
| `llm:12236:1` | 1 |
| `llm:12403:1` | 1 |
| `llm:12422:1` | 1 |
| `llm:12456:1` | 1 |
| `llm:12484:2` | 1 |
| `llm:12502:2` | 1 |
| `llm:12506:2` | 1 |
| `llm:12537:1` | 1 |
| `llm:12551:2` | 1 |
| `llm:12562:1` | 1 |
| `llm:12584:3` | 1 |
| `llm:12641:1` | 1 |
| `llm:12676:2` | 1 |
| `llm:12749:2` | 1 |
| `llm:12751:2` | 1 |
| `llm:1317:1` | 1 |
| `llm:15242:2` | 1 |
| `llm:16757:1` | 1 |
| `llm:16907:1` | 1 |
| `llm:3356:1` | 1 |
| `llm:3468:1` | 1 |
| `llm:3469:1` | 1 |
| `llm:3482:1` | 1 |
| `llm:3493:1` | 1 |
| `llm:3507:1` | 1 |
| `llm:3512:1` | 1 |
| `llm:3534:2` | 1 |
| `llm:5551:2` | 1 |
| `llm:5791:3` | 1 |
| `llm:6209:1` | 1 |
| `llm:6501:1` | 1 |
| `llm:7141:1` | 1 |
| `llm:7785:1` | 1 |
| `llm:9937:1` | 1 |

## Comparison Table

| Row | Route Bucket | Action-Only Action | Forced Choice | Equivalent Action | Agree? | Rationale |
| ---: | --- | --- | --- | --- | --- | --- |
| 5551 | `verifier_eligible_ambiguity` | `human_review` | `llm:5551:2` | `affirm` | no | The patient currently experiences several focal seizure episodes per day with occasional generalized seizures approximately once weekly. This combined frequency is best represented by candidate llm:5551:2, which explicitly states the daily focal seizures and weekly generalized breakthroughs. |
| 5791 | `verifier_eligible_ambiguity` | `affirm` | `llm:5791:3` | `affirm` | yes | The patient reports two brief myoclonic jerks on awakening and one generalised tonic–clonic event over the past three months. The tonic–clonic event is a primary seizure type indicating the seizure frequency burden, supported by the evidence text specifying the event timing and recovery. |
| 6209 | `verifier_eligible_ambiguity` | `abstain` | `llm:6209:1` | `affirm` | no | The clinical assessment and primary candidate IDs emphasize daily brief seizure-like events as the current primary seizure frequency burden, supported by the evidence text 'They described daily brief events'. The 2–3 longer episodes per month are also noted but appear secondary. |
| 6889 | `verifier_eligible_ambiguity` | `human_review` | `human_review` | `human_review` | yes | The patient has multiple seizure types with frequencies reported over different and overlapping time frames: several myoclonic jerks per week, three generalized tonic-clonic seizures in six months, and focal seizures once every 2-3 weeks. These frequencies are additive but have mismatched periods and vague counts, making it ambiguous to determine a single primary seizure frequency burden. |
| 12127 | `verifier_eligible_ambiguity` | `abstain` | `det:12127:3` | `affirm` | no | The primary seizure frequency burden is best represented by the focal non-motor seizures occurring several times each week, which is a current and frequent event. The generalised convulsions are rare (two per year) and less frequent, thus the weekly focal non-motor seizures dominate the seizure frequency burden. |
| 12192 | `verifier_eligible_ambiguity` | `human_review` | `llm:12192:1` | `affirm` | no | The primary and most frequent seizure type is daily drop attacks, which represent the main seizure frequency burden. Other seizure types occur less frequently (twice weekly or occasionally), making the daily drop attacks the best representation of the patient's current seizure frequency. |
| 12236 | `verifier_eligible_ambiguity` | `abstain` | `llm:12236:1` | `affirm` | no | The primary seizure frequency burden is best represented by the daily absence seizures, which are clearly stated as ongoing and current. Occasional generalized tonic-clonic seizures are less frequent and thus secondary. The myoclonic jerks in morning clusters are supportive but not the primary frequency measure. |
| 12366 | `verifier_eligible_ambiguity` | `human_review` | `human_review` | `human_review` | yes | The patient has two distinct seizure frequencies reported: simple partial seizures 4 times per day and tonic-clonic seizures 2 times per month. These frequencies are from different time windows and cannot be directly added without normalization, leading to ambiguity in defining a single primary seizure frequency burden. Therefore, human review is needed to resolve the mixed-window frequency aggregation. |
| 12378 | `verifier_eligible_ambiguity` | `abstain` | `human_review` | `human_review` | no | The patient has two distinct seizure frequencies reported: focal clonic seizures 4 times per day and tonic-clonic seizures 2 times per month. These frequencies are additive but cover different time windows, causing a frequency period mismatch and ambiguity in representing a single primary seizure frequency burden. Therefore, human review is needed to clarify and reconcile these mixed-window frequency values. |
| 12403 | `verifier_eligible_ambiguity` | `abstain` | `llm:12403:1` | `affirm` | no | The primary seizure frequency burden is best represented by the frequent focal aware seizures occurring 2 to 3 times per day, which is a current and certain frequency. The tonic-clonic seizures occur less frequently (2 times per month) and are secondary. The assessment notes additive frequency periods mismatch, so the daily frequency is the most direct and primary measure of seizure burden. |
| 12422 | `verifier_eligible_ambiguity` | `abstain` | `llm:12422:1` | `affirm` | no | The patient currently experiences nightly generalized convulsions seizures, which represents the primary and more frequent seizure burden compared to intermittent tonic seizures four times per year. |
| 12456 | `verifier_eligible_ambiguity` | `human_review` | `llm:12456:1` | `affirm` | no | The patient currently experiences nightly generalized tonic-clonic seizures, which represents the primary and most frequent seizure burden. Although there are intermittent tonic seizures three times per year, the nightly seizures dominate the frequency assessment. |
| 12460 | `verifier_eligible_ambiguity` | `abstain` | `human_review` | `human_review` | no | The patient has two distinct seizure frequencies reported: nightly generalized convulsions and intermittent tonic seizures twice per year. These frequencies cover different time windows and types, making it ambiguous to combine into a single primary seizure frequency burden without further clarification. |
| 12484 | `verifier_eligible_ambiguity` | `human_review` | `llm:12484:2` | `affirm` | no | The primary seizure frequency burden is best represented by the patient's three to four absences per day, which is a current and specific frequency rate. This is supported by llm:12484:2 and aligns with the clinical assessment summary emphasizing daily absences as a main frequency measure. |
| 12502 | `verifier_eligible_ambiguity` | `human_review` | `llm:12502:2` | `reject` | no | The most specific and recent seizure frequency reported is 'She has 4 absences per day,' which clearly quantifies the primary seizure burden. Other frequencies describe less frequent seizure types or clusters, but the daily absences represent the main ongoing seizure frequency. |
| 12506 | `verifier_eligible_ambiguity` | `human_review` | `llm:12506:2` | `affirm` | no | The primary seizure frequency burden is best represented by the current, certain evidence of '4 absences per day' (llm:12506:2). Although there are other seizure types and frequencies mentioned, the absences per day represent the most frequent and current seizure burden. The monthly generalized tonic-clonic seizures (llm:12506:1) are less frequent, and the 'once a month' cluster frequency (llm:12506:3) and seizure-free statement (llm:12506:4) do not override the daily absences frequency. The deterministic 'once a month' (det:12506:3) was rejected due to ambiguity. Therefore, llm:12506:2 best captures the primary seizure frequency. |
| 12537 | `verifier_eligible_ambiguity` | `reject` | `llm:12537:1` | `affirm` | no | The primary seizure frequency burden is best represented by 'up to three generalised tonic-clonic seizures per week' as stated in llm:12537:1, which is recent and certain. Although there are additional seizure types (daily drop attacks and focal impaired-awareness seizures every 4-6 weeks), the main frequency burden is captured by this candidate. The other candidates either represent different seizure types or seizure-free intervals but do not override the primary frequency. |
| 12548 | `verifier_eligible_ambiguity` | `reject` | `human_review` | `human_review` | no | The patient has multiple seizure types with different frequencies: up to 3 generalized tonic-clonic seizures per year, focal impaired-awareness seizures every 4 to 6 weeks, and daily drop attacks. These frequencies span different time windows and seizure types, making it ambiguous to select a single primary seizure frequency burden without further clarification or aggregation rules. |
| 12551 | `verifier_eligible_ambiguity` | `human_review` | `llm:12551:2` | `affirm` | no | The patient currently experiences daily drop attacks, which represent the highest frequency seizure type reported. Although other seizure types occur less frequently (up to 2 generalized tonic-clonic seizures per year and focal impaired-awareness seizures every 4 to 6 weeks), the daily drop attacks dominate the seizure frequency burden. |
| 12556 | `verifier_eligible_ambiguity` | `reject` | `human_review` | `human_review` | no | The patient has multiple seizure types with different frequencies: 2-3 generalized tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seizures every 4-6 weeks. Additionally, no events have occurred since the most recent review, creating ambiguity about the current primary seizure frequency burden. The mixed frequency periods and recent seizure-free interval make it unclear which frequency best represents the current burden, warranting human review. |
| 12562 | `verifier_eligible_ambiguity` | `human_review` | `llm:12562:1` | `affirm` | no | The patient currently experiences up to 3 to 4 generalized tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seizures every 4 to 6 weeks. These combined frequencies represent the primary seizure burden despite a recent seizure-free period. The evidence is certain and current, reflecting the ongoing seizure frequency. |
| 12573 | `verifier_eligible_ambiguity` | `reject` | `human_review` | `human_review` | no | The patient has multiple seizure types with different frequencies: up to two generalized tonic-clonic seizures per month, daily drop attacks, and focal impaired-awareness seizures every four to six weeks. These frequencies are additive but cover different time windows and seizure types, making it ambiguous to select a single primary seizure frequency. Additionally, no exact trace evidence links these frequencies into a unified frequency rate, and the presence of recent seizure-free intervals adds complexity. Therefore, human review is needed to reconcile these mixed and overlapping frequency data. |
| 12584 | `verifier_eligible_ambiguity` | `human_review` | `llm:12584:3` | `affirm` | no | The patient has multiple seizure types with different frequencies, but the most frequent and primary seizure burden is the persistent weekly absence seizures, which represent the highest frequency seizure type currently reported. |
| 12641 | `verifier_eligible_ambiguity` | `human_review` | `llm:12641:1` | `affirm` | no | The primary seizure frequency burden is best represented by the certain and recent evidence of one to two generalised tonic-clonic seizures per week (llm:12641:1). Although there are additional seizure types with different frequencies (daily absences and focal sensory seizures every three to four weeks), the tonic-clonic seizures per week represent the main frequency burden. The other frequencies are additive but represent different seizure types and periods, making the tonic-clonic seizures the primary frequency to select. |
| 12676 | `verifier_eligible_ambiguity` | `human_review` | `llm:12676:2` | `affirm` | no | The patient currently has daily absence seizures, which represent the primary and most frequent seizure burden. Other seizure types occur less frequently (one to two generalized tonic-clonic seizures per year and focal myoclonic seizures every three to four weeks). Daily absences are clearly stated as current and frequent, making llm:12676:2 the best representation of the primary seizure frequency. |
| 12679 | `verifier_eligible_ambiguity` | `human_review` | `human_review` | `human_review` | yes | The patient currently experiences multiple seizure types with different frequencies: one to two generalized tonic-clonic seizures per month, daily absence seizures, and focal non-motor seizures plus drop attacks every three to four weeks. These frequencies represent distinct seizure types and are all recent, indicating a mixed seizure burden rather than a single primary frequency. |
| 12749 | `verifier_eligible_ambiguity` | `reject` | `llm:12749:2` | `reject` | yes | The current primary seizure frequency burden is best represented by the statement that focal motor seizures occur 3-4 per day, which is a clear, current frequency. Other frequencies describe different seizure types or longer time frames, making llm:12749:2 the most precise current frequency. |
| 12751 | `verifier_eligible_ambiguity` | `human_review` | `llm:12751:2` | `reject` | no | The patient currently experiences focal clonic seizures occurring 4 times per day, which is the most specific and recent frequency data available. Other seizure types and frequencies are less frequent or less clearly quantified. |
| 12823 | `verifier_eligible_ambiguity` | `abstain` | `human_review` | `human_review` | no | The patient has two different seizure frequency reports: nine generalized tonic-clonic seizures documented this year and focal impaired-awareness seizures occurring roughly once every three to four weeks. These represent different seizure types and time frames, making it ambiguous to combine into a single primary seizure frequency burden without further clarification. |