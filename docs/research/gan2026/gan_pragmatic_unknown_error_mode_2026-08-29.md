# Pragmatic gold → unknown error modes

Date: 2026-08-29
Status: development answer for seizure-free → unknown types;
holdout counts only
Protocol:
[protocol](gan_pragmatic_unknown_error_mode_protocol_2026-08-29.md)
Artifact:
[gan_pragmatic_unknown_error_mode_2026-08-29.json](gan_pragmatic_unknown_error_mode_2026-08-29.json)
Prior types:
[rate → unknown / no-seizure](gan_pragmatic_infrequent_error_mode_2026-08-29.md)

Living Gemini cell 3 after `last_event_well_since`. Replay of saved
extract raws; zero model calls. `data_text_policy:
synthetic_development_raw_text_diagnostic` for the `dev750` quotes
below. `test450` is gold-and-predicted ε only. No holdout row ids or
letter text.

## Answer

Yes. After well-since removed almost all infrequent → seizure-free
errors, the remaining pragmatic mass is gold → unknown.

On living cell-3 select, gold → unknown is **37 / 54 = 0.69** of
`test450` errors (16 infrequent + 13 frequent + 8 seizure-free) and
**46 / 77 = 0.60** of `dev750` errors (21 + 19 + 6). Infrequent →
unknown and frequent → unknown keep the prior-study membership and
types. Seizure-free → unknown is smaller and a different letter
problem: gold codes qualitative freedom (including non-epileptic
current spells) as `seizure free for multiple month`; find writes
`unknown` or `no seizure frequency reference`.

All six `dev750` seizure-free → unknown select rows are already
wrong at extract. Rules recover **6 / 6**. Codebook encode of a
found `seizure_free` event is `no_reference` on **4 / 6**, so
picking that event would still score Unknown.

## Protocol in one line

- Dataset / split: Gan 2026 `gan2026_split_v1`. `test450` aggregate
  only; `dev750` row review permitted.
- Candidate: Gemini 3.7 Flash living cell 3 select
  (`last_event_well_since` on).
- Comparators: extract, encode, rules-only on `dev750`.
- Scorer: living `map_pragmatic`.
- Replay: saved labels; zero model calls.

Name note: gold-kind `no_reference` and `unknown` both map to
pragmatic **Unknown** (`monthly_frequency` 1000). Pragmatic
**Seizure free** is `currently_no_seizure` (`monthly_frequency` 0).

## 1. Quantitative

Living stack. The prior report’s `test450` 383 / `dev750` 665
matrices are the pre–well-since snapshot. Infrequent → unknown and
frequent → unknown counts did not move.

### `test450` living cell-3 select (n=450)

Source: no-text replay of saved extract raws through living
`llm_select_after_codebook`. Cited Purist / Pragmatic **387 / 396**.

| True \\ Pred | Frequent | Infrequent | Unknown | Seizure free | Support | Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frequent | 211 | 3 | 13 | 0 | 227 | 0.93 |
| Infrequent | 2 | 61 | **16** | **1** | 80 | 0.76 |
| Unknown | 4 | 3 | 67 | 2 | 76 | 0.88 |
| Seizure free | 1 | 1 | **8** | 57 | 67 | 0.85 |

- All pragmatic errors: **54** (was 67).
- Gold → unknown: **37 / 54 = 0.69**.
- Ranked off-diagonals: 16 infrequent→unknown, 13 frequent→unknown,
  8 seizure-free→unknown. Infrequent → seizure free is now 1.

### `dev750` living cell-3 select (n=750)

Select pragmatic **673 / 750 = 0.897**.

| True \\ Pred | Frequent | Infrequent | Unknown | Seizure free | Support | Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frequent | 364 | 2 | 19 | 2 | 387 | 0.941 |
| Infrequent | 5 | 95 | **21** | 3 | 124 | 0.766 |
| Unknown | 6 | 8 | 109 | 4 | 127 | 0.858 |
| Seizure free | 1 | 0 | **6** | 105 | 112 | 0.938 |

- All pragmatic errors: **77** (was 85).
- Gold → unknown: **46 / 77 = 0.60**.
- Same ranking as holdout: 21, then 19, then 6.
- Infrequent → unknown row ids and frequent → unknown row ids match
  the prior artifact exactly.

### Same `dev750` rows at earlier stops

| Stop | Pragmatic correct | Freq → unk | Infreq → unk | SF → unk | Gold → unk |
| --- | ---: | ---: | ---: | ---: | ---: |
| Extract | 613 | 36 | 33 | 7 | 76 |
| Encode | 632 | 21 | 31 | 7 | 59 |
| Select | 673 | **19** | **21** | **6** | **46** |
| Rules-only | 701 | 15 | 1 | **0** | 16 |

