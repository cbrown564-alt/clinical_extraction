# Gan 2026 RQ9 Cluster/Convention Monitoring

This is a validation-development monitoring artifact over v3 prediction-bearing cluster/convention rows.

## Decision

Keep cluster/convention rows prediction-bearing. Use the high-priority verifier queue for monitoring and future audit, not default human-review routing.

## Rationale

Do not restore default human-review routing for cluster/convention rows. Most v3 prediction-bearing cluster/convention rows are development-correct, but convention-risk subfamilies should be monitored through a high-priority verifier queue.

## Claim Boundary

Validation-development monitoring predeclaration over v3 prediction-bearing cluster/convention rows. The slice stays prediction-bearing; verifier priority is for monitoring and future audit only, not router action routing. This artifact does not change scorer, gold, prompts, projection policy, locked-test behavior, or benchmark-comparable claims.

## Artifacts

- Source router JSONL: `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl`
- Predeclaration: `docs/research/gan2026_rq9_cluster_convention_monitoring_predeclaration_2026-06-04.md`
- Row monitoring JSONL: `experiments/gan2026_rq9_cluster_convention_monitoring_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_rq9_cluster_convention_monitoring_2026-06-04.json`

## Metrics

| Metric | Value |
| --- | ---: |
| eligible prediction bearing rows | 115 |
| keep prediction bearing rows | 115 |
| high priority verifier rows | 61 |
| routine monitoring rows | 54 |
| development safe rows | 104 |
| development unsafe rows | 11 |
| development unsafe rate | 0.0957 |

## Monitoring Groups

| Group | Rows |
| --- | ---: |
| `cluster_structured_prediction` | 59 |
| `plain_frequency_with_cluster_context` | 36 |
| `seizure_free_with_cluster_context` | 7 |
| `sentinel_no_reference_with_cluster_context` | 13 |

## High-Priority Verifier Rows

