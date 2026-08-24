# Dataset gold support and methods-section summaries

Date: 2026-08-22
Status: development inventory; holdout aggregates only
Owners: [methods](../../paper/methods.md),
[score definitions](score_definitions_2026-08-17.md),
[what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md)
Artifact: [dataset_gold_support_2026-08-22.json](dataset_gold_support_2026-08-22.json)
Pin: `gold_headline_support()`;
`tests/test_exectv2_scoring_headlines.py::test_four_family_gold_support_matches_headline_f1_denominator`

## Question

What is the scored gold mass on each public split, and which other
dataset facts should Methods state so a reader can interpret F1,
accuracy, and stage volume?

## Protocol

| Item | Value |
| --- | --- |
| Data | ExECT `dev140` / `test60`; Gan `dev750` / `test450` |
| Scorer | ExECT 4-family micro F1 (`clinical_inventory_unit_keys`) for all five cited rows. Headline `clinical_headline_unit_keys` is the historical Compact Diagnosis-collapse ablation. Gan one Purist-mapped label |
| Inspection | Development rows permitted. `test60` and `test450` aggregate-only |
| Predictions | None. Gold inventory only |
| Volume metric | Added on paper stage summaries; not a gold fact |

No new model calls. Locked letters were not listed or read.

## Answer

ExECT four-family F1 is a **unit inventory**, not a letter score. The
cited inventory recall denominator is **836** units on `dev140` and
**349** on `test60` (59 letters). The Compact/headline collapse is
**796** / **328**. Gan accuracy is **one label per letter**:
**750** and **450**. Those denominators are not interchangeable.

Predicted volume is now recorded separately from those golds: ExECT
`predicted_mention_count` and Gan `predicted_candidate_count` at
extract, encode, and select. That is a pipeline inventory, not a
second gold.

## ExECT gold (4-family micro F1 denominator)

Headline units in the table below are the **Compact/headline collapse**
(796 / 328). The **cited inventory** recall denominator is **836** /
**349** (`clinical_inventory_unit_keys`). Diagnosis and SeizureFrequency
are de-duplicated inside a letter under Compact scoring only; the
inventory scorer does not collapse Diagnosis. Prescription and
Investigations keep one unit per occurrence after key filtering. Raw
mention counts are larger where the headline collapses repeats.

| Split | Letters | Diagnosis | SeizureFrequency | Prescription | Investigations | Compact/headline gold | Raw four-family mentions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `dev140` | 140 | 289 | 165 | 206 | 136 | **796** | 934 |
| `test60` | 59 | 122 | 74 | 85 | 47 | **328** | 375 |

Diagnosis carries most of the collapse (`405→289` development,
`166→122` holdout). SeizureFrequency collapses a little
(`187→165`, `76→74`). Prescription and Investigations are almost
one-to-one.

Empty gold in a family means **not annotated under the guideline**,
not “clinically false.” Occupancy:

