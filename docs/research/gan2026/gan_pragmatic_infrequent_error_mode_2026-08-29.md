# Pragmatic rate → unknown / no-seizure error modes

Date: 2026-08-29
Revised: 2026-08-29 (frequent → unknown types)
Status: development answer for types; holdout counts only
Protocol:
[protocol](gan_pragmatic_infrequent_error_mode_protocol_2026-08-29.md)
Artifact:
[gan_pragmatic_infrequent_error_mode_2026-08-29.json](gan_pragmatic_infrequent_error_mode_2026-08-29.json)
Figure owner: `paper/draft/confusion_matrix_pragmatic.pdf` (Gemini cell 3
select, `test450`)

`data_text_policy: synthetic_development_raw_text_diagnostic` for the
`dev750` quotes below. `test450` is gold-and-predicted ε only. No holdout
row ids or letter text.

## Answer

Yes. Infrequent → {unknown, seizure free} is the largest pragmatic error
on both splits. Frequent → unknown is the second-largest cell on both
splits and almost as large.

Together, gold rate → unknown is **29 / 67 = 0.43** of `test450` errors
(16 infrequent + 13 frequent) and **40 / 85 = 0.47** of `dev750` errors
(21 + 19). They are not the same letter type.

On `dev750`, infrequent misses are sparse dated rates collapsed to
unknown or a post-event seizure-free span. Frequent misses are mostly
cluster two-quantity labels, electrographic hourly EEG rates, and vague
“several / a couple last month” golds. All 31 + 19 select misses are
already wrong at extract. Rules recover 27 / 31 infrequent-sentinel
rows and 17 / 19 frequent-unknown rows, but rules still have **15**
frequent → unknown of their own (only 2 overlap with the LLM cell).

## Protocol in one line

- Dataset / split: Gan 2026 `gan2026_split_v1`. `test450` aggregate only;
  `dev750` row review permitted.
- Candidate: Gemini 3.7 Flash living cell 3 select.
- Comparators: extract, encode, rules-only on `dev750`.
- Scorer: living `map_pragmatic`.
- Replay: saved labels; zero model calls.

Name note: gold-kind `no_reference` maps to pragmatic **Unknown**
(`monthly_frequency` 1000). Pragmatic **Seizure free** is
`currently_no_seizure` (`monthly_frequency` 0). The figure’s two
sentinel columns are Unknown and Seizure free, not gold-kind
no-reference.

## 1. Quantitative

### `test450` living cell-3 select (n=450)

Source: published pragmatic confusion matrix. Diagonal sums to **383**
(class-report replay). Cited five-cell pragmatic is **382**; do not
retune from the one-count gap.

| True \\ Pred | Frequent | Infrequent | Unknown | Seizure free | Support | Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frequent | 210 | 3 | 13 | 1 | 227 | 0.93 |
| Infrequent | 2 | 49 | **16** | **13** | 80 | **0.61** |
| Unknown | 4 | 3 | 67 | 2 | 76 | 0.88 |
| Seizure free | 1 | 1 | 8 | 57 | 67 | 0.85 |

- All pragmatic errors: **67**.
- Infrequent → {Unknown, Seizure free}: **29 / 67 = 0.43** of all errors;
  **29 / 80 = 0.36** of gold infrequent; **29 / 31 = 0.94** of infrequent
  errors (the other 2 are infrequent → frequent).
- Frequent → unknown: **13 / 67 = 0.19** of all errors; **13 / 227 =
  0.057** of gold frequent; **13 / 17 = 0.76** of frequent errors (the
  others are 3 infrequent and 1 seizure free).
- Rate → unknown: **29 / 67 = 0.43**.
- Ranked off-diagonals: 16 infrequent→unknown, then 13 frequent→unknown
  and 13 infrequent→seizure free.

Infrequent is the weakest recall class. Frequent recall is high (0.93)
because the class is large; the unknown leak is still the second-biggest
cell. Frequent↔infrequent confusion is almost absent (5 rows).

### `dev750` living cell-3 select (n=750)

Same gold mapping. Select pragmatic **665 / 750 = 0.8867**.

