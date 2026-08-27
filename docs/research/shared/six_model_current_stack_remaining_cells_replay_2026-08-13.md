# Six-model current-stack remaining-cell hybrid replay

Date: 2026-08-13  
Status: complete  
Protocol: [predeclared protocol](six_model_current_stack_remaining_cells_replay_protocol_2026-08-13.md)  
Artifact: [`experiments/six_model_current_stack_remaining_cells_replay_20260813/replay_summary.json`](../../experiments/six_model_current_stack_remaining_cells_replay_20260813/replay_summary.json)  
Rebuild: `python scripts/replay_six_model_current_stack_remaining_cells.py`  
Sibling: [Gan `dev750` current-stack replay](../gan2026/six_model_current_stack_dev750_replay_2026-08-13.md)

## Finding

The three cells left after the 13 Aug Gan `dev750` replay are now current-stack
no-call readouts. Zero live model calls. Holdout outputs are aggregate-only.

**Gan `test450` (v0.5 raw, HEAD `hybrid_full_stack`).** Every model gains
against the scores stored in the saved files. Pooled Purist moves
**2157 → 2191 / 2700 (0.8115)** (+34); Pragmatic **2262 → 2287** (+25);
80 Purist rescues and 46 harms; parse-missing 14 → 8. Sol is **380/450
(0.8444)** versus a stored 373. Decision 0050 selects this Sol fill.

**ExECT `dev140`.** Current `default` / `default` assembly is mixed versus the
published July / 0731 `headline_target` F1. Luna and DeepSeek tick up; Sol
moves **0.8920 → 0.8895**; Qwen drops the most (**0.8571 → 0.8442**).
All-family key exactness across 840 model×letter cells is 36 rescue / 38 harm.

**ExECT `test60` (59 letters, aggregate-only).** Five of six models rise versus
the 1 Aug stage panel. Sol moves **0.8047 → 0.8196**. Selected DeepSeek 0731
moves **0.8118 → 0.8223**. Gemma's empty-event letters stay in the
denominator as empty predictions.

This is not a new model run. [Decision 0050](../../decisions/0050-current-stack-hybrid-primary-fills.md)
promotes these hybrid fills as the selected primary scores. DeepSeek holdout
uses the 0731 raws: Gan **366/450**, ExECT **0.8223**.

## What was replayed

| Cell | Prompt / sidecar | Raw source | Repair / assembly |
| --- | --- | --- | --- |
| Gan 6 × 450 | `gan2026_hybrid_structured_events_v0.5` | `scratch/holdout/gan2026_matched_v05/` and `_local/` | HEAD `hybrid_full_stack` |
| ExECT 6 × 140 | `exectv2_hybrid_key_family_event_ledger_v0.9.24` | July 15 / DeepSeek 0731 structured jsonl | HEAD `default` / `default` |
| ExECT 6 × 59 | same | sealed test60 structured sidecars, Sol credit-v2 | same |

## Gan `test450` versus stored same-raw finals

| Model | Stored Purist | HEAD Purist | Δ | Stored Prag. | HEAD Prag. | Δ | Parse before → after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-4.1-mini | 361 | 374 | +13 | 379 | 390 | +11 | 4 → 2 |
| GPT-5.6 Luna | 362 | 366 | +4 | 375 | 378 | +3 | 3 → 2 |
| GPT-5.6 Sol | 373 | 380 | +7 | 384 | 391 | +7 | 0 → 0 |
| DeepSeek V4 Flash | 344 | 348 | +4 | 366 | 368 | +2 | 3 → 2 |
| Qwen 3.6:35B | 362 | 364 | +2 | 384 | 384 | 0 | 2 → 1 |
| Gemma 4 26B | 355 | 359 | +4 | 374 | 376 | +2 | 2 → 1 |
| **Pooled** | **2157** | **2191** | **+34** | **2262** | **2287** | **+25** | **14 → 8** |

HEAD Purist rates on 450 letters: mini 0.8311, Sol 0.8444, Luna 0.8133,
Qwen 0.8089, Gemma 0.7978, DeepSeek 0.7733.

Largest same-raw lift is mini (+13). Qwen gains the least (+2) and is flat on
Pragmatic. Do not mix these after-scores with the 2026-08-03 final-panel
column: that panel's DeepSeek `test450` hybrid 0.8178 is a later floors
readout, not the generation-time stored comparison. The 11 Aug cluster-v2
pooled Purist 2180/2700 is a previous current-stack snapshot on the same raw
files; this pass is 2191/2700.

