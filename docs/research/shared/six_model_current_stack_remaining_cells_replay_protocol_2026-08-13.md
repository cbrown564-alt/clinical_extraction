# Protocol: six-model current-stack remaining-cell hybrid replay

Date: 2026-08-13  
Status: **complete** (predeclared before scoring; executed 2026-08-13)  
Parents: [Decision 0043](../../decisions/0043-gan-hosted-comparison-uses-v05-prompt.md),
[Decision 0046](../../decisions/0046-exect-primary-method-comparison-boundary.md),
[Decision 0047](../../decisions/0047-gan-primary-orchestration-and-scoring-boundary.md),
[13 Aug Gan `dev750` current-stack replay](../gan2026/six_model_current_stack_dev750_replay_protocol_2026-08-13.md),
[Decision 0050](../../decisions/0050-current-stack-hybrid-primary-fills.md) / current-stack remaining-cells report  
Report target: `docs/research/shared/six_model_current_stack_remaining_cells_replay_2026-08-13.md`  
Artifact target: `experiments/six_model_current_stack_remaining_cells_replay_20260813/`  
Rebuild: `python scripts/replay_six_model_current_stack_remaining_cells.py`

## 1. Primary question

On the six retained models, what do current `llm_with_rules` repairs score on
the three cells the 13 Aug `dev750` replay left undone, when the **same saved
raw / structured model outputs** are replayed with no new calls?

Remaining cells:

| Cell | Split policy | Prompt / sidecar identity |
| --- | --- | --- |
| Gan `test450` | locked, aggregate-only | `gan2026_hybrid_structured_events_v0.5` raw |
| ExECT `dev140` | development review permitted | `exectv2_hybrid_key_family_event_ledger_v0.9.24` structured |
| ExECT `test60` | locked, aggregate-only (59 loadable letters) | same structured identity |

This is a current-stack no-call readout. It is not a new model run. It is not
a rules-only or LLM-only study. It does not rewrite Decision 0046 / 0047
primary fills or C16 holdout numbers.

## 2. Why this study

The 13 Aug protocol replayed Gan `dev750` only. `PROJECT_STATUS.md` then queued
the other three `llm_with_rules` cells on the machine that holds the sealed
hybrid trees. Those trees are present on this checkout. This protocol finishes
the same measurement on the remaining cells.

## 3. Available inputs (declared before scoring)

Inventory 2026-08-13: every listed path exists; row counts and empty-raw /
empty-event counts below are machine-only.

### Gan `test450` raw (v0.5)

| Model | Path | n | empty raw | prompt |
| --- | --- | ---: | ---: | --- |
| GPT-4.1-mini | `scratch/holdout/gan2026_matched_v05/gpt41mini/rows.jsonl` | 450 | 0 | v0.5 |
| GPT-5.6 Luna | `scratch/holdout/gan2026_matched_v05/gpt56luna/rows.jsonl` | 450 | 0 | v0.5 |
| GPT-5.6 Sol | `scratch/holdout/gan2026_matched_v05/gpt56sol/rows.jsonl` | 450 | 0 | v0.5 |
| DeepSeek V4 Flash | `scratch/holdout/gan2026_matched_v05/deepseek_v4_flash/rows.jsonl` | 450 | 0 | v0.5 |
| Qwen 3.6:35B | `scratch/holdout/gan2026_matched_v05_local/qwen36_35b/rows.jsonl` | 450 | 0 | v0.5 |
| Gemma 4 26B | `scratch/holdout/gan2026_matched_v05_local/gemma4_26b/rows.jsonl` | 450 | 0 | v0.5 |

### ExECT `dev140` structured

Same sources as the 2026-08-03 final panel (DeepSeek is the 0731 update).

| Model | Structured sidecar | n | empty events |
| --- | --- | ---: | ---: |
| GPT-4.1-mini | `experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715_structured.jsonl` | 140 | 2 |
| GPT-5.6 Luna | `experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl` | 140 | 2 |
| GPT-5.6 Sol | `experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715_structured.jsonl` | 140 | 2 |
| DeepSeek V4 Flash | `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_structured.jsonl` | 140 | 2 |
| Qwen 3.6:35B | `experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715_structured.jsonl` | 140 | 0 |
| Gemma 4 26B | `experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl` | 140 | 2 |

### ExECT `test60` structured

Same holdout roots as the 10 Aug family-lens / Prescription v10 confirmations.
Sol uses the credit-v2 re-run, not the superseded `exectv2_test60/gpt56sol` tree.

| Model | Structured sidecar | n | empty events |
| --- | --- | ---: | ---: |
| GPT-4.1-mini | `scratch/holdout/exectv2_test60/gpt41mini/gpt41mini_structured.jsonl` | 59 | 0 |
| GPT-5.6 Luna | `scratch/holdout/exectv2_test60/gpt56luna/gpt56luna_structured.jsonl` | 59 | 0 |
| GPT-5.6 Sol | `scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol/gpt56sol_structured.jsonl` | 59 | 0 |
| DeepSeek V4 Flash | `scratch/holdout/exectv2_test60/deepseek_v4_flash/deepseek_v4_flash_structured.jsonl` | 59 | 0 |
| Qwen 3.6:35B | `scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b/qwen36_35b_structured.jsonl` | 59 | 0 |
| Gemma 4 26B | `scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b/gemma4_26b_structured.jsonl` | 59 | 2 |

## 4. Fixed conditions