| True \\ Pred | Frequent | Infrequent | Unknown | Seizure free | Support | Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frequent | 363 | 2 | 19 | 3 | 387 | 0.938 |
| Infrequent | 5 | 88 | **21** | **10** | 124 | **0.710** |
| Unknown | 6 | 6 | 109 | 6 | 127 | 0.858 |
| Seizure free | 1 | 0 | 6 | 105 | 112 | 0.938 |

- All pragmatic errors: **85**.
- Infrequent → {Unknown, Seizure free}: **31 / 85 = 0.36** of all errors;
  **31 / 124 = 0.25** of gold infrequent; **31 / 36 = 0.86** of infrequent
  errors.
- Frequent → unknown: **19 / 85 = 0.22** of all errors; **19 / 387 =
  0.049** of gold frequent; **19 / 24 = 0.79** of frequent errors (the
  others are 2 infrequent and 3 seizure free).
- Rate → unknown: **40 / 85 = 0.47**.
- Ranked off-diagonals: 21 infrequent→unknown, 19 frequent→unknown, 10
  infrequent→seizure free.

Same ranking as holdout. Infrequent miss rate is higher on `test450`
(0.36 of the class vs 0.25). Frequent → unknown is a similar fraction
of that class on both splits (about 5%).

### Same `dev750` rows at earlier stops

| Stop | Pragmatic correct | Infreq → unk | Infreq → no sz | Infreq sentinel | Freq → unk | Largest off-diagonal |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Extract | 613 | 33 | 15 | 48 | **36** | frequent → unknown (36) |
| Encode | 632 | 31 | 15 | 46 | 21 | infrequent → unknown (31) |
| Select | 665 | 21 | 10 | **31** | **19** | infrequent → unknown (21) |
| Rules-only | 701 | 1 | 4 | **5** | **15** | unknown → seizure free (16) |

Select shrinks both leaks (infrequent sentinel 48 → 31; frequent →
unknown 36 → 19) and does not create either. At extract, frequent →
unknown is the single largest cell. After encode and select, infrequent
→ unknown is first again.

The 31 infrequent-sentinel select rows already have extract and encode
in the same sentinel bin (21 `unknown`, 10 `seizure_free`). Gold Purist
is almost all submonthly or monthly.

The 19 frequent → unknown select rows are also already unknown at
extract. Encode matches extract on those 19; select rescues 2 other
encode-unknown frequent rows that are not in this cell. Predicted
labels: 16 bare `unknown`, 3 `unknown, K per cluster`. Gold Purist is
mostly more-than-weekly-less-than-daily (12) or daily (6), plus one
more-than-monthly-less-than-weekly. Gold kind is 10 frequency and 9
unresolved-multiple.

Rules vs select on frequent → unknown is not nested: both wrong on 2
rows, select-only 17, rules-only 13. Rules almost contain the
infrequent-sentinel cell (27 / 31) and do not contain the frequent
unknown cell.

## 2. Qualitative types (`dev750` only)

Not holdout types. Infrequent-sentinel and frequent-unknown share
extract-first collapse to `unknown`. They do not share letter pattern.

### Infrequent → unknown / seizure free (31)

Six letter types cover the 31 rows.

#### Last event, then a seizure-free interval (12)

The letter names a recent event and then a short clean interval
(“last event on 30/Jan … no further episodes in the past month”,
“seizure-free since”, “no recurrence for the past months”). Gold
converts that last-event-plus-interval into a rare rate (`1 per month`,
`1 per 2 month`, `1 per 3 month`, `2 per 2 month`). The model takes the
interval as the answer.

- 10 / 12 become seizure-free labels (`seizure free for 2 week` …
  `seizure free for multiple month`). That is **all** infrequent →
  seizure free errors on this split.
- 2 / 12 become `unknown` on the same template (14965, 14973).

Rules recover the gold rate on 10 / 12. The two rules misses predict
dense monthly rates (`12 per month`, `17 per month`) on the
“seizures earlier this month / absences reduced after restarting
Lamotrigine” variants.

#### Remission, then a dated breakthrough (8)

All predicted `unknown`. The letter pairs a long seizure-free run with
one or a few weekday-dated events: “seizure-free for 6 months, until a
focal impaired-awareness seizure occurred 2 Thursdays ago”; “no
seizures for nearly a year … tonic seizure two Saturdays ago”; “five
month remission, then a drop attack 3 Mondays ago, preceded by
myoclonic jerks”. Gold is events over that remission window (`1 per 6
month`, `1 per year`, `2 per 8 month`, `4 per 6 month`). Find writes
`unknown` (once `unknown, multiple per cluster`). Rules write the gold
rate on all 8.

