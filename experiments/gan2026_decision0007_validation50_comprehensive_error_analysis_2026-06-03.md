# Decision 0007 Validation50 Comprehensive Error Analysis

- Date: 2026-06-03
- Source JSONL: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation50_gpt41mini_v1_2026-06-03.jsonl`
- Pipeline: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v1`
- Split: first 50 `validation` rows under `gan2026_split_v1`; no test rows inspected
- Model/mode: `openai/gpt-4.1-mini`, live hosted calls
- Primary recommendation: make Decision 0007 the primary LLM-heavy lane; add explicit post-processing as named deterministic repair, not silent scorer drift.

## Executive Finding

Decision 0007 v1 should become the primary LLM-heavy architecture because its output contract is healthy: 50/50 typed structured outputs, 0 call failures, 0 parse failures, 49/50 exact selected evidence, and 49/50 complete selected operands. The current reported mechanical-adapter layer is 44/50 Purist, but the row-level evidence shows the main problem is not broad clinical selection failure. The raw parser label is already 45/50 Purist, and a small, explicitly named post-processing stack over model-selected labels/evidence would likely recover the six mechanical-adapter Purist misses on this validation50 prefix.

This should be treated as a hybrid LLM-selected plus deterministic post-processing development artifact until same-raw-output ablations prove which repairs are format/convention only and which are semantic benchmark policy.

## Stage Metrics

| Stage | Scorable | Purist | Pragmatic |
|---|---:|---:|---:|
| Raw parser | 50/50 | 45/50 (0.9000) | 47/50 (0.9400) |
| Clinical selection repair | 50/50 | 45/50 (0.9000) | 47/50 (0.9400) |
| Format-only repair | 50/50 | 45/50 (0.9000) | 47/50 (0.9400) |
| Mechanical adapter | 49/50 | 44/50 (0.8800) | 46/50 (0.9200) |
| Benchmark convention adapter | 49/50 | 44/50 (0.8800) | 46/50 (0.9200) |

## Component Health

- Structured typed outputs: 50/50
- Adapter parse failures: 0/50
- Selected evidence exact: 49/50
- Selected fact trace mismatches: 0/50
- Selected operand completeness: 49/50
- Non-ok component counts: `evidence_exactness:fail` 1, `mechanical_adapter_rendering:fail` 1, `selected_operand_completeness:fail` 1

## Candidate Post-Processing Projection

This is a no-call diagnostic projection over saved outputs, not an implemented score. The proposed final layer chooses only among the model-selected raw label, selected evidence, and typed operands; it does not inspect deterministic candidates or choose a different note fact.

- Projected scorable: 50/50
- Projected Purist: 50/50 (1.0000)
- Projected Pragmatic: 50/50 (1.0000)

| Repair family | Rows | Why it matters |
|---|---:|---|
| raw-preserving adapter fallback when mechanical operands are incomplete but raw parser label is scorable | 1 | Named deterministic post-processing over selected fact/evidence. |
| benchmark vague-weekday convention: most weekdays -> multiple per week rather than numeric weekday count | 1 | Named deterministic post-processing over selected fact/evidence. |
| current-state precedence inside selected evidence: currently reporting monthly seizures beats historical/year-to-date count | 1 | Named deterministic post-processing over selected fact/evidence. |
| selected-evidence phrase repair: every other day -> 1 per 2 day | 1 | Named deterministic post-processing over selected fact/evidence. |
| Gan-specific selected-evidence repair: bimonthly -> 1 per 2 month | 3 | Named deterministic post-processing over selected fact/evidence. |

## Mechanical-Adapter Misses

### Pos 32, Source 743

- Gold: `multiple per week`; row_ok=True
- Selected fact kind/raw value: `frequency` / `most shifts`
- Exact selected fact evidence: `Daniel Harris reports that these episodes crop up most shifts, especially during the busiest part of service, and his manager has had to reassign him from open flame stations as a precaution.`
- Raw answer selected evidence: `Daniel Harris reports that these episodes crop up most shifts, especially during the busiest part of service, and his manager has had to reassign him from open flame stations as a precaution.`
- Raw parser: `multiple per shift` (P=yes, Pr=yes)
- Raw clinical-selection repair: `multiple per shift` (P=yes, Pr=yes)
- Format-only repair: `multiple per shift` (P=yes, Pr=yes)
- Mechanical adapter: `None` (P=n/a, Pr=n/a, unscorable, err=missing_final_label)
- Benchmark convention adapter: `None` (P=n/a, Pr=n/a, unscorable, err=missing_final_label)
- Candidate post-processing: `multiple per shift` (raw-preserving adapter fallback when mechanical operands are incomplete but raw parser label is scorable); projected Purist=yes, Pragmatic=yes
- Interpretation:
  Raw parser label is already scorer-correct. The adapter should preserve a scorable raw vague label when operands are intentionally incomplete rather than returning `None`.

### Pos 33, Source 744

- Gold: `multiple per week`; row_ok=True
- Selected fact kind/raw value: `frequency` / `most weekdays for brief absences, 1 generalised tonic–clonic seizure in 8 weeks`
- Exact selected fact evidence: `Over the past two months she reports brief absences occurring on most weekdays, often clustering around late afternoon when she is more tired. There has been one generalised tonic–clonic seizure in the last eight weeks, witnessed at home.`
- Raw answer selected evidence: `Over the past two months she reports brief absences occurring on most weekdays, often clustering around late afternoon when she is more tired. There has been one generalised tonic–clonic seizure in the last eight weeks, witnessed at home.`
- Raw parser: `3 to 5 per 7 day` (P=no, Pr=no)
- Raw clinical-selection repair: `3 to 5 per 7 day` (P=no, Pr=no)
- Format-only repair: `3 to 5 per 7 day` (P=no, Pr=no)
- Mechanical adapter: `3 to 5 per 7 day` (P=no, Pr=no)
- Benchmark convention adapter: `3 to 5 per 7 day` (P=no, Pr=no)
- Candidate post-processing: `multiple per week` (benchmark vague-weekday convention: most weekdays -> multiple per week rather than numeric weekday count); projected Purist=yes, Pragmatic=yes
- Interpretation:
  Clinically, `3 to 5 per 7 day` is a reasonable interpretation of most weekdays. The Gan gold uses the vague label `multiple per week`, which maps to the unknown/vague category. This repair is benchmark-convention-sensitive and should be tested/flagged, not hidden as format-only normalization.

