# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-21

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `test` split, `gan2026_split_v1`, 450 rows.
Rare full-validation reason: Frozen aggregate-only Qwen v0.6 hybrid_structured_events repairfix test450 audit; candidate code, prompt, model, scorer, split, and repair policy frozen before run; no test row-level inspection for development.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.6`
- Temperature: `0.0`
- Max tokens: `2400`
- Mode: `live`
- DSPy cache enabled: `True`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-21T13:13:34.029836+00:00`
- Run finished UTC: `2026-06-21T17:48:44.163612+00:00`
- Wall-clock elapsed: `16510.133` seconds (`275.169` minutes)
- Throughput: `0.027256` rows/sec (`36.689` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `b179abf`
- Working tree note: `dirty/uncommitted local changes; includes frozen repairfix candidate code`
- JSONL artifact: `experiments/gan2026_v06_test450_hybrid_structured_events_qwen3635b_repairfix_2026-06-21.jsonl`

## Summary

- Structured records: 386 / 450
- Call failures: 63
- Parse/schema/label issues: 64
- JSON dialect repairs: 386
- Deterministic repair notes: 265
- Exact selection evidence substrings: 316 / 450
- Purist validation accuracy/micro F1 proxy: 0.7067 (318 / 450)
- Pragmatic validation accuracy/micro F1 proxy: 0.7311 (329 / 450)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 31 |  | 4 per day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 51 |  | 5 per week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 61 |  | 4 per week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 115 |  | 7 to 8 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 136 |  | 6 to 7 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 174 |  | 1 per 1 to 3 day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 176 |  | 1 per 6 to 7 day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 234 |  | 1 per 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 240 |  | 1 per 2 to 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server process has terminated: exit status 0xc0000409: The system detected an overrun of a stack-based buffer in this application. This overrun could potentially allow a malicious user to gain control of this application.: CUDA error"}; evidence_not_exact_substring |
| 364 |  | 1 per week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 493 |  | 11 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 503 |  | 11 to 28 per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 538 |  | 1 per 4 day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 610 |  | 1 per 2 to 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 632 |  | 1 per 1 to 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 666 |  | 2 per 2 to 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 685 |  | 1 per day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 714 |  | 2 per day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 722 |  | 1 per day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 735 |  | 1 per day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 739 |  | multiple per week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 748 |  | 1 per 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 750 |  | multiple per week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 803 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 804 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 824 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 836 |  | 1 per year | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 841 |  | 1 per year | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 892 |  | 1 per 2 day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 934 |  | 1 per 2 week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 938 |  | 1 per 2 week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 1005 |  | multiple per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 1017 |  | 1 per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 1060 |  | 6 to 7 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 1182 |  | 6 to 14 per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 1184 |  | 6 to 14 per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 1250 |  | 2 to 4 per week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 1289 |  | 5 to 6 per year | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 1290 |  | 8 to 9 per year | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 1326 |  | multiple per day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 1378 | 5 per month | 5 per month | yes | json_dialect_repaired: python_literal |
| 1422 | 9 per week | 9 per week | yes | json_dialect_repaired: python_literal |
| 1433 | 4 per month | 4 per month | yes | json_dialect_repaired: python_literal |
| 1460 | 7 per month | 7 per month | yes | json_dialect_repaired: python_literal |
| 1497 | 2 per month | 3 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per month' -> '2 per month' |
| 1511 | 7 per month | 7 per month | yes | json_dialect_repaired: python_literal |
| 1534 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 1624 | 12 per week | 12 per week | yes | json_dialect_repaired: python_literal |
| 1629 | 7 per month | 12 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '12 per month' -> '7 per month' |
| 1633 | 7 per week | 12 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '12 per week' -> '7 per week' |
| 1656 | 5 per month | 5 per month | yes | json_dialect_repaired: python_literal |
| 1683 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per month' -> 'multiple per month' |
| 1705 | unknown | 1 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'cluster' -> 'unknown' |
| 1722 | 3 per 2 month | 3 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 events in 2 months' -> '3 per 2 month' |
| 1736 | 1 per 6 month | 4 per 6 month | no | json_dialect_repaired: python_literal; final_label_repaired: '4 seizures per 6 months' -> '1 per 6 month' |
| 1812 | 12 per 3 month | 12 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '12 seizures in 3 months' -> '12 per 3 month' |
| 1868 | 8 per 2 month | 8 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 seizures in 2 months' -> '8 per 2 month' |
| 1883 | 4 per 3 month | 4 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 events in 3 months' -> '4 per 3 month' |
| 1889 | 4 per 6 month | 4 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 seizures in 6 months' -> '4 per 6 month' |
| 1898 | 4 per 6 month | 4 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 seizures in 6 months' -> '4 per 6 month' |
| 1911 | 7 per 2 month | 7 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 seizures in 2 months' -> '7 per 2 month' |
| 1934 | 2 per 2 month | 7 per 2 month | no | json_dialect_repaired: python_literal; final_label_repaired: '7 seizures in 2 months' -> '2 per 2 month' |
| 1938 | 5 per 4 month | 5 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 seizures in 4 months' -> '5 per 4 month' |
| 2071 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 2112 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 2135 | multiple per month | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional' -> 'multiple per month' |
| 2220 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2226 | 3 to 10 per 2 week | 3 to 10 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 to 10 per 2 weeks' -> '3 to 10 per 2 week' |
| 2246 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 to 8 per 3 weeks' -> '7 to 8 per 3 week' |
| 2262 | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 to 9 per 3 weeks' -> '7 to 9 per 3 week' |
| 2306 | 8 to 9 per month | 8 to 9 per month | yes | json_dialect_repaired: python_literal |
| 2311 | 5 to 7 per month | 5 to 7 per month | yes | json_dialect_repaired: python_literal |
| 2356 | 6 to 7 per week | 6 to 7 per week | yes | json_dialect_repaired: python_literal |
| 2404 | 6 to 7 per month | 6 to 7 per month | yes | json_dialect_repaired: python_literal |
| 2486 | 2 to 3 per month | 2 to 3 per 3 month | no | json_dialect_repaired: python_literal |
| 2543 | 2 to 4 per 2 week | 2 to 4 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 per 2 weeks' -> '2 to 4 per 2 week' |
| 2564 | 3 to 5 per 2 month | 3 to 5 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 to 5 per 2 months' -> '3 to 5 per 2 month' |
| 2596 | 2 per day | 2 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per night' -> '2 per day' |
| 2597 | multiple per day | 2 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per night' -> 'multiple per day' |
| 2652 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal |
| 2684 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal |
| 2725 | 1 to 2 per month | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster every 2 weeks and 1-2 per month' -> '1 to 2 per month'; evidence_not_exact_substring |
| 2749 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 2781 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal |
| 2795 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal |
| 2854 | 2 per month | 2 per month | yes | json_dialect_repaired: python_literal |
| 2879 | 2 per day | 2 per day | yes | json_dialect_repaired: python_literal |
| 2978 | seizure free for multiple year | seizure free for 9 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 24/6/2021' -> 'seizure free for multiple year' |
| 3054 | seizure free for 16 month | seizure free for 16 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3102 | seizure free for 14 month | seizure free for 14 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month'; evidence_not_exact_substring |
| 3214 | 1 cluster per month, 7 per cluster | 1 cluster per month, 5 to 7 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 to 7 per month in clusters' -> '1 cluster per month, 7 per cluster' |
| 3225 | 1 cluster per month, 10 per cluster | 1 cluster per month, 3 to 10 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'monthly clusters of 3-10 seizures' -> '1 cluster per month, 10 per cluster' |
| 3237 | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 clusters per month, ~5 events per cluster' -> '4 cluster per month, 5 per cluster' |
| 3246 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month, approx 8 total events' -> '2 cluster per month, 4 per cluster' |
| 3291 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 3293 | 8 per month | 8 per month | yes | json_dialect_repaired: python_literal |
| 3300 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 3327 | 5 to 6 per year | 5 to 6 per year | yes | json_dialect_repaired: python_literal |
| 3329 | 2 to 3 per day | 2 to 3 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '2 to 3 per day' |
| 3340 | 2 to 3 per month | 2 to 3 per month | yes | json_dialect_repaired: python_literal |
| 3353 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3355 | no seizure frequency reference | 1 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: '2 in 6 months' -> 'no seizure frequency reference' |
| 3407 | multiple per day | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per night' -> 'multiple per day' |
| 3452 | 6 to 8 per month | 6 to 8 per month | yes | json_dialect_repaired: python_literal |
| 3514 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3630 | 7 per week | 7 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'up to 7 per week' -> '7 per week' |
| 3638 | 3 per week | 3 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'up to 3 per week' -> '3 per week' |
| 3675 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 3706 | 6 per week | 6 per week | yes | json_dialect_repaired: python_literal |
| 3747 | 1 per day | 3 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per day' -> '1 per day'; evidence_not_exact_substring |
| 3831 | 7 per month | 7 per month | yes | json_dialect_repaired: python_literal |
| 3864 | 3 per day | 3 per day | yes | json_dialect_repaired: python_literal |
| 3867 | 3 per day | 3 per day | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 3888 | 8 per year | 8 per year | yes | json_dialect_repaired: python_literal |
| 3906 | 4 per year | 4 per year | yes | json_dialect_repaired: python_literal |
| 3918 | 9 per week | 9 per week | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 3934 | 9 per week | 9 per week | yes | json_dialect_repaired: python_literal |
| 4003 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 4004 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'abs ×monthly' -> '1 per month' |
| 4073 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4076 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4197 | no seizure frequency reference | 1 per 2 day | no | json_dialect_repaired: python_literal; final_label_repaired: 'approximately every second day' -> 'no seizure frequency reference' |
| 4217 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 4239 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 4342 | 5 per 3 month | 5 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '5 per 3 month'; evidence_not_exact_substring |
| 4352 | 5 per 10 month | 5 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: '5 seizures in the past 3 months' -> '5 per 10 month' |
| 4424 | 6 per 8 month | 3 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 4 month' -> '6 per 8 month'; evidence_not_exact_substring |
| 4679 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '~10 per hour' -> 'multiple per day' |
| 4707 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 4809 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'clusters' -> 'unknown' |
| 4831 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 4892 | seizure free for 11 month | seizure free for 11 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 4903 | seizure free for 1 year | seizure free for 1 year | yes | json_dialect_repaired: python_literal |
| 4967 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for many months' -> 'seizure free for multiple year' |
| 4996 | seizure free for multiple year | seizure free for 16 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for >1 year' -> 'seizure free for multiple year' |
| 5088 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for recent months' -> 'seizure free for multiple year' |
| 5174 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5213 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5385 | seizure free for multiple year | seizure free for 1 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 5395 | seizure free for multiple year | seizure free for 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 month' -> 'seizure free for multiple year' |
| 5505 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5527 | 1 per year | 1 per year | yes | json_dialect_repaired: python_literal |
| 5540 | seizure free for 1 month | 1 per 4 to 5 month | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 5555 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 5627 | 1 per 5 day | 1 per 5 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 5 days' -> '1 per 5 day' |
| 5653 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'every 2 days' -> '1 per 2 day' |
| 5684 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clusters)' -> 'unknown' |
| 5708 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'clusters of brief events' -> 'unknown' |
| 5764 | 3 per month | 3 per month | yes | json_dialect_repaired: python_literal |
| 5766 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 5976 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6025 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters in 6 months' -> 'unknown' |
| 6028 | seizure free for multiple year | 1 per 3 months | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 3 months ago' -> 'seizure free for multiple year' |
| 6063 | 3 per month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '3 per month'; evidence_not_exact_substring |
| 6073 | 1 per 6 month | 1 per 3 to 4 weeks | no | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3-4 weeks' -> '1 per 6 month' |
| 6164 | multiple per month | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional' -> 'multiple per month' |
| 6216 | 4 per 6 week | 4 per 6 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 in 6 weeks' -> '4 per 6 week' |
| 6252 | 2 to 4 per month | 2 to 4 per month | yes | json_dialect_repaired: python_literal |
| 6288 | 2 per 10 week | 2 per 10 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 10 weeks' -> '2 per 10 week' |
| 6296 | 3 per 4 month | 3 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6303 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple episodes over several days (clusters)' -> 'unknown'; evidence_not_exact_substring |
| 6330 | multiple per week | multiple per month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 6365 | 10 per 14 month | unknown, 1 to 2 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (during trigger exposure)' -> '1 to 2 per 10 month'; final_label_repaired: '1 to 2 per 10 month' -> '10 per 14 month'; evidence_not_exact_substring |
| 6380 | 2 per 3 month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'several per month' -> '2 per 3 month' |
| 6387 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 events since last contact' -> 'no seizure frequency reference' |
| 6408 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6592 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 6661 | 3 per 6 week | 0.5 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per 6 weeks' -> '3 per 6 week' |
| 6763 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per week' |
| 6775 | seizure free for 4 month | 1 per 5 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; evidence_not_exact_substring |
| 6787 | 11 per 6 week | 8 per 6 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 per 6 weeks' -> '11 per 6 week'; evidence_not_exact_substring |
| 6909 | 4 per 3 month | 1 per 2 to 3 weeks | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '4 per 3 month' |
| 6929 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 6930 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6976 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6979 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6986 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7005 | 2 per 6 month | 2 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 7047 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7061 | 2 to 3 per week | 2 per 6 week | no | json_dialect_repaired: python_literal |
| 7232 | 6 to 8 per month | 6 to 8 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal |
| 7280 | 5 per month | 5 per month | yes | json_dialect_repaired: python_literal |
| 7318 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week'; evidence_not_exact_substring |
| 7327 | 2 per 4 month | 2 per 4 months | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 7328 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7341 | 2 per month | unknown | no | json_dialect_repaired: python_literal |
| 7386 | 2 per 8 week | 7 per 8 week | no | json_dialect_repaired: python_literal; final_label_repaired: '7 in 8 weeks' -> '2 per 8 week' |
| 7393 | multiple per week | unknown | yes | json_dialect_repaired: python_literal |
| 7405 | 1 per multiple month | 1 per multiple months | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per few months' -> '1 per multiple month' |
| 7431 | 2 per 8 week | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 8 weeks' -> '2 per 8 week' |
| 7670 | 1 per day | multiple per week | no | json_dialect_repaired: python_literal; final_label_repaired: 'daily focal aware seizures with recent nocturnal convulsions' -> '1 per day'; evidence_not_exact_substring |
| 7688 | seizure free for 1 year | seizure free for 1 year | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7708 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7712 | seizure free for 3 month | 2 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 7719 | seizure free for 4 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 7783 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 7816 | seizure free for 1 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 7863 | seizure free for 2 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 7884 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7892 | seizure free for 4 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7935 | no seizure frequency reference | seizure free for multiple month | no | json_dialect_repaired: python_literal; final_label_repaired: 'low frequency / controlled' -> 'no seizure frequency reference' |
| 7958 | seizure free for 3 year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 years' -> 'seizure free for 3 year' |
| 7987 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7993 | 2 to 3 per 1 to 2 day | unknown, 2 to 3 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per 1-2 days' -> '2 to 3 per 1 to 2 day' |
| 8109 | seizure free for 12 month | seizure free for 12 month | yes | json_dialect_repaired: python_literal |
| 8116 | seizure free for 12 month | seizure free for 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8127 | seizure free for 18 month | seizure free for 18 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month'; evidence_not_exact_substring |
| 8135 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 8169 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since late May 2025' -> 'seizure free for multiple year' |
| 8221 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8222 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8244 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 8286 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8342 | seizure free for 9 month | seizure free for 9 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 8346 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since late February 2025' -> 'seizure free for multiple year' |
| 8423 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 10 weeks' -> 'seizure free for multiple year' |
| 8432 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2-3 months' -> '1 per 2 to 3 month' |
| 8488 | 11 per 2 month | seizure free for multiple month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since April' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '11 per 2 month' |
| 8540 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 8624 | seizure free for 13 month | seizure free for 13 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8645 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8723 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8790 | seizure free for 2 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8791 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year' |
| 8799 | seizure free for 3 month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8813 | no seizure frequency reference | seizure free for multiple month | no | json_dialect_repaired: python_literal; final_label_repaired: 'once every few weeks' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 8852 | seizure free for 6 month | seizure free for 8 month | yes | json_dialect_repaired: python_literal |
| 8858 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8954 | seizure free for 8 month | seizure free for 8 month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 8957 | seizure free for 8 month | seizure free for 8 month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 8979 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 4+ years' -> 'seizure free for multiple year' |
| 9014 | seizure free for 11 month | seizure free for 11 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month'; evidence_not_exact_substring |
| 9065 | seizure free for 1 year | seizure free for 13 month | yes | json_dialect_repaired: python_literal |
| 9109 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'decreased frequency' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 9114 | 1 per 4 to 6 week | 1 per 4 to 6 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month to 1 per 6 weeks' -> '1 per 4 to 6 week' |
| 9147 | no seizure frequency reference | seizure free for multiple month | no | json_dialect_repaired: python_literal |
| 9179 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since mid-August' -> 'seizure free for multiple year' |
| 9189 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9202 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9212 | seizure free for 3 month | seizure free for 3 months | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 9251 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9279 | 1 to 2 per week | 1 to 2 per week | yes | json_dialect_repaired: python_literal |
| 9294 | 3 to 4 per week | 3 to 4 per week | yes | json_dialect_repaired: python_literal |
| 9377 | 1 per 2 week | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 9471 | 8 per 14 month | 7 per 11 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 month' -> '8 per 14 month'; evidence_not_exact_substring |
| 9483 | 16 per 12 month | 8 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per 6 months' -> '8 per 6 month'; final_label_repaired: '8 per 6 month' -> '16 per 12 month'; evidence_not_exact_substring |
| 9562 | 1 to 2 per 1 year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'cluster over 1-2 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 to 2 per 1 year' |
| 9566 | 1 to 2 per week | unknown | no | json_dialect_repaired: python_literal |
| 9601 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9618 | seizure free for 4 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; evidence_not_exact_substring |
| 9654 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9696 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 9786 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'increasing frequency with clusters' -> 'unknown'; evidence_not_exact_substring |
| 9801 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 9891 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 9926 | 1 per month | 1 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'monthly clusters' -> '1 per month' |
| 9942 | 1 per month | 1 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 9946 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 9979 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 to 4 clusters per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10009 | unknown | 1 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10031 | unknown | 1 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown frequency (grouped events)' -> 'unknown' |
| 10052 | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 clusters per quarter' -> '4 cluster per 3 month, multiple per cluster' |
| 10159 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10186 | 3 to 5 per 12 month | unknown, 3 to 5 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '3 to 5 per cluster' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 to 5 per 12 month' |
| 10213 | unknown | unknown, 3 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (cluster pattern)' -> 'unknown' |
| 10292 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clusters and discrete events)' -> 'unknown'; evidence_not_exact_substring |
| 10298 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10316 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'clusters on weekends/off-duty days' -> 'unknown' |
| 10330 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (cluster tendency)' -> 'unknown'; evidence_not_exact_substring |
| 10398 | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week (2 seizures)' -> '1 cluster per week, 2 per cluster' |
| 10408 | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'weekly, 3-5 per cluster' -> '1 cluster per week, 3 to 5 per cluster' |
| 10441 | multiple per week | unknown | yes | json_dialect_repaired: python_literal |
| 10445 | unknown | 9 cluster per month, 2 to 4 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple clusters per week, increasing to 9 cluster-days in September' -> 'unknown'; evidence_not_exact_substring |
| 10447 | multiple per week | unknown | yes | json_dialect_repaired: python_literal |
| 10514 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (including 2 GTCS)' -> 'multiple per week' |
| 10538 | unknown | unknown, 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per hour (cluster)' -> 'unknown' |
| 10553 | unknown | unknown, 2 to 3 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per hour (in clusters)' -> 'unknown' |
| 10621 | unknown | multiple cluster per week, 4 to 6 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clusters of 4-6)' -> 'unknown' |
| 10737 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10751 | 24 to 48 per 4 month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'infrequent, clustered with travel' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '24 to 48 per 4 month'; evidence_not_exact_substring |
| 10794 | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 clusters per month' -> '3 cluster per month, multiple per cluster' |
| 10795 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month' -> '2 cluster per month, multiple per cluster' |
| 10863 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'weekly clusters' -> '1 cluster per week, multiple per cluster' |
| 10884 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'weekly clusters of 3-4 seizures' -> '1 cluster per week, 3 to 4 per cluster' |
| 10908 | 4 cluster per month, 4 per cluster | 4 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '16 per month' -> '4 cluster per month, 4 per cluster' |
| 10931 | 6 cluster per month, 4 per cluster | 6 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '24 per month' -> '6 cluster per month, 4 per cluster' |
| 10941 | 6 cluster per month, 5 per cluster | 6 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '30 per month' -> '6 cluster per month, 5 per cluster' |
| 10954 | 3 cluster per month, 5 to 6 per cluster | 3 cluster per month, 5 to 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 clusters per month, 5-6 events per cluster' -> '3 cluster per month, 5 to 6 per cluster' |
| 10977 | unknown | 4 cluster per month, 5 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '4 clusters per month, approx 20 seizures per month' -> 'unknown' |
| 10994 | 3 to 4 per 1 year | 3 to 4 cluster per month, 3 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '3 to 4 clusters per month' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 4 per 1 year' |
| 11076 | unknown | 1 cluster per 2 months, 2 to 4 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster every 2 months' -> 'unknown' |
| 11196 | 3 cluster per month, 5 per cluster | 3 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 clusters per month, ~5 events per cluster' -> '3 cluster per month, 5 per cluster' |
| 11207 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month, ~6 events per cluster' -> '2 cluster per month, 6 per cluster' |
| 11221 | 1 per 5 month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 30/5/2020' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 5 month' |
| 11334 | seizure free for multiple year | 1 per 2 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 23-Jun' -> 'seizure free for multiple year' |
| 11401 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11431 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11472 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11492 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11499 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11576 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11590 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11733 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11748 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11787 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11825 | unknown | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11842 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11844 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11864 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11867 | unknown | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11889 |  | no seizure frequency reference | no | schema_validation_error: Input should be a valid string; evidence_not_exact_substring |
| 11918 | 5 per week | 5 per week | yes | json_dialect_repaired: python_literal |
| 11936 | 3 to 4 per week | 3 to 4 per week | yes | json_dialect_repaired: python_literal |
| 11983 | 1 per day | 2 to 3 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per day' -> '1 per day' |
| 12005 | 1 per day | 2 to 6 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 6 per day' -> '1 per day' |
| 12060 | 1 per day | multiple per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_exact_substring |
| 12080 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12090 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12169 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 12173 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 12258 | 2 per day | 1 to 2 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 or 2 per day' -> '2 per day' |
| 12300 | 3 per week | 3 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types active; GTCS 3/week, drop attack clusters, tonic seizures daily' -> '3 per week' |
| 12319 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 12326 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '4 per week' |
| 12330 | 3 to 4 per week | 3 to 4 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '3 to 4 per week' |
| 12335 | 3 per week | 3 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types with high frequency (GTC 3x/week, clusters of drop attacks, daily tonic)' -> '3 per week' |
| 12348 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '2 to 3 per week' |
| 12392 | 4 per day | 4 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types with high frequency (focal: 4/day; drop attacks: clusters; tonic-clonic: 2/month)' -> '4 per day' |
| 12504 | 1 cluster per month, multiple per cluster | 3 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple frequencies: 1-2 GTCS weekly, 3 absence/day, ~1 cluster/month' -> '1 cluster per month, multiple per cluster' |
| 12590 | 1 per 2 to 3 month | 1 per week | no | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2-3 months' -> '1 per 2 to 3 month' |
| 12643 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types: 1-2 GTCS/week, daily absences, focal non-motor q3-4wks, drop attacks' -> '1 per day'; evidence_not_exact_substring |
| 12645 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types: daily absence, 1-2 GTC/year, complex partial every 3-4 weeks' -> '1 per day'; evidence_not_exact_substring |
| 12674 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 12778 | 8 per 3 month | 8 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 per year' -> '8 per 3 month' |
| 12791 | 6 per month | 6 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per year (tonic), increasing frequency of near-misses and loss-of-tone events in the past month' -> '6 per month'; evidence_not_exact_substring |
| 12826 | 10 per 4 month | 10 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12866 | 10 per 5 month | 10 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '10 per year' -> '10 per 5 month' |
| 12919 | 5 per 5 month | 5 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12948 | 7 per 5 month | 7 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 per year' -> '7 per 5 month' |
| 12985 | 3 per year | 3 per 5 month | yes | json_dialect_repaired: python_literal |
| 13043 | 2 per 5 month | 2 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 GTC and multiple absences in one recent cluster/event' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 5 month'; evidence_not_exact_substring |
| 13064 | 1 per 5 month | 2 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 event (breakthrough) with preceding cluster' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 5 month'; evidence_not_exact_substring |
| 13069 | multiple per week | 2 per 5 month | no | json_dialect_repaired: python_literal |
| 13077 | 3 per 3 month | 2 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: '2 per 3 months' -> '3 per 3 month' |
| 13079 | multiple per week | 2 per 8 month | no | json_dialect_repaired: python_literal |
| 13109 | unknown | 2 per year | no | json_dialect_repaired: python_literal |
| 13162 | seizure free for multiple year | 1 per 4 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since last event' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13167 | 1 per month | 1 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: '1 per month (approx)' -> '1 per month' |
| 13183 | 1 per 8 month | 1 per 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 event in recent past (recurrence)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 8 month' |
| 13210 | 1 per 5 month | 1 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 event in recent past (breakthrough after remission)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 5 month' |
| 13266 | 2 per 3 month | 2 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 13376 | seizure free for 2 year | seizure free for 2 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 13473 | seizure free for 5 year | seizure free for 5 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 5 years' -> 'seizure free for 5 year' |
| 13590 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13591 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13600 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13611 | 10 per 6 month | 57 per 11 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '71 per 11 month'; final_label_repaired: '71 per 11 month' -> '10 per 6 month' |
| 13645 | 46 per 4 month | 85 per 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '15 per 2 month'; final_label_repaired: '15 per 2 month' -> '46 per 4 month'; evidence_not_exact_substring |
| 13753 | 8 per 6 month | 33 per 9 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '47 per 9 month'; final_label_repaired: '47 per 9 month' -> '8 per 6 month' |
| 13765 | 14 per 5 month | 50 per 9 month | no | json_dialect_repaired: python_literal; final_label_repaired: '4 to 10 days per month' -> '50 per 9 month'; final_label_repaired: '50 per 9 month' -> '14 per 5 month' |
| 13796 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'low frequency / resolved' -> 'seizure free for multiple year' |
| 13822 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'managed/controlled' -> 'seizure free for multiple year' |
| 13841 | seizure free for multiple year | seizure free for 6 months | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13901 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 seizures since August 2020' -> 'no seizure frequency reference' |
| 13912 | 2 to 3 per month | unknown | no | json_dialect_repaired: python_literal |
| 13970 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 total recent seizures' -> 'no seizure frequency reference' |
| 13990 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 since discharge' -> 'no seizure frequency reference' |
| 14009 | 2 per month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '2 per month'; evidence_not_exact_substring |
| 14031 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 per ~3 months' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 14036 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 events since starting ketogenic diet' -> 'no seizure frequency reference' |
| 14081 | 2 to 3 per month | unknown | no | json_dialect_repaired: python_literal |
| 14145 | 2 to 3 per month | unknown | no | json_dialect_repaired: python_literal |
| 14236 | 4 per 1 month | 4 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '4 per 1 month' |
| 14237 |  | 3 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14243 |  | 4 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14271 |  | 2 to 3 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14306 |  | 4 per 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 14369 |  | 2 per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 14390 |  | 2 per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14443 |  | 4 per 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14468 |  | 2 per 6 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 14483 |  | 4 per 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14485 |  | 2 per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14551 |  | 2 per 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14590 |  | 2 per 6 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 14598 |  | 5 per 8 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14655 |  | 2 per 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14689 |  | 3 per 2 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 14792 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 14823 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 14824 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error: out of memory\nCUDA error"}; evidence_not_exact_substring |
| 14845 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14877 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14881 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14888 |  | 1 per month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14930 |  | 1 per 3 month | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - {"error":"llama-server reported out-of-memory during startup: CUDA error\nCUDA error: out of memory"}; evidence_not_exact_substring |
| 14944 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 10/Mar' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month'; evidence_not_exact_substring |
| 14954 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 week' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 15039 | unknown | multiple per 12 month | yes | json_dialect_repaired: python_literal |
| 15113 | 2 to 3 per 16 month | 3 to 4 per 16 month | no | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per month' -> '2 to 3 per 16 month' |
| 15148 | 1 to 2 per 16 month | 2 to 3 per 16 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 to 2 per month' -> '1 to 2 per 16 month' |
| 15203 | seizure free for multiple year | multiple per 13 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for >1 year' -> 'seizure free for multiple year' |
| 15240 | unknown | multiple cluster per 12 month, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters per week/month' -> 'unknown'; evidence_not_exact_substring |
| 15250 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15255 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters per week' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster'; evidence_not_exact_substring |
| 15268 | 3 per 15 month | 3 per 15 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'sporadic (3 since May 2015)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 15 month' |
| 15302 | 1 to 2 per 14 month | 1 to 2 per 14 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 to 2 per month' -> '1 to 2 per 14 month' |
| 15385 | 3 per 2 month | 1 cluster per 2 month, 3 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per day (in clusters)' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 2 month' |
| 15396 | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 per day (in clusters)' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15399 | 2 to 4 per day | 1 cluster per 4 month, 2 to 4 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'clusters of 2 to 4 per day' -> '2 to 4 per day' |
| 15434 | 1 cluster per 5 day, 2 per cluster | 1 cluster per 5 day, 2 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 cluster per 5 day, 2 per cluster' |
| 15518 | 1 cluster per 5 day, 5 per cluster | 1 cluster per 5 day, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per day (in clusters)' -> '1 cluster per 5 day, 5 per cluster' |
| 15544 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 per day (in clusters)' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15609 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 15620 | 3 per day | 3 per day | yes | json_dialect_repaired: python_literal |
| 15685 | 4 per week | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'almost daily' -> '4 per week'; evidence_not_exact_substring |
| 15737 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 15847 | 1 per 2 week | 6 per week | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 2 week'; evidence_not_exact_substring |
| 15900 | 12 per 2 month | 12 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 per month' -> '12 per 2 month' |
| 15927 | 10 per 2 month | 18 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '10 per month' -> '18 per 2 month'; final_label_repaired: '18 per 2 month' -> '10 per 2 month' |
| 16050 | 6 per 2 month | 6 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per month' -> '6 per 2 month'; evidence_not_exact_substring |
| 16128 | 10 per 3 month | 10 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '10 seizures over 3 months' -> '10 per 3 month' |
| 16158 | 13 per 4 month | 13 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '11 seizures in the last 3 months' -> '13 per 4 month' |
| 16253 | 1 per 2 month | 8 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: '7 per month' -> '8 per 3 month'; final_label_repaired: '8 per 3 month' -> '1 per 2 month' |
| 16257 | 7 per 2 month | 7 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'variable frequency (5 in July, 2 in August)' -> '7 per 2 month' |
| 16281 | 15 per 3 month | 21 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '21 per 4 month'; final_label_repaired: '21 per 4 month' -> '15 per 3 month' |
| 16286 | 7 per 2 month | 13 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '13 per 3 month'; final_label_repaired: '13 per 3 month' -> '7 per 2 month' |
| 16357 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per 2 days' -> '1 per 2 day' |
| 16368 | 2 per 2 month | 1 per 2 day | no | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster every 2 days' -> '1 per 2 day'; final_label_repaired: '1 per 2 day' -> '2 per 2 month' |
| 16422 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 to 3 day' |
| 16436 | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 3 to 4 day' |
| 16512 | multiple per week | 1 per multiple day | yes | json_dialect_repaired: python_literal |
| 16718 | 8 per 3 month | 9 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '8 per 3 month' |
| 16727 | 8 per 5 month | 8 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '8 per 5 month' |
| 16807 | 7 per 2 month | 8 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '7 per 2 month' |
| 16820 | 6 per 2 month | 7 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '6 per 2 month'; evidence_not_exact_substring |
| 16825 | 10 per 4 month | 10 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '10 per 4 month'; evidence_not_exact_substring |
| 16834 | 7 per 5 month | 7 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '7 per 5 month' |
| 16962 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types with varying frequencies (GTC: 2-3/quarter, Absence: <=2/week, Focal: 1-2/month)' -> '2 per week'; evidence_not_exact_substring |
| 16964 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 to 5 per 2 months (GTC), up to 2 per week (Absence)' -> '2 per week' |
| 16977 | 4 to 5 per month | 4 to 5 per month | yes | json_dialect_repaired: python_literal |
| 16991 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'few times per month' -> 'multiple per month' |
| 17107 | unknown | 5 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '5 days per week (absence clusters)' -> 'unknown' |
| 17133 | unknown | 2 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'clusters on 2 days per week' -> 'unknown' |
| 17202 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal |
| 17207 | 1 per day | 3 to 4 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 to 4 per day' -> '1 per day' |
| 17229 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal |
| 17258 | 1 per 4 day | 1 per 4 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 4 days' -> '1 per 4 day' |
| 17292 | 1 per 3 week | 1 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 17297 | 1 per multiple week | 1 per multiple week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per several weeks' -> '1 per multiple week' |
