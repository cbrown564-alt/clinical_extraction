# ExECTv2 Gold Schema Profile — 2026-06-09

One-shot profile of all 200 ExECTv2 letters (`load_letters()`).  The entity
registry in `contract/entities.py` is derived from this document.

## Corpus totals

| Entity | Mentions | Letters with ≥1 |
|--------|----------|-----------------|
| PatientHistory | 656 | — |
| Diagnosis | 572 | — |
| Prescription | 294 | — |
| SeizureFrequency | 263 | 142 |
| Investigations | 183 | — |
| BirthHistory | 47 | — |
| EpilepsyCause | 36 | — |
| Onset | 24 | — |
| WhenDiagnosed | 17 | — |

## Attribute schemas by entity

### BirthHistory

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| PrematureBirth | closed | `32to<37_ModerateToLatePreterm`, `34to<37_LatePreterm`, `34to<37_LatePretermBirth`, `37+_TermBirth` |
| CUI | reference | 9 distinct CUIs |
| CUIPhrase | redundant | mirrors annotated phrase |
| Certainty | closed | `4`, `5` |
| Negation | closed | `Affirmed` |

### Diagnosis

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| DiagCategory | closed | `Epilepsy`, `epilepsy` (annotation inconsistency — EA0138), `MultipleSeizures`, `SingleSeizure` |
| CUI | reference | 32 distinct CUIs |
| CUIPhrase | redundant | 84 distinct phrases |
| Certainty | closed | `3`, `4`, `5` |
| Negation | closed | `Affirmed` |

### EpilepsyCause

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| CUI | reference | 22 distinct CUIs |
| CUIPhrase | redundant | 25 distinct phrases |
| Certainty | closed | `4`, `5` |
| Negation | closed | `Affirmed` |

### Investigations

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| MRI_Performed | closed | `Yes` |
| MRI_Results | closed | `Normal`, `Abnormal` |
| CT_Performed | closed | `Yes` |
| CT_Results | closed | `Normal`, `Abnormal`, `Unknown` |
| EEG_Performed | closed | `Yes` |
| EEG_Results | closed | `Normal`, `Abnormal`, `Unknown` |
| EEG_Type | closed | `Standard`, `SleepDeprived`, `VideoTelemetry` |
| CUI | reference | 8 distinct CUIs |
| CUIPhrase | redundant | 17 distinct phrases |

### Onset

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| Age | free | `3`, `4`, `6`, `8`, `10`, `12`, `14`, `23` |
| AgeLower | free | `1`, `13` |
| AgeUpper | free | `6`, `19` |
| AgeUnit | closed | `Year` |
| NumberOfTimePeriods | free | `3`, `10`, `15`, `16` |
| TimePeriod | closed | `Year` |
| PointInTime | closed | `From_Birth` |
| CUI | reference | 5 distinct CUIs |
| CUIPhrase | redundant | 6 distinct phrases |
| Certainty | closed | `5` |
| Negation | closed | `Affirmed` |

### PatientHistory

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| Age | free | 21 distinct values (2–90) |
| AgeLower | free | 9 distinct values |
| AgeUpper | free | 10 distinct values |
| AgeUnit | closed | `Year`, `Month` |
| DayDate | free | `1`, `3` |
| MonthDate | free | `1`, `2`, `3`, `6`, `9`, `11` |
| YearDate | free | 2003–2018 |
| NumberOfTimePeriods | free | `1`, `2`, `6`, `10`, `12` |
| TimePeriod | closed | `Year`, `Month` |
| PointInTime | closed | `Last_Year`, `Surgery` |
| CUI | reference | 85 distinct CUIs |
| CUIPhrase | redundant | 133 distinct phrases |
| Certainty | closed | `1`, `3`, `4`, `5` |
| Negation | closed | `Affirmed`, `Negated` |
| **C0151744** | **noise** | `collapse` — CUI key used as attribute name on one mention |

### Prescription

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| DrugName | closed | `Brivaracetam`, `Carbamazepine`, `Clobazam`, `Epilim`, `EslicarbazepineAcetate`, `Lacosamide`, `Lamotrigine`, `Levetiracetam`, `Midazolam`, `Oxcarbazepine`, + 27 more |
| DrugDose | free | 33 distinct numeric values |
| DoseUnit | closed | `mg`, `g` |
| Frequency | closed | `1`, `2`, `3`, `As_Required` |
| CUI | reference | 23 distinct CUIs |
| CUIPhrase | redundant | 29 distinct phrases |

### SeizureFrequency

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| NumberOfSeizures | free | `0` (×92), `1`, `2`, `3`, `4`, `5`, `15` |
| LowerNumberOfSeizures | free | `0`, `1`, `2`, `3`, `4`, `6`, `10` |
| UpperNumberOfSeizures | free | `2`, `3`, `4`, `5`, `9`, `15` |
| NumberOfTimePeriods | free | `1`–`10` |
| LowerNumberOfTimePeriods | free | `1`, `2`, `3` |
| UpperNumberOfTimePeriods | free | `2`, `3`, `4` |
| TimePeriod | closed | `Day`, `Week`, `Month`, `Year`; `days` (1 mention — noise for `Day`) |
| TimeSince_or_TimeOfEvent | closed | `During`, `Since` |
| FrequencyChange | closed | `Decreased`, `Frequent`, `Increased`, `Infrequent`, `Same` |
| PointInTime | closed | `Birthday`, `DrugChange`, `LastClinic`, `Last_Month`, `Last_Week`, `Last_Year`, `Surgery` |
| DayDate | free | `2`, `3`, `6`, `15`, `23`, `25` |
| MonthDate | free | `2`–`12` (most months) |
| YearDate | free | 2005–2020 |
| AgeLower | free | `13` |
| AgeUpper | free | `19` |
| AgeUnit | closed | `Year` |
| CUI | reference | 16 distinct CUIs |
| CUIPhrase | redundant | 44 distinct phrases |
| Certainty | closed | `4`, `5` |
| Negation | closed | `Affirmed` |
| **DiagCategory** | **noise** | `MultipleSeizures` (2 mentions) — stray attribute from Diagnosis entity |

### WhenDiagnosed

| Attribute | Type | Observed values |
|-----------|------|-----------------|
| Age | free | `4`, `6`, `18`, `22`, `36` |
| AgeUnit | closed | `Year` |
| MonthDate | free | `5` |
| YearDate | free | 2009, 2012, 2015, 2017 |
| NumberOfTimePeriods | free | `6`, `10`, `16` |
| TimePeriod | closed | `Year` |
| CUI | reference | 1 distinct CUI |
| CUIPhrase | redundant | 1 distinct phrase |
| Certainty | closed | `5` |
| Negation | closed | `Affirmed` |

## Annotation noise summary

| Location | Noise attribute | Count | Note |
|----------|-----------------|-------|------|
| SeizureFrequency | `DiagCategory="MultipleSeizures"` | 2 | Stray from Diagnosis schema |
| PatientHistory | `C0151744="collapse"` | 1 | CUI used as attribute key |
| Diagnosis | `DiagCategory="epilepsy"` (lowercase) | 1 | Case inconsistency (EA0138) |
| SeizureFrequency | `TimePeriod="days"` | 1 | Plural form of `Day` |

These are documented in the registry (`noise_attributes` field) and accepted by the
validation gate rather than silently rejected.
