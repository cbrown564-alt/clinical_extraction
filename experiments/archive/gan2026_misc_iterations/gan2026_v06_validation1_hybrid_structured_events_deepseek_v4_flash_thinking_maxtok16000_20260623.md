# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-23

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 1 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-v4-flash`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.6`
- Temperature: `0.0`
- Max tokens: `16000`
- Mode: `live`
- DSPy cache enabled: `False`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-23T20:12:01.417405+00:00`
- Run finished UTC: `2026-06-23T20:12:08.742972+00:00`
- Wall-clock elapsed: `7.326` seconds (`0.122` minutes)
- Throughput: `0.136508` rows/sec (`7.326` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `3e99131`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v06_validation1_hybrid_structured_events_deepseek_v4_flash_thinking_maxtok16000_20260623.jsonl`

## Summary

- Structured records: 0 / 1
- Call failures: 1
- Parse/schema/label issues: 1
- JSON dialect repairs: 0
- Deterministic repair notes: 0
- Exact selection evidence substrings: 0 / 1
- Purist validation accuracy/micro F1 proxy: 0.0000 (0 / 1)
- Pragmatic validation accuracy/micro F1 proxy: 0.0000 (0 / 1)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 |  | 4 per day | no | not_run; AuthenticationError: litellm.AuthenticationError: AuthenticationError: DeepseekException - Authentication Fails (governor); evidence_not_exact_substring |
