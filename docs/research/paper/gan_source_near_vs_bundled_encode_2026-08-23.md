# Source-near extract vs codebook extract, and a separate encode call

Date: 2026-08-23
Revised: 2026-08-23 (test450 extract / encode / select table)
Status: working ablation draft; not a results column
Owners: [Gan extract label-forms](../gan2026/gan_extract_label_forms_2026-08-22.md),
[encode on codebook extract](../gan2026/gan_encode_on_codebook_extract_2026-08-22.md),
[codebook-encode holdout](../gan2026/gan_codebook_encode_holdout_2026-08-22.md),
[five-cell grid](../gan2026/gan_five_cell_grid_2026-08-22.md)
Related: [three variables](three_variables_rules_model_thinking_2026-08-23.md)

This is the Gan request-and-encode ablation. It is not the six-model
row and not a thinking or roster result. Holdout is aggregate-only.
Do not inspect `test450` rows.

## The question

Two Gan choices sit next to the headline method:

1. **What the extract writes.** `gan_llm_extract` asks the model for
   the codebook form (`label_forms` in the request).
   `gan_llm_extract_raw` keeps letter wording. Same clinical
   instructions, different written form.
2. **Who encodes, and in how many calls.** Encode can be bundled
   into extract, then optionally followed by recorded
   `gan_rules_encode`, or run on `gan_llm_extract_raw` as later-stage
   `gan_llm_encode` or as recorded rules. All then take rule select.

The paper cites the codebook extract. The source-near request and the
later-stage encode call stay ablations.

## Answer

`gan_llm_encode` helps `gan_llm_extract_raw` a lot (locked
`test450` extract **0.55 → 0.65**). It does not get close to the
combined extract-and-encode stop in `gan_llm_extract` (**0.79**).
Rule encode on the same wording ledger gets further (**0.74**).
Final selection rules then pull the raw stacks up to **0.79**.
Combined extract-and-encode plus rule select is **0.82**; the same
ledger plus recorded encode then select is **0.83**. Both bundled
rows still win, and both use one model call.

The trade-off is wording. Combined extract-and-encode writes the
codebook string and drops letter form (`up to 4 per day` becomes
`4 per day`). The raw extract keeps more of that wording. Rules
then recover most of the score, not all of it. Combined
extract-and-encode is the better general choice. Keeping source
wording, at a small select-stop cost, is sometimes the better
use case.

## 1. Source-near vs codebook extract

Gemini 3.7 Flash, Purist, extract stop (`raw_model`).

| Request | `dev750` | Locked `test450` |
| --- | ---: | ---: |
| `gan_llm_extract_raw` | 0.59 | 0.55 |
| `gan_llm_extract` | **0.78** | **0.79** |

On development, 216 of 218 previously unscorable source-near letters
became scorable under the codebook request. Same pick on 531/750
letters; on those rows the written label changed 289 times (111
Purist rescues, 2 harms). Changed pick: 219/750 (47 rescues, 15
harms). Most of the lift is form on a kept pick.

Source-near extract still needs a large rule encode/select repair
to look like a submitted label. That repair is a real mechanism
study. It is not the cited extract column.

## 2. Separate encode vs bundled form

Gemini 3.7 Flash, locked `test450`, Purist. Rows 1 and 4 start from
`gan_llm_extract` (form already written). Row 1 selects on that
string; row 4 runs recorded `gan_rules_encode` first. Rows 2 and 3
start from `gan_llm_extract_raw`. Row 2 encodes with later-stage
`gan_llm_encode`. Row 3 encodes with recorded rules.

| Stack | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| LLM extracts and encodes (1 phase), rules select | 0.79 (354) | 0.79 (354) | 0.82 (368) |
| LLM extracts, LLM encodes, rules select | 0.55 (246) | 0.65 (291) | 0.79 (357) |
| LLM extracts, rules encode, rules select | 0.55 (246) | 0.74 (335) | 0.79 (357) |
| LLM extracts and encodes (1 phase), rules encode, rules select | 0.79 (354) | 0.80 (359) | **0.83** (373) |

`gan_llm_encode` on source-near wording is a real lift (**0.55 →
0.65**) and still far from the bundled encode stop (**0.79**).
Rule encode on that raw gets closer (**0.74**). Select then brings
both raw stacks to **0.79**. The bundled call is **0.82** without
a second encode, **0.83** with recorded encode. Both bundled rows
are one model call.

That 0.03–0.04 select gap is the wording trade. Bundled extract
writes the gold form and drops the bound. Raw extract can keep
`up to 4 per day`; rules map most of those strings onto the
codebook, not all of them. Use the combined call unless the use
case needs the source phrasing more than that last slice of score.

The same `gan_llm_encode` call on a codebook extract is the
harmful direction (development **0.78 → 0.69**). It is not this
table.

## What the paper may say

It may say `gan_llm_encode` helps source-near extract and still
does not reach bundled extract-and-encode. It may say selection
rules close most of that gap, and that the bundled call stays
ahead with one fewer prompt (0.82, or 0.83 after recorded encode). It may say the raw extract keeps
letter wording the codebook string drops, and that rules recover
most but not all of the score. It may say bundled extract is the
default, and that keeping source wording can be worth the small
select-stop cost. It may not treat a later-stage encode on the
codebook ledger as this comparison.

It may not cite Sol or enveloped-request totals as this ablation.
It may not treat `gan_llm_only` as extract. It may not retune
`label_forms` from development misses.

## Claim boundary

Synthesis of the locked Gemini codebook cells. Mechanism on
`dev750` may name letters; holdout may not. Companion models have
`gan_llm_extract` extracts; this report does not restage them.
See [three variables](three_variables_rules_model_thinking_2026-08-23.md)
for the roster reading.
