# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-24

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 30 rows.
Rare full-validation reason: full_validation750_diagnostic_after_test450_gap_continue_from_validation250_validation_only_error_analysis
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-reasoner`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.6`
- Temperature: `0.0`
- Max tokens: `32000`
- Mode: `live`
- DSPy cache enabled: `False`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `3a866bf`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260624.resume-part.jsonl`

## Summary

- Structured records: 30 / 30
- Call failures: 0
- Parse/schema/label issues: 0
- JSON dialect repairs: 0
- Deterministic repair notes: 13
- Exact selection evidence substrings: 30 / 30
- Purist validation accuracy/micro F1 proxy: 0.9333 (28 / 30)
- Pragmatic validation accuracy/micro F1 proxy: 0.9333 (28 / 30)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: '1 per 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per 8 days' -> '1 per 8 day' |
| 5682 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 5696 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 events per 4 months' -> '3 per 4 month' |
| 5763 | 2 to 3 per month | 2 per month | yes |  |
| 5767 | 1 per 1 to 2 week | 1 per 1 to 2 week | yes | final_label_repaired: 'every 1-2 weeks' -> '1 per 1 to 2 week' |
| 5791 | 1 per month | 1 per month | yes |  |
| 5827 | multiple per week | multiple per week | yes |  |
| 5837 | unknown | 2 cluster per 3 week, multiple per cluster | no | final_label_repaired: '2 clusters in 3 weeks' -> 'unknown' |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '2 to 3 per month' -> '4 per 6 week' |
| 5873 | multiple per week | multiple per week | yes |  |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6-8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: 'less than once per week' -> '1 per 2 to 3 week' |
| 5974 | unknown | unknown | yes |  |
| 5977 | multiple per 6 week | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per 6 week' |
| 5995 | 3 per 7 month | 1 per 3 months | yes | final_label_repaired: 'less than 1 per month' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '3 per 7 month' |
| 5996 | unknown | unknown | yes |  |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes |  |
| 6034 | unknown | unknown | yes |  |
| 6065 | 5 per month | 5 per month | yes |  |
| 6077 | 1 per 8 month | unknown | no | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 6087 | unknown | unknown | yes |  |
| 6094 | 2 to 3 per month | 3 per month | yes |  |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 6131 | unknown | unknown | yes |  |
| 6137 | 1 per 2 to 3 week | 1 per 2 week | yes | final_label_repaired: '1 per 2-3 weeks' -> '1 per 2 to 3 week' |
| 6153 | 6 per month | 9 per month | yes |  |
| 6180 | multiple per week | multiple per week | yes |  |
