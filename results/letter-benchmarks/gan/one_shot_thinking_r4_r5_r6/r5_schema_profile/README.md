# R5 dev750 schema-use audit

## Findings and recommended decisions

**All six measurement types have substantial use. This audit does not support
removing any whole measurement type.** It does identify one structurally redundant
field and several candidates for reducing output verbosity or clarifying definitions.
Usage is model behaviour on synthetic letters, not a source-first reference or a
clinical necessity measure. A field can be absent because the source lacks the
information, because the model omitted it, or because the schema discouraged it.

| Component | Observed evidence | Recommendation |
| --- | --- | --- |
| `cluster_pattern.cadence.kind` | 88/88 populated cadence objects say `recurring_rate`; the field location already fixes its type. | Strongest lossless structural simplification: omit this nested discriminator in a new candidate. Retain the outer measurement and quantity discriminators, which select genuinely different structures. |
| Required null fields and `approximate: false` | `condition` is null in 2,091/2,355 findings; `observation_period` is null in 1,383/2,355. Numeric quantities say false for approximation in 1,924/2,079 occurrences. | Consider optional output fields with explicit defaults if the chosen structured-output API supports them. This reduces verbosity, not clinical information. Missing and explicit null must have identical declared semantics before doing this; no savings or accuracy improvement has been measured. |
| Event grouping | 1,279 one-type, 79 explicitly combined and 997 unspecified findings. Both invalid records fail this enum. | Review the definition and spelling guidance; do not remove grouping on low-use grounds. It protects the distinction between a combined count and separately reported event types. |
| Event seizure interpretation | 337 uncertain, 15 explicitly non-seizure and 54 not-specified findings, alongside 1,949 stated-seizure findings. | Retain. These are material distinctions, even if source-first review may revise individual classifications. |
| `temporal_status` | 1,791 current; 324 recent; 232 historical; 6 future; 2 unclear. | Clarify current versus recent with annotation examples. Their overlap is a possible modelling ambiguity, not demonstrated redundancy. Do not merge them based on these counts alone. |
| Unquantified cluster patterns | 130/277 have neither cadence nor size. | Retain cluster meaning. Moving these to generic qualitative wording would remove an explicit cluster category; consider that only as a deliberate redesign, not a lossless deletion. |
| Seizure-free intervals without a time | 237/543 have neither duration nor since. | Retain the event-scoped absence state. A date is not required for a source to state that a seizure type is absent. Review whether the name “interval” adequately covers this use. |
| Observation-period wording | 243/972 populated periods have no start, end or duration. | Retain wording: it is the only structured time content for these periods. Endpoints are sparse but not redundant. |
| `last_seizure` versus seizure-free `since` | Only 6 seizure-free findings have an identical event object and time point in a separate last-seizure finding from the same letter. | Retain both meanings. Matching timestamps do not make “last event at X” and “none since X” interchangeable. This exact-match test is conservative; it does not resolve paraphrased event names. |
| Time-point form and precision | 637 time points; none uses second, minute or hour precision. Day, week, month, year and unspecified all occur. | No observed need for sub-day **date precision** in this run. Keeping these enum options is cheap; removing form/precision would require reconstructing them from wording. Do not confuse date precision with duration units: hourly rates and minute observation windows do occur. |
| Answer evidence and finding evidence | Answer evidence exactly repeats a selected finding's evidence in 525/719 nonempty records (73.0%). | Potential storage deduplication only. Retain independently declared answer evidence in the current comparison; replacing it with links would change the answer-only comparator and fails to cover all records without an additional rule. |
| Finding IDs and answer links | 219/746 letters select multiple findings; 1,098/2,355 findings are selected. | Retain links for attribution. IDs are local to a letter; repeated `f1` values across letters are expected, not duplicate records. |

The sensible next candidate would start with the redundant nested cadence tag and,
if supported, optional null/default serialization. Keep the clinical distinctions
until the source-first annotation can measure whether they are accurate and useful.
No schema changes, new model calls or performance comparisons were made by this audit.

## Population, provenance and checks

- Dataset: synthetic Gan dev750, loader split `validation`; all 750 requested letters,
  including `row_ok=False`. No holdout or real-patient data was loaded.
- Candidate: `one_shot_frequency_v2_measurements_r5`, condition `r5_rich`.
- Runtime: DeepSeek V4.1 Flash (`deepseek-flash`), thinking enabled/low, temperature 0,
  24,000-token limit. Original timeout 300 seconds; 40 separate timeout reruns at
  600 seconds. The mixed view counts each letter once, not both attempts.
- Population used for field statistics: **746 schema-valid letters and 2,355 findings**.
  This includes 706 original responses and 40 rerun responses. There are 719 letters
  with findings and 27 valid empty inventories. Findings per valid letter: mean
  3.16, median 3, range 0–14. One finding per letter would not cover this output.
- Exclusions remain explicit: 2 invalid envelopes and 2 invalid schemas. Both schema
  failures are `event.grouping` enum errors (source rows 6029 and 13122). Envelope
  failures are rows 4624 and 13267. Excluded contents are not repaired or silently
  added to the field statistics. Valid output usage can therefore understate failure-prone fields.
- Scorer: none for this descriptive audit. Schema validity is independent of native
  answer-label validity or Purist/Pragmatic agreement; no benchmark score is inferred.
- Evidence checks: 2,352/2,355 finding quotations are exact source substrings. The
  three exceptions are row 3532/f1 and row 6571/f2 and f3. They remain counted as
  schema-valid output; exact quotation matching is not a correctness review.
- Join checks: unique request IDs and source rows; exactly 750 R5 requests; exactly
  40 originally timed-out R5 replacements; mixed-view bodies equal the corresponding
  original or rerun response. No duplicate findings after removing only finding ID;
  22 findings share evidence with another finding in the same letter, which can be legitimate.
- Source paths and SHA-256 hashes, runtime parameters and excluded-record details
  are in [summary.json](summary.json). Detailed fields are in [attributes.json](attributes.json).
  The authoritative input is saved requests/responses under
  `runs/one_shot_thinking_r4_r5_r6/dev750/`, including `timeout600/`.
- Reproduce from the repository root with
  `.venv/bin/python scripts/benchmarks/profile_r5_measurements.py`.
  [Notebook](profile.ipynb) runs that same code and displays the main results.
  The source-ID-preserving working table remains local under
  `runs/one_shot_thinking_r4_r5_r6/dev750/r5_schema_profile/`.

## Measurement-type counts

Finding shares use 2,355; letter coverage uses 746 schema-valid letters. Letter
counts overlap across measurement types. “Selected” means linked by the model to
its declared answer, not judged correct or necessary by a reviewer.

