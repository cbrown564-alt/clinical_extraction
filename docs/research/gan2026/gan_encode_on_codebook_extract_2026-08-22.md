# Why encode harms LLM extract and helps LLM then rules

Date: 2026-08-22
Status: development answer
Owner: [select-from-extract protocol](gan_select_from_extract_protocol_2026-08-22.md)
Artifact: `experiments/paper/gan_codebook_extract_grid/gemini37flash/dev750/encode_comparison.json`

## Answer

Later-stage LLM encode never sees the extract `final_label`. It
rewrites each event from `raw_value` and a quote, with no letter.
On a codebook extract that already wrote the designed form, that
throws away the answer. Rule encode keeps that `final_label` and
only runs evidence-aware form repair.

Same 748 parsed `dev750` letters. Same extract pick in every
later-stage encode row (0 pick changes).

| Path | Starts from | Purist vs extract |
| --- | --- | ---: |
| Later-stage LLM encode | event `raw_value` + quote | 0.78 → 0.69 (89 harm, 21 rescue) |
| Rule encode | extract `final_label` | 0.78 → 0.80 (5 harm, 22 rescue) |

Rule encode keeps the extract string on **677/748** letters. The 71
changes are all `gan.render.selected_evidence`. LLM encode keeps the
extract string on 573 letters and rewrites 175.

## Why LLM encode harms

The encode request is letter-out by design. Extract already did the
work that needs the letter: elapsed seizure-free duration, summing
types, and writing a codebook form that is not the event wording.

On 706/748 letters, extract `final_label` already differs from the
pick's `raw_value`. That is the codebook step. LLM encode is asked
not to reuse `raw_value` unless it already matches a form.

The 89 Purist harms are almost all that rewrite:

- **Seizure-free duration → `unknown` (about 50 letters).** Extract
  wrote `seizure free for 6 month` from a dated last event. Encode
  sees `Seizure-free since 27 March 2024` and cannot compute the
  window without the letter, so it writes `unknown`.
- **Subtype count overwrites the overall count.** Gold `12 per week`;
  extract kept that. The pick event says `five drop attacks in last
  week`; encode writes `5 per week`.
- **Split counts cannot be added.** Extract combined two events into
  `6 per 3 month`. Encode of the parts yields `unknown` or one part.

Of 111 letters where extract was already Purist-correct *and* its
codebook `final_label` differed from `raw_value`, and encode rewrote
it, **89** became wrong.

## Why rule encode helps

`llm_encode` repair keeps `selection.final_label` when it is present.
It then runs `repair_prediction_label_with_evidence` on that string
plus the quote and the letter.

That is a conservative edit of an already-designed answer, not a
second extract. Net **+17** (22 rescue, 5 harm). Rescues are mostly
`unknown` → a countable form from diary dates or a cluster wrapper
dropped to match gold (`1 cluster per 4 week, multiple per cluster`
→ `1 per 4 week`). The five harms are small count or unit edits.

## Claim boundary

Development mechanism on Gemini `dev750`. Not holdout. Does not
retune `label_forms`. Does not by itself decide whether to skip
later-stage encode. Select-from-extract is 590 versus 592 after
encode; see [select-from-extract](gan_select_from_extract_2026-08-22.md).
