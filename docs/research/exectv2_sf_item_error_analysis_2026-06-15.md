# ExECTv2 SeizureFrequency Item-Level Error Analysis

Date: 2026-06-15
Scope: dev split only. The local LLM artifacts are pilot slices, not full-dev evidence.

## Artifacts

- Item JSONL: `experiments\exectv2_sf_item_error_analysis_20260615.jsonl`
- Item CSV: `experiments\exectv2_sf_item_error_analysis_20260615.csv`

## Score Matrix

| System | Scope | Config | Per-item P/R/F1 | TP/FP/FN | Per-letter F1 |
| --- | --- | --- | --- | --- | ---: |
| `deterministic_dev140` | dev140 | `phrase_only` | 0.665/0.561/0.609 | 105/53/82 | 0.811 |
| `deterministic_dev140` | dev140 | `sf_semantic` | 0.519/0.439/0.475 | 82/76/105 | 0.716 |
| `deterministic_dev140` | dev140 | `sf_benchmark` | 0.519/0.439/0.475 | 82/76/105 | 0.716 |
| `deterministic_dev140_current` | dev140 | `phrase_only` | 0.714/0.802/0.756 | 150/60/37 | 0.942 |
| `deterministic_dev140_current` | dev140 | `sf_semantic` | 0.667/0.749/0.705 | 140/70/47 | 0.925 |
| `deterministic_dev140_current` | dev140 | `sf_benchmark` | 0.667/0.749/0.705 | 140/70/47 | 0.925 |
| `deterministic_dev25` | dev25_matched_to_llm | `phrase_only` | 0.794/0.871/0.831 | 27/7/4 | 0.966 |
| `deterministic_dev25` | dev25_matched_to_llm | `sf_semantic` | 0.618/0.677/0.646 | 21/13/10 | 0.929 |
| `deterministic_dev25` | dev25_matched_to_llm | `sf_benchmark` | 0.618/0.677/0.646 | 21/13/10 | 0.929 |
| `local_llm_only_qwen36_35b_dev25` | dev25 | `phrase_only` | 0.552/0.516/0.533 | 16/13/15 | 0.774 |
| `local_llm_only_qwen36_35b_dev25` | dev25 | `sf_semantic` | 0.103/0.097/0.100 | 3/26/28 | 0.273 |
| `local_llm_only_qwen36_35b_dev25` | dev25 | `sf_benchmark` | 0.000/0.000/0.000 | 0/29/31 | 0.000 |
| `local_hybrid_qwen36_35b_dev5` | dev5 | `phrase_only` | 0.429/0.545/0.480 | 6/8/5 | 0.750 |
| `local_hybrid_qwen36_35b_dev5` | dev5 | `sf_semantic` | 0.429/0.545/0.480 | 6/8/5 | 0.750 |
| `local_hybrid_qwen36_35b_dev5` | dev5 | `sf_benchmark` | 0.429/0.545/0.480 | 6/8/5 | 0.750 |

## Failure Category Counts (sf_benchmark)

### deterministic_dev140_current
- Outcomes: TP=140, FP=70, FN=47
- Residual FN families from item inspection: zero/control/date-since statements,
  remaining projection-specific phrase truncations, rate/period attributes, and
  dated count/PIT statements. The tail is smaller but still dominated by exact
  ExECTv2 projection conventions rather than CUI assignment.
- The active deterministic strict item-level goal is met:
  `sf_benchmark` per-item F1=0.705 and phrase-only F1=0.756.
- The latest deterministic additions that crossed the threshold were structured
  same-sentence statements, dated/rate composition templates, typo-tolerant
  month/date handling scoped to SF statements, seizure-free C129 projection
  handling, and explicit post-extraction precision filters for generic
  `seizures`/`seizure-free` artifacts.

### deterministic_dev140
- Outcomes: TP=82, FP=76, FN=105
- missing_anchor_or_text: 129
- mixed_attribute_mismatch: 24
- missing_attributes: 12
- extra_attributes: 12
- attribute_value_mismatch: 4

