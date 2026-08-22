# Gan semantic family order protocol

Date: 2026-08-20
Revised: 2026-08-22 (replays source-near ablation cells)
Status: answered — see [gan_semantic_family_order_2026-08-20.md](gan_semantic_family_order_2026-08-20.md)
Owner: this file
Identity: replay of source-near `gan_llm_with_rules` and living
`gan_llm_pre_post` raw output (not the cited five-cell table)

## Question

After moving monthly diary after elapsed-anchor, is any other adjacent
pair of clinical post-stack families in the wrong order?

Diary after elapsed-anchor was a harm-free development improvement.
The remaining eight adjacent pairs have not been swapped on the same
saved outputs.

## Why it matters

Each family reads the current submitted label. Two families that both
propose a new label can overwrite each other. The current sequence is
historical, not a measured order, except the diary/elapsed pair.

## Dataset and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `dev750` (`gan2026_split_v1` validation) |
| Row policy | Development review permitted |
| Holdout | Do not inspect `test450`. Do not start holdout calls. |
| Scorer | Purist primary; Pragmatic secondary |
| Replay | No new model calls |

## Cells

- Grok source-near (`gan_llm_with_rules`): `paper_experiments/gan/gan_llm_with_rules/grok46/dev750/rows.jsonl`
- Luna source-near (`gan_llm_with_rules`): `paper_experiments/gan/gan_llm_with_rules/gpt56luna/dev750/rows.jsonl`
- Luna pre-post: `experiments/paper/gan_llm_pre_post/gpt56luna/dev750/rows.jsonl`

Comparator: current default order with diary after elapsed-anchor.

## Design

Keep format stages first (`selected_evidence`). Vary only the nine
semantic families:

1. `usual_interval`
2. `typical_over_ytd`
3. `breakthrough`
4. `non_epileptic`
5. `residual_jerk`
6. `post_change_burst`
7. `dated_sequence`
8. `elapsed_anchor`
9. `monthly_diary`

Conditions: the default order, plus each of the eight adjacent swaps.
The already-known control is diary before elapsed-anchor (swap of
positions 8 and 9).

Do not run the 9! permutation set. Order only matters when two or more
families change the same row.

## Stop rule

- Adopt a swap only if Purist help is at least 1 and Purist harm is 0
  on all three cells.
- If a swap helps one cell and harms another, keep the default and
  record the conflict.
- If no remaining adjacent swap is harm-free on all three cells, the
  answer is that only diary after elapsed-anchor has evidence.

## Claim boundary

Development answer on these three saved `dev750` raw files. Not holdout.
Not a paper rung change unless a swap is later promoted.

## Artifact

`experiments/paper/gan_semantic_family_order/dev750_adjacent_swaps.json`
