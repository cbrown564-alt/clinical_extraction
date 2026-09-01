# Gemini five-cell vs Qwen-2.5-14B COT synthetic

Date: 2026-08-28
Status: equivalent synthetic-to-synthetic compare; not a shared leaderboard
Owners: [five-cell grid](gan_five_cell_grid_2026-08-22.md),
[class report](gan_test450_classification_report_2026-08-28.md)
Qwen source: Gan et al. 2026 Table 7 (local PDF:
`literature/core/Reproducible Synthetic Clinical Letters for Seizure Frequency Information Extraction (Gan et. al, 2026).pdf`)

This is the equivalent **synthetic-to-synthetic** compare. It is not an evaluation
on their Synthetic(1,166). It does not treat KCH Real(300) as the same test.

## Same kind of number

Exclusive multi-class: one gold bin, one predicted bin.
Bins are Purist (fine) and Pragmatic (coarse).
**Purist micro-F1** equals accuracy here. **Pragmatic micro-F1** is the companion.
Gan et al. 2026 Table 7 reports Micro F1 under those two schemes.
`gan_llm_only` is not a results column.

## Not the same experiment

| | Gan et al. 2026 Qwen-2.5-14B | This repo, Gemini 3.7 Flash |
| --- | --- | --- |
| Train | Fine-tune. Closest row: COT 1,548 synthetic | Not trained on the 1,500. Prompt v0.5 plus recorded rules |
| Test | Their Synthetic(1,166) | Locked `test450` of public `synthetic_data_subset_1500` (`gan2026_split_v1`). n=450 |
| Draw | Their 1,166 | Our holdout. Different draw and mix |

Do not write that we evaluated on their 1,166.
Do not claim we beat or lose on a shared leaderboard.

## Qwen-2.5-14B on their Synthetic(1,166)

Verified from Table 7 (Micro F1). Columns below are **Synthetic(1,166) only**.
Real(300) / Real(150) columns exist on the same table and are a different test.

| Train | Purist micro-F1 | Pragmatic micro-F1 |
| --- | ---: | ---: |
| COT 1,548 synthetic | 0.782 | 0.848 |
| Real + synthetic, x per M | 0.817 | 0.889 |
| Real only, x per M | 0.562 | 0.666 |

The comparable Qwen row is **COT 1,548 → Synthetic(1,166): 0.782 / 0.848**.

The 15k Qwen row in the abstract (0.788 / 0.847) is **Real(300)**, COT(15,000),
not 1,166, and is a different train size. Do not use it as the equivalent row.

Ministral-8B COT(1,548) on Synthetic(1,166) is 0.808 / 0.869 (Table 7).
That is higher than Qwen on this test. Mentioned only as a parenthetical;
the cited peer row is Qwen.

## Gemini 3.7 Flash on our `test450`

Model: Gemini 3.7 Flash. Prompt v0.5. Five-cell. **Not trained** on the 1,500.
Test: locked `test450`. n=450. Not their Synthetic(1,166).
Living headline: cell 3 LLM extract / rules encode / rules select.

| Recognise | Encode | Select | Purist micro-F1 | Pragmatic micro-F1 |
| --- | --- | --- | ---: | ---: |
| rules | rules | rules | 325/450 = 0.7222 cited 0.72 | 345/450 = 0.7667 cited 0.77 |
| both | rules | rules | 368/450 = 0.82 | 380/450 = 0.8444 |
| LLM | rules | rules (cell 3) | **373/450 = 0.8289 cited 0.83** | 382/450 = 0.8489 cited 0.85 |
| LLM | LLM | rules | 368/450 = 0.82 | 377/450 = 0.8378 cited 0.84 |
| LLM | LLM | LLM | 383/450 = 0.85 | 391/450 = 0.8689 |

Purist select stops: `paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`.
Rules Purist/Pragmatic aggregates: `paper_experiments/gan/rungs/gemini37flash/test450/comparison.json` `rules_only`.
Rules per-class tables in the [class report](gan_test450_classification_report_2026-08-28.md) are the pre-promotion 321-program reading.
Cell 3 / cell 4 Pragmatic: [codebook-encode holdout](gan_codebook_encode_holdout_2026-08-22.md).
Cell 5 Pragmatic: [class report](gan_test450_classification_report_2026-08-28.md).
Cell 2 Pragmatic: [class report](gan_test450_classification_report_2026-08-28.md) / `gan_llm_and_rules_extract` comparison.

Gemini five-cell per-class P/R for cells 1, 3, and 5 is in
[class report](gan_test450_classification_report_2026-08-28.md).

## Mix (UNK class)

Gan et al. 2026 Table 3 class support, UNK:

| Set | UNK | n | Share |
| --- | ---: | ---: | ---: |
| Their Synthetic(1,166) | 316 | 1,166 | 27.1% |
| Their Real(300) | 163 | 300 | 54.3% |

Our `test450` Purist UNK **class support** in the
[class report](gan_test450_classification_report_2026-08-28.md) is 102/450 (22.7%).
That is the scored UNK bin, not gold-kind `unknown` alone.
[Dataset gold support](../paper/dataset_gold_support_2026-08-22.md) records
gold-kind `unknown` 60/450 (13.3%) and Purist unknown (gold-kind unknown +
`no_reference`) 76/450. Different cuts. Do not treat 23% as gold-kind unknown.

## Closest equivalent

Their Qwen COT synthetic→synthetic (0.782 / 0.848 on Synthetic(1,166))
versus our Gemini five-cell on our synthetic holdout
(cell 3 373/450 = 0.83 Purist micro-F1; 382/450 = 0.85 Pragmatic micro-F1).
Same *kind* of number. Not the same test set. Not the same train setup
(they fine-tune; we prompt + recorded rules).
Do not claim a win or a loss on a shared leaderboard.