### deterministic_dev25
- Outcomes: TP=21, FP=13, FN=10
- missing_anchor_or_text: 10
- missing_attributes: 4
- extra_attributes: 4
- mixed_attribute_mismatch: 3
- attribute_value_mismatch: 2

### local_llm_only_qwen36_35b_dev25
- Outcomes: TP=0, FP=29, FN=31
- missing_anchor_or_text: 24
- mixed_attribute_mismatch: 21
- cui_missing_or_wrong: 7
- missing_attributes: 4
- extra_attributes: 4

### local_hybrid_qwen36_35b_dev5
- Outcomes: TP=6, FP=8, FN=5
- missing_anchor_or_text: 13

## Directional Error Anatomy (sf_benchmark)

### Deterministic dev140

- FNs: 105 total. Category split: `missing_anchor_or_text` 80,
  `mixed_attribute_mismatch` 11, `missing_attributes` 7, `extra_attributes` 5,
  `attribute_value_mismatch` 2.
- Top FN phrases: `seizures` 23, `seizure` 19,
  `generalised tonic clonic seizures` 7,
  `focal to bilateral convulsive seizure` 6,
  `generalised tonic clonic seizure` 4, `absences` 4, `generalised` 4.
- FN attribute pressure: `NumberOfSeizures` 70, `TimePeriod` 47,
  `NumberOfTimePeriods` 46, `TimeSince_or_TimeOfEvent` 41,
  `FrequencyChange` 23, `PointInTime` 20, `MonthDate` 16.
- FPs: 76 total. Category split: `missing_anchor_or_text` 49,
  `mixed_attribute_mismatch` 13, `extra_attributes` 7, `missing_attributes` 5,
  `attribute_value_mismatch` 2.
- Top FP phrases: `seizures` 28, `seizure free` 12, `seizure` 11,
  `focal seizures` 3, `absences` 3.

Reading: deterministic recall is hurt by both missed anchors and missed
multi-attribute statements, but precision is hurt by the same generic surfaces
(`seizures`, `seizure`, `seizure free`) being over-attached to weak or wrong
frequency evidence.

### Local LLM-only Qwen dev25

- FNs: 31 total. Category split: `mixed_attribute_mismatch` 12,
  `missing_anchor_or_text` 11, `cui_missing_or_wrong` 4,
  `missing_attributes` 4.
- FPs: 29 total. Category split: `missing_anchor_or_text` 13,
  `mixed_attribute_mismatch` 9, `extra_attributes` 4,
  `cui_missing_or_wrong` 3.
- Top FP phrases include non-gold anchor rewrites such as
  `single focal seizure`, `minor seizures`, and other plausible-but-not-gold
  surfaces.

Reading: the local LLM has acceptable transport health, but it is not learning
the ExECTv2 projection. It rewrites anchors, invents or drops attributes, and
does not emit CUI. Its best role is therefore not final attribute formatting.

### Local hybrid Qwen dev5

- FNs: 5 total, all `missing_anchor_or_text`.
- FPs: 8 total, all `missing_anchor_or_text`.
- The most revealing FP surfaces are `seizure taking frequency`,
  `seizures per year`, and `seizures every 3 to 4 weeks`: these are evidence
  fragments or rate phrases, not gold anchor phrases.

Reading: candidate adjudication needs a hard deterministic anchor contract. The
small renderer change that forces candidate anchor text is directionally right,
but the local model still over-keeps weak/noisy candidates.

## Main Failure Modes

1. **Deterministic extraction is no longer CUI-limited for SF.** `sf_semantic` and `sf_benchmark` are equal for deterministic outputs; remaining strict misses are phrase/attribute extraction errors.
2. **The deterministic full-dev gap was attribute-heavy, and the current patch closes enough of it to pass dev140 strict `>0.7`.** Remaining errors are still mostly exact temporal/rate/change projection issues rather than CUI gaps.
3. **Header/list and statement templates remain the main residual risk.** Multi-line `Seizure type and frequency` sections and narrative statements contain continuation-line rates, repeated seizure types, date lists, and projection-specific phrase truncations that still need robustness work before any held-out claim.
4. **The local LLM is not a reliable replacement.** On dev25 it has no call or parse failures and good evidence validity, but phrase-only item F1 is below deterministic, semantic attributes are poor, and benchmark F1 is zero because no CUI is emitted.
5. **Local hybrid candidate adjudication over-keeps and rewrites clinical facts.** The dev5 hybrid pilot keeps noisy candidates and, before deterministic anchor rendering, rewrites anchors into non-gold phrases. Even after re-rendering, it does not beat deterministic on the comparable slice.

