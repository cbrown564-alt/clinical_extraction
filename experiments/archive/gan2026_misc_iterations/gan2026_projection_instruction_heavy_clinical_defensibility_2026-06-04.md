# Projection Clinical Defensibility Audit

Question: when the instruction-heavy projection prompt disagrees with the reference label, is the selected clinical statement still defensible?

- JSONL artifact: `experiments/gan2026_projection_instruction_heavy_clinical_defensibility_2026-06-04.jsonl`
- Rows audited: 125
- Full-note projection errors: 64
- Full-note clinically defensible or debatable: 61
- Full-note errors that were defensible or debatable from the fixed input: 51
- Scope: validation-development rows only; reference labels are metadata, not the judge target.

## Defensibility Counts

| Defensibility | Full note | Fixed input |
| --- | ---: | ---: |
| `clinically_debatable` | 2 | 19 |
| `clinically_defensible` | 59 | 92 |
| `insufficient_information_to_judge` | 3 | 9 |
| `not_clinically_defensible` | 61 | 5 |

## Panel Summary

| Panel | Rows | Clinically defensible | Debatable | Not defensible | Input problem |
| --- | ---: | ---: | ---: | ---: | ---: |
| `balanced_validation50` | 50 | 31 | 0 | 16 | 20 |
| `hidden_family_hard_panel` | 75 | 28 | 2 | 45 | 41 |

## Primary Error Families For Full-Note Errors

| Family | Rows |
| --- | ---: |
| `input_target_distractor` | 20 |
| `seizure_free_overreach` | 20 |
| `other` | 13 |
| `ignores_active_events_or_spells` | 4 |
| `conditional_event_mishandled` | 3 |
| `no_reference_collapse` | 2 |
| `none_defensible` | 1 |
| `wrong_rate_or_over_specific_label` | 1 |

## Non-Error Clinical Patterns

| Family | Rows |
| --- | ---: |
| `none_defensible` | 43 |
| `other` | 8 |
| `input_target_distractor` | 5 |
| `cluster_cadence_or_burden_confusion` | 2 |
| `reasonable_alternative_to_answer_key` | 1 |
| `wrong_rate_or_over_specific_label` | 1 |
| `seizure_free_overreach` | 1 |

## Representative Rows

### `input_target_distractor`

| Row | Panel | Selected statement | Full-note defensibility | Rationale |
| ---: | --- | --- | --- | --- |
| 744 | `balanced_validation50` | One generalised tonic–clonic seizure in the last eight weeks. | `not_clinically_defensible` | Note states frequent brief absences on most weekdays, contradicting seizure freedom implied by candidate; candidate only mentions tonic–clonic seizure. |
| 869 | `balanced_validation50` | No seizure frequency information present in the candidate or evidence. | `not_clinically_defensible` | Candidate and evidence lack frequency data but note states ongoing events. |
| 1317 | `balanced_validation50` | No seizure frequency information is present in the supplied candidate or evidence. | `not_clinically_defensible` | Fixed input lacks seizure frequency data; note reports recent cluster of events. |
| 3436 | `balanced_validation50` | No seizure frequency information present in the candidate or evidence. | `not_clinically_defensible` | Fixed input lacks seizure frequency data; note states active clustered events. |
| 11408 | `balanced_validation50` | No seizure frequency information present in the candidate or evidence. | `not_clinically_defensible` | No seizure frequency data in note or candidate; note lacks seizure info but candidate is empty, so input is a distractor. |

### `seizure_free_overreach`

| Row | Panel | Selected statement | Full-note defensibility | Rationale |
| ---: | --- | --- | --- | --- |
| 3356 | `balanced_validation50` | Seizure free for multiple years | `not_clinically_defensible` | Note reports seizures in past 3 months after curtailed sleep; contradicts seizure freedom claim. |
| 278 | `hidden_family_hard_panel` | Seizure free for multiple year | `not_clinically_defensible` | Note states "events have been occurring multiple times in past week" contradicting seizure freedom. |
| 3528 | `hidden_family_hard_panel` | Seizure free for multiple years with no witnessed generalised tonic–clonic seizures since 2018. | `not_clinically_defensible` | Note reports ongoing brief jerks and absences despite no generalised tonic–clonic seizures since 2018. |
| 4368 | `hidden_family_hard_panel` | Seizure free for multiple year | `not_clinically_defensible` | Note documents multiple recent seizures in 2023, contradicting seizure freedom. |
| 5534 | `hidden_family_hard_panel` | Seizure free for multiple years with no generalised tonic–clonic seizures since last year. | `not_clinically_defensible` | Note reports a recent brief event; seizure freedom over multiple years is contradicted. |

### `other`

| Row | Panel | Selected statement | Full-note defensibility | Rationale |
| ---: | --- | --- | --- | --- |
| 278 | `balanced_validation50` | Seizure free for multiple year | `not_clinically_defensible` | Note states "events have been occurring multiple times in past week" contradicting seizure freedom. |
| 338 | `balanced_validation50` | No seizure frequency information present in the candidate or evidence. | `not_clinically_defensible` | Fixed input lacks seizure frequency data; note states 'many convulsions in past month'. |
| 466 | `balanced_validation50` | Seizure free for multiple year | `not_clinically_defensible` | Note states 21 to 28 seizures per month, contradicting seizure freedom claim. |
| 743 | `balanced_validation50` | No seizure frequency information present in the candidate or evidence. | `not_clinically_defensible` | Fixed input lacks seizure frequency data; note states "ongoing events arising on most working days." |
| 2149 | `balanced_validation50` | No seizure frequency information present in the supplied candidate or evidence. | `not_clinically_defensible` | Fixed input lacks seizure frequency data; note shows ongoing seizures and clusters. |