| Measurement | Findings (% of all) | Letters (% of valid) | Selected (% of type) | Observation period (% of type) | Condition (% of type) |
| --- | --- | --- | --- | --- | --- |
| recurring_rate | 360/2,355 (15.3%) | 246/746 (33.0%) | 224/360 (62.2%) | 107/360 (29.7%) | 28/360 (7.8%) |
| observed_count | 560/2,355 (23.8%) | 288/746 (38.6%) | 408/560 (72.9%) | 507/560 (90.5%) | 42/560 (7.5%) |
| cluster_pattern | 277/2,355 (11.8%) | 260/746 (34.9%) | 116/277 (41.9%) | 78/277 (28.2%) | 72/277 (26.0%) |
| seizure_free_interval | 543/2,355 (23.1%) | 355/746 (47.6%) | 186/543 (34.3%) | 145/543 (26.7%) | 19/543 (3.5%) |
| last_seizure | 88/2,355 (3.7%) | 88/746 (11.8%) | 43/88 (48.9%) | 1/88 (1.1%) | 11/88 (12.5%) |
| qualitative_frequency | 527/2,355 (22.4%) | 340/746 (45.6%) | 121/527 (23.0%) | 134/527 (25.4%) | 92/527 (17.5%) |

## Quantity variants and date attributes

There are 2,190 quantity objects across counts, cluster counts/sizes and durations:
1,832 exact (83.7%), 184 ranges (8.4%), 63 bounds (2.9%) and 111 qualitative (5.1%).
Approximation is true in 155/2,079 numeric quantities (7.5%). These flags and variants
have observed use; replacing them all with a single number would lose information.
Occurrence counts are not finding counts: one finding may contain several quantities.

There are 637 time points: 378 month, 112 day, 110 unspecified, 27 year and 10 week
precision. Observation periods contain 321 starts, 52 ends and 453 durations among
972 populated period objects. The small end-date count does not make start and end
interchangeable. The schema has no dedicated letter-date field, so zero letter-date
attributes is a schema limitation rather than evidence that letters lack dates.

R7-only compound ranges and `observed_cluster_count` cannot be assessed from R5
outputs: R5 cannot emit them. Their absence here is not evidence against those additions.

## Cluster and seizure-free combinations

| Cluster fields | Findings / 277 |
| --- | --- |
| Neither cadence nor size | 130 (46.9%) |
| Cadence and size | 74 (26.7%) |
| Size only | 59 (21.3%) |
| Cadence only | 14 (5.1%) |

| Seizure-free fields | Findings / 543 |
| --- | --- |
| Neither duration nor since | 237 (43.6%) |
| Since only | 158 (29.1%) |
| Duration only | 130 (23.9%) |
| Duration and since | 18 (3.3%) |

## Every attribute: how to read the tables

**Eligible** means its containing object/variant was emitted. **Populated** excludes
explicit nulls; a missing parent does not create null child fields. For example,
`observation_period.end` has denominator 972, not 2,355. Angle-bracket names such as
`count<range>` denote schema variants, not literal JSON keys. Allowed enum values
with zero use are retained. Rows with 0/0 mark variants never emitted, not failed fields.

Numeric summaries describe raw emitted numbers, with no unit normalization. Consult
the adjacent unit distribution before comparing duration numbers. Numeric means across
units are only a mechanical profile, not a meaningful clinical duration. Text rows show
distinct counts and up to three most common exact strings (long previews truncated to
75 characters); the JSON retains the five leading complete values. Distinctness is
case- and punctuation-sensitive. Top strings are illustrative, not source-reviewed labels.

### documents

Answer object fields below use 746 records. Finding-list lengths: mean 3.16, median 3, min 0, max 14; selected-ID-list lengths: mean 1.47, median 1, min 0, max 12. There are 500 singleton selections, 219 multiple selections and 27 empty selections. All selected IDs resolve within their record by schema validation.

| Attribute | Populated / eligible | Null | Values / numeric summary |
| --- | --- | --- | --- |
| `answer` | 746/746 (100.0%) | 0 | Object/union; see child fields |
| `answer.evidence` | 719/746 (96.4%) | 27 | 693 distinct; daily drop attacks: 6; He has daily absences.: 4; having been seizure free for years: 3 |
| `answer.label` | 746/746 (100.0%) | 0 | 291 distinct; unknown: 73; 1 per day: 33; no seizure frequency reference: 27 |

### all_findings