| Split | Dx empty | SF empty | Rx empty | Inv empty | Letters with zero four-family units |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dev140` | 10 | 41 | 27 | 62 | 3 |
| `test60` | 1 | 16 | 7 | 29 | 0 |

A typical development letter has a median of **3** occupied families
and **6** headline units (range 0–12). Holdout letters have a median
of **5** units (range 1–12). Investigations is the family most often
absent.

## Gan gold (Purist accuracy denominator)

Each letter contributes one current-frequency label. Paper cells score
the full split, including `row_ok=False` rows (32 / 750 development,
20 / 450 holdout). Those flags stay available for separate analysis;
they are not a second denominator in the cited totals.

| Split | n | Frequency | Seizure-free | Unknown | Unresolved multiple | No reference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `dev750` | 750 | 468 | 112 | 100 | 43 | 27 |
| `test450` | 450 | 281 | 67 | 60 | 26 | 16 |

Purist unknown (`127` / `76`) equals gold-kind `unknown` plus
`no_reference`. Seizure-free kind matches the `currently_no_seizure`
band (`112` / `67`). The remaining letters are numeric rates, plus
43 / 26 unresolved-multiple labels that still map to a Purist band.

The largest numeric Purist band on both splits is
**more than weekly and less than daily** (196 / 123). Rare exact
anchors are 1/year, 1/6 months, and 1/week. Pragmatic collapses the
numeric remainder into frequent (387 / 227) versus infrequent
(124 / 80).

## Stage volume (instrumentation, not gold)

Paper summaries now carry:

- ExECT: `predicted_mention_count` at extract / encode / select
- Gan: `predicted_candidate_count` at those same stops

Rung replay also writes `gold_count` and `pred_count` next to F1.
Sealed five-cell `comparison.json` files do not yet include the new
fields; they appear on the next no-call replay or later-stage
rescore.

Volume answers “how large was the ledger at this stop?” It does not
replace Purist accuracy or 4-family micro F1.

## Hidden-family and slice notes

- ExECT F1 can move when a family with a large gold mass (Diagnosis)
  changes, even if letter-exact rates look stable.
- An empty family is a precision risk if the system invents and a
  recall risk only when gold is non-empty.
- Gan sentinels (`unknown`, no-reference, seizure-free) are a large
  minority. A methods sentence that only says “750 frequency labels”
  would hide that mix.
- Unresolved-multiple gold (43 / 26) is a selection problem: more
  than one countable statement, one submitted label.
- Three development letters have no four-family headline units. They
  sit in the letter count and not in the F1 denominator.

Holdout rows were not inspected. No letter identifiers are reported
for `test60` or `test450`.

## Claim boundary

**Development inventory** of gold mass and occupancy, plus
**aggregate-only** holdout gold mass. Not predicted performance, not
holdout generalization, and not a claim that gold is the task.

The volume fields are **engineering**: they make ledger size
replayable. They are not a clinical-quality metric.

## Decision

Methods should state the scored unit and its split counts, not only
letter n. For ExECT the cited inventory denominator is 836 / 349
four-family units; Compact/headline collapse is 796 / 328. For Gan
that is 750 / 450 labels, with the sentinel and band mix named.

## What Methods should include

The current methods table already names splits and primary scores.
The useful additions are the facts that change how a reader reads
those scores. Ranked for a short Methods paragraph, then a
supplement if space allows.

### Include in the main Methods paragraph

1. **Scored unit and denominator.** ExECT cited inventory: four-family
   units without Diagnosis collapse (836 / 349); Compact/headline
   collapse (796 / 328) is a historical ablation view. Gan: one
   Purist-mapped current label (750 / 450). Letter n is not the ExECT
   F1 denominator.
2. **`test60` is 59 letters.** The split name is historical. The
   locked loadable set is 59.
3. **Golds are evaluation forms.** One current state versus a
   complete inventory. Empty ExECT family means unannotated, not
   false. Already owned by
   [what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md);
   the new counts make that sentence quantitative.
4. **Family gold mass.** Diagnosis is the largest ExECT family;
   Investigations is the smallest and the most often empty. That is
   why a Diagnosis encode change can move 4-family micro F1 more than an
   Investigations change of the same letter count.
5. **Gan label mix.** Numeric frequency is the majority, but
   seizure-free, unknown, no-reference, and unresolved-multiple are
   large enough that accuracy is not “rate extraction only.”
6. **Purist versus Pragmatic occupancy.** Name that Purist is a
   fine band map with a dominant weekly-to-daily bin and two
   sentinels, and that Pragmatic is frequent / infrequent plus those
   sentinels. A 0.01 Purist move is not a 0.01 Pragmatic move.

### Useful in Methods or a short supplement table

7. **Raw mentions versus Compact/headline units.** 934→796 and
   375→328. Shows that the historical Compact score collapses
   Diagnosis and SeizureFrequency repeats. Predicted mention counts
   will often exceed `pred_count`.
8. **Facts per letter.** Median 6 / 5 Compact/headline units, max 12.
   The inventory task is dense relative to letter count.
9. **Letter length.** ExECT median ~1.2k characters; Gan median
   ~2.7k. Same architecture, different context size and temporal
   density. Do not treat them as matched corpora.
10. **`row_ok=False` count.** 32 / 20 letters remain in the cited
    Gan n. Methods should say whether they stay in the denominator
    (they do, today).
11. **Stage volume as a reported secondary.** Once five-cell
    replays write `predicted_mention_count` /
    `predicted_candidate_count`, a Methods sentence can say that
    extract / encode / select ledger size is recorded so a score
    change can be read as grow, shrink, or rewrite.

### Keep out of Methods, or keep diagnostic-only

- Holdout row examples, failure lists, or per-letter keys.
- Predicted mention or candidate totals from a single unfinished
  cell, presented as dataset facts.
- Published ExECT phrase / CUI / all-features macros as if they
  were the paper headline. They remain a separate view.
- Train-300 Gan rows. They are not a paper development surface.
- Synthetic-letter provenance colour as if it were a score slice,
  unless a predeclared figure uses it.

## Attribution

The gold counts come from `gold_headline_support()` (Compact/headline
796 / 328) and Gan split records. Cited inventory denominators are
836 / 349. Compact/headline `gold_count` fields on disk remain
796 / 328. The volume metric is new paper instrumentation.

## Next

1. On the next no-call five-cell or rung replay, persist extract /
   encode / select volume on the comparison artifacts.
2. When drafting Methods, add the denominator table and the Gan
   kind / sentinel sentence. Do not wait for predicted volumes.
3. Optional later: a one-page supplement with family occupancy,
   Purist band counts, and letter-length medians.

Do not inspect `test60` or `test450` rows to enlarge this inventory.