Select shrinks the two rate leaks and rescues one extract
seizure-free → unknown row (13889 → `seizure free for multiple
year`). It does not create the six remaining seizure-free → unknown
rows. Rules have zero seizure-free → unknown; their leftover
unknown leak is almost all frequent (15).

## 2. Seizure-free → unknown types (`dev750` only)

Not holdout types. Gold on all six is `seizure free for multiple
month`. Predicted labels: 4 `unknown`, 2 `no seizure frequency
reference`. Three letter types.

### Controlled epilepsy plus occasional aura or warning (3)

8144, 8400, 9250. The letter states durable control (“sustained
spell without clinical events”, “durable seizure control … no
convulsive events”, “essentially no clear-cut events to suggest
recent seizures”) and also names non-progressive warnings:
occasional déjà vu; occasional brief warning episodes; sleep-
deprivation clusters of usual warning features that “have not
progressed to definite events”.

Gold takes the quiet interval. Find writes a `seizure_free` event
and an `unknown_frequency` event, then scores `unknown` from the
warning. Encode of the unused `seizure_free` event is
`no_reference` on all three. Rules write `seizure free for multiple
year`.

### Current spells judged non-epileptic (2)

13843, 13858. The letter describes ongoing behavioural or sensory
spells and then judges them non-epileptic (“events at present are
considered non-epileptic”; “Seizure-like episodes are currently
non-epileptic”). Gold is seizure-free. Find writes `no_reference`
or `unknown` on the spell description and never emits a
`seizure_free` event. Rules match gold (`seizure free for multiple
month`).

### No epilepsy, no clinical seizures (1)

5092. Work-up concludes “No epilepsy.” The family report “No
clinical seizures observed since the initial referral.” Find
selects that span as `seizure_free` but already writes `no seizure
frequency reference` as `final_label`. Codebook encode of the
selected event is also `no_reference`. Rules write `seizure free
for multiple year`.

## 3. Prior rate → unknown types (unchanged)

Infrequent → unknown (21) and frequent → unknown (19) are the same
rows as the prior report. Short restatement only:

- Infrequent: sparse dated rates (remission then breakthrough;
  residual events after a last convulsion; last-event-plus-interval
  that already went to unknown rather than seizure-free).
- Frequent: cluster two-quantity, electrographic hourly EEG, vague
  “several / a couple last month”, plus two single-word gold
  references and one year-window count.

They share extract-first collapse to unknown with the seizure-free
slice. They do not share letter pattern. Seizure-free → unknown is
a gold-boundary / qualitative-freedom problem, not a missed numeric
rate.

## Attribution

On the six seizure-free → unknown rows, the first component that
leaves the gold band is **find** (`gan_llm_extract`). Living encode
and select keep the extract label.

Find does two different things inside the slice:

- **Wrong competitor (3):** a usable quiet-interval event is in the
  ledger; the scored answer is the aura / warning.
- **No seizure-free event, or a seizure-free event that cannot
  score (3):** non-epileptic spells typed `no_reference` /
  `unknown`, or a selected `seizure_free` span already labelled
  `no_reference`.

Codebook encode is not the scored cause (the model already wrote
unknown), but it is not a latent rescue either: qualitative
freedom phrases encode to `no_reference` on 5092, 8144, 8400, and
9250. That is the same unused-event / sentinel pattern as the
prior residual-jerk rows, for seizure-free grammar rather than a
count without a denominator.

Rules-only already writes a seizure-free label on all six. Rules
are not a general unknown-avoider: they still have 15 frequent →
unknown of their own.

`last_event_well_since` does not apply. The gate needs a numeric
short seizure-free label; these rows are already unknown.

## Claim boundary

- `test450`: aggregate description of the living matrix. Not a
  row-level holdout claim.
- `dev750`: development answer for seizure-free → unknown types
  and extract-first attribution.
- Infrequent / frequent unknown types remain owned by the prior
  report.
- Not a new cited score. Not a warrant to retune from holdout.

## Decision

Do not add a select-family for this slice. The six rows are
extract-first, and four of them would still score Unknown if
select kept the `seizure_free` event. A codebook encode of
qualitative freedom, or a find rule for non-epileptic current
spells, would be a different study.

## Next

Do not inspect `test450` rows. The largest remaining unknown
cells are still infrequent and frequent find misses (dated sparse
rates; cluster / EEG). Seizure-free → unknown is typed and
rules-contained on `dev750`.
