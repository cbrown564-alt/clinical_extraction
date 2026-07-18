# Gan 2026 LLM-Structured Validation Run

Date: 2026-07-18

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 1 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.7`
- Temperature: `0.0`
- Max tokens: `100`
- Mode: `prompt-only`
- DSPy cache enabled: `True`
- Reused raw model outputs: `1`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `clean_scorer_facing`
- Repair policy: raw structured model selection plus clean scorer-facing Gan gold-normalization policy.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=True`, `breakthrough_repair=False`, `clean_scorer_facing_gold_policy=True`, `dated_sequence_repair=False`, `elapsed_anchor_repair=False`, `json_dialect_repair=True`, `monthly_diary_repair=False`, `non_epileptic_repair=False`, `post_change_burst_repair=False`, `repair_mode=clean_scorer_facing`, `residual_jerk_repair=False`, `selected_evidence_repair=False`, `usual_interval_repair=False`
- Git commit: `6c6df72c`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `C:/Users/cbrow/Code/clinical_extraction/.tmp/status-audit-20260718/test_write_report_names_clean_0/rows.jsonl`

## Summary

- Structured records: 1 / 1
- Call failures: 0
- Parse/schema/label issues: 0
- Initial parse/schema/label issues: 0
- Format retries applied: 0
- Format retries rejected: 0
- JSON dialect repairs: 0
- Deterministic repair notes: 1
- Exact selection evidence substrings: 1 / 1
- Purist validation accuracy/micro F1 proxy: 0.0000 (0 / 1)
- Pragmatic validation accuracy/micro F1 proxy: 0.0000 (0 / 1)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | multiple per week | 2 per month | no | final_label_repaired: 'most weekdays' -> 'multiple per week' |
