# Gan 2026 LLM-Only Canonical-Pipeline Validation Run

Date: 2026-06-10

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that collapses extract/select/normalize/project/render into one pass, with the now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing — can produce a directly scorable, fully rendered label without any deterministic normalization or projection stage downstream.

Minimal change: add an `llm_only_canonical_pipeline` runner alongside (not replacing) `llm_only_direct_labeler` and `hybrid_structured_events`. No deterministic `CandidateSet` is built or consumed; final_label is the model's directly rendered answer.

Data surface: `validation` split, `gan2026_split_v1`, 3 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only canonical-pipeline single-shot extract/select/normalize/project/render extractor
- Prompt/program version: `gan2026_llm_only_canonical_pipeline_v0.8`
- Temperature: `0.0`
- Max tokens: `2400`
- Mode: `live`
- DSPy cache enabled: `True`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-10T08:14:14.330812+00:00`
- Run finished UTC: `2026-06-10T08:18:14.409025+00:00`
- Wall-clock elapsed: `238.962` seconds (`3.983` minutes)
- Throughput: `0.012554` rows/sec (`79.654` sec/row)
- Optimizer: none
- Deterministic rule configuration: none as pre/post processing; the deterministic/hybrid rule taxonomy is embedded as prompt instructions only, and deterministic code is limited to label repair, evidence text-containment checking, and scoring.
- Git commit: `3ed082a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_only_canonical_pipeline_validation_gpt41mini_2026-06-07.jsonl`

## Summary

- Decision records: 0 / 3
- Call failures: 3
- Parse/schema/label issues: 3
- Deterministic repair notes: 0
- Evidence text-containment (free-text evidence found verbatim in note, the comparator-appropriate metric in place of `CandidateSet` source-id validity rate): 0 / 3 (0.0000)
- Purist validation accuracy/micro F1 proxy: 0.0000 (0 / 3)
- Pragmatic validation accuracy/micro F1 proxy: 0.0000 (0 / 3)

## Applied Rule-Taxonomy Families (Self-Reported)

These counts reflect which embedded rule-taxonomy families the model itself reported as shaping its answer (`applied_rule_families`); they are a prompt-compliance signal, not a verified trace.

- (none reported)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 |  | 4 per day | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - [WinError 10061] No connection could be made because the target machine actively refused it; evidence_not_text_contained |
| 40 |  | 4 per week | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - [WinError 10061] No connection could be made because the target machine actively refused it; evidence_not_text_contained |
| 79 |  | 6 to 7 per year | no | not_run; APIConnectionError: litellm.APIConnectionError: Ollama_chatException - [WinError 10061] No connection could be made because the target machine actively refused it; evidence_not_text_contained |