#### Residual rare events after a named last convulsion (8)

All predicted `unknown`. A dated last tonic-clonic sits next to leftover
jerks or absences: “No further tonic-clonic seizures have occurred since
12/2020, although two to three single jerks remain”; “Last tonic-clonic
seizure was in Apr/2022, with 3 morning jerks since then”. Gold sums
those leftovers over a long window (`2 to 3 per 15 month`, `4 per 13
month`).

Six of eight have an explicit residual count; rules match gold. Two are
unresolved-multiple gold (`multiple per 15 month`, `multiple per 13
month`) with only “from time to time”. Rules also fail those two
(`seizure free for multiple year`).

#### Two calendar-dated isolated events (1)

14524: seizures in May 2017 and November 2017. Gold `2 per 6 month`.
Select `unknown`. Rules correct.

#### Abbreviated monthly phrase (1)

3999: gold reference `abs *monthly` → `1 per month`. Select `unknown`.
Rules correct.

#### Yearly count under remission rhetoric (1)

9002: “only seven brief seizures recorded in 2024 so far” plus language
of durable remission / postoperative freedom. Gold `7 per year`. Select
`unknown`. Rules correct.

### Frequent → unknown (19)

Five letter types cover the 19 rows. Frequent → seizure free (3) is
counted above and not typed here.

#### Cluster two-quantity (9)

Gold is a cluster expression: how often clusters occur and how many
events sit in one cluster. Find writes `unknown`, or keeps only the
in-cluster count (`unknown, 3 per cluster`, `unknown, 4 per cluster`,
`unknown, 2 to 3 per cluster`). Rules recover all 9.

- **This month unclear, last month counted (2).** “Cluster frequency
  unclear this month; last month ≈4 clusters” / “≈three clusters”.
- **Gap then batch (2).** “He may go 3 days without seizures, but when
  they happen he often has them in batches, with four occurring within
  24 hours.”
- **Morning or daytime clustering (3).** Predominantly daytime; more
  frequent morning clusters two or three times in the same morning;
  monthly clusters on awakening.
- **Residual myoclonic clusters after a last convulsion (2).** “Her last
  convulsive seizure was recorded in 03/2022, with occasional clusters
  of myoclonic jerks persisting.” Same leftover-after-last-TC shape as
  the infrequent residual type, but gold is a cluster rate that maps
  frequent.

This is the Gan cluster floor named in
[failures and limits](../paper/failures_and_limits_2026-08-10.md).

#### Electrographic hourly EEG (4)

Gold `multiple per day`. Reference is an EEG rate, not a clinic
count: “Electrographic seizures frequent on EEG (~ten/h)” and the
4/h, 6/h, 9/h variants. Find writes `unknown`. Rules write
`multiple per day`.

#### Vague “several / a couple last month” (3)

Gold unresolved-multiple `multiple per month`. The letter has
approximate month counts: “several focal seizures last month”, “a
couple of seizures last month”, “in the following week, he had several
seizures … No further seizures have occurred since.” Find writes
`unknown`. Rules recover all 3.

#### Single-word gold reference (2)

The only frequent-unknown rows rules also miss. Gold is
`multiple per week` / `multiple per month`; the recorded reference is
the single token `daily` or `yearly`. Select `unknown`. Rules:
`no seizure frequency reference` and `unknown`.

#### Year-window count that still lands frequent (1)

12901: “eight tonic seizures documented in 2016 so far.” Gold `8 per 5
month` (1.6 / month, pragmatic frequent). Same improvement-plus-year-
count shape as infrequent 9002, but the count crosses the frequent
cut. Find `unknown`. Rules correct.

## 3. Is encode normalisation the direct cause?

Asked against row 15267: find selects `e2` (`frequency_rate`, raw
`three single jerks`), encode displays
`no_reference_sentinel` / monthly 1000, select keeps `e2` as
`unknown`. Replay of all **50** dest750 focal rows (31 infrequent →
sentinel + 19 frequent → unknown). `test450` not loaded.

