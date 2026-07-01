> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 First Verifier Live Run Main29 V6

Validation-development action-only verifier run over the main 29-row ambiguity V6 surface. This is not a scorer-label replacement protocol, does not authorize locked-test inspection, and excludes appendix and provenance-only rows from the retuning surface.

## Decision

The verifier produced non-abstain action decisions on the main ambiguity surface. The primary table remains the 29-row ambiguity set.

## Artifacts

- Row JSONL: `experiments\gan2026_validation750_first_verifier_live_main29_context_repair_v6_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation750_first_verifier_live_main29_context_repair_v6_2026-06-06.json`
- Source input: `experiments\gan2026_validation750_first_verifier_experiment_input_main29_context_repair_v6_2026-06-06.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| call ok rows | 29 |
| parse ok rows | 29 |
| parse error rows | 0 |
| contract ok rows | 29 |
| contract error rows | 0 |
| changed action rows | 28 |
| main score table rows | 29 |
| main score table changed action rows | 28 |
| appendix rows | 0 |
| affirm rows | 0 |
| reject rows | 9 |
| abstain rows | 1 |
| human review rows | 19 |
| parse error action rows | 0 |

## Main Table Actions

| Action | Rows |
| --- | ---: |
| `abstain` | 1 |
| `human_review` | 19 |
| `reject` | 9 |

## Appendix Actions

| Action | Rows |
| --- | ---: |

## Main Ambiguity Table

| Row | Baseline | Verifier | Sidecar | Route bucket | Rationale |
| ---: | --- | --- | --- | --- | --- |
| 5551 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Evidence shows ongoing several focal seizures daily plus occasional generalized seizures about once weekly, but frequency periods and counts are vague and additive normalization is incomplete, requiring human judgment to resolve. |
| 5791 | `abstain` | `abstain` | present | `verifier_eligible_ambiguity` | The evidence reports two brief myoclonic jerks and one generalized tonic-clonic seizure over the past three months (candidates llm:5791:2 and llm:5791:3) but frequency values are unparsed and additive frequency count is incomplete, making it unsafe to affirm a single seizure frequency. No contradictions exist, but the mixed event types and incomplete normalization prevent a definitive frequency assignment. |
| 6209 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence supports two distinct seizure frequency types: daily brief events and 2-3 longer episodes per month (llm:6209:1, llm:6209:2, det:6209:1, det:6209:2). There is no direct contradiction, but the additive frequency periods differ, causing normalization issues. This ambiguity and mixed window data require human review to decide on the final frequency assessment. |
| 6889 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes several seizure types with different frequencies: myoclonic jerks several times per week, three generalized tonic-clonic seizures over six months, and focal seizures once every 2-3 weeks. These are additive but have mixed and vague time windows, making a single clear current seizure burden unclear and requiring human review. |
| 12127 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Evidence shows several focal non-motor seizures weekly (det:12127:3, llm:12127:1) and rare generalised convulsions twice per year (llm:12127:2). These frequencies span different time windows and are additive but vague and mismatched, requiring human judgment to finalize. |
| 12192 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Evidence shows daily drop attacks (llm:12192:1), twice weekly focal aware seizures (det:12192:2, llm:12192:4), and occasional generalized tonic-clonic seizures (llm:12192:3). These frequencies are current and additive but have mismatched periods and incomplete normalization, making a single clear frequency unsupported without human judgment. |
| 12236 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence shows daily absence seizures, occasional generalized tonic-clonic seizures, and myoclonic jerks in morning clusters, but the additive frequency period mismatch and incomplete frequency parsing prevent a clear single frequency burden determination. No direct contradictions exist, but multiple plausible burdens require human judgment. |
| 12366 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Candidate llm:12366:1 reports simple partial seizures 4 times per day, and candidate llm:12366:3 reports tonic-clonic seizures 2 times per month, both current and certain. The clinical assessment notes additive frequency period mismatch and contextual clustering not additive to primary burden. No direct contradiction exists, but the mixed frequency periods and incomplete projection semantics require human review to determine final frequency burden. |
| 12378 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence shows focal clonic seizures 4 times daily and tonic-clonic seizures 2 times monthly (llm:12378:1, llm:12378:3), but the aggregation policy notes additive frequency period mismatch and incomplete normalization, making a single clear frequency label unresolved. |
| 12403 | `abstain` | `human_review` | absent | `verifier_eligible_ambiguity` | The evidence shows focal aware seizures 2-3 times daily (llm:12403:1) and tonic-clonic seizures twice monthly (llm:12403:3), plus drop attacks in clusters once or twice monthly (llm:12403:2). These mixed frequencies and cluster data create ambiguity in a single clear seizure burden. No direct contradictions exist, but the mixed windows and cluster frequency prevent a definitive single frequency label without expert review. |
| 12422 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Candidate llm:12422:1 reports nightly generalized convulsions currently, while candidate llm:12422:2 reports intermittent tonic seizures four times per year currently. The clinical assessment attempts additive aggregation but notes frequency period mismatch and incomplete normalization, making a single clear frequency unsupported. No direct contradiction exists, but the mixed frequency windows and incomplete projection semantics require human review to determine the best combined seizure frequency. |
| 12456 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Candidate llm:12456:1 asserts nightly generalized tonic-clonic seizures currently, while candidate llm:12456:2 asserts intermittent tonic seizures three times per year currently. These frequencies differ substantially and are additive with mismatched periods, creating ambiguity. The aggregation policy notes additive frequency period mismatch and incomplete frequency values, preventing a clear single frequency determination. Hence, human review is needed to resolve the plausible competing burdens. |
| 12460 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Candidate llm:12460:1 reports nightly generalized convulsions, while llm:12460:2 reports intermittent tonic seizures twice per year. These frequencies differ substantially and cannot be safely combined without human judgment. The evidence is current but involves mixed frequency periods, leading to additive frequency period mismatch issues. No direct contradiction exists, but the burden is unresolved and requires human review. |
| 12484 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidates det:12484:1 and det:12484:2 assert no seizures/events recorded since an unspecified time, conflicting with llm:12484:1 and llm:12484:2 which report ongoing seizures (1-2 generalized tonic-clonic yearly and 3-4 absences daily). This direct contradiction mandates rejection of seizure-free interpretation. |
| 12502 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidate det:12502:1 and llm:12502:5 assert no seizures recorded recently, contradicting llm:12502:2 and llm:12502:1 which report recent frequent seizures (4 absences/day and 1-2 generalized tonic-clonic seizures monthly). This direct contradiction mandates rejection of the seizure-free interpretation. |
| 12506 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidate llm:12506:4 asserts no seizures since last appointment, contradicting candidates llm:12506:1 and llm:12506:2 which report ongoing seizures (1-2 generalized tonic-clonic monthly and 4 absences daily). This direct contradiction mandates rejection of the proposed interpretation. |
| 12537 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidate det:12537:1 asserts 'No events have occurred since' (unclear temporality), and llm:12537:5 states 'No events have occurred since his most recent review' (recent), which directly contradicts llm:12537:1 reporting up to three generalized tonic-clonic seizures per week recently. This direct contradiction invalidates the seizure-free interpretation, requiring rejection of the proposed interpretation. |
| 12548 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence shows up to 3 generalized tonic-clonic seizures per year and focal impaired-awareness seizures every 4-6 weeks (llm:12548:1, llm:12548:3), but also daily drop attacks (det:12548:4) which contradict the seizure-free claim (det:12548:1). The temporal overlap and aggregation of these frequencies are unclear, making a single clear seizure frequency label impossible without expert review. |
| 12551 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidates det:12551:1 and llm:12551:5 assert no events have occurred recently, but llm:12551:1, llm:12551:3, and llm:12551:2 report ongoing seizures including daily drop attacks and focal seizures every 4-6 weeks. Also, llm:12551:4 states rarely more than 10 seizure-free days, contradicting seizure-free claims. This direct contradiction mandates rejection of seizure-free interpretation. |
| 12556 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidates llm:12556:1, llm:12556:2, and llm:12556:3 report ongoing frequent seizures (2-3 generalized tonic-clonic per week, daily drop attacks, and focal seizures every 4-6 weeks). However, candidates llm:12556:4, det:12556:1, and det:12556:2 assert no events have occurred since the most recent review or no events since an unclear time. This is a direct contradiction between active seizure burden and seizure freedom statements, requiring rejection of the proposed interpretation. |
| 12562 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidate llm:12562:1, llm:12562:2, and llm:12562:3 assert ongoing frequent seizures (3-4 GTCS per week, daily drop attacks, focal seizures every 4-6 weeks), while det:12562:1 and llm:12562:5 claim no events since recent review or no events have occurred since, directly contradicting ongoing seizure burden. This contradiction mandates rejection of the proposed interpretation. |
| 12573 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Candidate det:12573:1 and llm:12573:5 assert no events since recent review, contradicting llm:12573:1 and det:12573:4 which report ongoing seizures (daily drop attacks and up to two generalized seizures monthly). This direct contradiction prevents affirm or reject. The mixed seizure types and frequency periods create additive frequency period mismatch and vague aggregation issues, requiring human review to resolve. |
| 12584 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Evidence shows one generalized tonic-clonic seizure every 3 months, weekly absences, and atonic plus focal impaired awareness seizures every few months, plus a max seizure-free period of 4 weeks and no seizures since last visit. These mixed frequencies and vague periods prevent a single clear frequency label. |
| 12641 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes one to two generalized tonic-clonic seizures per week, daily absences, and focal sensory seizures every three to four weeks, plus a seizure-free interval of around three weeks. These frequencies span different time windows and are additive per policy, but the mixed periods and lack of exact trace for combined burden create ambiguity. The rejected candidate (det:12641:3) conflicts with the daily absences assertion. Thus, human review is needed to resolve the combined seizure burden. |
| 12676 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence shows one to two generalized tonic-clonic seizures per year, daily absences, and focal myoclonic seizures every three to four weeks, plus a seizure-free interval of around three weeks and no seizures since last visit. These mixed frequencies and seizure types with overlapping and additive periods create ambiguity that cannot be resolved automatically. |
| 12679 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Evidence shows ongoing generalized tonic-clonic seizures monthly, daily absences, and focal non-motor seizures plus drop attacks every 3-4 weeks, but also a recent statement of no further seizures since last visit. These mixed event types and timing inconsistencies prevent a clear single frequency determination. |
| 12749 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidate det:12749:1 and llm:12749:5 assert no seizures noted recently, but llm:12749:2 and llm:12749:1 report current frequent seizures (3-4 focal motor per day and generalized tonic-clonic twice monthly). This direct contradiction mandates rejection of seizure-free interpretation. |
| 12751 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Candidates det:12751:1, det:12751:2, and llm:12751:5 assert no seizures noted or documented since a certain time, indicating seizure freedom. However, candidates llm:12751:2, llm:12751:1, and llm:12751:3 report recent active seizures (4 focal clonic per day, generalized tonic-clonic twice monthly, and monthly drop attack clusters). This direct contradiction invalidates a seizure-free interpretation. |
| 12823 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence shows two distinct seizure frequencies: 9 generalized tonic-clonic seizures this year and focal impaired-awareness seizures every 3-4 weeks. These frequencies are additive but have mismatched periods and incomplete projection semantics, making a single clear frequency label unresolved without human review. |

## Appendix By Section

| Section | Rows |
| --- | ---: |