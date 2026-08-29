# Where Gemini cell 3 select gains come from on Gan `dev750`

Date: 2026-08-29
Status: development answer
Protocol:
[encode→select protocol](gan_gemini_cell3_encode_to_select_dev750_protocol_2026-08-29.md)
Artifact:
[`gan_gemini_cell3_encode_to_select_dev750_changed_rows_2026-08-29.jsonl`](gan_gemini_cell3_encode_to_select_dev750_changed_rows_2026-08-29.jsonl)
Owners: [five-cell grid](../gan2026/gan_five_cell_grid_2026-08-22.md),
[rules and models across stages](gan_rules_and_llms_across_stages_2026-08-21.md)

This is a no-call replay of the living Gemini 3.7 Flash cell 3 stack on
Gan `dev750`: `gan_llm_extract` → `gan_rules_encode` →
`llm_select_after_codebook`. The cited cell-3 score is the select stop.
`test450` was not loaded.

## Answer

Select is a small, high-precision rewrite of the same ledger. It
changes **67 / 750** submitted labels and raises Purist from
**608 / 750 (0.8107)** to **649 / 750 (0.8653)**. That **+41** is
**45** wrong-to-correct minus **4** correct-to-wrong. Changed-label
Purist precision is **45 / 67 = 0.67**.

The increment is not a new reading of the letter and not an
event-switch. Selected event ids never change. The first family that
moves the label accounts for every changed row. Three families do
almost all of the helpful work:

| First select family | Changed | Purist W2C | Purist C2W | Net |
| --- | ---: | ---: | ---: | ---: |
| `monthly_diary` | 47 | 27 | 2 | +25 |
| `dated_sequence` | 10 | 10 | 0 | +10 |
| `post_change_burst` | 7 | 7 | 0 | +7 |
| `non_epileptic` | 1 | 1 | 0 | +1 |
| `breakthrough` | 2 | 0 | 2 | −2 |
| **All changed** | **67** | **45** | **4** | **+41** |

`usual_interval` and `typical_over_ytd` are enabled and recorded in
hops. They are never the first family that changes the encode label on
this split.

The common helpful change is: encode kept a last-month rate, a
seizure-free interval after a counted burst, or `unknown` over dated
events; select rewrites that into the gold’s counted window. The
common harmful change is: select invents or shortens a window when
encode had already kept the gold’s conservative object.

## Protocol in one line

- Dataset / split: Gan 2026 `dev750` (`gan2026_split_v1` / machine
  `validation`). Development inspection permitted.
- Comparator: encode stop (`gan_rules_encode`).
- Candidate: select stop (`llm_select_after_codebook`).
- Scorer: Purist category accuracy; Pragmatic and exact label secondary.
- Replay: saved Gemini extract raw; zero model calls.
- Attribution: first `gan.select.*` hop whose `after` is the select
  label. Hop start matched the encode label on all 67 rows.

## 1. Quantitative ladder

| Stop | Purist | Pragmatic | Predicted kinds (freq / SF / unknown / unresolved / none) |
| --- | ---: | ---: | --- |
| Encode | 608 / 750 | 632 / 750 | 411 / 135 / 149 / 34 / 21 |
| Select | 649 / 750 | 665 / 750 | 437 / 124 / 134 / 34 / 21 |
| Delta | **+41** | **+33** | +26 frequency; −11 SF; −15 unknown |

Unchanged labels: **683**. On the 67 changes:

| Direction | Purist | Pragmatic | Exact label |
| --- | ---: | ---: | ---: |
| Wrong → correct | 45 | 37 | 41 |
| Correct → wrong | 4 | 4 | 9 |
| Correct stay (label moves, score stays) | 13 | 25 | 0 |
| Wrong stay | 5 | 1 | 17 |

Of the 45 Purist rescues, **34** also become exact gold. Eleven land
in the right Purist band with a nearby count or window. Of the 13
Purist-correct stays, seven become exact gold and five leave an
already-exact encode label for a same-band restatement.

Encode already matched extract on **64 / 67** changed rows. The three
exceptions are codebook-encode rescues that select later restates
inside the same Purist band (rows `13732`, `16220`, `16324`). Select’s
increment is therefore semantic current-state policy, not codebook
dialect.

Kind moves on the 67 rows:

| Encode → select kind | n | Purist W2C | Purist C2W |
| --- | ---: | ---: | ---: |
| frequency → frequency | 40 | 22 | 2 |
| unknown → frequency | 14 | 10 | 2 |
| seizure_free → frequency | 12 | 12 | 0 |
| unknown → seizure_free | 1 | 1 | 0 |

