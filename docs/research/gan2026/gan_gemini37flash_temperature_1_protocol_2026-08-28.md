# Protocol: Gemini 3.7 Flash `gan_llm_extract` at temperature 1

Date: 2026-08-28
Status: complete; report
[gan_gemini37flash_temperature_1_2026-08-28.md](gan_gemini37flash_temperature_1_2026-08-28.md)
Owner: this file
Roster: [`paper_experiments/roster.json`](../../../paper_experiments/roster.json)
Related: [Grok temperature 0](gan_grok46_temperature_0_2026-08-28.md),
[six-model roster](../../paper/decisions/six-model-roster.md),
[experiment environment](../../paper/experiment_environment.md)

## Question

Does Gemini 3.7 Flash complete living cell-3 Gan extract
(`gan_llm_extract`) on `dev750` and locked `test450` when
temperature is `1.0` instead of the living paper setting `0.0`?

This is the matched reverse of the Grok temperature-0 ablation.
It does not ask whether to change the living Gemini setting.

## Why it matters

Living Gemini, Grok, DeepSeek, Qwen, and Gemma request temperature
`0.0`. Luna stays at `1.0` because that provider rejects `0`.
Grok at `0` left holdout select **12** letters lower than its cited
temperature-1 cell. A Gemini temperature-1 pair on the same cell
shows whether that shift is Grok-specific or a temperature effect
on codebook recognise plus rule select.

## Data and row policy

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Splits | `dev750` then `test450` (`gan2026_split_v1`) |
| Rows | 750 development; 450 holdout |
| Method | `gan_llm_extract` (cell 3 recognise) |
| Model | `gemini37flash` / `gemini/gemini-3.7-flash` |
| Candidate | temperature `1.0`; other living Gemini fields unchanged |
| Comparator | living Gemini temperature `0.0` (not overwritten) |
| Scorer | Purist accuracy; Pragmatic is secondary |
| `dev750` row policy | development review permitted |
| `test450` row policy | aggregate-only |
| Inspection | Do not inspect holdout identifiers, notes, predictions, evidence, or errors |

The runner may read locked notes only to make the frozen calls.

## Frozen condition

| Field | Value |
| --- | --- |
| Temperature | `1.0` (non-living; `--temperature 1`) |
| Reasoning | `low` |
| Max tokens | 5,000 |
| Cache | off |
| Transport | OpenRouter batch |
| Work cells | `experiments/paper/gan_llm_extract/gemini37flash/temperature_1/dev750/` and `scratch/holdout/paper/gan_llm_extract/gemini37flash/temperature_1/test450/` |

Do not write these runs into the living Gemini work cell or promote
them to `paper_experiments/`. Do not start later-stage LLM encode or
select. Select is a no-call `llm_select` replay of the new raws.
Do not retune from holdout rows.

## Stop rule

- **Answer:** both extracts complete with 750 and 450 scored rows
  and aggregate Purist/Pragmatic recognise and select stops.
- **Negative:** route rejects `1` or either run fails before a
  complete aggregate.
- **Not a promotion:** even a higher score stays a temperature
  ablation.

## Claim boundary

Diagnostic temperature ablation. Not a living roster change. Not a
matched latency or cost study. Holdout is not row-level mechanism
evidence.