| Attribute | Populated / eligible | Null | Values / numeric summary |
| --- | --- | --- | --- |
| `condition` | 264/2,355 (11.2%) | 2091 | 225 distinct; under stress: 4; around periods of marked sleep deprivation: 3; after nights of curtailed sleep: 3 |
| `event` | 2,355/2,355 (100.0%) | 0 | Object/union; see child fields |
| `event.description` | 2,355/2,355 (100.0%) | 0 | 722 distinct; seizures: 519; events: 117; generalised tonic-clonic seizures: 76 |
| `event.grouping` | 2,355/2,355 (100.0%) | 0 | one_type: 1279; explicit_combined_group: 79; unspecified: 997 |
| `event.seizure_interpretation` | 2,355/2,355 (100.0%) | 0 | stated_seizure: 1949; uncertain_seizure: 337; explicitly_non_seizure: 15; not_specified: 54 |
| `evidence` | 2,355/2,355 (100.0%) | 0 | 2156 distinct; daily drop attacks: 6; focal impaired-awareness seizures with disorientation are reported every fo: 6; drop attacks occurring in batches: 5 |
| `finding_id` | 2,355/2,355 (100.0%) | 0 | 15 distinct; f1: 719; f2: 634; f3: 458 |
| `observation_period` | 972/2,355 (41.3%) | 1383 | Object/union; see child fields |
| `observation_period.duration` | 453/972 (46.6%) | 519 | Object/union; see child fields |
| `observation_period.duration.quantity` | 453/453 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<bound>` | 1/1 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<bound>.approximate` | 1/1 (100.0%) | 0 | False: 1; True: 0 |
| `observation_period.duration.quantity<bound>.kind` | 1/1 (100.0%) | 0 | bound: 1 |
| `observation_period.duration.quantity<bound>.relation` | 1/1 (100.0%) | 0 | at_least: 0; more_than: 1; at_most: 0; less_than: 0 |
| `observation_period.duration.quantity<bound>.value` | 1/1 (100.0%) | 0 | min 1; median 1; max 1; mean 1.00 |
| `observation_period.duration.quantity<exact>` | 452/452 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<exact>.approximate` | 452/452 (100.0%) | 0 | False: 451; True: 1 |
| `observation_period.duration.quantity<exact>.kind` | 452/452 (100.0%) | 0 | exact: 452 |
| `observation_period.duration.quantity<exact>.value` | 452/452 (100.0%) | 0 | min 1; median 2; max 90; mean 3.70 |
| `observation_period.duration.quantity<range>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<range>.kind` | 0/0 (not observed) | 0 | range: 0 |
| `observation_period.duration.quantity<range>.lower` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.upper` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.unit` | 453/453 (100.0%) | 0 | second: 0; minute: 1; hour: 0; day: 10; week: 97; month: 305; year: 40 |
| `observation_period.end` | 52/972 (5.3%) | 920 | Object/union; see child fields |
| `observation_period.end.form` | 52/52 (100.0%) | 0 | calendar: 48; relative: 4 |
| `observation_period.end.precision` | 52/52 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 9; week: 0; month: 39; year: 2; unspecified: 2 |
| `observation_period.end.wording` | 52/52 (100.0%) | 0 | 44 distinct; 30 September 2025: 3; August: 3; September: 2 |
| `observation_period.start` | 321/972 (33.0%) | 651 | Object/union; see child fields |
| `observation_period.start.form` | 321/321 (100.0%) | 0 | calendar: 282; relative: 39 |
| `observation_period.start.precision` | 321/321 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 21; week: 1; month: 257; year: 14; unspecified: 28 |
| `observation_period.start.wording` | 321/321 (100.0%) | 0 | 147 distinct; August: 14; May: 14; December: 13 |
| `observation_period.wording` | 972/972 (100.0%) | 0 | 459 distinct; this month: 26; this year: 20; over the past three months: 18 |
| `temporal_status` | 2,355/2,355 (100.0%) | 0 | current: 1791; recent: 324; historical: 232; future: 6; unclear: 2 |

### recurring_rate

| Attribute | Populated / eligible | Null | Values / numeric summary |
| --- | --- | --- | --- |
| `condition` | 28/360 (7.8%) | 332 | 26 distinct; brief periods: 2; on awakening: 2; if events become more frequent: 1 |
| `event` | 360/360 (100.0%) | 0 | Object/union; see child fields |
| `event.description` | 360/360 (100.0%) | 0 | 140 distinct; seizures: 65; generalised tonic-clonic seizures: 26; absence seizures: 20 |
| `event.grouping` | 360/360 (100.0%) | 0 | one_type: 265; explicit_combined_group: 7; unspecified: 88 |
| `event.seizure_interpretation` | 360/360 (100.0%) | 0 | stated_seizure: 332; uncertain_seizure: 27; explicitly_non_seizure: 0; not_specified: 1 |
| `evidence` | 360/360 (100.0%) | 0 | 319 distinct; daily drop attacks: 6; focal impaired-awareness seizures with disorientation are reported every fo: 6; tonic-clonic seizures 2 times per month: 5 |
| `finding_id` | 360/360 (100.0%) | 0 | 7 distinct; f1: 190; f2: 97; f3: 49 |
| `measurement` | 360/360 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count` | 360/360 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<bound>` | 20/20 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<bound>.approximate` | 20/20 (100.0%) | 0 | False: 18; True: 2 |
| `measurement.count<bound>.kind` | 20/20 (100.0%) | 0 | bound: 20 |
| `measurement.count<bound>.relation` | 20/20 (100.0%) | 0 | at_least: 1; more_than: 3; at_most: 16; less_than: 0 |
| `measurement.count<bound>.value` | 20/20 (100.0%) | 0 | min 1; median 2; max 7; mean 2.45 |
| `measurement.count<exact>` | 263/263 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<exact>.approximate` | 263/263 (100.0%) | 0 | False: 214; True: 49 |
| `measurement.count<exact>.kind` | 263/263 (100.0%) | 0 | exact: 263 |
| `measurement.count<exact>.value` | 263/263 (100.0%) | 0 | min 1; median 1; max 17; mean 2.08 |
| `measurement.count<qualitative>` | 23/23 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<qualitative>.kind` | 23/23 (100.0%) | 0 | qualitative: 23 |
| `measurement.count<qualitative>.wording` | 23/23 (100.0%) | 0 | 8 distinct; several: 15; dozens: 2; multiple: 1 |
| `measurement.count<range>` | 54/54 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<range>.approximate` | 54/54 (100.0%) | 0 | False: 45; True: 9 |
| `measurement.count<range>.kind` | 54/54 (100.0%) | 0 | range: 54 |
| `measurement.count<range>.lower` | 54/54 (100.0%) | 0 | min 1; median 2; max 21; mean 2.70 |
| `measurement.count<range>.upper` | 54/54 (100.0%) | 0 | min 2; median 3; max 30; mean 4.33 |
| `measurement.denominator` | 360/360 (100.0%) | 0 | Object/union; see child fields |
| `measurement.denominator.quantity` | 360/360 (100.0%) | 0 | Object/union; see child fields |
| `measurement.denominator.quantity<bound>` | 0/0 (not observed) | 0 | Variant not emitted |
| `measurement.denominator.quantity<bound>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `measurement.denominator.quantity<bound>.kind` | 0/0 (not observed) | 0 | bound: 0 |
| `measurement.denominator.quantity<bound>.relation` | 0/0 (not observed) | 0 | at_least: 0; more_than: 0; at_most: 0; less_than: 0 |
| `measurement.denominator.quantity<bound>.value` | 0/0 (not observed) | 0 | Variant not emitted |
| `measurement.denominator.quantity<exact>` | 318/318 (100.0%) | 0 | Object/union; see child fields |
| `measurement.denominator.quantity<exact>.approximate` | 318/318 (100.0%) | 0 | False: 304; True: 14 |
| `measurement.denominator.quantity<exact>.kind` | 318/318 (100.0%) | 0 | exact: 318 |
| `measurement.denominator.quantity<exact>.value` | 318/318 (100.0%) | 0 | min 1; median 1; max 12; mean 1.50 |
| `measurement.denominator.quantity<range>` | 42/42 (100.0%) | 0 | Object/union; see child fields |
| `measurement.denominator.quantity<range>.approximate` | 42/42 (100.0%) | 0 | False: 36; True: 6 |
| `measurement.denominator.quantity<range>.kind` | 42/42 (100.0%) | 0 | range: 42 |
| `measurement.denominator.quantity<range>.lower` | 42/42 (100.0%) | 0 | min 1; median 3; max 14; mean 3.21 |
| `measurement.denominator.quantity<range>.upper` | 42/42 (100.0%) | 0 | min 2; median 4; max 21; mean 4.62 |
| `measurement.denominator.unit` | 360/360 (100.0%) | 0 | second: 0; minute: 0; hour: 5; day: 89; week: 129; month: 98; year: 39 |
| `measurement.kind` | 360/360 (100.0%) | 0 | recurring_rate: 360 |
| `observation_period` | 107/360 (29.7%) | 253 | Object/union; see child fields |
| `observation_period.duration` | 76/107 (71.0%) | 31 | Object/union; see child fields |
| `observation_period.duration.quantity` | 76/76 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<bound>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<bound>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<bound>.kind` | 0/0 (not observed) | 0 | bound: 0 |
| `observation_period.duration.quantity<bound>.relation` | 0/0 (not observed) | 0 | at_least: 0; more_than: 0; at_most: 0; less_than: 0 |
| `observation_period.duration.quantity<bound>.value` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<exact>` | 76/76 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<exact>.approximate` | 76/76 (100.0%) | 0 | False: 76; True: 0 |
| `observation_period.duration.quantity<exact>.kind` | 76/76 (100.0%) | 0 | exact: 76 |
| `observation_period.duration.quantity<exact>.value` | 76/76 (100.0%) | 0 | min 1; median 4; max 18; mean 4.51 |
| `observation_period.duration.quantity<range>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<range>.kind` | 0/0 (not observed) | 0 | range: 0 |
| `observation_period.duration.quantity<range>.lower` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.upper` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.unit` | 76/76 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 0; week: 16; month: 51; year: 9 |
| `observation_period.end` | 0/107 (0.0%) | 107 | Object/union; see child fields |
| `observation_period.end.form` | 0/0 (not observed) | 0 | calendar: 0; relative: 0 |
| `observation_period.end.precision` | 0/0 (not observed) | 0 | second: 0; minute: 0; hour: 0; day: 0; week: 0; month: 0; year: 0; unspecified: 0 |
| `observation_period.end.wording` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.start` | 6/107 (5.6%) | 101 | Object/union; see child fields |
| `observation_period.start.form` | 6/6 (100.0%) | 0 | calendar: 2; relative: 4 |
| `observation_period.start.precision` | 6/6 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 0; week: 0; month: 3; year: 0; unspecified: 3 |
| `observation_period.start.wording` | 6/6 (100.0%) | 0 | 6 distinct; the last clinic contact: 1; March this year: 1; late spring: 1 |
| `observation_period.wording` | 107/107 (100.0%) | 0 | 63 distinct; over the last six months: 10; for many years: 6; over the past three months: 5 |
| `temporal_status` | 360/360 (100.0%) | 0 | current: 316; recent: 4; historical: 35; future: 5; unclear: 0 |

