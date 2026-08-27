# Gan 2026 six-model current-stack `dev750` hybrid replay

Date: 2026-08-13  
Status: complete  
Protocol: [predeclared protocol](six_model_current_stack_dev750_replay_protocol_2026-08-13.md)  
Artifact: [`experiments/gan2026_six_model_current_stack_dev750_replay_20260813/replay_summary.json`](../../experiments/gan2026_six_model_current_stack_dev750_replay_20260813/replay_summary.json)  
Rows: `experiments/gan2026_six_model_current_stack_dev750_replay_20260813/{slug}/validation750.rows.jsonl` (tracked; Git LFS)  
Rebuild: `python scripts/replay_gan2026_six_model_current_stack_dev750.py`

## Finding

Current `llm_with_rules` repairs raise every one of the six published July 18
hybrid `dev750` cells. On the 4,500-cell pool the same v0.7 raw outputs score
**3986/4500 Purist (0.8858)** versus **3910/4500 (0.8689)** in the July 18
files: **+76 Purist, +71 Pragmatic**. That is 135 Purist rescues and 59 harms.
Parse-missing rows fall from 18 to 7. Zero model calls.

The selected-prompt companion (GPT-4.1-mini, 7 June v0.5 raw) is unchanged
from the earlier single-cell readout: **682/750 Purist (0.9093)** and
**696/750 Pragmatic** versus 661 / 679. One row still fails to parse.

This is not the six-model **v0.5** panel. Those scratch sidecars are not on
this checkout. It is not holdout. Rules-only and LLM-only were not replayed.
Decision 0046 / 0047 and C16 holdout fills are unchanged.

The remaining current-stack cells (`test450`, ExECT `dev140`, ExECT `test60`)
are now in
[remaining-cell replay](../shared/six_model_current_stack_remaining_cells_replay_2026-08-13.md).

## What was replayed

| Cell | Prompt | Raw source | Repair |
| --- | --- | --- | --- |
| Six models × 750 | `gan2026_hybrid_structured_events_v0.7` | `experiments/gan2026_six_model_validation_20260718/*--llm_with_rules.jsonl` | HEAD `hybrid_full_stack` |
| GPT-4.1-mini companion | v0.5 | `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl` | same |

`test450` and ExECT remaining cells are in the
[sibling remaining-cell report](../shared/six_model_current_stack_remaining_cells_replay_2026-08-13.md).

## Six-model v0.7 current stack versus July 18 saved finals

| Model | July 18 Purist | HEAD Purist | Δ | July 18 Prag. | HEAD Prag. | Δ | Labels changed | Parse before → after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-4.1-mini | 653 | 663 | +10 | 674 | 684 | +10 | 88 | 1 → 0 |
| GPT-5.6 Luna | 646 | 665 | +19 | 669 | 685 | +16 | 94 | 5 → 3 |
| GPT-5.6 Sol | 655 | 671 | +16 | 672 | 687 | +15 | 93 | 0 → 0 |
| DeepSeek V4 Flash | 643 | 653 | +10 | 664 | 674 | +10 | 62 | 1 → 0 |
| Qwen 3.6:35B | 667 | 675 | +8 | 683 | 693 | +10 | 71 | 3 → 1 |
| Gemma 4 26B | 646 | 659 | +13 | 674 | 684 | +10 | 81 | 8 → 3 |
| **Pooled** | **3910** | **3986** | **+76** | **4036** | **4107** | **+71** | **489** | **18 → 7** |

Rates on 750 letters: Sol 0.8947, Qwen 0.9000, Luna 0.8867, mini 0.8840,
Gemma 0.8787, DeepSeek 0.8707.

Largest lift on this v0.7 cell is Luna (+19 Purist), then Sol (+16). Qwen
gains the least (+8) but remains the highest July 18 and HEAD score on this
prompt identity.

## Companion: selected v0.5 mini cell

| When | Purist | Pragmatic | Parse missing |
| --- | ---: | ---: | ---: |
| 7 June saved finals | 661 | 679 | 2 |
| HEAD replay | 682 | 696 | 1 |

Transitions: 30 Purist rescues, 9 harms, 102 labels rewritten (including
wording-only changes). Net +21 Purist, +17 Pragmatic. Matches the commit-band
story that most durable lift on this cell is late-July selected-evidence /
floors plus August cluster grammar.

Do not mix this 682 with the v0.7 mini 663. Same model, different prompt raw.

## How to read this against older six-model numbers

| Artifact | Prompt | What it is |
| --- | --- | --- |
| July 18 LFS panel / dashboards printing ~653 mini hybrid | v0.7 | Frozen published development panel. Unchanged on disk. |
| 27 July `gan2026_matched_v05_dev750_panel` | v0.5 | Historical six-model aggregates. Raw files not on this checkout, so they were **not** re-scored. |
| 31 July floors replay | v0.5 | Historical current-floors readout. Same missing-raw limit. |
| This 13 Aug replay | v0.7 six-model + v0.5 mini | Current repair on the raw files that actually exist. |

July 27 / 31 v0.5 columns in the JSON are labelled `historical_not_same_raw`.
They are not this replay's before-scores.

## Claim boundary

Development no-call evidence. Not a new model run. Not the six-model published
v0.5 panel. Not `test450`. Not rules-only or LLM-only. Do not replace the
2026-08-03 final holdout panel or Decision 0046 / 0047 fills with these
numbers.
