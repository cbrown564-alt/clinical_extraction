# Gan extract label-forms protocol

Date: 2026-08-22
Status: completed 2026-08-22
Result: [extract label-forms result](gan_extract_label_forms_2026-08-22.md)
Owner: this file

## Question

If Gemini extract (`gan_llm_with_rules`) is given the same closed
`label_forms` block that lifted later-stage encode from 0.56 to
0.67, does the extract-stop Purist score move toward that encode
cell, or does the letter-in call also change collection and the pick?

This is a new request. It does not overwrite `gan_llm_with_rules`.

## Why it matters

Later-stage encode showed that form, not pick, was the large gap on
the saved Gemini extract ledger. Extract today only shows a short
example list. The next measurement is whether teaching the codebook
at extract recovers that form lift without a second call.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `dev750` (`gan2026_split_v1` validation) |
| Row policy | Development review permitted |
| Holdout | Frozen-candidate aggregate only. Do not inspect `test450` rows or retune. |
| Model | Gemini 3.7 Flash (`gemini37flash`) |
| Scorer | Purist accuracy; secondary Pragmatic and scorable count |
| Repair policy | Extract stop only (`raw_model`): parse plus JSON dialect, no selected-evidence encode, no select families |
| Prompt/program | `gan_llm_extract_label_forms` |

## Candidate and comparator

Candidate: same event and selection schema as `gan_llm_with_rules`,
plus the shared `label_forms` payload from `prompt_label_forms.py`.
Events still keep the note wording in `raw_value`. The seizure-frequency
label must use only those forms.

Fixed comparators on the same `dev750` letters, Gemini 3.7 Flash:

- current extract stop on saved `gan_llm_with_rules`: **0.59**, 532 scorable
- later-stage `gan_llm_encode` on that same extract ledger: **0.67**

Same-pick form-only lift would approach 0.67. A higher or lower score
means the new call also changed events or the pick.

## Required comparison

After the live cell:

1. Extract Purist / Pragmatic / scorable versus 444 and 506.
2. How often `selected_event_ids` match the saved `gan_llm_with_rules` extract pick.
3. Among same-pick rows, how often the submitted label changes toward gold (form rescue) versus away from gold (form harm).
4. No-call encode and select replay of the new raw, as mechanism only. Those scores are not paper cells.

## Stop rule

Stop after the Gemini `dev750` extract comparison is written. Do not
retune the form list from those misses. A later holdout run is
aggregate-only and uses the frozen prompt. Do not promote into the
four-method table from these cells alone.

## Claim boundary

Development answer on Gemini `dev750` extract. Not holdout. Not a
replacement for `gan_llm_with_rules`, later-stage encode, or hybrid
encode/select.

## Artifact

Work cell: `experiments/paper/gan_llm_extract_label_forms/gemini37flash/dev750/`
