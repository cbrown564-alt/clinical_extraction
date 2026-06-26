# Gan 2026 LLM Component Mechanics Rows

Compact row-level artifact for the RQ1/RQ2/RQ4 reset. This is a validation-development diagnostic artifact; deterministic outputs are included only as comparator context.

- JSONL artifact: `experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl`
- Mechanism rows: 195
- Source rows represented: 111

## Buckets

| Bucket | Rows |
| --- | ---: |
| `rq1_llm_candidate_burden` | 12 |
| `rq1_llm_candidate_loss_vs_deterministic` | 12 |
| `rq1_llm_candidate_win_over_deterministic_miss` | 11 |
| `rq1_llm_selected_state_recall` | 12 |
| `rq2_exact_evidence_but_wrong_state` | 48 |
| `rq2_incomplete_typed_operands` | 12 |
| `rq2_llm_correct_to_wrong` | 16 |
| `rq2_llm_wrong_to_correct` | 7 |
| `rq4_projection_correct_to_wrong` | 16 |
| `rq4_projection_wrong_to_correct` | 25 |
| `rq4_schema_near_projection_miss` | 24 |

## Components

| Component | Rows |
| --- | ---: |
| `boundary_state_priority` | 12 |
| `claim_table_final_query` | 24 |
| `competing_frequency_uncertainty` | 1 |
| `graph_gated_month_bucket_duration` | 12 |
| `hybrid_adjudicator_raw` | 20 |
| `llm_candidate_selector_raw` | 66 |
| `llm_heavy_selected_fact` | 36 |
| `llm_selected_state_or_evidence` | 12 |
| `state_graph_projection` | 12 |

## Example Index

