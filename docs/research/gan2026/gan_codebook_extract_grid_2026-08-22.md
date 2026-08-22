# Gan codebook-extract grid result

Date: 2026-08-22
Revised: 2026-08-22 (development grid; cited table is five-cell)
Status: development answer
Owner: [protocol](gan_codebook_extract_grid_protocol_2026-08-22.md)
Machine artifact: `experiments/paper/gan_codebook_extract_grid/gemini37flash/dev750/grid.json`

Development grid that chose the cited LLM extract and both extract
(`gan_llm_pre_post_label_forms`). `gan_llm_with_rules` is the source-near
wording ablation, not the paper extract. Living `gan_llm_pre_post` is not
the cited both row. Leftover living extracts stay on disk; they are not
the paper primary.

## Answer

The codebook extract is the cited Gemini LLM extract. Later-stage LLM
encode on that ledger **lowers** the score. Rules after the same raw
still raise it. A new Rules-then-LLM request with the same form list
moves most of the gain into extract; rule encode then adds nothing on
Purist and rule select still adds 21 letters.

`gan_llm_with_rules` is kept as a source-near ablation: it can keep
wording such as `up to 4 per day` instead of `4 per day`, at a lower
extract score.

## Protocol

Gemini 3.7 Flash, Gan `dev750`, Purist. New extract
`gan_llm_extract_label_forms`. Fresh later-stage encode and select
calls on that ledger. Rule encode/select replay on the same raw
(`note_text` on). Fresh `gan_llm_pre_post_label_forms`, then the same
rule stops. Promoted `gan_llm_with_rules` and living `gan_llm_pre_post`
were not overwritten. `test450` was not loaded in this cut.

## Component result

Purist accuracy.

| Method | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| LLM (later-stage on codebook extract) | **0.78** | **0.69** | **0.79** |
| LLM then rules (rules on that raw) | 0.78 | **0.80** | **0.86** |
| Rules then LLM (`pre_post` + forms) | **0.86** | **0.86** | **0.89** |
| Standalone rules | — | — | 0.89 |

Source-near ablation (`gan_llm_with_rules` / living `gan_llm_pre_post`):

| Method | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| LLM later-stage | 0.59 | 0.67 | 0.76 |
| LLM then rules | 0.59 | 0.81 | 0.88 |
| Rules then LLM | 0.67 | 0.84 | 0.89 |

## Attribution

Later-stage encode is not a form rescue on a codebook ledger: it drops
68 letters versus extract (0.78 → 0.69). Later-stage select recovers to
0.79, seven letters above extract and 16 below the old later-stage
select on the source-near ledger (0.76).

Rule encode on the codebook raw adds 17 letters (0.78 → 0.80). Rule
select adds 44 more (0.86). That path is below the old source-near LLM
then rules select (0.88), because the new extract already wrote codebook
strings and changed 219 picks.

Rules then LLM extract jumps from 0.67 to 0.86. Rule encode is flat on
Purist. Rule select is 0.89, one letter above the living no-forms cell
(0.89) and four below standalone rules (0.89).

## Claim boundary

Development candidate grid. Not holdout. Informed the cited five-cell
`test450` table; does not replace it. Do not retune `label_forms`. Do
not overwrite `gan_llm_with_rules` or living `gan_llm_pre_post`.

## Next

Stop this cut. Promote only after a holdout aggregate on the new
later-stage and pre-post cells, if that is wanted. The source-near
ablation stays available.