### observed_count

| Attribute | Populated / eligible | Null | Values / numeric summary |
| --- | --- | --- | --- |
| `condition` | 42/560 (7.5%) | 518 | 36 distinct; with more severe seizures: 3; around periods of marked sleep deprivation: 2; Prior to recent lifestyle changes: 2 |
| `event` | 560/560 (100.0%) | 0 | Object/union; see child fields |
| `event.description` | 560/560 (100.0%) | 0 | 179 distinct; seizures: 140; focal seizures: 21; generalised tonic-clonic seizures: 20 |
| `event.grouping` | 560/560 (100.0%) | 0 | one_type: 321; explicit_combined_group: 6; unspecified: 233 |
| `event.seizure_interpretation` | 560/560 (100.0%) | 0 | stated_seizure: 497; uncertain_seizure: 62; explicitly_non_seizure: 0; not_specified: 1 |
| `evidence` | 560/560 (100.0%) | 0 | 518 distinct; two drop attacks: 4; Jun x1: 4; one while awake: 3 |
| `finding_id` | 560/560 (100.0%) | 0 | 12 distinct; f1: 175; f2: 152; f3: 100 |
| `measurement` | 560/560 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count` | 560/560 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<bound>` | 2/2 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<bound>.approximate` | 2/2 (100.0%) | 0 | False: 2; True: 0 |
| `measurement.count<bound>.kind` | 2/2 (100.0%) | 0 | bound: 2 |
| `measurement.count<bound>.relation` | 2/2 (100.0%) | 0 | at_least: 2; more_than: 0; at_most: 0; less_than: 0 |
| `measurement.count<bound>.value` | 2/2 (100.0%) | 0 | min 1; median 1.5; max 2; mean 1.50 |
| `measurement.count<exact>` | 499/499 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<exact>.approximate` | 499/499 (100.0%) | 0 | False: 494; True: 5 |
| `measurement.count<exact>.kind` | 499/499 (100.0%) | 0 | exact: 499 |
| `measurement.count<exact>.value` | 499/499 (100.0%) | 0 | min 0; median 2; max 19; mean 2.94 |
| `measurement.count<qualitative>` | 15/15 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<qualitative>.kind` | 15/15 (100.0%) | 0 | qualitative: 15 |
| `measurement.count<qualitative>.wording` | 15/15 (100.0%) | 0 | 5 distinct; several: 11; multiple: 1; handful: 1 |
| `measurement.count<range>` | 44/44 (100.0%) | 0 | Object/union; see child fields |
| `measurement.count<range>.approximate` | 44/44 (100.0%) | 0 | False: 37; True: 7 |
| `measurement.count<range>.kind` | 44/44 (100.0%) | 0 | range: 44 |
| `measurement.count<range>.lower` | 44/44 (100.0%) | 0 | min 1; median 3; max 21; mean 4.16 |
| `measurement.count<range>.upper` | 44/44 (100.0%) | 0 | min 3; median 5; max 28; mean 5.91 |
| `measurement.kind` | 560/560 (100.0%) | 0 | observed_count: 560 |
| `observation_period` | 507/560 (90.5%) | 53 | Object/union; see child fields |
| `observation_period.duration` | 216/507 (42.6%) | 291 | Object/union; see child fields |
| `observation_period.duration.quantity` | 216/216 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<bound>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<bound>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<bound>.kind` | 0/0 (not observed) | 0 | bound: 0 |
| `observation_period.duration.quantity<bound>.relation` | 0/0 (not observed) | 0 | at_least: 0; more_than: 0; at_most: 0; less_than: 0 |
| `observation_period.duration.quantity<bound>.value` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<exact>` | 216/216 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<exact>.approximate` | 216/216 (100.0%) | 0 | False: 215; True: 1 |
| `observation_period.duration.quantity<exact>.kind` | 216/216 (100.0%) | 0 | exact: 216 |
| `observation_period.duration.quantity<exact>.value` | 216/216 (100.0%) | 0 | min 1; median 1; max 30; mean 2.72 |
| `observation_period.duration.quantity<range>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<range>.kind` | 0/0 (not observed) | 0 | range: 0 |
| `observation_period.duration.quantity<range>.lower` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.upper` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.unit` | 216/216 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 7; week: 55; month: 148; year: 6 |
| `observation_period.end` | 36/507 (7.1%) | 471 | Object/union; see child fields |
| `observation_period.end.form` | 36/36 (100.0%) | 0 | calendar: 34; relative: 2 |
| `observation_period.end.precision` | 36/36 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 5; week: 0; month: 29; year: 1; unspecified: 1 |
| `observation_period.end.wording` | 36/36 (100.0%) | 0 | 31 distinct; September: 2; May: 2; August: 2 |
| `observation_period.start` | 238/507 (46.9%) | 269 | Object/union; see child fields |
| `observation_period.start.form` | 238/238 (100.0%) | 0 | calendar: 227; relative: 11 |
| `observation_period.start.precision` | 238/238 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 6; week: 1; month: 215; year: 10; unspecified: 6 |
| `observation_period.start.wording` | 238/238 (100.0%) | 0 | 96 distinct; August: 14; May: 12; June: 11 |
| `observation_period.wording` | 507/507 (100.0%) | 0 | 236 distinct; last month: 14; July: 10; last week: 9 |
| `temporal_status` | 560/560 (100.0%) | 0 | current: 286; recent: 197; historical: 77; future: 0; unclear: 0 |