### Pos 36, Source 816

- Gold: `1 per month`; row_ok=True
- Selected fact kind/raw value: `frequency` / `4 per year`
- Exact selected fact evidence: `Currently reporting monthly seizures, typically brief focal-onset episodes with rapid recovery as described by the family. Since commencing ketogenic diet therapy, the family notes a marked reduction in seizure frequency with only four brief seizures recorded in 2017 so far.`
- Raw answer selected evidence: `Currently reporting monthly seizures, typically brief focal-onset episodes with rapid recovery as described by the family. Since commencing ketogenic diet therapy, the family notes a marked reduction in seizure frequency with only four brief seizures recorded in 2017 so far.`
- Raw parser: `4 per 1 year` (P=no, Pr=yes)
- Raw clinical-selection repair: `4 per 1 year` (P=no, Pr=yes)
- Format-only repair: `4 per year` (P=no, Pr=yes)
- Mechanical adapter: `4 per 1 year` (P=no, Pr=yes)
- Benchmark convention adapter: `4 per year` (P=no, Pr=yes)
- Candidate post-processing: `1 per month` (current-state precedence inside selected evidence: currently reporting monthly seizures beats historical/year-to-date count); projected Purist=yes, Pragmatic=yes
- Interpretation:
  The selected evidence contains both `Currently reporting monthly seizures` and a lower historical/year-to-date count. The model chose the lower count, but a current-state precedence repair would recover the gold label.

### Pos 40, Source 891

- Gold: `1 per 2 day`; row_ok=True
- Selected fact kind/raw value: `frequency` / `1 per 2 days`
- Exact selected fact evidence: `She experiences brief right temporal tingling and rising epigastric discomfort, followed by staring and speech arrest lasting 1–2 minutes. These have become frequent, with seizures every other day.`
- Raw answer selected evidence: `She experiences brief right temporal tingling and rising epigastric discomfort, followed by staring and speech arrest lasting 1–2 minutes. These have become frequent, with seizures every other day.`
- Raw parser: `3 to 4 per 6 week` (P=no, Pr=yes)
- Raw clinical-selection repair: `3 to 4 per 6 week` (P=no, Pr=yes)
- Format-only repair: `3 to 4 per 6 week` (P=no, Pr=yes)
- Mechanical adapter: `3 to 4 per 6 week` (P=no, Pr=yes)
- Benchmark convention adapter: `3 to 4 per 6 week` (P=no, Pr=yes)
- Candidate post-processing: `1 per 2 day` (selected-evidence phrase repair: every other day -> 1 per 2 day); projected Purist=yes, Pragmatic=yes
- Interpretation:
  The exact evidence says `seizures every other day`; operands drift to a six-week range. Selected-evidence phrase repair is a strong candidate.

### Pos 42, Source 959

- Gold: `1 per 2 month`; row_ok=True
- Selected fact kind/raw value: `frequency` / `bimonthly on average`
- Exact selected fact evidence: `She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession.`
- Raw answer selected evidence: `She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession.`
- Raw parser: `2 per 1 to 2 month` (P=no, Pr=no)
- Raw clinical-selection repair: `2 per 1 to 2 month` (P=no, Pr=no)
- Format-only repair: `2 per 1 to 2 month` (P=no, Pr=no)
- Mechanical adapter: `2 per 1 to 2 month` (P=no, Pr=no)
- Benchmark convention adapter: `2 per 1 to 2 month` (P=no, Pr=no)
- Candidate post-processing: `1 per 2 month` (Gan-specific selected-evidence repair: bimonthly -> 1 per 2 month); projected Purist=yes, Pragmatic=yes
- Interpretation:
  The exact evidence says bimonthly. Existing Gan policy already treats bare bimonthly as `1 per 2 month`; the typed operand packet currently misrenders it as two events over one/two months.

### Pos 45, Source 987

- Gold: `1 per 2 month`; row_ok=True
- Selected fact kind/raw value: `frequency` / `bimonthly seizures`
- Exact selected fact evidence: `This patient reports bimonthly seizures, generally occurring after sequences of night shifts and rapid rota changes.`
- Raw answer selected evidence: `This patient reports bimonthly seizures, generally occurring after sequences of night shifts and rapid rota changes.`
- Raw parser: `2 per 1 month` (P=no, Pr=no)
- Raw clinical-selection repair: `2 per 1 month` (P=no, Pr=no)
- Format-only repair: `2 per month` (P=no, Pr=no)
- Mechanical adapter: `2 per 1 month` (P=no, Pr=no)
- Benchmark convention adapter: `2 per month` (P=no, Pr=no)
- Candidate post-processing: `1 per 2 month` (Gan-specific selected-evidence repair: bimonthly -> 1 per 2 month); projected Purist=yes, Pragmatic=yes
- Interpretation:
  The exact evidence says bimonthly. Existing Gan policy already treats bare bimonthly as `1 per 2 month`; the typed operand packet currently misrenders it as two events over one/two months.

## All Rows With Exact Evidence And Processing Stages

### Pos 1, Source 10

- Gold: `4 per day`; gold normalized: `4 per day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`64 four per day`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `On the accommodation logs, the observed frequency is noted as ≤ four per day, with variable clustering, often in the late afternoon or evening.`
- Raw answer selected evidence: `On the accommodation logs, the observed frequency is noted as ≤ four per day, with variable clustering, often in the late afternoon or evening.`
- Raw parser: `4 per 1 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `4 per 1 day` (P=yes, Pr=yes)
- Format-only repair: `4 per day` (P=yes, Pr=yes)
- Mechanical adapter: `4 per 1 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `4 per day` (P=yes, Pr=yes)
- Candidate post-processing: `4 per 1 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 2, Source 40