Gold on changed rows is almost all frequency (64). The two unknown
golds are the `breakthrough` regressions. The one seizure-free gold is
the `non_epileptic` rescue.

## 2. Groups: what select actually does

### A. Monthly diary window (47 rows; net +25)

This is the select increment. Encode often writes the last populated
month (`1 per month`, `6 per month`). Select sums the dated month
counts already sitting on the ledger into `N per M month`.

**Helpful subtype — last-month recency (21 of 27 diary W2C).** The
ledger already lists several months. Encode takes the newest month as
the current rate. Select keeps the same events and writes the counted
span. Row `15964`: encode `6 per month` (May: 3 sleep + 3 wake); select
`11 per 3 month` (March 5 + May 6), matching gold. Row `9449`: encode
`2 per month` from `Oct x2`; select `4 per 6 month` from
`May x0 … Oct x2`.

**Helpful subtype — unknown or seizure-free over a diary (6 of 27).**
Encode refuses to collapse a scattered month list. Select does.
Row `16714`: encode `unknown`; select `5 per 6 month`. Row `16750`:
encode `seizure free for multiple week`; select `6 per 7 month`.

**Same-band restatement (13).** Some of these are exact-label wins
(`4410`: `1 per 2 to 3 month` → `4 per 7 month`). Others leave gold
for a shorter recent window that still shares a Purist band
(`13732`: exact `52 per 8 month` → `16 per 3 month`; `4345`:
`4 per month` → `4 per 1 month`).

**Harmful subtype — wrong window (2 C2W + 5 wrong-stay).** Select
counts a subset of the months gold uses. Row `12979`: gold and encode
`3 per 4 month` (year-to-date at an April clinic); select
`3 per 2 month`. Row `16203`: gold and encode `9 per 3 month`
(July 3 + August 5 + September 1); select `8 per 2 month`, dropping
the incomplete current month. The five wrong-stays move toward a
counted window but miss a month or a day-count (`16195`:
`6 per month` → `10 per 3 month` vs gold `16 per 4 month`;
`13627`: `1 per month` → `20 per 9 month` vs gold `64 per 12 month`).

### B. Dated lifetime sequence (10 rows; net +10; no harms)

Encode sees two or three dated first-events and writes `unknown` (5)
or the quiet interval since the last date (4), or a last-month rate
(1). Gold wants the count over the dated span. Select writes that
span exactly on all ten rows.

Row `14530`: two nocturnal events in March 2019 and May 2019; encode
`unknown`; select `2 per 2 month`. Row `14562`: three events from
January to July 2021 plus “no further events”; encode
`seizure free for 1 month`; select `3 per 6 month`. Row `14662`:
encode `2 per month` from the last cluster month; select
`3 per 4 month`.

This is current-state policy, not missing evidence. The dates were
already extracted.

### C. Post-change burst (7 rows; net +7; no harms)

A drug stop or similar change is followed by a short burst, then a
quiet interval to clinic. Encode keeps the quiet interval. Gold keeps
the burst as `N per window`. Select overwrites every seizure-free
encode label with the burst rate.

Row `14187`: valproate stopped 10 July, then 2–3 seizures, then quiet
to 10 August; encode `seizure free for a duration`; select
`2 to 3 per 1 month`. Row `14317`: lamotrigine stopped 4 April, four
seizures, then quiet to 5 June; encode `seizure free for 2 month`;
select `4 per 2 month`.

All seven are seizure_free → frequency. That is the entire
seizure-free-to-frequency lift except the one diary row `16750`.

### D. Non-epileptic current episodes (1 row; +1)

Row `13889`: gold `seizure free for multiple month`. Encode
`unknown` over “currently non-epileptic … less troublesome.” Select
writes the family’s fixed form `seizure free for multiple year`.
Purist matches; exact label does not. The family does not read the
true quiet duration.

### E. Breakthrough invention (2 rows; −2)

These are the only first-family harms that are not diary-window
errors. `breakthrough` fires only on encode `unknown`. It pairs a
seizure-free duration with an inferred recent count and writes
`count per duration`.

Row `2166`: gold `unknown` because current petit mal is “frequent”
and uncounted. The ledger also has GTC-free “for over a year.” Encode
keeps `unknown`. Select writes `1 per 1 year`.

