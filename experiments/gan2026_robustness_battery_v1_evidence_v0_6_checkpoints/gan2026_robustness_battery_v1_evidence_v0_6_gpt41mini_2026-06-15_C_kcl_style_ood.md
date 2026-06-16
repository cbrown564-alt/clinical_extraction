# Gan 2026 LLM-First Validation Run

Date: 2026-06-15

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `robustness_battery` split, `authored_v1`, 8 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only direct-labeler note-to-label extractor
- Prompt/program version: `gan2026_llm_only_direct_labeler_v0.6`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels, validates evidence, and scores.
- Git commit: `af23a16a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `C:/Users/cbrow/Code/clinical_extraction/experiments/gan2026_robustness_battery_v1_evidence_v0_6_checkpoints/gan2026_robustness_battery_v1_evidence_v0_6_gpt41mini_2026-06-15_C_kcl_style_ood.jsonl`

## Summary

- Decision records: 8 / 8
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 0
- Exact evidence substrings: 8 / 8
- Purist validation accuracy/micro F1 proxy: 1.0000 (8 / 8)
- Pragmatic validation accuracy/micro F1 proxy: 1.0000 (8 / 8)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 992007 | unknown | unknown | yes |  |
| 992011 | unknown | unknown | yes |  |
| 992015 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 992019 | 2 per month | 2 per month | yes |  |
| 992023 | 1 per week | 1 per week | yes |  |
| 992027 | 1 cluster per 3 week, multiple per cluster | 1 cluster per 3 week, multiple per cluster | yes |  |
| 992031 | unknown | unknown | yes |  |
| 992035 | unknown | unknown | yes |  |