- Gold: `4 per week`; gold normalized: `4 per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`≤ four seizures per week`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Since my last assessment he reports a variable pattern of episodes but overall a frequency of ≤ four seizures per week, typically brief generalised convulsions or absence episodes as described below.`
- Raw answer selected evidence: `Since my last assessment he reports a variable pattern of episodes but overall a frequency of ≤ four seizures per week, typically brief generalised convulsions or absence episodes as described below.`
- Raw parser: `4 per 1 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `4 per 1 week` (P=yes, Pr=yes)
- Format-only repair: `4 per week` (P=yes, Pr=yes)
- Mechanical adapter: `4 per 1 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `4 per week` (P=yes, Pr=yes)
- Candidate post-processing: `4 per 1 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 3, Source 79

- Gold: `6 to 7 per year`; gold normalized: `6 to 7 per year`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`≤ 6 to 7 per year`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Seizure frequency currently reported as ≤ 6 to 7 per year, typically clustering around periods of jet lag and sleep loss related to frequent business travel across time zones.`
- Raw answer selected evidence: `Seizure frequency currently reported as ≤ 6 to 7 per year, typically clustering around periods of jet lag and sleep loss related to frequent business travel across time zones.`
- Raw parser: `6 to 7 per 1 year` (P=yes, Pr=yes)
- Raw clinical-selection repair: `6 to 7 per 1 year` (P=yes, Pr=yes)
- Format-only repair: `6 to 7 per year` (P=yes, Pr=yes)
- Mechanical adapter: `6 to 7 per 1 year` (P=yes, Pr=yes)
- Benchmark convention adapter: `6 to 7 per year` (P=yes, Pr=yes)
- Candidate post-processing: `6 to 7 per 1 year` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 4, Source 103

- Gold: `2 to 4 per year`; gold normalized: `2 to 4 per year`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`6#8804; 2 to 4 per year`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Over the past year, however, the patient and family report that events have become markedly infrequent, such that the current pattern is ≤ two or four per year.`
- Raw answer selected evidence: `Over the past year, however, the patient and family report that events have become markedly infrequent, such that the current pattern is ≤ two or four per year.`
- Raw parser: `2 to 4 per 1 year` (P=yes, Pr=yes)
- Raw clinical-selection repair: `2 to 4 per 1 year` (P=yes, Pr=yes)
- Format-only repair: `2 to 4 per year` (P=yes, Pr=yes)
- Mechanical adapter: `2 to 4 per 1 year` (P=yes, Pr=yes)
- Benchmark convention adapter: `2 to 4 per year` (P=yes, Pr=yes)
- Candidate post-processing: `2 to 4 per 1 year` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 5, Source 128

- Gold: `17 per month`; gold normalized: `17 per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`17 per month`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `He reports a current seizure frequency of 17 per month, typically clustering around periods of sleep deprivation and high work-related stress.`
- Raw answer selected evidence: `He reports a current seizure frequency of 17 per month, typically clustering around periods of sleep deprivation and high work-related stress.`
- Raw parser: `17 per 1 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `17 per 1 month` (P=yes, Pr=yes)
- Format-only repair: `17 per month` (P=yes, Pr=yes)
- Mechanical adapter: `17 per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `17 per month` (P=yes, Pr=yes)
- Candidate post-processing: `17 per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 6, Source 156

- Gold: `1 per 6 day`; gold normalized: `1 per 6 day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per 6 days`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Patient reports seizures every 6 days, typically brief focal aware episodes with auditory distortion and right-sided facial tingling. Family corroborates this pattern over the past two months.`
- Raw answer selected evidence: `Patient reports seizures every 6 days, typically brief focal aware episodes with auditory distortion and right-sided facial tingling. Family corroborates this pattern over the past two months.`
- Raw parser: `1 per 6 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 6 day` (P=yes, Pr=yes)
- Format-only repair: `1 per 6 day` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 6 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 6 day` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 6 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 7, Source 180

- Gold: `1 per 7 day`; gold normalized: `1 per 7 day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per 7 days`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `The patient keeps a diary and describes a pattern of seizures every seven days, with post-event morning headaches and tongue soreness on occasion.`
- Raw answer selected evidence: `The patient keeps a diary and describes a pattern of seizures every seven days, with post-event morning headaches and tongue soreness on occasion.`
- Raw parser: `1 per 7 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 7 day` (P=yes, Pr=yes)
- Format-only repair: `1 per 7 day` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 7 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 7 day` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 7 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 8, Source 182

- Gold: `1 per 2 day`; gold normalized: `1 per 2 day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per 2 days`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `The carer reports that seizures are occurring every 2 days on average, based on a written diary and a smartphone log that have been kept consistently since the last review.`
- Raw answer selected evidence: `The carer reports that seizures are occurring every 2 days on average, based on a written diary and a smartphone log that have been kept consistently since the last review.`
- Raw parser: `1 per 2 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 2 day` (P=yes, Pr=yes)
- Format-only repair: `1 per 2 day` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 2 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 2 day` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 2 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 9, Source 187

- Gold: `1 per 7 to 9 day`; gold normalized: `1 per 7 to 9 day`; row_ok=True
- Selected fact: kind=`cluster_frequency`, temporality=`current`, assertion=`asserted`, raw_value=`every 7 to 9 days`
- Benchmark caveat flags: `cluster_axis`
- Exact selected fact evidence: `Since the last review, Ms Aisha Rahman reports that events tend to cluster every seven to nine days.`
- Raw answer selected evidence: `Since the last review, Ms Aisha Rahman reports that events tend to cluster every seven to nine days.`
- Raw parser: `1 per 7 to 9 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 7 to 9 day` (P=yes, Pr=yes)
- Format-only repair: `1 per 7 to 9 day` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 7 to 9 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 7 to 9 day` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 7 to 9 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 10, Source 190

