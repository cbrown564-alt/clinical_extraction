# Dataset description

Date: 2026-08-26
Revised: 2026-08-27 (split-stratum percentages)
Status: development inventory; holdout aggregates only
Owners: [dataset gold support](dataset_gold_support_2026-08-22.md),
[what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md),
[score definitions](score_definitions_2026-08-17.md)
Artifact: [dataset_description_2026-08-26.json](dataset_description_2026-08-26.json)

## Question

What should a Methods dataset table state so a reader can see that
the two corpora are different sizes, different lengths, and different
evaluation forms?

## Protocol

| Item | Value |
| --- | --- |
| Data | ExECT public 200, paper `dev140` / `test60`; Gan public 1,500, paper `dev750` / `test450` |
| Letter length | Whitespace-split word counts on official cleaned `note_text` |
| ExECT gold | Cited 4-family inventory units (`clinical_inventory_unit_keys`) |
| Gan gold | One Purist-mapped current-frequency label per letter |
| Splits | Frozen manifests. ExECT `exectv2_split_v2` stratified on `has_seizure_frequency_mention`. Gan `gan2026_split_v1` stratified on `gold_label_kind` × `row_ok` |
| Inspection | Development rows permitted. `test60` and `test450` aggregate-only |
| Predictions | None |

No new model calls. Locked letters were not listed or read. Gan
`train300` is on disk and is not a paper development surface.

## What belongs in this table

A Methods dataset table should answer four questions: how many
letters, how long they are, how dense the gold is, and what kind of
gold it is. The useful extras beyond letter n and mean words are the
ones that stop a reader from treating the two tasks as matched
corpora:

- **Paper n versus public n.** ExECT scores 199 of 200 letters
  (`test60` is 59). Gan scores 1,200 of 1,500.
- **Gold units, not only letters.** ExECT F1 is an inventory
  denominator (836 / 349). Gan accuracy is one label per letter
  (750 / 450).
- **Density.** A typical ExECT letter has about six inventory facts
  and three of four families. Gan always submits one current state.
- **Sentinel mix on Gan.** About 38% of paper labels are not a single
  numeric rate (seizure-free, unknown, no-reference, or unresolved
  multiple). `row_ok=False` letters stay in the cited n (32 / 20).
- **Split mix.** Both paper splits are stratified. ExECT keeps the
  seizure-frequency-present / absent cut near 71% / 29%. Gan keeps
  each label kind and the `row_ok=False` share aligned across
  `dev750` and `test450`.

Leave family occupancy, Compact collapse, and Purist band counts in
[dataset gold support](dataset_gold_support_2026-08-22.md). Do not put
predicted ledger volume, holdout examples, or train-300 rows here.

## Letter corpus

Word counts are whitespace-split. Character medians match the earlier
gold-support inventory.

| Statistic | ExECT `dev140` | ExECT `test60` | ExECT total | Gan `dev750` | Gan `test450` | Gan total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Letters | 140 | 59 | **199** | 750 | 450 | **1,200** |
| Mean words | 215.9 | 218.2 | 216.6 | 397.6 | 401.8 | 399.2 |
| Median words | 198.5 | 202 | 200 | 391.5 | 395 | 393 |
| Word range | 49–693 | 96–552 | 49–693 | 115–756 | 146–740 | 115–756 |
| Median characters | 1,180.5 | 1,190 | 1,185 | 2,681.5 | 2,715.5 | 2,689.5 |

Totals are the paper unions (`dev140`+`test60`, `dev750`+`test450`).
Public corpora: ExECT **200** letters (mean **216.4** words); Gan
**1,500** letters (mean **400.2** words). One ExECT public letter sits
outside both paper splits. Gan notes are about 1.8× longer. Split
means sit close to the corpus means.

## Split composition

ExECT `exectv2_split_v2` (seed 20260610) stratifies on whether the
letter has any SeizureFrequency gold mention. That count uses gold
JSON only. Gan `gan2026_split_v1` (seed 20260531) stratifies on
`gold_label_kind` × `row_ok`. Kind counts below reuse the locked
manifest `strata_counts`. Locked letters were not listed or read.

