# Gan 2026 Selected Candidate Decision Diagnostics

Validation250 selector-decision diagnostics only. This verifies candidate-id traceability and selection shape; it does not score, normalize, project, or render labels.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_validation250_selected_candidate_decision_v2_diagnostics.jsonl`
- Summary JSON: `experiments\gan2026_validation250_selected_candidate_decision_v2_diagnostics.json`
- Selector source: `experiments\gan2026_validation250_selected_candidate_decision_v2_v2_high_recall.jsonl`

## Summary

- Rows: 250
- Selected decision rows: 250
- Missing decision rows: 0
- Invalid selected-reference rows: 0
- High-burden rows: 69
- Related-candidate-group rows: 21
- Related groups with coherence flags: 14

## Selection Modes

- `no_reliable_candidate`: 3
- `related_candidate_group`: 21
- `single_candidate`: 226

## Selected Candidate Source Types

- `deterministic_candidate`: 48
- `llm_candidate`: 222

## Selected Candidate Kinds

- `cluster_frequency`: 26
- `frequency_rate`: 175
- `last_event_only`: 3
- `seizure_free`: 48
- `unknown_frequency`: 18

## Source Composition

- `deterministic_only`: 44
- `llm_only`: 200
- `mixed`: 3
- `none`: 3

## Related Group Policy Actions

- `aggregate_selected_candidates`: 4
- `preserve_as_cluster_axis`: 1
- `preserve_as_cluster_modifier_context`: 7
- `preserve_as_corrob_seizure_free`: 2
- `route_to_verifier_before_normalization`: 3
- `split_primary_with_context`: 4

## Inspection Examples

### Invalid Reference Rows

- None.

### Related Group Rows

- 338: mode `related_candidate_group`, selected ['det:338:1', 'llm:338:2'], kinds ['unknown_frequency', 'cluster_frequency'], source types ['deterministic_candidate', 'llm_candidate'], flags ['mixed_candidate_kind', 'mixed_temporality'], policy `preserve_as_cluster_modifier_context`. Rationale: The patient has many convulsions in the past month that cluster after eastbound flights and restricted sleep, so both candidates together best describe the current seizure frequency burden.
- 466: mode `related_candidate_group`, selected ['llm:466:1', 'llm:466:2'], kinds ['frequency_rate', 'cluster_frequency'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `preserve_as_cluster_modifier_context`. Rationale: The current seizure frequency and cluster information together best describe the patient's seizure burden.
- 744: mode `related_candidate_group`, selected ['det:744:2', 'det:744:1'], kinds ['frequency_rate', 'frequency_rate'], source types ['deterministic_candidate', 'deterministic_candidate'], flags [], policy `aggregate_selected_candidates`. Rationale: Both the frequent brief absences on most weekdays and the single generalised tonic–clonic seizure in the last eight weeks jointly describe the current seizure frequency burden.
- 1046: mode `related_candidate_group`, selected ['det:1046:1', 'llm:1046:2'], kinds ['frequency_rate', 'frequency_rate'], source types ['deterministic_candidate', 'llm_candidate'], flags ['mixed_temporality'], policy `route_to_verifier_before_normalization`. Rationale: The combined candidates describe the recent seizure frequency including both total count and specific focal seizure types, providing a fuller picture of current seizure burden.
- 1165: mode `related_candidate_group`, selected ['llm:1165:1', 'llm:1165:2'], kinds ['cluster_frequency', 'seizure_free'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `split_primary_with_context`. Rationale: The recent seizure cluster and subsequent six seizure-free weeks together best describe the current seizure frequency burden.
- 1573: mode `related_candidate_group`, selected ['llm:1573:1', 'llm:1573:2'], kinds ['frequency_rate', 'cluster_frequency'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `preserve_as_cluster_modifier_context`. Rationale: The total seizure count and cluster frequency together best describe the current seizure burden.
- 1591: mode `related_candidate_group`, selected ['llm:1591:1', 'llm:1591:2'], kinds ['frequency_rate', 'frequency_rate'], source types ['llm_candidate', 'llm_candidate'], flags [], policy `aggregate_selected_candidates`. Rationale: Both five focal onset seizures and six focal non-motor seizures in the last month jointly describe the current seizure frequency burden.
- 1880: mode `related_candidate_group`, selected ['llm:1880:2', 'llm:1880:3'], kinds ['frequency_rate', 'frequency_rate'], source types ['llm_candidate', 'llm_candidate'], flags [], policy `aggregate_selected_candidates`. Rationale: The one drop attack and seven convulsions in the past two months together best describe the current seizure frequency burden.
- 3468: mode `related_candidate_group`, selected ['llm:3468:1', 'llm:3468:2'], kinds ['cluster_frequency', 'seizure_free'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `split_primary_with_context`. Rationale: The seizure frequency burden is best described by both the perimenstrual seizure clustering and the seizure-free periods outside this window.
- 3469: mode `related_candidate_group`, selected ['llm:3469:1', 'llm:3469:2'], kinds ['cluster_frequency', 'seizure_free'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind', 'mixed_temporality'], policy `split_primary_with_context`. Rationale: Seizures occur only perimenstrually with no events outside this window over six months, so both candidates together describe the current seizure frequency burden.
- 3643: mode `related_candidate_group`, selected ['llm:3643:1', 'llm:3643:5'], kinds ['cluster_frequency', 'frequency_rate'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `preserve_as_cluster_modifier_context`. Rationale: Clusters up to 7 in bad weeks and one daytime convulsion together best describe current seizure frequency burden.
- 3774: mode `related_candidate_group`, selected ['llm:3774:1', 'llm:3774:2'], kinds ['frequency_rate', 'frequency_rate'], source types ['llm_candidate', 'llm_candidate'], flags [], policy `aggregate_selected_candidates`. Rationale: Both candidates describe related recent seizure frequency evidence within the same clinical window and should be interpreted together.

### Related Group Coherence Flags

- 338: mode `related_candidate_group`, selected ['det:338:1', 'llm:338:2'], kinds ['unknown_frequency', 'cluster_frequency'], source types ['deterministic_candidate', 'llm_candidate'], flags ['mixed_candidate_kind', 'mixed_temporality'], policy `preserve_as_cluster_modifier_context`. Rationale: The patient has many convulsions in the past month that cluster after eastbound flights and restricted sleep, so both candidates together best describe the current seizure frequency burden.
- 466: mode `related_candidate_group`, selected ['llm:466:1', 'llm:466:2'], kinds ['frequency_rate', 'cluster_frequency'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `preserve_as_cluster_modifier_context`. Rationale: The current seizure frequency and cluster information together best describe the patient's seizure burden.
- 1046: mode `related_candidate_group`, selected ['det:1046:1', 'llm:1046:2'], kinds ['frequency_rate', 'frequency_rate'], source types ['deterministic_candidate', 'llm_candidate'], flags ['mixed_temporality'], policy `route_to_verifier_before_normalization`. Rationale: The combined candidates describe the recent seizure frequency including both total count and specific focal seizure types, providing a fuller picture of current seizure burden.
- 1165: mode `related_candidate_group`, selected ['llm:1165:1', 'llm:1165:2'], kinds ['cluster_frequency', 'seizure_free'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `split_primary_with_context`. Rationale: The recent seizure cluster and subsequent six seizure-free weeks together best describe the current seizure frequency burden.
- 1573: mode `related_candidate_group`, selected ['llm:1573:1', 'llm:1573:2'], kinds ['frequency_rate', 'cluster_frequency'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `preserve_as_cluster_modifier_context`. Rationale: The total seizure count and cluster frequency together best describe the current seizure burden.
- 3468: mode `related_candidate_group`, selected ['llm:3468:1', 'llm:3468:2'], kinds ['cluster_frequency', 'seizure_free'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `split_primary_with_context`. Rationale: The seizure frequency burden is best described by both the perimenstrual seizure clustering and the seizure-free periods outside this window.
- 3469: mode `related_candidate_group`, selected ['llm:3469:1', 'llm:3469:2'], kinds ['cluster_frequency', 'seizure_free'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind', 'mixed_temporality'], policy `split_primary_with_context`. Rationale: Seizures occur only perimenstrually with no events outside this window over six months, so both candidates together describe the current seizure frequency burden.
- 3643: mode `related_candidate_group`, selected ['llm:3643:1', 'llm:3643:5'], kinds ['cluster_frequency', 'frequency_rate'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `preserve_as_cluster_modifier_context`. Rationale: Clusters up to 7 in bad weeks and one daytime convulsion together best describe current seizure frequency burden.
- 3949: mode `related_candidate_group`, selected ['llm:3949:1', 'llm:3949:2'], kinds ['frequency_rate', 'cluster_frequency'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `preserve_as_cluster_modifier_context`. Rationale: The average seizure frequency and the peri-menstrual exacerbation together best describe the current seizure burden.
- 4026: mode `related_candidate_group`, selected ['llm:4026:3', 'llm:4026:4'], kinds ['frequency_rate', 'seizure_free'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind', 'no_cluster_or_shared_kind_signal'], policy `split_primary_with_context`. Rationale: These candidates together describe the current seizure frequency and seizure-free months, providing a complete picture of the current burden.
- 4478: mode `related_candidate_group`, selected ['det:4478:2', 'llm:4478:2'], kinds ['frequency_rate', 'unknown_frequency'], source types ['deterministic_candidate', 'llm_candidate'], flags ['mixed_candidate_kind', 'mixed_temporality', 'no_cluster_or_shared_kind_signal'], policy `route_to_verifier_before_normalization`. Rationale: Both candidates describe related seizure frequency events in the same recent clinical window and should be interpreted together.
- 4771: mode `related_candidate_group`, selected ['llm:4771:3', 'llm:4771:4'], kinds ['frequency_rate', 'unknown_frequency'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind', 'no_cluster_or_shared_kind_signal'], policy `route_to_verifier_before_normalization`. Rationale: Two recent secondary generalised seizures and short runs of events over several days together best describe current seizure frequency burden.

### High Burden Rows

- 182: mode `single_candidate`, selected ['llm:182:1'], kinds ['frequency_rate'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: This candidate explicitly states the current seizure frequency as every 2 days on average with certainty.
- 190: mode `single_candidate`, selected ['llm:190:1'], kinds ['cluster_frequency'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: The candidate llm:190:1 explicitly describes the current seizure frequency as clusters every 4 weeks over 1-2 days, which best captures the patient's current seizure burden.
- 198: mode `single_candidate`, selected ['llm:198:1'], kinds ['frequency_rate'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: The candidate llm:198:1 explicitly states the current seizure frequency as every 4 weeks, which best describes the patient's current seizure burden.
- 280: mode `single_candidate`, selected ['det:280:1'], kinds ['frequency_rate'], source types ['deterministic_candidate'], flags [], policy `not_applicable`. Rationale: The candidate 'multiple seizures in past day' explicitly describes the current seizure frequency burden.
- 446: mode `single_candidate`, selected ['llm:446:3'], kinds ['frequency_rate'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: This candidate provides the most current and explicit seizure frequency evidence as ≤ twice per week over the past month.
- 466: mode `related_candidate_group`, selected ['llm:466:1', 'llm:466:2'], kinds ['frequency_rate', 'cluster_frequency'], source types ['llm_candidate', 'llm_candidate'], flags ['mixed_candidate_kind'], policy `preserve_as_cluster_modifier_context`. Rationale: The current seizure frequency and cluster information together best describe the patient's seizure burden.
- 598: mode `single_candidate`, selected ['llm:598:2'], kinds ['frequency_rate'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: This candidate provides a clear, recent, and averaged seizure frequency over the past 16 months, directly describing the current seizure burden.
- 678: mode `single_candidate`, selected ['llm:678:1'], kinds ['frequency_rate'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: This candidate explicitly states the current seizure frequency as twice every 4 months, which is the clearest and most relevant evidence.
- 744: mode `related_candidate_group`, selected ['det:744:2', 'det:744:1'], kinds ['frequency_rate', 'frequency_rate'], source types ['deterministic_candidate', 'deterministic_candidate'], flags [], policy `aggregate_selected_candidates`. Rationale: Both the frequent brief absences on most weekdays and the single generalised tonic–clonic seizure in the last eight weeks jointly describe the current seizure frequency burden.
- 763: mode `single_candidate`, selected ['llm:763:1'], kinds ['frequency_rate'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: The candidate llm:763:1 explicitly states ongoing seizure-like events occurring roughly weekly, reflecting the current seizure frequency burden.
- 816: mode `single_candidate`, selected ['llm:816:1'], kinds ['frequency_rate'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: The note explicitly states the current seizure frequency as monthly seizures, making llm:816:1 the best current evidence.
- 959: mode `single_candidate`, selected ['llm:959:2'], kinds ['frequency_rate'], source types ['llm_candidate'], flags [], policy `not_applicable`. Rationale: Candidate llm:959:2 provides the most complete and current description of seizure frequency including variability within months.