| Row | Group | Candidate label | Dev unsafe | Evidence |
| ---: | --- | --- | --- | --- |
| 1317 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `Centre for Epilepsy Neurosciences Division Clinic Date: 09 August 2024 Dr Aisha Rahman Consulta...` |
| 4771 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `Over the past three months, the patient describes spells of increased seizure activity occurrin...` |
| 6501 | `seizure_free_with_cluster_context` | `seizure free for multiple year` | yes | `No consistent auras reported` |
| 6509 | `plain_frequency_with_cluster_context` | `2 per 2 week` | no | `two generalised tonic–clonic seizures in the past fortnight` |
| 9937 | `plain_frequency_with_cluster_context` | `1 per multiple week` | yes | `every few weeks` |
| 9943 | `plain_frequency_with_cluster_context` | `1 per 4 to 5 week` | yes | `every four to five weeks` |
| 9955 | `plain_frequency_with_cluster_context` | `1 per month` | yes | `once each month` |
| 10147 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `Centre for Epilepsy Neurosciences Division Clinic Date: 02 October 2025 Dr Sarah Ahmed Consulta...` |
| 10183 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `King's College Hospital Department of Neurosciences Clinic Date: 21 September 2015 Dr Amelia Ha...` |
| 10189 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `KINGS NEUROSCIENCES CENTRE Clinic Date: 02 October 2025 Dr Ahmed Rahman Riverside Health Centre...` |
| 10200 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `KINGS NEUROSCIENCES CENTRE Clinic Date: 07 November 2024 Dr Wang Saffron Park Hospital Saffron ...` |
| 10237 | `cluster_structured_prediction` | `4 cluster per month, multiple per cluster` | no | `last month ≈4 clusters` |
| 10245 | `cluster_structured_prediction` | `3 cluster per month, multiple per cluster` | no | `last month ≈three clusters` |
| 10260 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `he describes occasional brief morning myoclonic jerks when sleep-deprived, with rare episodes o...` |
| 10264 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `St Mary's Hospital Institute of Neurology Clinic Date: 02 October 2025 Dr Patel St Mary's Hospi...` |
| 10266 | `plain_frequency_with_cluster_context` | `1 per 5 day` | yes | `every 5 days` |
| 10268 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `Department of Neurology Clinic Date: 13 April 2014 Dr Aisha Rahman St George’s University Hospi...` |
| 10371 | `seizure_free_with_cluster_context` | `seizure free for 25 month` | no | `Prior cluster pattern resolved since 11 Aug 2023` |
| 10386 | `plain_frequency_with_cluster_context` | `1 per day` | yes | `daily Seizure` |
| 10509 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `KINGS NEUROSCIENCES CENTRE Clinic Date: 24 May 2020 Dr Patel Elm Grove Health Centre 12 Elm Gro...` |
| 10542 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `Epilepsy Centre Neurosciences Division Clinic Date: 13 August 2014 Dr Patel Southwark Community...` |
| 10578 | `cluster_structured_prediction` | `unknown, 3 to 4 per cluster` | no | `clusters characterized by three - four focal impaired-awareness seizures; frequency unclear` |
| 10583 | `cluster_structured_prediction` | `unknown, 2 to 3 per cluster` | no | `Clusters characterized by two - three focal impaired-awareness seizures; frequency unclear` |
| 10594 | `cluster_structured_prediction` | `unknown, 2 per cluster` | no | `Clusters characterized by two focal impaired-awareness seizures; frequency unclear` |
| 10618 | `seizure_free_with_cluster_context` | `seizure free for multiple year` | yes | `no consistent focal auras reported` |
| 10629 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `KINGS NEUROSCIENCES CENTRE Clinic Date: 21 September 2025 Dr Harpreet Sandhu Riverside Health C...` |
| 10677 | `plain_frequency_with_cluster_context` | `1 per month` | yes | `consistent pattern over the last three months of short runs of events approximately monthly` |
| 10753 | `sentinel_no_reference_with_cluster_context` | `no seizure frequency reference` | no | `The entries over the last 12 months show that most weeks are quiet; however, when he undertakes...` |
| 10942 | `plain_frequency_with_cluster_context` | `5 per month` | no | `This month he experienced two clusters this month; each ~five focal impaired-awareness seizures` |
| 11035 | `plain_frequency_with_cluster_context` | `1 per 3 month` | no | `every three months` |
| 12192 | `plain_frequency_with_cluster_context` | `1 per day` | no | `continues to experience drop attack on a daily basis` |
| 12218 | `plain_frequency_with_cluster_context` | `1 per day` | no | `continues to experience epileptic spasm on a daily basis` |
| 12236 | `plain_frequency_with_cluster_context` | `1 per day` | no | `continues to experience absence seizures on a daily basis` |
| 12246 | `plain_frequency_with_cluster_context` | `1 to 2 per day` | no | `one or two per day` |
| 12484 | `plain_frequency_with_cluster_context` | `3 to 4 per day` | no | `three - four absences per day` |
| 12502 | `plain_frequency_with_cluster_context` | `4 per day` | no | `4 absences per day` |
| 12506 | `plain_frequency_with_cluster_context` | `4 per day` | no | `4 absences per day` |
| 12749 | `plain_frequency_with_cluster_context` | `3 to 4 per day` | no | `focal motor seizures occur 3 - 4 per day` |
| 12751 | `plain_frequency_with_cluster_context` | `4 per day` | no | `focal clonic occur 4 per day` |
| 13051 | `plain_frequency_with_cluster_context` | `2 per 8 month` | no | `seizure-free for 8 months after starting Levetiracetam 500 mg twice daily, before experiencing ...` |
| 13058 | `plain_frequency_with_cluster_context` | `2 per 7 month` | no | `seizure-free for seven months after starting Levetiracetam 500 mg twice daily, before experienc...` |
| 13574 | `seizure_free_with_cluster_context` | `seizure free for multiple year` | no | `currently in long-term remission, having been seizure free for years` |
| 13595 | `seizure_free_with_cluster_context` | `seizure free for multiple year` | no | `currently in long-term remission, having been seizure free for years` |
| 13598 | `seizure_free_with_cluster_context` | `seizure free for multiple year` | no | `currently in long-term remission, having been seizure free for years` |
| 13608 | `seizure_free_with_cluster_context` | `seizure free for multiple year` | no | `currently in long-term remission, having been seizure free for years` |
| 15593 | `plain_frequency_with_cluster_context` | `2 per 6 month` | yes | `two nocturnal episodes over the past six months` |
| 15672 | `plain_frequency_with_cluster_context` | `2 per 6 week` | yes | `two definite drop events in the last six weeks` |
| 15697 | `plain_frequency_with_cluster_context` | `1 per day` | no | `1 per day` |
| 15715 | `plain_frequency_with_cluster_context` | `1 per day` | no | `Over the last six weeks, coinciding with an intensified travel schedule, she has experienced cl...` |
| 16356 | `plain_frequency_with_cluster_context` | `1 per 4 day` | no | `clusters every 4 days` |
| 16394 | `plain_frequency_with_cluster_context` | `1 per 2 to 4 day` | no | `Seizures remain relatively stable, typically occurring in clusters every 2 to 4 days.` |
| 16529 | `plain_frequency_with_cluster_context` | `1 per 5 day` | no | `Seizures are occurring with a clustering pattern, most often every 5 days, with occasional shor...` |
| 16557 | `plain_frequency_with_cluster_context` | `1 per 2 to 3 day` | no | `every 2 - 3 days` |
| 16574 | `plain_frequency_with_cluster_context` | `1 per 4 day` | no | `seizures typically occur in clusters, generally spaced four days apart` |
| 16590 | `plain_frequency_with_cluster_context` | `1 per 4 to 5 day` | no | `seizures typically occur in clusters, generally spaced four to five days apart` |
| 16618 | `plain_frequency_with_cluster_context` | `1 per 5 day` | no | `seizures typically occur in clusters, generally spaced 5 days apart` |
| 16645 | `plain_frequency_with_cluster_context` | `5 per 7 month` | no | `He had a cluster of three seizures in August (short, not full convulsions, fluctuating awarenes...` |
| 16674 | `plain_frequency_with_cluster_context` | `7 per 6 month` | no | `In Apr she experienced four short absences in a cluster (self-limited). In Jul there was 2 furt...` |
| 16685 | `plain_frequency_with_cluster_context` | `10 per 3 month` | no | `He had a cluster of three seizures in Aug (short, not full convulsions, fluctuating awareness, ...` |
| 16714 | `plain_frequency_with_cluster_context` | `5 per 6 month` | no | `In November he presented with a cluster of three seizures (self-terminating, fluctuating awaren...` |
| 16824 | `plain_frequency_with_cluster_context` | `11 per 5 month` | no | `He had a cluster of three seizures in Dec (short, not full convulsions, fluctuating awareness, ...` |