| Bucket | Component | Source row | Gold | Candidate | Evidence snippet |
| --- | --- | ---: | --- | --- | --- |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 79 | 6 to 7 per year | ≤6-7 per year | Seizure frequency currently reported as ≤ 6 to 7 per year |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 187 | 1 per 7 to 9 day | cluster every 7-9 days | events tend to cluster every seven to nine days |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 212 | 1 per 3 to 4 week | 3-4 weeks | Since the last clinic contact, the patient reports ongoing episodes occurring every 3 - 4 weeks |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 218 | 1 per 3 week | seizures every 2-3 days | Prior to these changes, seizures occurred once every two to three days. |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 446 | 2 per week | twice per week or less | Over the past month, the overall frequency has been ≤ twice per week, occurring both nocturnally and during... |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 665 | 2 per 2 week | twice every two weeks | The app logs indicate a regular pattern of seizures twice every two weeks |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 725 | 1 per day | daily | He reports events occur daily, most commonly during the late dinner rush between 19:00 and 21:00, particula... |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 763 | 1 per week | weekly | ongoing events occurring roughly weekly |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 854 | 1 per year | yearly | she describes her seizures as occurring roughly yearly |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 1880 | 8 per 2 month | 3 clusters/month | Prior to this deterioration, his seizure frequency was three clusters this month; each ≈four absences in th... |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 2681 | 1 per day | daily | Over the past 6 weeks, there has been clear worsening with an absence seizure every night |
| `rq1_llm_candidate_burden` | `llm_candidate_selector_raw` | 2765 | 1 per month | monthly | According to the carer-maintained diary over the past six months, Bill has a focal onset seizure monthly. |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 278 | multiple per week | multiple times per week | These events have been occurring multiple times in past week, including two episodes witnessed by a friend. |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 338 | multiple per month | many | Over the last four weeks he has experienced many convulsions in past month |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 744 | multiple per week | frequent | Over the past two months she reports brief absences occurring on most weekdays, often clustering around lat... |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 869 | multiple per month | seizure cluster frequency | Diary review suggests several events spread across most months, typically brief, with occasional back-to-ba... |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 1249 | 2 to 4 per week | 2 to 4 per week | 2 or 4 focal impaired awareness seizures this week |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 1317 | unknown, multiple per cluster | cluster | Since the last appointment, Ms Hannah Cooper described a cluster of events over a single day, reporting mul... |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 1357 | 1 per day | seizure | The patient reported 1 tonic-clonic seizures yesterday |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 1636 | 5 per month | 5 per month | two drop attacks and three petit mal in last month |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 1687 | multiple per week | several focal seizures per week | Since the last review, the patient reports several focal seizures last week characterised by brief behaviou... |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 1707 | multiple per week | cluster | brief cluster of events occurring on multiple days within the past week |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 2094 | multiple per month | seizure_frequency | Over the past month, she reports several absence seizures in the past month, typically brief lapses in awar... |
| `rq1_llm_candidate_loss_vs_deterministic` | `llm_candidate_selector_raw` | 2149 | unknown | ongoing focal aware and focal impaired-awareness seizures | She describes ongoing focal aware and focal impaired-awareness episodes with auras of rising epigastric dis... |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 3356 | unknown | unknown | Over the past three months, the carer’s records indicate brief generalised tonic–clonic seizures occurring ... |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 4690 | multiple per day | unknown | He notes occasional limb twitching on waking and brief lapses in concentration described by his partner |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 6077 | unknown | unknown | one breakthrough episode on 12/09/2025 while on a late-evening flight from London to Lisbon |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 6244 | unknown | unknown | episodes that her partner mainly witnesses during the night |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 6321 | unknown | unknown | spells are uncommon when meals are regular |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 6987 | unknown | unknown | The carer’s records indicate brief episodes of behavioural arrest with oral automatisms and post‑event conf... |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 10266 | unknown | unknown | Uncertain frequency; device logs suggest short clusters without counts |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 10618 | unknown, 4 to 6 per cluster | unknown | There may then be several days without events |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 14076 | unknown | unknown | since her last clinic appointment she has had several myoclonic jerks, the last reported on 10-Oct |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 15168 | multiple per 15 month | unknown | he continues to experience brief jumps from time to time. He describes these as sudden myoclonic jerks pred... |
| `rq1_llm_candidate_win_over_deterministic_miss` | `llm_candidate_selector_raw` | 15193 | multiple per 13 month | unknown | though continues to experience brief absence from time to time |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 10 | 4 per day | 4 per 1 day | On the accommodation logs, the observed frequency is noted as ≤ four per day, with variable clustering, oft... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 40 | 4 per week | 4 per 1 week | Since my last assessment he reports a variable pattern of episodes but overall a frequency of ≤ four seizur... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 79 | 6 to 7 per year | 6 to 7 per 1 year | Seizure frequency currently reported as 6le; 6 to 7 per year, typically clustering around periods of jet la... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 103 | 2 to 4 per year | 2 to 4 per year | Over the past year, however, the patient and family report that events have become markedly infrequent, suc... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 128 | 17 per month | 17 per month | He reports a current seizure frequency of 17 per month, typically clustering around periods of sleep depriv... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 156 | 1 per 6 day | 1 per 6 day | Patient reports seizures every 6 days, typically brief focal aware episodes with auditory distortion and ri... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 180 | 1 per 7 day | 1 per 7 day | The patient keeps a diary and describes a pattern of seizures every seven days, with post-event morning hea... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 182 | 1 per 2 day | 1 per 2 day | The carer reports that seizures are occurring every 2 days on average, based on a written diary and a smart... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | Since the last review, Ms Aisha Rahman reports that events tend to cluster every seven to nine days. |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 190 | 1 per 4 week | 1 per 4 week | At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precip... |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 198 | 1 per 4 week | 1 per 4 week | Despite good adherence to Levetiracetam, they continue to have seizures every 4 weeks. |
| `rq1_llm_selected_state_recall` | `llm_selected_state_or_evidence` | 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | Since the last clinic contact, the patient reports ongoing episodes occurring every 3 - 4 weeks, typically ... |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 338 | multiple per month | 1 cluster per month, multiple per cluster | These events clustered after eastbound flights and consecutive nights of restricted sleep (3–4 hours) |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 1046 | 3 to 5 per month | 5 per month | The patient reports uncertainty when recalling counts due to clustering; they believe there were 3 or 5 sei... |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 1317 | unknown, multiple per cluster | 1 cluster per 1 day, multiple per cluster | Since the last appointment, Ms Hannah Cooper described a cluster of events over a single day, reporting mul... |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 1695 | multiple per month | seizure free for 1 month | In the current month to date, no events have been recorded |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 1706 | multiple cluster per month, multiple per cluster | unknown | Over the past month, the patient reports a cluster of short events on multiple days, each beginning with a ... |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 1923 | 7 per 6 month | 2 to 3 per 6 month | Over the past six months he describes two drop attacks and five epileptic spasms |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 3137 | seizure free for multiple month | no seizure frequency reference | the patient reports no definite seizure events |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 3261 | 2 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | She reports two clusters this month; each ≈four absences in the morning. |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 3623 | 7 per week | unknown | Over the past three months, he and his partner report clusters of events with variable frequency: on steadi... |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 3988 | multiple per week | 1 per week | The parent has witnessed some of these episodes and notes that they tend to cluster when the patient is sle... |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 4337 | 3 per 3 month | 3 per 4 month | Seizure events on 06-03, 06-13, 09-23 as recorded in the patient’s diary |
| `rq2_exact_evidence_but_wrong_state` | `claim_table_final_query` | 4402 | 7 per 7 month | 1 to 2 per month | Seizure record (patient-reported and cross-checked with his app timestamps): Seizure: 2022: Jan x1, Feb x0,... |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 190 | 1 per 4 week | unknown | clusters of brief absence episodes every 4 weeks, usually over 1–2 days |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 2822 | 1 per day | unknown | On specific questioning, they report a myoclonic jerk daily, occasionally clustering in the morning, and ve... |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 3356 | unknown | seizure free for multiple year | no events reported |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 3528 | unknown | seizure free for multiple year | no witnessed generalised tonic–clonic seizures since |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 3623 | 7 per week | unknown | Over the past three months, he and his partner report clusters of events with variable frequency: on steadi... |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 4116 | 1 per 1 to 2 day | 1 per day | Currently: Escalation over the last six weeks with events occurring qone to twod on workdays, often cluster... |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 4690 | multiple per day | seizure free for multiple year | no witnessed convulsions since |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 5534 | 1 per multiple month | seizure free for multiple year | no generalised tonic–clonic seizures since |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 5921 | 1 per 6 to 8 week | 1 per day | daily Seizures |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 5974 | unknown | seizure free for multiple year | No convulsive events reported |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 6077 | unknown | seizure free for 8 month | no episodes in the preceding eight months |
| `rq2_exact_evidence_but_wrong_state` | `hybrid_adjudicator_raw` | 6094 | 3 per month | 3 per week | three times per week |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 1695 | multiple per month | seizure free | In the current month to date, no events have been recorded |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 2992 | seizure free for 7 month | unknown | He reports that his last seizure on 19-May-2024 occurred during rigging and programming with a rapid strobe... |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 5767 | 1 per 1 to 2 week | 1-2 per week | seizure activity has become more regular, with spells now occurring every one to two weeks |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 5791 | 1 per month | 2-3 per 3 months | Over the past three months they report two brief myoclonic jerks on awakening and one generalised tonic–clo... |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 6738 | 1 per 6 to 8 week | unknown | these events occur roughly once every 6–8 weeks |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 6889 | multiple per week | 3 per 6 months | three generalised tonic–clonic seizures in the past six months |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 7275 | 1 per month | 2-5 per month | Over the last 12 weeks he recorded: July 0, August 2 brief events over one weekend, September 1 isolated event |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 9449 | 4 per 6 month | 1-2 per month | Seizure diary review: Focal seizure: 2019: May x0, Jun x0, Jul x1, Aug x0, Sep x1, Oct x2. |
| `rq2_exact_evidence_but_wrong_state` | `llm_candidate_selector_raw` | 10097 | 3 cluster per month, multiple per cluster | 3 per month | nocturnal clusters 3×/month |

## Claim Boundary

Rows are sampled from saved validation and diagnostic replay matrices. They support mechanism analysis and follow-up protocol design, not holdout-transfer claims or architecture promotion.