- Gold: `1 per 4 week`; gold normalized: `1 per 4 week`; row_ok=True
- Selected fact: kind=`cluster_frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 cluster every 4 weeks`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress.`
- Raw answer selected evidence: `At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress.`
- Raw parser: `1 per 4 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 4 week` (P=yes, Pr=yes)
- Format-only repair: `1 per 4 week` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 4 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 4 week` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 4 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 11, Source 198

- Gold: `1 per 4 week`; gold normalized: `1 per 4 week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per 4 week`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Despite good adherence to Levetiracetam, they continue to have seizures every 4 weeks.`
- Raw answer selected evidence: `Despite good adherence to Levetiracetam, they continue to have seizures every 4 weeks.`
- Raw parser: `1 per 4 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 4 week` (P=yes, Pr=yes)
- Format-only repair: `1 per 4 week` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 4 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 4 week` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 4 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 12, Source 212

- Gold: `1 per 3 to 4 week`; gold normalized: `1 per 3 to 4 week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`every 3 - 4 weeks`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Since the last clinic contact, the patient reports ongoing episodes occurring every 3 - 4 weeks, typically without a consistent aura.`
- Raw answer selected evidence: `Since the last clinic contact, the patient reports ongoing episodes occurring every 3 - 4 weeks, typically without a consistent aura.`
- Raw parser: `1 per 3 to 4 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 3 to 4 week` (P=yes, Pr=yes)
- Format-only repair: `1 per 3 to 4 week` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 3 to 4 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 3 to 4 week` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 3 to 4 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 13, Source 218

- Gold: `1 per 3 week`; gold normalized: `1 per 3 week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 seizure every 3 weeks`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Prior to these changes, seizures occurred once every two to three days. Over the past three months, they have stabilised at seizures every 3 weeks by the patient’s report, with shorter duration and quicker recovery times.`
- Raw answer selected evidence: `Prior to these changes, seizures occurred once every two to three days. Over the past three months, they have stabilised at seizures every 3 weeks by the patient’s report, with shorter duration and quicker recovery times.`
- Raw parser: `1 per 3 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 3 week` (P=yes, Pr=yes)
- Format-only repair: `1 per 3 week` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 3 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 3 week` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 3 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 14, Source 243

- Gold: `1 per 4 month`; gold normalized: `1 per 4 month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per 4 months`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `He and his partner report that the seizures occur every four months, with the last event taking place on site in the loading area.`
- Raw answer selected evidence: `He and his partner report that the seizures occur every four months, with the last event taking place on site in the loading area.`
- Raw parser: `1 per 4 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 4 month` (P=yes, Pr=yes)
- Format-only repair: `1 per 4 month` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 4 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 4 month` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 4 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 15, Source 278

- Gold: `multiple per week`; gold normalized: `multiple per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`multiple per week`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `These events have been occurring multiple times in past week, including two episodes witnessed by a friend.`
- Raw answer selected evidence: `These events have been occurring multiple times in past week, including two episodes witnessed by a friend.`
- Raw parser: `multiple per week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `multiple per week` (P=yes, Pr=yes)
- Format-only repair: `multiple per week` (P=yes, Pr=yes)
- Mechanical adapter: `multiple per 1 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `multiple per week` (P=yes, Pr=yes)
- Candidate post-processing: `multiple per 1 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 16, Source 280

- Gold: `multiple per day`; gold normalized: `multiple per day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`multiple seizures in past day`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `In the 24 hours prior to clinic he experienced multiple seizures in past day, described by him and his partner as brief episodes of loss of awareness with post-event confusion and marked fatigue.`
- Raw answer selected evidence: `In the 24 hours prior to clinic he experienced multiple seizures in past day, described by him and his partner as brief episodes of loss of awareness with post-event confusion and marked fatigue.`
- Raw parser: `multiple per day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `multiple per day` (P=yes, Pr=yes)
- Format-only repair: `multiple per day` (P=yes, Pr=yes)
- Mechanical adapter: `multiple per 1 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `multiple per day` (P=yes, Pr=yes)
- Candidate post-processing: `multiple per 1 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 17, Source 338

- Gold: `multiple per month`; gold normalized: `multiple per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`many convulsions in past month`
- Benchmark caveat flags: `vague_count`
- Exact selected fact evidence: `Over the last four weeks he has experienced many convulsions in past month, described as sudden loss of awareness followed by generalised tonic–clonic activity lasting 1–2 minutes with tongue‑bite on one occasion and post‑ictal confusion for up to an hour.`
- Raw answer selected evidence: `Over the last four weeks he has experienced many convulsions in past month, described as sudden loss of awareness followed by generalised tonic–clonic activity lasting 1–2 minutes with tongue‑bite on one occasion and post‑ictal confusion for up to an hour.`
- Raw parser: `multiple per month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `multiple per month` (P=yes, Pr=yes)
- Format-only repair: `multiple per month` (P=yes, Pr=yes)
- Mechanical adapter: `multiple per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `multiple per month` (P=yes, Pr=yes)
- Candidate post-processing: `multiple per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 18, Source 409

