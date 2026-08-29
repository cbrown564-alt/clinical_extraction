# Grok 4.6 cell 3 at temperature 0

Date: 2026-08-28
Revised: 2026-08-28 (codebook cell-3 rescore)
Status: complete; living cell is temperature 0
Protocol: [temperature-0 `test450`](gan_grok46_temperature_0_test450_protocol_2026-08-28.md)
Owner: this file
Cited comparator: Grok temperature-1 `gan_llm_extract` raws, rescored
on the same codebook stack

## Living default

Grok temperature is now **0.0**, the same living setting as Gemini,
DeepSeek, Qwen, and Gemma. Luna stays at **1.0** because that provider
rejects `0`. The earlier cited Grok cell-3 row was temperature 1.

## Stack

Cell 3 is LLM find (`gan_llm_extract`), then `gan_rules_encode`,
then `llm_select_after_codebook`. The first write of this report
scored both temperatures with historical `llm_select` (367 vs 379 on
`test450`; 663 vs 650 on `dev750`). That is not cell 3.

Living temperature-0 codebook rungs are already in
`paper_experiments/gan/rungs/grok46/`. Temperature-1 holdout raws
still exist at
`scratch/holdout/paper/gan_llm_extract/grok46/temperature_1_incomplete/test450/`
(450 unique rows, zero empty raws; the folder name is stale). Those
raws were replayed through the codebook stack. Temperature-1
`dev750` codebook raws were overwritten by the living temperature-0
extract, so that split has no matched cell-3 temperature-1 select.

## Shift versus Grok cell 3 at temperature 1.0

| Split | Stop | Temp. 1.0 | Temp. 0.0 (living) | Δ (0 − 1) |
| --- | --- | ---: | ---: | ---: |
| `test450` | Find | 0.784 (353/450) | 0.789 (355/450) | **+2** |
| `test450` | Encode | 0.804 (362/450) | 0.811 (365/450) | **+3** |
| `test450` | Select | 0.842 (379/450) | 0.838 (377/450) | **−2** |

Holdout select is **2** letters lower at temperature 0, not 12.
Find is essentially unchanged. The historical `llm_select`
reading (367 vs 379) is an old-stack ablation.

## Joint reading with Gemini temperature 1

Same codebook cell-3 stack on both models. Gemini living is 0;
temperature 1 is unpromoted. Grok living is 0; temperature 1 is the
earlier cited extract.

| Model | Split | Stop | Temp. 0 | Temp. 1 | Δ (1 − 0) |
| --- | --- | ---: | ---: | ---: | ---: |
| Gemini 3.7 Flash | `test450` | Select | 0.831 (374) | 0.824 (371) | −3 |
| Gemini 3.7 Flash | `dev750` | Select | 0.865 (649) | 0.867 (650) | +1 |
| Grok 4.6 | `test450` | Select | 0.838 (377) | 0.842 (379) | +2 |

Grok `dev750` temperature 1 is omitted: the codebook extract raws
are not on disk. Effects are mixed and small. Temperature 0 remains
the living default for every model that accepts it. Luna was not run
at 0. Stage ownership on the Gemini holdout still moves the select
stop far more (0.71 rules versus 0.83 cell 3).

Living temperature-0 cells:
`paper_experiments/gan/gan_llm_extract/grok46/` and
`paper_experiments/gan/rungs/grok46/`.

Temperature-1 holdout codebook replay:
`experiments/paper/gan/rungs/grok46/temperature_1/test450/comparison.json`.
