# Gan extract label-forms result

Date: 2026-08-22
Revised: 2026-08-22 (cited LLM extract column)
Status: development answer plus locked aggregate
Owner: [protocol](gan_extract_label_forms_protocol_2026-08-22.md)
Work cells: `experiments/paper/gan_llm_extract/gemini37flash/dev750/`
and scratch `.../test450/` (aggregate only).

This request is the cited Gemini LLM extract
(`gan_llm_extract`). `gan_llm_extract_raw` is the source-near
wording ablation (extract ~0.55 holdout; rules recover to ~0.79), not the
paper extract column. Leftover living extracts stay on disk; they are not
the paper primary.

## Answer

Putting the later-stage `label_forms` list into Gemini extract raises
the `dev750` extract-stop score from **0.59** to **0.78**. Locked
`test450` (aggregate only, frozen prompt) is **0.79**, versus
source-near extract **0.55** and later-stage encode **0.65**.
Development extra letters were not form-only: 219 picks changed.
Holdout rows were not inspected.

## Protocol

Gemini 3.7 Flash, Purist, extract stop (`raw_model`). New request
`gan_llm_extract`. The promoted `gan_llm_extract_raw`
prompt was not changed. `test450` is aggregate-only.

## Component result

| Cell | Purist | Pragmatic | Scorable |
| --- | ---: | ---: | ---: |
| `gan_llm_extract_raw` extract | 0.59 | 0.62 | 532 |
| Later-stage encode on that ledger | 0.67 | 0.71 | 750 |
| `gan_llm_extract` extract | **0.78** | **0.82** | **748** |
| Locked `test450` extract (aggregate) | **0.79** | **0.81** | 449 structured |

216 of the 218 previously unscorable extract letters became scorable.
Two letters still fail parse. Call failures: 0.

Same `selected_event_ids` as the old extract: **531/750**. On those
rows the written label changed 289 times: **111 Purist rescues**, **2
harms**. Changed pick: **219/750**, **47 rescues**, **15 harms**.

No-call replay of the new raw (not paper cells): encode **0.79**,
select **0.85**. Encode now adds only 10 letters, because extract
already wrote the codebook string.

## Attribution

Most of the lift is form on a kept pick (net +109). A smaller part is
a different current fact (net +32). The 0.67 encode cell cannot be the
ceiling for a letter-in extract change.

## Claim boundary

Development answer on Gemini `dev750`, plus a frozen-prompt
aggregate on `test450`. Cited as the LLM extract column in the five-cell
table. `gan_llm_extract_raw` remains the source-near wording ablation. Do
not retune
`label_forms` from development misses or holdout totals. Do not
inspect holdout rows.

## Next

Stop. Promoted as the cited LLM extract column.
