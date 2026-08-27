# Protocol: Gan 2026 six-model current-stack `dev750` hybrid replay

Date: 2026-08-13  
Status: **complete** (predeclared before scoring; executed 2026-08-13)  
Parents: [Decision 0043](../../decisions/0043-gan-hosted-comparison-uses-v05-prompt.md),
[Decision 0047](../../decisions/0047-gan-primary-orchestration-and-scoring-boundary.md),
[July 18 six-model comparison protocol](../../experiments/gan2026/gan2026_six_model_validation_comparison_protocol_2026-07-18.md),
[July 31 floors replay](../../experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json)  
Report target: `docs/research/gan2026/six_model_current_stack_dev750_replay_2026-08-13.md`  
Artifact target: `experiments/gan2026_six_model_current_stack_dev750_replay_20260813/`

## 1. Primary question

On the six retained models, what do current `llm_with_rules` repairs score on
Gan `dev750` when the **same saved raw model outputs** are replayed with no
new calls?

This is a current-stack no-call readout. It is not a new model run. It is not
a rules-only or LLM-only study. It does not rewrite Decision 0046 / 0047
primary fills or C16 holdout numbers.

## 2. Why this study

The GPT-4.1-mini v0.5 June cell now scores 682/750 Purist under HEAD versus
661 on the 7 June finals. Published six-model `dev750` JSON still prints the
July 18 / July 27 numbers (for example mini 653 on the v0.7 LFS panel, 668 on
the v0.5 July 27 panel). Cluster and diary studies already measured other
models piecemeal. This protocol regenerates one six-model current-stack
replay and the docs that should cite it.

## 3. Available inputs (declared before scoring)

| Input | Prompt identity | Role |
| --- | --- | --- |
| `experiments/gan2026_six_model_validation_20260718/*--llm_with_rules.jsonl` | `gan2026_hybrid_structured_events_v0.7` | **Primary six-model raw source.** All six models, 750 rows, raw outputs present. This is the published July 18 development panel. |
| `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl` | v0.5 | **Companion mini cell only.** Selected prompt identity. |
| `scratch/validation/gan2026_matched_v05_dev750_20260727/` | v0.5 six-model | **Absent.** Gitignored and not on this checkout. July 27 v0.5 six-model raw cannot be replayed here. |
| `scratch/holdout/gan2026_matched_v05/` | v0.5 test450 | **Absent.** No test450 hybrid replay in this study. |

## 4. Fixed conditions

- Dataset / split: Gan 2026 `validation` (`dev750`); row review permitted.
- Method: `llm_with_rules` only. Rules-only and LLM-only are out of scope.
- Models: GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, DeepSeek V4 Flash,
  Qwen 3.6:35B, Gemma 4 26B.
- Replay: `reuse_raw_outputs` through current `hybrid_full_stack`. Zero model
  calls.
- Prompt version set on replay matches the **source artifact** (v0.7 for the
  six-model cell; v0.5 for the mini companion). Repair code is HEAD.
- Scorer: Gan Purist primary; Pragmatic secondary.
- Holdout: `test450` sealed; no restore of sealed ledgers; no row inspection.

## 5. Comparators (frozen before scoring)

Primary six-model cell, from the July 18 LFS files themselves:

| Model | July 18 saved Purist | July 18 saved Pragmatic | Parse-missing rows |
| --- | ---: | ---: | ---: |
| GPT-4.1-mini | 653 | 674 | 1 |
| GPT-5.6 Luna | 646 | 669 | 5 |
| GPT-5.6 Sol | 655 | 672 | 0 |
| DeepSeek V4 Flash | 643 | 664 | 1 |
| Qwen 3.6:35B | 667 | 683 | 3 |
| Gemma 4 26B | 646 | 674 | 8 |
| **Pooled** | **3910** | **4036** | **18** |

Historical **not same-raw** references (do not treat as this replay's before):

- 7 June mini v0.5 finals: 661 / 679 Purist / Pragmatic.
- 27 July v0.5 six-model panel aggregates in
  `experiments/gan2026_matched_v05_dev750_panel_20260727.json`.
- 31 July floors replay after-scores in
  `experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json`.

## 6. Measurements

For each model and for the 4,500-cell pool:

- After Purist / Pragmatic counts and rates on all 750 rows (missing parse
  counts as incorrect).
- Changed final labels versus the July 18 saved finals.
- Purist / Pragmatic rescue and harm counts.
- Parse-missing after versus before.
- Companion: June 7 mini v0.5 replay versus 661 / 679 (expected ~682 / 696
  if HEAD is unchanged).

No new category catalog, no LOO, no holdout aggregates.

## 7. Decision rules

This is a **measurement**. It does not promote or delete a rule.

| Outcome | Documentation action |
| --- | --- |
| Replay completes with 6×750 rows and zero live calls | Write the report and dated artifact. Update `PROJECT_STATUS.md` and the research index. Add a dated addendum to the six-model comparison report that cites this current-stack v0.7 `dev750` readout **beside** the historical tables, without replacing holdout or July 18 historical figures. |
| Replay cannot complete (missing raw, identity failure) | Stop. Do not invent scores. Record the blocker. |

Do **not**:

- overwrite `experiments/six_model_final_panel_20260803/`;
- overwrite `experiments/gan2026_six_model_validation_comparison_20260718.json`;
- change Decision 0046 / 0047 or C16 holdout fills;
- present this v0.7 current-stack replay as the selected v0.5 six-model panel.

## 8. Claim boundary

Development no-call evidence only. The six-model cell is current repair on
**v0.7** saved outputs. The selected paper prompt remains v0.5; that six-model
raw set is not on this checkout. Synthetic `dev750` scores are not holdout
generalization.