Row `12963`: gold `unknown` (“small handful” this year; longer gaps,
including the last 10 weeks). Encode keeps `unknown`. Select writes
`1 per 10 week`.

Both invent a countable rate the gold refused.

## 3. Representative letters

Evidence spans below are already on the saved extract. Letters are
synthetic development notes. They illustrate mechanism, not holdout.

### Helpful: last month is not the current object

**Row `15964`.** Gold `11 per 3 month`. Extract/encode take May alone
(`3 in sleep and 3 while awake`) as `6 per month`. March (`3` sleep +
`2` wake) is already event `e1`. `monthly_diary` writes
`11 per 3 month`. Same selected ids. The gain is denominator choice.

**Row `9449`.** Gold `4 per 6 month` from `May x0 … Oct x2`. Encode
`2 per month` from October. Select sums the six-month log.

This pattern is the modal rescue: **21** diary W2C rows are last-month
rates rewritten to a multi-month count.

### Helpful: dated events are a rate, not a quiet interval

**Row `14530`.** Two dated first events, March and May 2019. Extract
rationale: no “ongoing baseline,” so `unknown`. Gold is the two-event
span. `dated_sequence` writes `2 per 2 month`.

**Row `14540`.** Same template plus “since commencing levetiracetam he
has not had further events.” Encode `seizure free for a vague
duration`. Select `2 per 8 month`. The quiet clause is true and not
the submitted object.

### Helpful: the burst after a change is the submitted object

**Row `14187`.** The letter states both the 2–3 seizures after
stopping valproate and “remained seizure-free since then.” Encode
believes the second sentence. Gold and `post_change_burst` keep the
burst as `2 to 3 per 1 month`.

This is the cleanest encode/select disagreement: two true facts, one
allowed label.

### Harmful: inventing a rate from a quiet interval

**Row `2166`.** Current absence is “frequent” and unquantified; GTCs
are absent for over a year. Gold and encode `unknown`. `breakthrough`
writes `1 per 1 year` from the GTC-free duration. That is a false
resolution, not a diary sum.

**Row `12963`.** “Small handful” this year plus longer gaps. Gold
refuses a rate. Select writes `1 per 10 week` from the recent quiet
clause.

### Harmful: counting the wrong months

**Row `16203`.** The diary is complete in the selected evidence:
September 1, August 5, July 3. Encode already has gold
`9 per 3 month`. Select drops September-to-date and submits
`8 per 2 month`.

**Row `12979`.** “Three … this year to date” at a 24 April clinic,
with January 2 and March 1 named. Encode `3 per 4 month`. Select
`3 per 2 month`. The events are right; the year-to-date window is
shortened.

**Row `16195`** (wrong-stay). June 3 + July 5 + August 2 + “6 so far
this month” (September clinic) is gold `16 per 4 month`. Encode takes
the current month (`6 per month`). Select takes three months
(`10 per 3 month`) and still misses June.

## 4. Attribution

Select here is recorded rules after codebook encode. It is not LLM
select (cell 5) and not a new model call.

| Decision | Owner |
| --- | --- |
| Which events exist | Gemini find (`gan_llm_extract`) |
| Codebook form of the find pick | `gan_rules_encode` (already correct on 64/67 changed rows) |
| Which fact is current | First fired select family |
| Event switch | None (0 selected-id changes) |
| Score projection | Purist band; 13 label moves stay correct |

Do not credit the model for the +41. The model already collected the
month counts, dated events, and burst-plus-quiet pairs. Select chooses
the gold’s current-state convention.

Do not call the four regressions “format.” All four change clinical
window or invent a rate.

## 5. Claim boundary

Development answer on Gemini cell 3 `dev750`. It explains the living
select-stop increment on this split. It does not support:

- a holdout letter attribution or a new `test450` number;
- an LLM-select or LLM-first claim;
- a claim that diary select is safe in general (`breakthrough` and
  short-window diary still harm).

The helpful mechanisms are transferable as hypotheses: last-month
versus diary span, dated-event span versus post-event quiet, burst
versus post-burst freedom. The two `breakthrough` harms are the clearest anti-overfit warning on
this surface.

## Decision and next

Keep living cell 3 as codebook encode plus these select families. The
select stop is the right cited stop because encode still submits the
wrong current fact on 45 later-rescued rows.

If a later repair is wanted, inspect `breakthrough` on encode
`unknown` before touching diary. Do not retune from these 67 rows
into holdout. Do not inspect `test450`.
