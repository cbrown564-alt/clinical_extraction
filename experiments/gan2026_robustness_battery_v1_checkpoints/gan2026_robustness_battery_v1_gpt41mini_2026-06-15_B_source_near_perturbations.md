# Gan 2026 LLM-First Validation Run

Date: 2026-06-15

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `robustness_battery` split, `authored_v1`, 7 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only direct-labeler note-to-label extractor
- Prompt/program version: `gan2026_llm_only_direct_labeler_v0.5`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `7`
- Reuse source: `C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_robustness_battery_v1_checkpoints\gan2026_robustness_battery_v1_gpt41mini_2026-06-15_B_source_near_perturbations.jsonl`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels, validates evidence, and scores.
- Git commit: `af23a16a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `C:/Users/cbrow/Code/clinical_extraction/experiments/gan2026_robustness_battery_v1_checkpoints/gan2026_robustness_battery_v1_gpt41mini_2026-06-15_B_source_near_perturbations.jsonl`

## Summary

- Decision records: 7 / 7
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 2
- Exact evidence substrings: 6 / 7
- Purist validation accuracy/micro F1 proxy: 0.7143 (5 / 7)
- Pragmatic validation accuracy/micro F1 proxy: 0.7143 (5 / 7)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 991006 | unknown | unknown | yes |  |
| 991010 | unknown | unknown | yes | evidence_not_exact_substring |
| 991014 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 991018 | unknown | unknown | yes |  |
| 991022 | no seizure frequency reference | unknown | yes |  |
| 991026 | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: '1 cluster per 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 991030 | unknown | unknown | yes |  |
