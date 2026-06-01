# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-first structured event extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 25 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first structured event extractor and clinical selector
- Prompt/program version: `gan2026_llm_structured_event_selector_v0.5`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `prompt-only`
- DSPy cache enabled: `True`
- Reused raw model outputs: `25`
- Reuse source: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair policy: raw structured model selection plus strict format-preserving basic label repair only.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=True`, `breakthrough_repair=False`, `dated_sequence_repair=False`, `elapsed_anchor_repair=False`, `monthly_diary_repair=False`, `non_epileptic_repair=False`, `post_change_burst_repair=False`, `residual_jerk_repair=False`, `selected_evidence_repair=False`, `usual_interval_repair=False`
- Git commit: `7f2bc88`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_structured_validation25_gpt41mini_v05_strict_format_replay2_2026-06-01.jsonl`

## Summary

- Structured records: 25 / 25
- Call failures: 0
- Parse/schema/label issues: 2
- Deterministic repair notes: 12
- Exact selection evidence substrings: 25 / 25
- Purist validation accuracy/micro F1 proxy: 0.8800 (22 / 25)
- Pragmatic validation accuracy/micro F1 proxy: 0.8800 (22 / 25)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: 'up to 4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per week | 1 per 7 day | yes |  |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 cluster per week | 1 per 7 to 9 day | no | unscorable_final_label: Unparsable cluster label: '1 cluster per week' |
| 190 | 1 cluster per 4 week | 1 per 4 week | no | final_label_repaired: '1 cluster per 4 weeks' -> '1 cluster per 4 week'; unscorable_final_label: Unparsable cluster label: '1 cluster per 4 week' |
| 198 | 1 per month | 1 per 4 week | yes |  |
| 212 | 1 per month | 1 per 3 to 4 week | no |  |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes |  |
| 409 | 1 per month | 1 per month | yes | final_label_repaired: '1 per month or less' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 2 per week | 2 per week | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |

## Interpretation

This no-call replay resolves the prior strict-format smoke blocker. Upper-bound
surface forms (`up to`, `<=`/`≤`, and `or less`) and `per quarter` are treated as
benchmark-format normalization because they preserve the selected count/range and
only make the label scorer-compatible.

Cluster-only labels remain raw attribution failures in this condition. Rows 187
and 190 now stay as cluster labels and fail scoring instead of being converted to
`unknown`; any conversion of cluster cadence into a countable Gan frequency needs
a named cluster module and ablation before it can support claim language.