## Gold / Projection Peculiarities

- Exact duplicate gold SF items beyond the first copy on dev140: 5. These make one-anchor/one-output architectures under-recall even when they capture the clinical fact once.
- Letter+phrase pairs with multiple different gold attribute sets: 17. These require multiple mentions for the same anchor phrase, not just merged attributes.
- Phrase->CUI collisions in gold/projection inventory: `{"focal": {"C0016399": 1, "C0877017": 1}, "seizure": {"C0036572": 25, "C1299590": 4}}`. The existing SF lexicon resolves the important bare-token collisions (`seizure`, `focal`) by dominance, but these are annotation/projection quirks, not clinical synonymy.
- Gold text is canonicalized from `CUIPhrase`/markup rather than raw offset spans; hyphenated gold phrases normalize to spaces for scoring.
- Some gold labels encode conventions that are not obvious from surface text: `last event <date>` means `NumberOfSeizures=0` with `Since`; `Christmas` is treated as December; bare plural seizure phrases may imply count 2, while some header shorthand implies count 1.
- Historical facts are intentionally annotated as SeizureFrequency in many letters, including diagnosis-section/header statements and repeated narrative restatements.
- Typos and spelling variants are present in notes (`Novemebr`, `seizrue`, generalized/generalised), so robust month/seizure-free normalization needs explicit handling if those become targetable failure slices.

## What We Need To Build To Close The Gap

1. **Harden the statement model against held-out variation.** The current deterministic association plus statement parser can now emit multiple mentions for the same phrase and crosses the dev target, but several rules are intentionally narrow and should be stress-tested before broad claims.
2. **A frequency-section parser.** Treat `Seizure type and frequency` blocks as structured mini-tables: anchor lines, continuation rate lines, comma-separated `last event` fields, and date lists. This should be a clinical-epilepsy/seizure-frequency rule family with its own ablation, not a global newline relaxation.
3. **Temporal/date normalization upgrades.** Add typo-tolerant month handling only where tied to a seizure-frequency statement; add explicit support for age windows, `teenage years`, `since reaching/current dose`, and `last event/last one` variants. Keep these separate from benchmark-format CUI logic.
4. **Continue precision gates for zero/control statements.** Several remaining deterministic FPs are over-broad seizure-free/control statements, especially driving/status/history contexts. The new filters help, but this remains the core precision risk.
5. **LLM role redesign: evidence/statement selector, not attribute formatter.** Local Qwen is weak at exact ExECTv2 attributes and CUI. If used, it should select candidate statements/evidence; deterministic code should render attributes/CUI. The current pilot shows this is not yet better than deterministic, so the next LLM experiment should be a purpose-built selector prompt with deterministic candidate IDs and no free-form attributes.
6. **Gold-aware but non-cheating diagnostics.** Keep dev-only item tables, hard slices, and rule ablations. Do not optimize against locked/full holdout row failures; document each deterministic rule as `clinical_epilepsy`, `seizure_frequency`, or `benchmark_format` depending on what it actually does.

## Representative Examples

### deterministic_dev140
- `missing_anchor_or_text`
  - FP EA0004 text=`seizures` gold={} pred={"CUI": "C0036572", "NumberOfSeizures": "0"}; excerpt: tic medication: Lamotrigine 125 milligrams twice a day | Seizure taking frequency: Uncertain, several seizures since the last clinic appointment |  | I reviewed this 68-year-old man alone in clinic today. He lives with his son and has no recollection of 
  - FP EA0005 text=`seizures` gold={} pred={"CUI": "C0036572", "NumberOfSeizures": "2", "TimeSince_or_TimeOfEvent": "During", "YearDate": "2010"}; excerpt: Dear Dr, |  | Diagnosis: genetic generalised epilepsy-epilepsy with generalised tonic chronic seizures alone. |  | Current medication: sodium valproate 500 mg twice a day | Carbamazepine 200 mg twice a day |  | Seizure type and frequency: Generalised t