- Gold: `1 per month`; gold normalized: `1 per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`6#8804; once per month`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Over the past five months on the present regimen, events have reduced to ≤ once per month, typically brief focal impaired awareness episodes without generalisation, with faster post-ictal recovery and minimal injury risk.`
- Raw answer selected evidence: `Over the past five months on the present regimen, events have reduced to ≤ once per month, typically brief focal impaired awareness episodes without generalisation, with faster post-ictal recovery and minimal injury risk.`
- Raw parser: `1 per 1 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 1 month` (P=yes, Pr=yes)
- Format-only repair: `1 per month` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per month` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 19, Source 419

- Gold: `2 per year`; gold normalized: `2 per year`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`approximately twice per year`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `She attended alone and reported that her current pattern of seizures is stable at approximately twice per year.`
- Raw answer selected evidence: `She attended alone and reported that her current pattern of seizures is stable at approximately twice per year.`
- Raw parser: `2 per 1 year` (P=yes, Pr=yes)
- Raw clinical-selection repair: `2 per 1 year` (P=yes, Pr=yes)
- Format-only repair: `2 per year` (P=yes, Pr=yes)
- Mechanical adapter: `2 per 1 year` (P=yes, Pr=yes)
- Benchmark convention adapter: `2 per year` (P=yes, Pr=yes)
- Candidate post-processing: `2 per 1 year` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 20, Source 446

- Gold: `2 per week`; gold normalized: `2 per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`64 twice per week`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Over the past month, the overall frequency has been ≤ twice per week, occurring both nocturnally and during wakefulness, with variable clustering.`
- Raw answer selected evidence: `Over the past month, the overall frequency has been ≤ twice per week, occurring both nocturnally and during wakefulness, with variable clustering.`
- Raw parser: `2 per 1 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `2 per 1 week` (P=yes, Pr=yes)
- Format-only repair: `2 per week` (P=yes, Pr=yes)
- Mechanical adapter: `2 per 1 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `2 per week` (P=yes, Pr=yes)
- Candidate post-processing: `2 per 1 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 21, Source 466

- Gold: `21 to 28 per month`; gold normalized: `21 to 28 per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`21 to 28 per month`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `The patient reports an ongoing pattern of 21 to 28 seizures per month, predominantly brief focal impaired awareness events lasting 30–90 seconds with post-ictal fatigue.`
- Raw answer selected evidence: `The patient reports an ongoing pattern of 21 to 28 seizures per month, predominantly brief focal impaired awareness events lasting 30–90 seconds with post-ictal fatigue.`
- Raw parser: `21 to 28 per 1 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `21 to 28 per 1 month` (P=yes, Pr=yes)
- Format-only repair: `21 to 28 per month` (P=yes, Pr=yes)
- Mechanical adapter: `21 to 28 per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `21 to 28 per month` (P=yes, Pr=yes)
- Candidate post-processing: `21 to 28 per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 22, Source 467

- Gold: `9 per month`; gold normalized: `9 per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`9 per month`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Current average frequency is 9 per month, which the patient tracks on a phone diary.`
- Raw answer selected evidence: `Current average frequency is 9 per month, which the patient tracks on a phone diary.`
- Raw parser: `9 per month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `9 per month` (P=yes, Pr=yes)
- Format-only repair: `9 per month` (P=yes, Pr=yes)
- Mechanical adapter: `9 per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `9 per month` (P=yes, Pr=yes)
- Candidate post-processing: `9 per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 23, Source 531

- Gold: `12 to 30 per 3 month`; gold normalized: `12 to 30 per 3 month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`12 to 30 per quarter`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Current estimated seizure frequency is 12 to 30 per quarter, with clusters typically following nights of interrupted rest.`
- Raw answer selected evidence: `Current estimated seizure frequency is 12 to 30 per quarter, with clusters typically following nights of interrupted rest.`
- Raw parser: `12 to 30 per 3 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `12 to 30 per 3 month` (P=yes, Pr=yes)
- Format-only repair: `12 to 30 per 3 month` (P=yes, Pr=yes)
- Mechanical adapter: `12 to 30 per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `12 to 30 per month` (P=yes, Pr=yes)
- Candidate post-processing: `12 to 30 per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 24, Source 598

- Gold: `1 per 8 month`; gold normalized: `1 per 8 month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`1 per 8 months`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `patient has self-reported seizure frequency averaging 1 per eight months`
- Raw answer selected evidence: `patient has self-reported seizure frequency averaging 1 per eight months`
- Raw parser: `1 per 8 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 8 month` (P=yes, Pr=yes)
- Format-only repair: `1 per 8 month` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 8 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 8 month` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 8 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 25, Source 659

- Gold: `2 per 4 day`; gold normalized: `2 per 4 day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`2 per 4 days`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `She reports that the frequency is consistent at seizures twice every 4 days, with clustering around nights following particularly fragmented sleep.`
- Raw answer selected evidence: `She reports that the frequency is consistent at seizures twice every 4 days, with clustering around nights following particularly fragmented sleep.`
- Raw parser: `2 per 4 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `2 per 4 day` (P=yes, Pr=yes)
- Format-only repair: `2 per 4 day` (P=yes, Pr=yes)
- Mechanical adapter: `2 per 4 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `2 per 4 day` (P=yes, Pr=yes)
- Candidate post-processing: `2 per 4 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 26, Source 665

- Gold: `2 per 2 week`; gold normalized: `2 per 2 week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`2 per 2 weeks`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `The app logs indicate a regular pattern of seizures twice every two weeks, typically clustering on days following consecutive late shifts.`
- Raw answer selected evidence: `The app logs indicate a regular pattern of seizures twice every two weeks, typically clustering on days following consecutive late shifts.`
- Raw parser: `2 per 2 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `2 per 2 week` (P=yes, Pr=yes)
- Format-only repair: `2 per 2 week` (P=yes, Pr=yes)
- Mechanical adapter: `2 per 2 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `2 per 2 week` (P=yes, Pr=yes)
- Candidate post-processing: `2 per 2 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 27, Source 678

- Gold: `2 per 4 month`; gold normalized: `2 per 4 month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`2 per 4 months`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `at present he is experiencing seizures twice every 4 months`
- Raw answer selected evidence: `at present he is experiencing seizures twice every 4 months`
- Raw parser: `2 per 4 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `2 per 4 month` (P=yes, Pr=yes)
- Format-only repair: `2 per 4 month` (P=yes, Pr=yes)
- Mechanical adapter: `2 per 4 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `2 per 4 month` (P=yes, Pr=yes)
- Candidate post-processing: `2 per 4 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 28, Source 694

- Gold: `1 per week`; gold normalized: `1 per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`once a week`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `On current therapy she reports seizures once a week.`
- Raw answer selected evidence: `On current therapy she reports seizures once a week.`
- Raw parser: `1 per week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per week` (P=yes, Pr=yes)
- Format-only repair: `1 per week` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 1 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per week` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 1 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 29, Source 704

