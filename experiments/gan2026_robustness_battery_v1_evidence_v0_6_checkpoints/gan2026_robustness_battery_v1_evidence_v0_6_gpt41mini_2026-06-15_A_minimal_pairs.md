# Gan 2026 LLM-First Validation Run

Date: 2026-06-15

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `robustness_battery` split, `authored_v1`, 12 rows.
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
- JSONL artifact: `C:/Users/cbrow/Code/clinical_extraction/experiments/gan2026_robustness_battery_v1_evidence_v0_6_checkpoints/gan2026_robustness_battery_v1_evidence_v0_6_gpt41mini_2026-06-15_A_minimal_pairs.jsonl`

## Summary

- Decision records: 12 / 12
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 5
- Exact evidence substrings: 11 / 12
- Purist validation accuracy/micro F1 proxy: 0.7500 (9 / 12)
- Pragmatic validation accuracy/micro F1 proxy: 0.7500 (9 / 12)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 990006 | unknown | unknown | yes | evidence_not_exact_substring |
| 990007 | 2 per 3 month | 2 per 3 month | yes |  |
| 990010 | 3 per 6 week | unknown | no | final_label_repaired: 'unknown' -> '3 per 6 week' |
| 990011 | 3 per 6 week | 3 per 6 week | yes |  |
| 990014 | no seizure frequency reference | unknown | yes |  |
| 990015 | 1 per month | 1 per month | yes |  |
| 990018 | multiple per day | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: '1 cluster per 4 to 5 week, multiple per cluster' -> 'multiple per day' |
| 990019 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | final_label_repaired: '1 per month' -> '1 per 4 to 5 week' |
| 990022 | seizure free for 4 month | seizure free for 4 month | yes |  |
| 990023 | unknown | unknown | yes |  |
| 990026 | 2 per 6 week | unknown | no | final_label_repaired: 'unknown' -> '2 per 6 week' |
| 990027 | 2 per 6 week | 2 per 6 week | yes | final_label_repaired: '2 per month' -> '2 per 6 week' |