- `mixed_attribute_mismatch`
  - FN EA0008 text=`seizure` gold={"CUI": "C0036572", "FrequencyChange": "Increased"} pred={}; excerpt:  |  | Diagnosis: symptomatic structural focal epilepsy | 	Previous meningioma resection 3rd January 2005 |  | Seizure type and frequency: focal seizures with altered awareness every 3 weeks |  | Current anti-epileptic medication: lamotrigine 75mg bd (to reduce
  - FP EA0008 text=`seizure` gold={} pred={"CUI": "C0036572", "NumberOfSeizures": "0"}; excerpt:  |  | Diagnosis: symptomatic structural focal epilepsy | 	Previous meningioma resection 3rd January 2005 |  | Seizure type and frequency: focal seizures with altered awareness every 3 weeks |  | Current anti-epileptic medication: lamotrigine 75mg bd (to reduce
- `missing_attributes`
  - FN EA0002 text=`focal seizures` gold={"CUI": "C0751495", "LowerNumberOfSeizures": "2", "MonthDate": "3", "TimeSince_or_TimeOfEvent": "During", "UpperNumberOfSeizures": "3"} pred={}; excerpt: led this 42 year old lady together with her husband in clinic today. In March she had 2 to 3 of her focal seizures without change in awareness. Since her last clinic appointment she has had four secondary generalised seizures. During her focal seizures s
  - FN EA0009 text=`cluster of seizures` gold={"CUI": "C3203523", "MonthDate": "8", "NumberOfSeizures": "1", "TimeSince_or_TimeOfEvent": "During", "YearDate": "2017"} pred={}; excerpt: ure frequency does vary.  Currently she get around 2-4 seizures per month.  Although she did have a cluster of seizures in August, 2017 where she had 6-9 seizures every week for 3 weeks.  She was born normally but did have 2 febrile seizures at the age of 2 m
- `extra_attributes`
  - FP EA0002 text=`focal seizures` gold={} pred={"CUI": "C0751495", "LowerNumberOfSeizures": "2", "UpperNumberOfSeizures": "3"}; excerpt: led this 42 year old lady together with her husband in clinic today. In March she had 2 to 3 of her focal seizures without change in awareness. Since her last clinic appointment she has had four secondary generalised seizures. During her focal seizures s
  - FP EA0009 text=`cluster of seizures` gold={} pred={"CUI": "C3203523", "MonthDate": "8", "NumberOfSeizures": "1", "TimeSince_or_TimeOfEvent": "During"}; excerpt: ure frequency does vary.  Currently she get around 2-4 seizures per month.  Although she did have a cluster of seizures in August, 2017 where she had 6-9 seizures every week for 3 weeks.  She was born normally but did have 2 febrile seizures at the age of 2 m

### local_llm_only_qwen36_35b_dev25
- `missing_anchor_or_text`
  - FN EA0005 text=`seizures` gold={"CUI": "C0036572", "NumberOfSeizures": "2", "NumberOfTimePeriods": "1", "TimePeriod": "Year"} pred={}; excerpt: Dear Dr, |  | Diagnosis: genetic generalised epilepsy-epilepsy with generalised tonic chronic seizures alone. |  | Current medication: sodium valproate 500 mg twice a day | Carbamazepine 200 mg twice a day |  | Seizure type and frequency: Generalised to
  - FP EA0006 text=`seizure free` gold={} pred={"NumberOfTimePeriods": "Current", "PointInTime": "LastClinic", "TimePeriod": "Year", "TimeSince_or_TimeOfEvent": "Since"}; excerpt: rmal. |  | I reviewed this 26 year old man alone in clinic today. I was pleased to hear that he remains seizure free and is now driving. As you know he had 2 generalised tonic clonic seizures in 2014 without warning. They may have been preceded by leg jerk
- `mixed_attribute_mismatch`
  - FN EA0002 text=`focal seizures` gold={"CUI": "C0751495", "LowerNumberOfSeizures": "2", "MonthDate": "3", "TimeSince_or_TimeOfEvent": "During", "UpperNumberOfSeizures": "3"} pred={}; excerpt: led this 42 year old lady together with her husband in clinic today. In March she had 2 to 3 of her focal seizures without change in awareness. Since her last clinic appointment she has had four secondary generalised seizures. During her focal seizures s
  - FN EA0002 text=`secondary generalised seizures` gold={"CUI": "C0270838", "NumberOfSeizures": "4", "PointInTime": "LastClinic", "TimeSince_or_TimeOfEvent": "Since"} pred={}; excerpt:  her focal seizures without change in awareness. Since her last clinic appointment she has had four secondary generalised seizures. During her focal seizures she may have a strange taste and an unusual sensation in her tummy. She will have a change in awarenes
- `cui_missing_or_wrong`
  - FN EA0007 text=`seizures` gold={"CUI": "C0036572", "LowerNumberOfTimePeriods": "3", "NumberOfSeizures": "1", "TimePeriod": "Week", "UpperNumberOfTimePeriods": "4"} pred={}; excerpt: includes: Ramipril, lansoprazole, metformin, propranolol, clopidogrel. |  | Seizure type and frequency: seizures every 3 to 4 weeks, possibly focal onset |  | Previous investigations MRI 2011 Normal |  | I reviewed this 37 year old lady together with her husba
  - FN EA0007 text=`seizures` gold={"CUI": "C0036572", "LowerNumberOfTimePeriods": "3", "NumberOfSeizures": "1", "TimePeriod": "Week", "UpperNumberOfTimePeriods": "4"} pred={}; excerpt: includes: Ramipril, lansoprazole, metformin, propranolol, clopidogrel. |  | Seizure type and frequency: seizures every 3 to 4 weeks, possibly focal onset |  | Previous investigations MRI 2011 Normal |  | I reviewed this 37 year old lady together with her husba
- `missing_attributes`
  - FN EA0008 text=`focal seizures with altered awareness` gold={"CUI": "C0270834", "NumberOfSeizures": "1", "NumberOfTimePeriods": "3", "TimePeriod": "Week"} pred={}; excerpt: uctural focal epilepsy | 	Previous meningioma resection 3rd January 2005 |  | Seizure type and frequency: focal seizures with altered awareness every 3 weeks |  | Current anti-epileptic medication: lamotrigine 75mg bd (to reduce and stop as detailed below) | T
  - FN EA0019 text=`generalised tonic clonic seizure` gold={"CUI": "C0494475", "NumberOfSeizures": "1", "PointInTime": "Last_Week", "TimeSince_or_TimeOfEvent": "During"} pred={}; excerpt: ine 300mg bd. |  | Unfortunately he forgot to take his normal dose of carbamazepine last week and had a generalised tonic clonic seizure. He last had a seizure before this around a year ago. |  | I suggest that we don’t make any management changes at present. 

### local_hybrid_qwen36_35b_dev5
- `missing_anchor_or_text`
  - FN EA0004 text=`seizures` gold={"CUI": "C0036572", "NumberOfSeizures": "3", "PointInTime": "LastClinic", "TimeSince_or_TimeOfEvent": "Since"} pred={}; excerpt: tic medication: Lamotrigine 125 milligrams twice a day | Seizure taking frequency: Uncertain, several seizures since the last clinic appointment |  | I reviewed this 68-year-old man alone in clinic today. He lives with his son and has no recollection of his se
  - FN EA0004 text=`seizures` gold={"CUI": "C0036572", "NumberOfSeizures": "2", "NumberOfTimePeriods": "1", "TimePeriod": "Year"} pred={}; excerpt: tic medication: Lamotrigine 125 milligrams twice a day | Seizure taking frequency: Uncertain, several seizures since the last clinic appointment |  | I reviewed this 68-year-old man alone in clinic today. He lives with his son and has no recollection of h
