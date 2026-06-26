# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-20

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 1 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `None`
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.6`
- Temperature: `0.0`
- Max tokens: `2400`
- Mode: `live`
- DSPy cache enabled: `True`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-20T00:27:40.540069+00:00`
- Run finished UTC: `2026-06-20T00:29:00.034912+00:00`
- Wall-clock elapsed: `79.495` seconds (`1.325` minutes)
- Throughput: `0.012579` rows/sec (`79.495` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `6d226f4`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/_tmp_qwen_se_v06_smoke_validation1_2026-06-19.jsonl`

## Summary

- Structured records: 1 / 1
- Call failures: 0
- Parse/schema/label issues: 0
- JSON dialect repairs: 1
- Deterministic repair notes: 1
- Exact selection evidence substrings: 1 / 1
- Purist validation accuracy/micro F1 proxy: 1.0000 (1 / 1)
- Pragmatic validation accuracy/micro F1 proxy: 1.0000 (1 / 1)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 4 per day' -> '4 per day' |