### cluster_pattern

| Attribute | Populated / eligible | Null | Values / numeric summary |
| --- | --- | --- | --- |
| `condition` | 72/277 (26.0%) | 205 | 69 distinct; after nights of curtailed sleep: 2; in bad weeks: 2; on workdays: 2 |
| `event` | 277/277 (100.0%) | 0 | Object/union; see child fields |
| `event.description` | 277/277 (100.0%) | 0 | 118 distinct; seizures: 66; clusters: 22; events: 12 |
| `event.grouping` | 277/277 (100.0%) | 0 | one_type: 126; explicit_combined_group: 12; unspecified: 139 |
| `event.seizure_interpretation` | 277/277 (100.0%) | 0 | stated_seizure: 240; uncertain_seizure: 31; explicitly_non_seizure: 1; not_specified: 5 |
| `evidence` | 277/277 (100.0%) | 0 | 262 distinct; drop attacks occurring in batches: 5; myoclonic jerks in morning clusters: 4; device logs suggest short clusters without counts: 3 |
| `finding_id` | 277/277 (100.0%) | 0 | 10 distinct; f1: 95; f2: 80; f3: 48 |
| `measurement` | 277/277 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence` | 88/277 (31.8%) | 189 | Object/union; see child fields |
| `measurement.cadence.count` | 88/88 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.count<bound>` | 3/3 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.count<bound>.approximate` | 3/3 (100.0%) | 0 | False: 3; True: 0 |
| `measurement.cadence.count<bound>.kind` | 3/3 (100.0%) | 0 | bound: 3 |
| `measurement.cadence.count<bound>.relation` | 3/3 (100.0%) | 0 | at_least: 0; more_than: 0; at_most: 2; less_than: 1 |
| `measurement.cadence.count<bound>.value` | 3/3 (100.0%) | 0 | min 5; median 7; max 7; mean 6.33 |
| `measurement.cadence.count<exact>` | 74/74 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.count<exact>.approximate` | 74/74 (100.0%) | 0 | False: 63; True: 11 |
| `measurement.cadence.count<exact>.kind` | 74/74 (100.0%) | 0 | exact: 74 |
| `measurement.cadence.count<exact>.value` | 74/74 (100.0%) | 0 | min 1; median 1; max 5; mean 1.51 |
| `measurement.cadence.count<qualitative>` | 5/5 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.count<qualitative>.kind` | 5/5 (100.0%) | 0 | qualitative: 5 |
| `measurement.cadence.count<qualitative>.wording` | 5/5 (100.0%) | 0 | 3 distinct; multiple: 2; several: 2; several evenings: 1 |
| `measurement.cadence.count<range>` | 6/6 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.count<range>.approximate` | 6/6 (100.0%) | 0 | False: 6; True: 0 |
| `measurement.cadence.count<range>.kind` | 6/6 (100.0%) | 0 | range: 6 |
| `measurement.cadence.count<range>.lower` | 6/6 (100.0%) | 0 | min 1; median 2; max 4; mean 2.17 |
| `measurement.cadence.count<range>.upper` | 6/6 (100.0%) | 0 | min 2; median 3.5; max 5; mean 3.33 |
| `measurement.cadence.denominator` | 88/88 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.denominator.quantity` | 88/88 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.denominator.quantity<bound>` | 3/3 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.denominator.quantity<bound>.approximate` | 3/3 (100.0%) | 0 | False: 3; True: 0 |
| `measurement.cadence.denominator.quantity<bound>.kind` | 3/3 (100.0%) | 0 | bound: 3 |
| `measurement.cadence.denominator.quantity<bound>.relation` | 3/3 (100.0%) | 0 | at_least: 0; more_than: 0; at_most: 3; less_than: 0 |
| `measurement.cadence.denominator.quantity<bound>.value` | 3/3 (100.0%) | 0 | min 2; median 4; max 4; mean 3.33 |
| `measurement.cadence.denominator.quantity<exact>` | 75/75 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.denominator.quantity<exact>.approximate` | 75/75 (100.0%) | 0 | False: 72; True: 3 |
| `measurement.cadence.denominator.quantity<exact>.kind` | 75/75 (100.0%) | 0 | exact: 75 |
| `measurement.cadence.denominator.quantity<exact>.value` | 75/75 (100.0%) | 0 | min 1; median 1; max 6; mean 1.65 |
| `measurement.cadence.denominator.quantity<range>` | 10/10 (100.0%) | 0 | Object/union; see child fields |
| `measurement.cadence.denominator.quantity<range>.approximate` | 10/10 (100.0%) | 0 | False: 7; True: 3 |
| `measurement.cadence.denominator.quantity<range>.kind` | 10/10 (100.0%) | 0 | range: 10 |
| `measurement.cadence.denominator.quantity<range>.lower` | 10/10 (100.0%) | 0 | min 2; median 4; max 7; mean 3.90 |
| `measurement.cadence.denominator.quantity<range>.upper` | 10/10 (100.0%) | 0 | min 3; median 5; max 9; mean 5.10 |
| `measurement.cadence.denominator.unit` | 88/88 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 18; week: 28; month: 41; year: 1 |
| `measurement.cadence.kind` | 88/88 (100.0%) | 0 | recurring_rate: 88 |
| `measurement.kind` | 277/277 (100.0%) | 0 | cluster_pattern: 277 |
| `measurement.seizures_per_cluster` | 133/277 (48.0%) | 144 | Object/union; see child fields |
| `measurement.seizures_per_cluster<bound>` | 3/3 (100.0%) | 0 | Object/union; see child fields |
| `measurement.seizures_per_cluster<bound>.approximate` | 3/3 (100.0%) | 0 | False: 0; True: 3 |
| `measurement.seizures_per_cluster<bound>.kind` | 3/3 (100.0%) | 0 | bound: 3 |
| `measurement.seizures_per_cluster<bound>.relation` | 3/3 (100.0%) | 0 | at_least: 3; more_than: 0; at_most: 0; less_than: 0 |
| `measurement.seizures_per_cluster<bound>.value` | 3/3 (100.0%) | 0 | min 4; median 5; max 6; mean 5.00 |
| `measurement.seizures_per_cluster<exact>` | 35/35 (100.0%) | 0 | Object/union; see child fields |
| `measurement.seizures_per_cluster<exact>.approximate` | 35/35 (100.0%) | 0 | False: 21; True: 14 |
| `measurement.seizures_per_cluster<exact>.kind` | 35/35 (100.0%) | 0 | exact: 35 |
| `measurement.seizures_per_cluster<exact>.value` | 35/35 (100.0%) | 0 | min 1; median 4; max 6; mean 3.89 |
| `measurement.seizures_per_cluster<qualitative>` | 68/68 (100.0%) | 0 | Object/union; see child fields |
| `measurement.seizures_per_cluster<qualitative>.kind` | 68/68 (100.0%) | 0 | qualitative: 68 |
| `measurement.seizures_per_cluster<qualitative>.wording` | 68/68 (100.0%) | 0 | 17 distinct; multiple: 38; clusters: 5; several: 5 |
| `measurement.seizures_per_cluster<range>` | 27/27 (100.0%) | 0 | Object/union; see child fields |
| `measurement.seizures_per_cluster<range>.approximate` | 27/27 (100.0%) | 0 | False: 16; True: 11 |
| `measurement.seizures_per_cluster<range>.kind` | 27/27 (100.0%) | 0 | range: 27 |
| `measurement.seizures_per_cluster<range>.lower` | 27/27 (100.0%) | 0 | min 1; median 3; max 6; mean 3.04 |
| `measurement.seizures_per_cluster<range>.upper` | 27/27 (100.0%) | 0 | min 2; median 4; max 8; mean 4.52 |
| `observation_period` | 78/277 (28.2%) | 199 | Object/union; see child fields |
| `observation_period.duration` | 42/78 (53.8%) | 36 | Object/union; see child fields |
| `observation_period.duration.quantity` | 42/42 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<bound>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<bound>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<bound>.kind` | 0/0 (not observed) | 0 | bound: 0 |
| `observation_period.duration.quantity<bound>.relation` | 0/0 (not observed) | 0 | at_least: 0; more_than: 0; at_most: 0; less_than: 0 |
| `observation_period.duration.quantity<bound>.value` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<exact>` | 42/42 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<exact>.approximate` | 42/42 (100.0%) | 0 | False: 42; True: 0 |
| `observation_period.duration.quantity<exact>.kind` | 42/42 (100.0%) | 0 | exact: 42 |
| `observation_period.duration.quantity<exact>.value` | 42/42 (100.0%) | 0 | min 1; median 2.5; max 90; mean 4.98 |
| `observation_period.duration.quantity<range>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<range>.kind` | 0/0 (not observed) | 0 | range: 0 |
| `observation_period.duration.quantity<range>.lower` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.upper` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.unit` | 42/42 (100.0%) | 0 | second: 0; minute: 1; hour: 0; day: 2; week: 11; month: 26; year: 2 |
| `observation_period.end` | 2/78 (2.6%) | 76 | Object/union; see child fields |
| `observation_period.end.form` | 2/2 (100.0%) | 0 | calendar: 2; relative: 0 |
| `observation_period.end.precision` | 2/2 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 1; week: 0; month: 1; year: 0; unspecified: 0 |
| `observation_period.end.wording` | 2/2 (100.0%) | 0 | 2 distinct; 13-Nov-2015: 1; August: 1 |
| `observation_period.start` | 15/78 (19.2%) | 63 | Object/union; see child fields |
| `observation_period.start.form` | 15/15 (100.0%) | 0 | calendar: 13; relative: 2 |
| `observation_period.start.precision` | 15/15 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 2; week: 0; month: 11; year: 0; unspecified: 2 |
| `observation_period.start.wording` | 15/15 (100.0%) | 0 | 15 distinct; May 2025: 1; late August: 1; last review: 1 |
| `observation_period.wording` | 78/78 (100.0%) | 0 | 56 distinct; this month: 12; over the past three months: 4; Over the past month: 3 |
| `temporal_status` | 277/277 (100.0%) | 0 | current: 234; recent: 19; historical: 23; future: 1; unclear: 0 |

### seizure_free_interval

| Attribute | Populated / eligible | Null | Values / numeric summary |
| --- | --- | --- | --- |
| `condition` | 19/543 (3.5%) | 524 | 17 distinct; between clusters: 2; with treatment: 2; outside of nights with curtailed rest: 1 |
| `event` | 543/543 (100.0%) | 0 | Object/union; see child fields |
| `event.description` | 543/543 (100.0%) | 0 | 166 distinct; seizures: 162; events: 40; generalised tonic–clonic seizures: 39 |
| `event.grouping` | 543/543 (100.0%) | 0 | one_type: 221; explicit_combined_group: 41; unspecified: 281 |
| `event.seizure_interpretation` | 543/543 (100.0%) | 0 | stated_seizure: 452; uncertain_seizure: 64; explicitly_non_seizure: 0; not_specified: 27 |
| `evidence` | 543/543 (100.0%) | 0 | 495 distinct; No events have occurred since his most recent review: 5; There have been no generalised tonic–clonic seizures reported.: 4; No generalised tonic–clonic seizures reported.: 4 |
| `finding_id` | 543/543 (100.0%) | 0 | 12 distinct; f2: 145; f3: 143; f1: 110 |
| `measurement` | 543/543 (100.0%) | 0 | Object/union; see child fields |
| `measurement.duration` | 148/543 (27.3%) | 395 | Object/union; see child fields |
| `measurement.duration.quantity` | 148/148 (100.0%) | 0 | Object/union; see child fields |
| `measurement.duration.quantity<bound>` | 31/31 (100.0%) | 0 | Object/union; see child fields |
| `measurement.duration.quantity<bound>.approximate` | 31/31 (100.0%) | 0 | False: 25; True: 6 |
| `measurement.duration.quantity<bound>.kind` | 31/31 (100.0%) | 0 | bound: 31 |
| `measurement.duration.quantity<bound>.relation` | 31/31 (100.0%) | 0 | at_least: 1; more_than: 26; at_most: 4; less_than: 0 |
| `measurement.duration.quantity<bound>.value` | 31/31 (100.0%) | 0 | min 1; median 2; max 18; mean 4.58 |
| `measurement.duration.quantity<exact>` | 116/116 (100.0%) | 0 | Object/union; see child fields |
| `measurement.duration.quantity<exact>.approximate` | 116/116 (100.0%) | 0 | False: 106; True: 10 |
| `measurement.duration.quantity<exact>.kind` | 116/116 (100.0%) | 0 | exact: 116 |
| `measurement.duration.quantity<exact>.value` | 116/116 (100.0%) | 0 | min 1; median 5; max 18; mean 5.70 |
| `measurement.duration.quantity<range>` | 1/1 (100.0%) | 0 | Object/union; see child fields |
| `measurement.duration.quantity<range>.approximate` | 1/1 (100.0%) | 0 | False: 0; True: 1 |
| `measurement.duration.quantity<range>.kind` | 1/1 (100.0%) | 0 | range: 1 |
| `measurement.duration.quantity<range>.lower` | 1/1 (100.0%) | 0 | min 1; median 1; max 1; mean 1.00 |
| `measurement.duration.quantity<range>.upper` | 1/1 (100.0%) | 0 | min 2; median 2; max 2; mean 2.00 |
| `measurement.duration.unit` | 148/148 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 5; week: 32; month: 76; year: 35 |
| `measurement.kind` | 543/543 (100.0%) | 0 | seizure_free_interval: 543 |
| `measurement.since` | 176/543 (32.4%) | 367 | Object/union; see child fields |
| `measurement.since.form` | 176/176 (100.0%) | 0 | calendar: 86; relative: 90 |
| `measurement.since.precision` | 176/176 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 41; week: 2; month: 50; year: 9; unspecified: 74 |
| `measurement.since.wording` | 176/176 (100.0%) | 0 | 143 distinct; his most recent review: 5; last clinic visit: 5; then: 4 |
| `observation_period` | 145/543 (26.7%) | 398 | Object/union; see child fields |
| `observation_period.duration` | 56/145 (38.6%) | 89 | Object/union; see child fields |
| `observation_period.duration.quantity` | 56/56 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<bound>` | 1/1 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<bound>.approximate` | 1/1 (100.0%) | 0 | False: 1; True: 0 |
| `observation_period.duration.quantity<bound>.kind` | 1/1 (100.0%) | 0 | bound: 1 |
| `observation_period.duration.quantity<bound>.relation` | 1/1 (100.0%) | 0 | at_least: 0; more_than: 1; at_most: 0; less_than: 0 |
| `observation_period.duration.quantity<bound>.value` | 1/1 (100.0%) | 0 | min 1; median 1; max 1; mean 1.00 |
| `observation_period.duration.quantity<exact>` | 55/55 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<exact>.approximate` | 55/55 (100.0%) | 0 | False: 55; True: 0 |
| `observation_period.duration.quantity<exact>.kind` | 55/55 (100.0%) | 0 | exact: 55 |
| `observation_period.duration.quantity<exact>.value` | 55/55 (100.0%) | 0 | min 1; median 6; max 18; mean 5.27 |
| `observation_period.duration.quantity<range>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<range>.kind` | 0/0 (not observed) | 0 | range: 0 |
| `observation_period.duration.quantity<range>.lower` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.upper` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.unit` | 56/56 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 0; week: 4; month: 40; year: 12 |
| `observation_period.end` | 10/145 (6.9%) | 135 | Object/union; see child fields |
| `observation_period.end.form` | 10/10 (100.0%) | 0 | calendar: 10; relative: 0 |
| `observation_period.end.precision` | 10/10 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 3; week: 0; month: 7; year: 0; unspecified: 0 |
| `observation_period.end.wording` | 10/10 (100.0%) | 0 | 9 distinct; 30 September 2025: 2; late July: 1; June: 1 |
| `observation_period.start` | 53/145 (36.6%) | 92 | Object/union; see child fields |
| `observation_period.start.form` | 53/53 (100.0%) | 0 | calendar: 34; relative: 19 |
| `observation_period.start.precision` | 53/53 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 12; week: 0; month: 23; year: 4; unspecified: 14 |
| `observation_period.start.wording` | 53/53 (100.0%) | 0 | 50 distinct; 10 March 2025: 2; our last review: 2; 11th June 2025: 2 |
| `observation_period.wording` | 145/145 (100.0%) | 0 | 123 distinct; this year: 6; over the past six months: 4; Since her last review six months ago: 3 |
| `temporal_status` | 543/543 (100.0%) | 0 | current: 498; recent: 17; historical: 28; future: 0; unclear: 0 |

