# Results: Local same-model policy-example select on Gan `dev750`

Date: 2026-09-04
Protocol: [protocol](gan_llm_select_policy_examples_local_dev750_protocol_2026-09-03.md)
Work cells:
`experiments/paper/gan_llm_select_from_extract/<slug>/gan_llm_extract/dev750`
Split: `dev750` development review. No `test450` row inspection.

## Answer

The living policy-example select call lowers Purist on both local
models, same direction as sealed `test450`. The mechanisms differ.

| Model | Find Purist | Select Purist | Δ | Find Prag | Select Prag |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.8 27B | 505/750 | **481**/750 | −24 | 552 | 522 |
| Gemma 4 26B | 501/750 | **476**/750 | −25 | 547 | 525 |

Changed-row counts (paired on `source_row_index`):

| | Qwen | Gemma |
| --- | ---: | ---: |
| Both right | 415 | 465 |
| Rescue (find miss, select hit) | 66 | 11 |
| Harm (find hit, select miss) | 90 | 36 |
| Both wrong | 179 | 238 |
| Both right, different label | 36 | 6 |

Net = rescue − harm. Hybrid rule repair on the find cell is **not**
the story: the sampled harm rows kept the same find label after rules.

## Mechanism

**Qwen: unusable select JSON, then leftover written-label overwrites.**

Of 90 harms, **62** have no `selected_event_ids` in the select
payload. The later-stage scorer then records parse errors and leaves
`comparison` empty, so the row is counted wrong even though the
extract pick (and often the same label) is still sitting on the
row. Those 62 would have stayed find-correct if the empty comparison
were not treated as a miss. The other **28** harms write a new label
(sometimes after adding events). Rescues are also written labels
(66). Dominant failure is schema-invalid select output, not a better
competing event.

**Gemma: pick overwrite onto a source-near event that is not a legal
label.**

Of 36 harms, **30** change `selected_event_ids` and then project that
event's `raw_value` (`daily`, `once or twice per week`, `several times
per week`, `no confirmed events`). Six write a new label (often a
cluster form). Rescues are few (11). Dominant failure is choosing
another ledger event whose text is not an allowed Gan form.

## Claim boundary

Development mechanism reading. Promoted into
`paper_experiments/gan/gan_llm_select_from_extract/` for a wider
comparison. Not Table 1. Not cited cell 5. Not holdout evidence.
The living select prompt was not retuned.