- Gold: `2 per month`; gold normalized: `2 per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`2 per month`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Frequency is now reported as twice a month, often clustering around the late luteal phase.`
- Raw answer selected evidence: `Frequency is now reported as twice a month, often clustering around the late luteal phase.`
- Raw parser: `2 per 1 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `2 per 1 month` (P=yes, Pr=yes)
- Format-only repair: `2 per month` (P=yes, Pr=yes)
- Mechanical adapter: `2 per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `2 per month` (P=yes, Pr=yes)
- Candidate post-processing: `2 per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 30, Source 725

- Gold: `1 per day`; gold normalized: `1 per day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per day`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `He reports events occur daily, most commonly during the late dinner rush between 19:00 and 21:00, particularly on days after poor sleep.`
- Raw answer selected evidence: `He reports events occur daily, most commonly during the late dinner rush between 19:00 and 21:00, particularly on days after poor sleep.`
- Raw parser: `1 per 1 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 1 day` (P=yes, Pr=yes)
- Format-only repair: `1 per day` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 1 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per day` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 1 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 31, Source 731

- Gold: `1 per day`; gold normalized: `1 per day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`daily`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `brief episodes occur daily, typically between 06:00–08:00, characterised by a sudden behavioural pause with unresponsiveness lasting 20–40 seconds`
- Raw answer selected evidence: `brief episodes occur daily, typically between 06:00–08:00, characterised by a sudden behavioural pause with unresponsiveness lasting 20–40 seconds`
- Raw parser: `1 per 1 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 1 day` (P=yes, Pr=yes)
- Format-only repair: `1 per day` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 1 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per day` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 1 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 32, Source 743

- Gold: `multiple per week`; gold normalized: `multiple per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`most shifts`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Daniel Harris reports that these episodes crop up most shifts, especially during the busiest part of service, and his manager has had to reassign him from open flame stations as a precaution.`
- Raw answer selected evidence: `Daniel Harris reports that these episodes crop up most shifts, especially during the busiest part of service, and his manager has had to reassign him from open flame stations as a precaution.`
- Raw parser: `multiple per shift` (P=yes, Pr=yes)
- Raw clinical-selection repair: `multiple per shift` (P=yes, Pr=yes)
- Format-only repair: `multiple per shift` (P=yes, Pr=yes)
- Mechanical adapter: `None` (P=n/a, Pr=n/a, unscorable, err=missing_final_label)
- Benchmark convention adapter: `None` (P=n/a, Pr=n/a, unscorable, err=missing_final_label)
- Candidate post-processing: `multiple per shift` (raw-preserving adapter fallback when mechanical operands are incomplete but raw parser label is scorable); projected Purist=yes, Pragmatic=yes
- Component issues: `mechanical_adapter_rendering=fail, selected_operand_completeness=fail`

### Pos 33, Source 744

- Gold: `multiple per week`; gold normalized: `multiple per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`most weekdays for brief absences, 1 generalised tonic–clonic seizure in 8 weeks`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Over the past two months she reports brief absences occurring on most weekdays, often clustering around late afternoon when she is more tired. There has been one generalised tonic–clonic seizure in the last eight weeks, witnessed at home.`
- Raw answer selected evidence: `Over the past two months she reports brief absences occurring on most weekdays, often clustering around late afternoon when she is more tired. There has been one generalised tonic–clonic seizure in the last eight weeks, witnessed at home.`
- Raw parser: `3 to 5 per 7 day` (P=no, Pr=no)
- Raw clinical-selection repair: `3 to 5 per 7 day` (P=no, Pr=no)
- Format-only repair: `3 to 5 per 7 day` (P=no, Pr=no)
- Mechanical adapter: `3 to 5 per 7 day` (P=no, Pr=no)
- Benchmark convention adapter: `3 to 5 per 7 day` (P=no, Pr=no)
- Candidate post-processing: `multiple per week` (benchmark vague-weekday convention: most weekdays -> multiple per week rather than numeric weekday count); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 34, Source 763

- Gold: `1 per week`; gold normalized: `1 per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`weekly`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `ongoing events occurring roughly weekly, with brief warning symptoms of unease and difficulty focusing, followed by a lapse in awareness noted by colleagues at work and by his partner at home. The occupational health summaries corroborate a weekly frequency over the past three months, documenting short episodes leading to temporary removal from safety-critical tasks.`
- Raw answer selected evidence: `ongoing events occurring roughly weekly, with brief warning symptoms of unease and difficulty focusing, followed by a lapse in awareness noted by colleagues at work and by his partner at home. The occupational health summaries corroborate a weekly frequency over the past three months, documenting short episodes leading to temporary removal from safety-critical tasks.`
- Raw parser: `1 per 1 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 1 week` (P=yes, Pr=yes)
- Format-only repair: `1 per week` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 1 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per week` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 1 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `evidence_exactness=fail`

### Pos 35, Source 790

- Gold: `1 per 7 to 10 day`; gold normalized: `1 per 7 to 10 day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per 7 to 10 days`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Since then, his events have continued at a fairly regular cadence, occurring roughly once every seven to ten days.`
- Raw answer selected evidence: `Since then, his events have continued at a fairly regular cadence, occurring roughly once every seven to ten days.`
- Raw parser: `1 per 7 to 10 day` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 7 to 10 day` (P=yes, Pr=yes)
- Format-only repair: `1 per 7 to 10 day` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 7 to 10 day` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 7 to 10 day` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 7 to 10 day` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 36, Source 816

- Gold: `1 per month`; gold normalized: `1 per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`4 per year`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Currently reporting monthly seizures, typically brief focal-onset episodes with rapid recovery as described by the family. Since commencing ketogenic diet therapy, the family notes a marked reduction in seizure frequency with only four brief seizures recorded in 2017 so far.`
- Raw answer selected evidence: `Currently reporting monthly seizures, typically brief focal-onset episodes with rapid recovery as described by the family. Since commencing ketogenic diet therapy, the family notes a marked reduction in seizure frequency with only four brief seizures recorded in 2017 so far.`
- Raw parser: `4 per 1 year` (P=no, Pr=yes)
- Raw clinical-selection repair: `4 per 1 year` (P=no, Pr=yes)
- Format-only repair: `4 per year` (P=no, Pr=yes)
- Mechanical adapter: `4 per 1 year` (P=no, Pr=yes)
- Benchmark convention adapter: `4 per year` (P=no, Pr=yes)
- Candidate post-processing: `1 per month` (current-state precedence inside selected evidence: currently reporting monthly seizures beats historical/year-to-date count); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 37, Source 849

- Gold: `1 per year`; gold normalized: `1 per year`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per year`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `she states that she can go many months without an event, describing her pattern as “yearly seizures,” with some years having one event and others none.`
- Raw answer selected evidence: `she states that she can go many months without an event, describing her pattern as “yearly seizures,” with some years having one event and others none.`
- Raw parser: `1 per year` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per year` (P=yes, Pr=yes)
- Format-only repair: `1 per year` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 1 year` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per year` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 1 year` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 38, Source 854