## ExECT `dev140` versus published hybrid F1

| Model | Published F1 | HEAD F1 | Δ | Key-exact rescue / harm |
| --- | ---: | ---: | ---: | --- |
| GPT-4.1-mini | 0.8202 | 0.8160 | −0.0042 | 4 / 5 |
| GPT-5.6 Luna | 0.8832 | 0.8848 | +0.0016 | 9 / 6 |
| GPT-5.6 Sol | 0.8920 | 0.8895 | −0.0025 | 9 / 6 |
| DeepSeek V4 Flash | 0.8994 | 0.8999 | +0.0005 | 8 / 7 |
| Qwen 3.6:35B | 0.8571 | 0.8442 | −0.0129 | 4 / 9 |
| Gemma 4 26B | 0.8016 | 0.7988 | −0.0028 | 2 / 5 |

Sol remains the Decision 0046 method-identity number at the published
**0.8920**. Current-stack Sol is 0.8895. Qwen's drop is the only
development movement larger than about 0.005.

HEAD F1 uses official-split four-family gold (803 mentions). The published
July Sol file prints gold_count 807, so the F1 deltas mix current assembly
with a four-mention gold-count difference. Same-gold movement is the
key-exact rescue/harm column.

## ExECT `test60` versus 1 Aug stage panel (aggregate only)

| Model | Stage-panel F1 | HEAD F1 | Δ |
| --- | ---: | ---: | ---: |
| GPT-4.1-mini | 0.7572 | 0.7613 | +0.0041 |
| GPT-5.6 Luna | 0.7950 | 0.8089 | +0.0139 |
| GPT-5.6 Sol | 0.8047 | 0.8196 | +0.0149 |
| DeepSeek V4 Flash (pre-0731 tree) | 0.7881 | 0.8020 | +0.0139 |
| Qwen 3.6:35B | 0.7872 | 0.7892 | +0.0020 |
| Gemma 4 26B | 0.7169 | 0.7392 | +0.0223 |

Sol's after family scores: Diagnosis 0.8401, SeizureFrequency 0.6143,
Prescription 0.9157, Investigations 0.9032. The stage-panel Sol families
were 0.8424 / 0.6143 / 0.8554 / 0.9032. The holdout lift is Prescription
(v10 landed after the 1 Aug panel). Decision 0050 cites Sol hybrid
**0.8196**.

The selected DeepSeek holdout cell is the **0731** sidecar, replayed the
same day: **0.8118 → 0.8223**. The pre-0731 tree above is not the selected
fill. Gemma has two empty structured-event letters; they scored as empty
predictions and remain in the 59-letter denominator.

## DeepSeek 0731 current-stack (selected holdout identity)

| Surface | Stored / live 0731 | HEAD | Δ |
| --- | ---: | ---: | ---: |
| Gan `test450` Purist | 368 | 366 | −2 |
| Gan `test450` Pragmatic | 377 | 375 | −2 |
| ExECT `test60` four-family F1 | 0.8118 | 0.8223 | +0.0105 |

Gan 0731 transitions: 4 Purist rescues / 6 harms. ExECT 0731 after families:
Diagnosis 0.8468, SeizureFrequency 0.6099, Prescription 0.9102,
Investigations 0.9231.

## How to read this against older six-model numbers

| Artifact | What it is |
| --- | --- |
| 2026-08-03 final panel | Historical snapshot. Living primary panel is `experiments/six_model_current_stack_primary_panel_20260813/`. |
| 1 Aug ExECT `test60` stage panel | Frozen Decision 0046 holdout hybrid fills. Unchanged. |
| 13 Aug Gan `dev750` current-stack replay | v0.7 current repair on July 18 development raw. |
| This remaining-cell replay | Current repair on the v0.5 Gan holdout raw and ExECT structured sidecars that exist on this checkout. |

## Claim boundary

No-call current-repair evidence. Gan `test450` is current repair on **v0.5**
saved outputs. ExECT cells are current `default` / `default` assembly on
saved v0.9.24 structured sidecars. `dev140` is development. Holdout cells are
aggregate-only. [Decision 0050](../../decisions/0050-current-stack-hybrid-primary-fills.md)
selects these hybrid fills as primary. DeepSeek holdout is the 0731
current-stack cell (Gan 366/450, ExECT 0.8223).
Scores are not interchangeable across tasks.