The scored label never changes after the model’s
`selection.final_label`. Encode hops on these 50 rows are only
`gan.model.selection`. Living `gan_rules_encode` /
`llm_select_after_codebook` have `residual_jerk_repair=False`.

**Same mechanism as 15267: 4 / 50 (0.08).** Selected
`frequency_rate` residual-jerk count; that event encodes to
`no_reference` / 1000; scored answer stays `unknown`. Rows 15267
(`three single jerks` → gold `3 per 14 month`), 15094, 15127, 15129.
If `residual_jerk` were on, it would write `3 per 14 month` and
`4 per 15 month` exactly, and `3 per 13 month` / `4 per 13 month`
against golds `4 per 13 month` / `5 per 13 month` (count omits the
named last convulsion).

**Close but not the same: 6 / 50.** Selected a rate or cluster
phrase that encode sentinels or fails to promote: 13114 (myoclonic
jerks, no remain/since-then trigger), 13290 (two seizures on one
past day), 13051 / 13058 (cluster of absences plus last-event),
15519 (in-cluster count only → no_reference), 9815 (qualitative
clustering). On 15529 encode of the selected event already equals
gold (`1 cluster per 3 day, 4 per cluster`) and on 10434 it writes
`1 per week`; the scored label still keeps the model’s
`unknown, K per cluster`. That is unused event encode, not a
collapse of a good scored rate.

**Not normalisation of the selected event: 40 / 50.** The model
already wrote `unknown` or a seizure-free interval as
`final_label`. Ten of those are last-event-plus-interval →
`seizure_free`. Eight more have a *different* ledger event whose
encode already matches gold or the gold pragmatic band (10237,
10245, 5837, 9002, 12901, 4690, 4700, 4709); find selected the
unknown or empty set instead. 15306 / 15317 are the same residual-
jerk letters as 15267, but find typed the jerks
`unknown_frequency`, so encode never sees a rate to convert.

So 15267 is real and local: residual count without a codebook
denominator. It is not the main cause of the two pragmatic cells.

## Attribution

The first component that leaves the gold rate is **find**
(`gan_llm_extract`) on both slices. Codebook encode and living rule
select do not change the 31 + 19 focal labels.

Rules-only already converts dated windows on 27 / 31 infrequent-
sentinel rows and cluster / EEG / vague-month counts on 17 / 19
frequent-unknown rows. The leftover infrequent 4 are two over-counted
monthly restarts and two “from time to time” unresolved-multiples. The
leftover frequent 2 are the single-word `daily` / `yearly` references.

Rules are not a general unknown-avoider on frequent gold: they still
write frequent → unknown on **15** `dev750` rows, 13 of which select
gets right. The LLM frequent-unknown cell is mostly cluster and EEG
find misses. The rules frequent-unknown cell is a different set.

Neither slice is frequent↔infrequent confusion or a select rewrite.
Infrequent collapse is sparse dated evidence → unknown or a seizure-free
span. Frequent collapse is two-quantity cluster / EEG / vague-multiple
evidence → unknown.

## Claim boundary

- `test450`: aggregate description of the published matrix. Not a
  row-level holdout claim.
- `dev750`: development answer for infrequent-sentinel types,
  frequent-unknown types, and extract-first attribution.
- Not a new cited score. Not a warrant to retune from holdout.

## Candidate: `last_event_well_since`

Gated select rewrite, default on for living `llm_select` /
`llm_select_after_codebook`. Off on encode-only modes. Protocol:
[last-event well-since](gan_last_event_well_since_protocol_2026-08-29.md).

On `dev750` Gemini extract replay, select moves **649 / 665 → 656 /
673** Purist / Pragmatic. Seven of the ten infrequent → no-seizure
numeric short-SF rows become a rate. The three `multiple month`
letters stay. The twelve already-correct short numeric SF rows stay
pragmatic-correct.

`test450` after promotion (same extract replay; no row inspection):
**387 / 396** cited. Infrequent → no-seizure **13 → 1**; infrequent
correct **49 → 61**. Infrequent → unknown stays 16.

## Next

Do not inspect `test450` rows. Frequent collapse (cluster two-quantity
/ electrographic EEG) is still a find problem. The leftover infrequent
misses after this family are the three `multiple month` well-since
letters plus unknown-at-extract rows.