- Gold: `1 per year`; gold normalized: `1 per year`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`roughly yearly`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `she describes her seizures as occurring roughly yearly, with the last episode in late January this year after several consecutive nights of poor sleep due to a child’s illness.`
- Raw answer selected evidence: `she describes her seizures as occurring roughly yearly, with the last episode in late January this year after several consecutive nights of poor sleep due to a child’s illness.`
- Raw parser: `1 per year` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per year` (P=yes, Pr=yes)
- Format-only repair: `1 per year` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 1 year` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per year` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 1 year` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 39, Source 869

- Gold: `multiple per month`; gold normalized: `multiple per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`several events spread across most months`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Diary review suggests several events spread across most months, typically brief, with occasional back-to-back occurrences on successive days.`
- Raw answer selected evidence: `Diary review suggests several events spread across most months, typically brief, with occasional back-to-back occurrences on successive days.`
- Raw parser: `multiple per month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `multiple per month` (P=yes, Pr=yes)
- Format-only repair: `multiple per month` (P=yes, Pr=yes)
- Mechanical adapter: `multiple per month` (P=yes, Pr=yes)
- Benchmark convention adapter: `multiple per month` (P=yes, Pr=yes)
- Candidate post-processing: `multiple per month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 40, Source 891

- Gold: `1 per 2 day`; gold normalized: `1 per 2 day`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per 2 days`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `She experiences brief right temporal tingling and rising epigastric discomfort, followed by staring and speech arrest lasting 1–2 minutes. These have become frequent, with seizures every other day.`
- Raw answer selected evidence: `She experiences brief right temporal tingling and rising epigastric discomfort, followed by staring and speech arrest lasting 1–2 minutes. These have become frequent, with seizures every other day.`
- Raw parser: `3 to 4 per 6 week` (P=no, Pr=yes)
- Raw clinical-selection repair: `3 to 4 per 6 week` (P=no, Pr=yes)
- Format-only repair: `3 to 4 per 6 week` (P=no, Pr=yes)
- Mechanical adapter: `3 to 4 per 6 week` (P=no, Pr=yes)
- Benchmark convention adapter: `3 to 4 per 6 week` (P=no, Pr=yes)
- Candidate post-processing: `1 per 2 day` (selected-evidence phrase repair: every other day -> 1 per 2 day); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 41, Source 899

- Gold: `1 per 2 week`; gold normalized: `1 per 2 week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`1 per 2 week`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `On direct questioning, the current pattern is seizures every other week, typically overnight, with post-ictal tiredness the following morning.

The patient keeps a diary corroborating a roughly fortnightly pattern.`
- Raw answer selected evidence: `On direct questioning, the current pattern is seizures every other week, typically overnight, with post-ictal tiredness the following morning.

The patient keeps a diary corroborating a roughly fortnightly pattern.`
- Raw parser: `1 per 2 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 2 week` (P=yes, Pr=yes)
- Format-only repair: `1 per 2 week` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 2 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 2 week` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 2 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 42, Source 959

- Gold: `1 per 2 month`; gold normalized: `1 per 2 month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`bimonthly on average`
- Benchmark caveat flags: `bimonthly`
- Exact selected fact evidence: `She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession.`
- Raw answer selected evidence: `She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession.`
- Raw parser: `2 per 1 to 2 month` (P=no, Pr=no)
- Raw clinical-selection repair: `2 per 1 to 2 month` (P=no, Pr=no)
- Format-only repair: `2 per 1 to 2 month` (P=no, Pr=no)
- Mechanical adapter: `2 per 1 to 2 month` (P=no, Pr=no)
- Benchmark convention adapter: `2 per 1 to 2 month` (P=no, Pr=no)
- Candidate post-processing: `1 per 2 month` (Gan-specific selected-evidence repair: bimonthly -> 1 per 2 month); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 43, Source 960

