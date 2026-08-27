# 0050: Current-stack no-call hybrid fills are the selected primary scores

Date: 2026-08-13  
Status: accepted  
Amends: numeric hybrid fills implied by
[decision 0046](0046-exect-primary-method-comparison-boundary.md),
[canon scoring](../canon/04_scoring.md), and
[paper provenance](../canon/10_paper_provenance.md) C10 / C16 / C17  
Does not change: Decision 0046 method identity (Sol-matched three-method
comparison; `raw_lane_score` as LLM-only; `v08` and GEPA remain secondary),
[decision 0043](0043-gan-hosted-comparison-uses-v05-prompt.md) v0.5 prompt
identity, or rules-only / LLM-only fills (those cells were not replayed).
Six-model slot amendment: [decision 0052](0052-gemini-37-flash-holdout-six-model-slot.md)
replaces GPT-4.1-mini with Gemini 3.7 Flash in the living panel.

## Decision

The selected primary **LLM-with-rules** scores are the latest current-stack
no-call replay of the saved raws named in
[`paper_experiments/current_stack/SOURCES.json`](../../paper_experiments/current_stack/SOURCES.json).
Living numbers live in
[`paper_experiments/current_stack/latest/fills.json`](../../paper_experiments/current_stack/latest/fills.json).
Repeat the readout with
[the current-stack runbook](../runbooks/current_stack_six_model_replay.md).

The 14 Aug Sol snapshot (method-identity fill set after SF projection
v0.14 and Diagnosis convention/noise refinements) is:

| Cell | Selected primary hybrid fill |
| --- | ---: |
| ExECT Sol `dev140` | clinical fact F1 **0.9119** |
| ExECT Sol `test60` | clinical fact F1 **0.8302** |
| Gan Sol `test450` | Purist **380/450 (0.8444)** |

The 13 Aug snapshot was ExECT Sol `0.8895` / `0.8196` and the same Gan
380/450. That readout remains the historical current-stack panel in
`paper_experiments/current_stack/runs/20260813/`.

Gan `dev750` six-model current-stack remains the **v0.7** development readout
([13 Aug `dev750` replay](../research/gan2026/six_model_current_stack_dev750_replay_2026-08-13.md)).
It is not promoted over Decision 0043's selected v0.5 prompt. The selected
v0.5 development companion is still the GPT-4.1-mini 7 June cell at **682/750**.

## DeepSeek 0731 current-stack

DeepSeek V4 Flash holdout identity is the **0731** raws replayed through HEAD
on 2026-08-14:

- Gan `test450` hybrid **366/450 (0.8133)** versus stored 0731 368/450
- ExECT `test60` hybrid **0.8305** versus the 0731 live panel 0.8118
  (13 Aug current-stack was 0.8223)
- ExECT `dev140` hybrid **0.9171** (0731 structured sidecar; 13 Aug was
  0.8999)

The pre-0731 matched trees scored 348/450 and 0.8020 under the same HEAD
repairs. Those are not the selected DeepSeek fills.

## Why

HEAD repairs after the 1 Aug / 3 Aug panels, and the 14 Aug ExECT
SeizureFrequency projection landings through v0.14, change the scored
hybrid answer on the same saved model outputs. The paper and supervisor
glance should cite the current stack, not the generation-time or 13 Aug
snapshots. Gan is unchanged by the SF landings.

This is a no-call measurement promotion, not a new model run and not a
method-identity change.

## Consequences

- After each remasure, run `assemble` then the promote checklist. Do not
  silently edit canon or README from the machine stage.
- Keep `experiments/six_model_final_panel_20260803/` as the historical 3 Aug
  panel. Living machine cites use `paper_experiments/current_stack/latest/`.
- Do not rewrite retained-evidence `result_summary` for the original live-run
  packages; those hashes still describe the saved raw artifacts.
- Do not change LLM-only primary fills from this hybrid remasure.
  Rules-only fills were remasured separately on 2026-08-15 after the
  Investigations result-binding rewrite ([decision 0046 amendment](0046-exect-primary-method-comparison-boundary.md#2026-08-15-amendment--rules-only-investigations-result-binding)).
- Charts and HTML exhibits that still print the 3 Aug panel are stale pictures
  until regenerated; they are not claim owners.

## Evidence

- [Runbook](../runbooks/current_stack_six_model_replay.md)
- [Living fills](../../paper_experiments/current_stack/latest/fills.json)
- [Living panel](../../paper_experiments/current_stack/latest/panel_aggregate.json)
- [13 Aug remaining-cell report](../research/shared/six_model_current_stack_remaining_cells_replay_2026-08-13.md)
- [0731 matched comparison](../research/shared/deepseek_v4_flash_0731_matched_comparison_report_2026-08-03.md)