### `ignores_active_events_or_spells`

| Row | Panel | Selected statement | Full-note defensibility | Rationale |
| ---: | --- | --- | --- | --- |
| 4690 | `hidden_family_hard_panel` | Seizure free for multiple years with no witnessed convulsions since last contact. | `not_clinically_defensible` | Note reports frequent electrographic seizures despite no witnessed convulsions. |
| 12438 | `hidden_family_hard_panel` | 2 - 3 times per year | `not_clinically_defensible` | Note states "nightly generalised tonic-clonic seizures" indicating higher frequency than 2-3 per year. |
| 14025 | `hidden_family_hard_panel` | Seizure free for multiple year | `not_clinically_defensible` | Note reports two recent drop attacks; seizure freedom claim ignores these events. |
| 15168 | `hidden_family_hard_panel` | Seizure free for multiple years with no generalised seizures since 9-2018 | `not_clinically_defensible` | Note reports ongoing myoclonic jerks and focal auras despite no generalised seizures. |

### `conditional_event_mishandled`

| Row | Panel | Selected statement | Full-note defensibility | Rationale |
| ---: | --- | --- | --- | --- |
| 3371 | `balanced_validation50` | Seizure freedom for multiple years | `not_clinically_defensible` | Note states seizures occur with significantly short sleep, so seizure freedom is not supported. |
| 3469 | `balanced_validation50` | Seizure free for 6 months | `not_clinically_defensible` | Note states seizures occur perimenstrually, so seizure freedom is conditional, not absolute. |
| 3356 | `hidden_family_hard_panel` | Seizure free for multiple years | `not_clinically_defensible` | Note reports seizures after curtailed sleep; candidate ignores these conditional events. |

### `no_reference_collapse`

| Row | Panel | Selected statement | Full-note defensibility | Rationale |
| ---: | --- | --- | --- | --- |
| 11405 | `balanced_validation50` | No seizure frequency information present in the candidate or evidence. | `insufficient_information_to_judge` | No seizure frequency data in note or candidate. |
| 11409 | `balanced_validation50` | No seizure frequency information present in the candidate or evidence. | `insufficient_information_to_judge` | Candidate and evidence contain no seizure frequency data; note lacks explicit frequency details. |

### `none_defensible`

| Row | Panel | Selected statement | Full-note defensibility | Rationale |
| ---: | --- | --- | --- | --- |
| 11400 | `balanced_validation50` | No seizure frequency information present in the candidate or evidence. | `insufficient_information_to_judge` | No seizure frequency or seizure-related information is present in the note or candidate. |

### `wrong_rate_or_over_specific_label`

| Row | Panel | Selected statement | Full-note defensibility | Rationale |
| ---: | --- | --- | --- | --- |
| 6889 | `hidden_family_hard_panel` | Several times per week | `not_clinically_defensible` | Note states focal seizures occur once every 2–3 weeks, contradicting 'several times per week'. |

## Representative Defensible Rows

| Row | Panel | Selected statement | Family | Rationale |
| ---: | --- | --- | --- | --- |
| 10 | `balanced_validation50` | Seizure frequency is multiple per day, specifically four per day. | `other` | Note states '≤ four per day' and 'brief episodes most days'; fixed evidence 'four per day' supports multiple daily seizures. |
| 40 | `balanced_validation50` | Four seizures per week | `none_defensible` | Note states 'frequency of ≤ four seizures per week' and 'corroborates this frequency'. |
| 79 | `balanced_validation50` | 6 to 7 per year | `none_defensible` | Note states 'seizure burden remains ≤ 6 to 7 per year' with no contradictions. |
| 103 | `balanced_validation50` | Seizure frequency is two or four per year. | `reasonable_alternative_to_answer_key` | Note states '≤ two or four per year' and 'current pattern is ≤ two or four per year'. |
| 128 | `balanced_validation50` | Current seizure frequency is 17 per month | `none_defensible` | Note states 'He reports a current seizure frequency of 17 per month' matching evidence. |
| 156 | `balanced_validation50` | Seizures every 6 days | `none_defensible` | Note states 'Patient reports seizures every 6 days' with family corroboration. |
| 180 | `balanced_validation50` | Seizures every seven days | `other` | Note states "a pattern of seizures every seven days"; fixed evidence matches. |
| 182 | `balanced_validation50` | Seizures occurring every 2 days | `other` | Note states seizures "are occurring every 2 days on average"; no contradictory info. |
| 187 | `balanced_validation50` | cluster every seven to nine days | `cluster_cadence_or_burden_confusion` | Note states 'events tend to cluster every seven to nine days' supporting cluster frequency; fixed input lacks numeric count and time basis, making it incomplete. |
| 190 | `balanced_validation50` | Episodes every 4 weeks | `none_defensible` | Note states 'clusters of brief absence episodes every 4 weeks'. Fixed evidence matches this exactly. |
| 198 | `balanced_validation50` | Seizures every 4 weeks | `none_defensible` | Note states 'they continue to have seizures every 4 weeks' with no contradictions. |
| 212 | `balanced_validation50` | Seizures occurring every 3-4 weeks | `none_defensible` | Note states "ongoing episodes occurring every 3 - 4 weeks"; evidence matches. |