### last_seizure

| Attribute | Populated / eligible | Null | Values / numeric summary |
| --- | --- | --- | --- |
| `condition` | 11/88 (12.5%) | 77 | 11 distinct; after a period of sleep deprivation: 1; after an overnight shift and early start the following day: 1; after a missed evening dose: 1 |
| `event` | 88/88 (100.0%) | 0 | Object/union; see child fields |
| `event.description` | 88/88 (100.0%) | 0 | 45 distinct; seizures: 9; episode: 6; generalised convulsion: 5 |
| `event.grouping` | 88/88 (100.0%) | 0 | one_type: 56; explicit_combined_group: 0; unspecified: 32 |
| `event.seizure_interpretation` | 88/88 (100.0%) | 0 | stated_seizure: 76; uncertain_seizure: 11; explicitly_non_seizure: 0; not_specified: 1 |
| `evidence` | 88/88 (100.0%) | 0 | 87 distinct; a focal impaired-awareness seizure occurred 2 Thursdays ago: 2; His last generalised tonic–clonic seizure was in May 2025 after a night of : 1; The most recent event occurred 10 days ago: 1 |
| `finding_id` | 88/88 (100.0%) | 0 | 5 distinct; f2: 42; f1: 20; f4: 12 |
| `measurement` | 88/88 (100.0%) | 0 | Object/union; see child fields |
| `measurement.kind` | 88/88 (100.0%) | 0 | last_seizure: 88 |
| `measurement.when` | 88/88 (100.0%) | 0 | Object/union; see child fields |
| `measurement.when.form` | 88/88 (100.0%) | 0 | calendar: 59; relative: 29 |
| `measurement.when.precision` | 88/88 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 41; week: 7; month: 32; year: 2; unspecified: 6 |
| `measurement.when.wording` | 88/88 (100.0%) | 0 | 82 distinct; May 2025: 2; 10 days ago: 2; over two years ago: 2 |
| `observation_period` | 1/88 (1.1%) | 87 | Object/union; see child fields |
| `observation_period.duration` | 0/1 (0.0%) | 1 | Object/union; see child fields |
| `observation_period.duration.quantity` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<bound>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<bound>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<bound>.kind` | 0/0 (not observed) | 0 | bound: 0 |
| `observation_period.duration.quantity<bound>.relation` | 0/0 (not observed) | 0 | at_least: 0; more_than: 0; at_most: 0; less_than: 0 |
| `observation_period.duration.quantity<bound>.value` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<exact>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<exact>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<exact>.kind` | 0/0 (not observed) | 0 | exact: 0 |
| `observation_period.duration.quantity<exact>.value` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<range>.kind` | 0/0 (not observed) | 0 | range: 0 |
| `observation_period.duration.quantity<range>.lower` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.upper` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.unit` | 0/0 (not observed) | 0 | second: 0; minute: 0; hour: 0; day: 0; week: 0; month: 0; year: 0 |
| `observation_period.end` | 0/1 (0.0%) | 1 | Object/union; see child fields |
| `observation_period.end.form` | 0/0 (not observed) | 0 | calendar: 0; relative: 0 |
| `observation_period.end.precision` | 0/0 (not observed) | 0 | second: 0; minute: 0; hour: 0; day: 0; week: 0; month: 0; year: 0; unspecified: 0 |
| `observation_period.end.wording` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.start` | 0/1 (0.0%) | 1 | Object/union; see child fields |
| `observation_period.start.form` | 0/0 (not observed) | 0 | calendar: 0; relative: 0 |
| `observation_period.start.precision` | 0/0 (not observed) | 0 | second: 0; minute: 0; hour: 0; day: 0; week: 0; month: 0; year: 0; unspecified: 0 |
| `observation_period.start.wording` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.wording` | 1/1 (100.0%) | 0 | 1 distinct; Since the last review: 1 |
| `temporal_status` | 88/88 (100.0%) | 0 | current: 24; recent: 46; historical: 18; future: 0; unclear: 0 |

### qualitative_frequency

| Attribute | Populated / eligible | Null | Values / numeric summary |
| --- | --- | --- | --- |
| `condition` | 92/527 (17.5%) | 435 | 80 distinct; when overtired: 3; under stress: 3; following the use of her prescribed medication: 3 |
| `event` | 527/527 (100.0%) | 0 | Object/union; see child fields |
| `event.description` | 527/527 (100.0%) | 0 | 278 distinct; seizures: 77; events: 44; myoclonic jerks: 20 |
| `event.grouping` | 527/527 (100.0%) | 0 | one_type: 290; explicit_combined_group: 13; unspecified: 224 |
| `event.seizure_interpretation` | 527/527 (100.0%) | 0 | stated_seizure: 352; uncertain_seizure: 142; explicitly_non_seizure: 14; not_specified: 19 |
| `evidence` | 527/527 (100.0%) | 0 | 488 distinct; rarely achieving more than ten consecutive seizure-free days: 5; occasional generalised tonic-clonic seizures: 4; occasional generalised tonic–clonic seizures: 3 |
| `finding_id` | 527/527 (100.0%) | 0 | 13 distinct; f1: 129; f2: 118; f3: 106 |
| `measurement` | 527/527 (100.0%) | 0 | Object/union; see child fields |
| `measurement.kind` | 527/527 (100.0%) | 0 | qualitative_frequency: 527 |
| `measurement.wording` | 527/527 (100.0%) | 0 | 323 distinct; occasional: 58; intermittent: 24; infrequent: 19 |
| `observation_period` | 134/527 (25.4%) | 393 | Object/union; see child fields |
| `observation_period.duration` | 63/134 (47.0%) | 71 | Object/union; see child fields |
| `observation_period.duration.quantity` | 63/63 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<bound>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<bound>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<bound>.kind` | 0/0 (not observed) | 0 | bound: 0 |
| `observation_period.duration.quantity<bound>.relation` | 0/0 (not observed) | 0 | at_least: 0; more_than: 0; at_most: 0; less_than: 0 |
| `observation_period.duration.quantity<bound>.value` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<exact>` | 63/63 (100.0%) | 0 | Object/union; see child fields |
| `observation_period.duration.quantity<exact>.approximate` | 63/63 (100.0%) | 0 | False: 63; True: 0 |
| `observation_period.duration.quantity<exact>.kind` | 63/63 (100.0%) | 0 | exact: 63 |
| `observation_period.duration.quantity<exact>.value` | 63/63 (100.0%) | 0 | min 1; median 3; max 18; mean 3.86 |
| `observation_period.duration.quantity<range>` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.approximate` | 0/0 (not observed) | 0 | False: 0; True: 0 |
| `observation_period.duration.quantity<range>.kind` | 0/0 (not observed) | 0 | range: 0 |
| `observation_period.duration.quantity<range>.lower` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.quantity<range>.upper` | 0/0 (not observed) | 0 | Variant not emitted |
| `observation_period.duration.unit` | 63/63 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 1; week: 11; month: 40; year: 11 |
| `observation_period.end` | 4/134 (3.0%) | 130 | Object/union; see child fields |
| `observation_period.end.form` | 4/4 (100.0%) | 0 | calendar: 2; relative: 2 |
| `observation_period.end.precision` | 4/4 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 0; week: 0; month: 2; year: 1; unspecified: 1 |
| `observation_period.end.wording` | 4/4 (100.0%) | 0 | 4 distinct; 2023: 1; dose stabilisation: 1; dose increase in May: 1 |
| `observation_period.start` | 9/134 (6.7%) | 125 | Object/union; see child fields |
| `observation_period.start.form` | 9/9 (100.0%) | 0 | calendar: 6; relative: 3 |
| `observation_period.start.precision` | 9/9 (100.0%) | 0 | second: 0; minute: 0; hour: 0; day: 1; week: 0; month: 5; year: 0; unspecified: 3 |
| `observation_period.start.wording` | 9/9 (100.0%) | 0 | 9 distinct; March 2025: 1; 10 June 2025: 1; Since adding lamotrigine alongside levetiracetam: 1 |
| `observation_period.wording` | 134/134 (100.0%) | 0 | 83 distinct; this year: 9; over the past three months: 8; Over the past three months: 7 |
| `temporal_status` | 527/527 (100.0%) | 0 | current: 433; recent: 41; historical: 51; future: 0; unclear: 2 |

## Limits of the simplification decision

These statistics describe one model, prompt and synthetic development distribution.
Required fields naturally have 100% population in schema-valid records; that does not
prove utility. Sparse fields may reflect omitted extraction. Identical evidence can
support distinct claims, and unselected findings matter for the planned complete
inventory. No field-ablation experiment, token-saving calculation or clinical review
was performed. Recommendations are candidates for review, not adopted schema rules.