- Gold: `1 per 2 month`; gold normalized: `1 per 2 month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`bimonthly seizures`
- Benchmark caveat flags: `bimonthly`
- Exact selected fact evidence: `He remains on long-term antiepileptic therapy and reports ongoing events occurring with bimonthly seizures.`
- Raw answer selected evidence: `He remains on long-term antiepileptic therapy and reports ongoing events occurring with bimonthly seizures.`
- Raw parser: `1 per 2 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 2 month` (P=yes, Pr=yes)
- Format-only repair: `1 per 2 month` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 2 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 2 month` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 2 month` (Gan-specific selected-evidence repair: bimonthly -> 1 per 2 month); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 44, Source 978

- Gold: `1 per 2 month`; gold normalized: `1 per 2 month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`~1 per 2 months`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `Over recent months, he describes a steadying of this pattern, with focal impaired-awareness events now occurring only every other month or so, and importantly without clustering.`
- Raw answer selected evidence: `Over recent months, he describes a steadying of this pattern, with focal impaired-awareness events now occurring only every other month or so, and importantly without clustering.`
- Raw parser: `1 per 2 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 per 2 month` (P=yes, Pr=yes)
- Format-only repair: `1 per 2 month` (P=yes, Pr=yes)
- Mechanical adapter: `1 per 2 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 per 2 month` (P=yes, Pr=yes)
- Candidate post-processing: `1 per 2 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 45, Source 987

- Gold: `1 per 2 month`; gold normalized: `1 per 2 month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`bimonthly seizures`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `This patient reports bimonthly seizures, generally occurring after sequences of night shifts and rapid rota changes.`
- Raw answer selected evidence: `This patient reports bimonthly seizures, generally occurring after sequences of night shifts and rapid rota changes.`
- Raw parser: `2 per 1 month` (P=no, Pr=no)
- Raw clinical-selection repair: `2 per 1 month` (P=no, Pr=no)
- Format-only repair: `2 per month` (P=no, Pr=no)
- Mechanical adapter: `2 per 1 month` (P=no, Pr=no)
- Benchmark convention adapter: `2 per month` (P=no, Pr=no)
- Candidate post-processing: `1 per 2 month` (Gan-specific selected-evidence repair: bimonthly -> 1 per 2 month); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 46, Source 1030

- Gold: `1 to 3 per month`; gold normalized: `1 to 3 per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`1 to 3 per month`
- Benchmark caveat flags: `vague_count`
- Exact selected fact evidence: `one or three seizures last month`
- Raw answer selected evidence: `one or three seizures last month`
- Raw parser: `1 to 3 per 1 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `1 to 3 per 1 month` (P=yes, Pr=yes)
- Format-only repair: `1 to 3 per month` (P=yes, Pr=yes)
- Mechanical adapter: `1 to 3 per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `1 to 3 per month` (P=yes, Pr=yes)
- Candidate post-processing: `1 to 3 per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 47, Source 1046

- Gold: `3 to 5 per month`; gold normalized: `3 to 5 per month`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`3 to 5 per month`
- Benchmark caveat flags: `vague_count`
- Exact selected fact evidence: `The patient reports uncertainty when recalling counts due to clustering; they believe there were 3 or 5 seizures last month.`
- Raw answer selected evidence: `The patient reports uncertainty when recalling counts due to clustering; they believe there were 3 or 5 seizures last month.`
- Raw parser: `3 to 5 per 1 month` (P=yes, Pr=yes)
- Raw clinical-selection repair: `3 to 5 per 1 month` (P=yes, Pr=yes)
- Format-only repair: `3 to 5 per month` (P=yes, Pr=yes)
- Mechanical adapter: `3 to 5 per 1 month` (P=yes, Pr=yes)
- Benchmark convention adapter: `3 to 5 per month` (P=yes, Pr=yes)
- Candidate post-processing: `3 to 5 per 1 month` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 48, Source 1070

- Gold: `3 to 4 per week`; gold normalized: `3 to 4 per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`3 to 4 per week`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `He describes three or four seizures last week, all occurring in the evenings.`
- Raw answer selected evidence: `He describes three or four seizures last week, all occurring in the evenings.`
- Raw parser: `3 to 4 per 1 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `3 to 4 per 1 week` (P=yes, Pr=yes)
- Format-only repair: `3 to 4 per week` (P=yes, Pr=yes)
- Mechanical adapter: `3 to 4 per 1 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `3 to 4 per week` (P=yes, Pr=yes)
- Candidate post-processing: `3 to 4 per 1 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 49, Source 1094

- Gold: `3 to 5 per week`; gold normalized: `3 to 5 per week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`current`, assertion=`asserted`, raw_value=`3 to 5 seizures last week`
- Benchmark caveat flags: `none`
- Exact selected fact evidence: `she describes 3 to 5 seizures last week, predominantly occurring in the early hours of the morning after delayed bedtimes.`
- Raw answer selected evidence: `she describes 3 to 5 seizures last week, predominantly occurring in the early hours of the morning after delayed bedtimes.`
- Raw parser: `3 to 5 per 1 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `3 to 5 per 1 week` (P=yes, Pr=yes)
- Format-only repair: `3 to 5 per week` (P=yes, Pr=yes)
- Mechanical adapter: `3 to 5 per 1 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `3 to 5 per week` (P=yes, Pr=yes)
- Candidate post-processing: `3 to 5 per 1 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

### Pos 50, Source 1165

- Gold: `5 to 7 per 3 week`; gold normalized: `5 to 7 per 3 week`; row_ok=True
- Selected fact: kind=`frequency`, temporality=`recent`, assertion=`asserted`, raw_value=`5 to 7 per 3 week`
- Benchmark caveat flags: `vague_count`
- Exact selected fact evidence: `he and staff document 5 or 7 focal onset seizures in three weeks during a recent period that included an episode while travelling by air`
- Raw answer selected evidence: `he and staff document 5 or 7 focal onset seizures in three weeks during a recent period that included an episode while travelling by air`
- Raw parser: `5 to 7 per 3 week` (P=yes, Pr=yes)
- Raw clinical-selection repair: `5 to 7 per 3 week` (P=yes, Pr=yes)
- Format-only repair: `5 to 7 per 3 week` (P=yes, Pr=yes)
- Mechanical adapter: `5 to 7 per 3 week` (P=yes, Pr=yes)
- Benchmark convention adapter: `5 to 7 per 3 week` (P=yes, Pr=yes)
- Candidate post-processing: `5 to 7 per 3 week` (no additional post-processing proposed); projected Purist=yes, Pragmatic=yes
- Component issues: `none`

## Recommendation

Promote Decision 0007 as the primary LLM-heavy lane, with a new explicit post-processing layer that is ablated separately from raw parser labels and mechanical adapters. The first implementation should be test-first and narrow: preserve scorable raw labels when adapter operands are incomplete; repair bimonthly and every-other-day from exact selected evidence; add current-state precedence for evidence containing monthly-current plus lower historical count; and decide whether `most weekdays` should be a Gan benchmark-convention repair to vague `multiple per week` or left as a clinically numeric label.