**ExECT** — `has_seizure_frequency_mention`

| Split | n | Has SF | No SF |
| --- | ---: | ---: | ---: |
| Public 200 | 200 | 142 (71.0%) | 58 (29.0%) |
| `dev140` | 140 | 99 (70.7%) | 41 (29.3%) |
| `test60` (59) | 59 | 43 (72.9%) | 16 (27.1%) |
| Paper 199 | 199 | 142 (71.4%) | 57 (28.6%) |

The public letter outside both paper splits is EA0159 (no SF gold).
That is why public “no SF” is 58 and the paper union is 57. The
59-letter holdout sits 1.9 points above the public SF-present share.

**Gan** — `gold_label_kind`

| Kind | `dev750` | `test450` | Paper 1,200 | Public 1,500 |
| --- | ---: | ---: | ---: | ---: |
| frequency | 468 (62.4%) | 281 (62.4%) | 749 (62.4%) | 937 (62.5%) |
| seizure_free | 112 (14.9%) | 67 (14.9%) | 179 (14.9%) | 223 (14.9%) |
| unknown | 100 (13.3%) | 60 (13.3%) | 160 (13.3%) | 200 (13.3%) |
| unresolved_multiple | 43 (5.7%) | 26 (5.8%) | 69 (5.8%) | 86 (5.7%) |
| no_reference | 27 (3.6%) | 16 (3.6%) | 43 (3.6%) | 54 (3.6%) |

**Gan** — `row_ok`

| Split | `row_ok=true` | `row_ok=false` |
| --- | ---: | ---: |
| `dev750` | 718 (95.7%) | 32 (4.3%) |
| `test450` | 430 (95.6%) | 20 (4.4%) |
| Paper 1,200 | 1,148 (95.7%) | 52 (4.3%) |

Almost all `row_ok=false` mass is `no_reference`, plus a few
frequency and seizure-free rows. `unknown` and `unresolved_multiple`
are all `row_ok=true` in this split. `train300` is on disk and is
omitted here.

## Gold units

| Statistic | ExECT `dev140` | ExECT `test60` | ExECT total | Gan `dev750` | Gan `test450` | Gan total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Scored gold units | **836** inventory | **349** inventory | **1,185** inventory | **750** labels | **450** labels | **1,200** labels |
| Mean gold units / letter | 5.97 | 5.92 | 5.95 | 1 | 1 | 1 |
| Median gold units (range) | 6 (0–14) | 6 (1–12) | 6 (0–14) | 1 (1–1) | 1 (1–1) | 1 (1–1) |
| Occupied families, median | 3 of 4 | 3 of 4 | 3 of 4 | — | — | — |
| Letters with no scored gold | 3 | 0 | 3 | 0 | 0 | 0 |
| Compact/headline units | 796 | 328 | 1,124 | — | — | — |
| Numeric-rate gold | — | — | — | 468 (62.4%) | 281 (62.4%) | 749 (62.4%) |
| Non-rate gold | — | — | — | 282 (37.6%) | 169 (37.6%) | 451 (37.6%) |
| `row_ok=False` in cited n | — | — | — | 32 | 20 | 52 |

Non-rate Gan gold is seizure-free + unknown + no-reference +
unresolved multiple. Empty ExECT family gold means unannotated under
the guideline, not clinically false. The three development letters
with zero four-family units sit in letter n and not in the F1
denominator.

## Claim boundary

**Development inventory** of letter length, gold density, and
split-stratum mix, plus **aggregate-only** holdout totals. Not
predicted performance, not holdout generalization, and not a claim
that gold is the task.

## Attribution

Lengths use official ExECT and Gan loaders on cleaned `note_text`.
Inventory totals reuse `clinical_inventory_unit_keys` (836 / 349).
Compact/headline totals and Gan kind / `row_ok` counts match
[dataset gold support](dataset_gold_support_2026-08-22.md). ExECT SF
presence is a JSON-entity count (`entity == SeizureFrequency`). Gan
kind × `row_ok` cells are the `gan2026_split_v1` manifest
`strata_counts`.