- Method: `llm_with_rules` only.
- Models: GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, DeepSeek V4 Flash,
  Qwen 3.6:35B, Gemma 4 26B.
- Replay: zero model calls.
  - Gan: `reuse_raw_outputs` through current `hybrid_full_stack`; prompt
    version is the **source** identity (`v0.5`). Repair code is HEAD.
  - ExECT: ordered no-call replay of structured sidecars through current
    `default` / `default` assembly (`StructuredMethodConfig.selected()`),
    the same `replay_letter` path as the 6 Aug hybrid stage ablation.
- Scorers: Gan Purist primary, Pragmatic secondary. ExECT four-family
  clinical fact F1 (`clinical_headline` / `headline_target`).
- Empty Gan parse after replay counts as incorrect. Empty ExECT structured
  events stay in the denominator as empty predictions.
- Holdout: `test450` and `test60` are aggregate-only. No restore of sealed
  ledgers for human reading. No letter IDs, source-row indices, note text,
  raw output, or mention lists in `experiments/`. Development `dev140` may
  record letter-level transition counts; holdout artifacts may not.

## 5. Comparators (frozen before scoring)

### Gan `test450` — same-raw before (scores stored in the v0.5 jsonl files)

| Model | Stored Purist | Stored Pragmatic | Parse-missing |
| --- | ---: | ---: | ---: |
| GPT-4.1-mini | 361 | 379 | 4 |
| GPT-5.6 Luna | 362 | 375 | 3 |
| GPT-5.6 Sol | 373 | 384 | 0 |
| DeepSeek V4 Flash | 344 | 366 | 3 |
| Qwen 3.6:35B | 362 | 384 | 2 |
| Gemma 4 26B | 355 | 374 | 2 |
| **Pooled** | **2157** | **2262** | **14** |

Historical **not same-raw** references (do not treat as this replay's before):

- 2026-08-03 final panel `test450` hybrid Purist: mini 0.8200, Luna 0.8089,
  Sol 0.8467 (381/450), DeepSeek 0.8178, Qwen 0.8000, Gemma 0.7911.
- 2026-08-11 cluster-v2 / baseline-refresh pooled Purist **2180/2700 (0.8074)**;
  Sol fill cited there is **381/450**. Those are later current-stack readouts
  on the same raw files, not the generation-time stored scores.

### ExECT `dev140` — published July / 0731 assembly `headline_target` F1

From the 2026-08-03 final panel (DeepSeek 0731):

| Model | Published hybrid F1 |
| --- | ---: |
| GPT-4.1-mini | 0.8202 |
| GPT-5.6 Luna | 0.8832 |
| GPT-5.6 Sol | 0.8920 |
| DeepSeek V4 Flash | 0.8994 |
| Qwen 3.6:35B | 0.8571 |
| Gemma 4 26B | 0.8016 |

### ExECT `test60` — Decision 0046 / 1 Aug stage panel hybrid F1

| Model | Published hybrid F1 |
| --- | ---: |
| GPT-4.1-mini | 0.7572 |
| GPT-5.6 Luna | 0.7950 |
| GPT-5.6 Sol | 0.8047 |
| DeepSeek V4 Flash | 0.8118 |
| Qwen 3.6:35B | 0.7872 |
| Gemma 4 26B | 0.7169 |

Sol `0.8047` is the Decision 0046 primary hybrid holdout fill.

## 6. Measurements

**Gan `test450` (aggregate only):**

- After Purist / Pragmatic counts and rates on all 450 rows per model
  (missing parse counts as incorrect).
- Pooled 2,700-cell Purist / Pragmatic.
- Rescue / harm counts versus the stored same-raw comparison fields.
- Parse-missing after versus before.

**ExECT `dev140`:**

- After four-family clinical fact F1, plus per-family F1.
- Letter-level all-family key exactness versus the saved assembly
  `predicted_mentions` (rescue / harm / unchanged).
- Unreplayable / empty-event counts.

**ExECT `test60` (aggregate only):**

- After four-family clinical fact F1, plus per-family F1.
- Empty-event counts.
- No letter IDs and no mention lists.

No new category catalog, no leave-one-out, no sealed-row inspection.

## 7. Decision rules

This is a **measurement**. It does not promote or delete a rule.

| Outcome | Documentation action |
| --- | --- |
| All three cells complete with zero live calls | Write the report and dated artifact. Update `PROJECT_STATUS.md` and the research index. Extend the six-model comparison-report addendum so it cites these current-stack readouts **beside** the historical tables. |
| A cell cannot complete (missing raw, identity failure) | Stop that cell. Do not invent scores. Record the blocker. Finish any cell that can complete. |

Do **not**:

- overwrite `experiments/six_model_final_panel_20260803/`;
- overwrite `experiments/exectv2_six_model_test60_stage_panel_20260801/`;
- overwrite `experiments/gan2026_six_model_validation_comparison_20260718.json`;
- change Decision 0046 / 0047 or C16 holdout fills;
- present Gan `test450` current-stack scores as a new selected paper fill
  without a separate promotion protocol;
- inspect or publish locked holdout rows.

## 8. Claim boundary

No-call current-repair evidence only. Gan `test450` is current repair on
**v0.5** saved outputs. ExECT cells are current `default` / `default`
assembly on saved v0.9.24 structured sidecars. Development `dev140` is not
holdout. Holdout cells are aggregate-only and are not authorization to
retune. Scores are not interchangeable across tasks.
