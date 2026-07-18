# Gan 2026 LLM-Only Canonical-Pipeline Validation Run

Date: 2026-07-18

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that collapses extract/select/normalize/project/render into one pass, with the now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing — can produce a directly scorable, fully rendered label without any deterministic normalization or projection stage downstream.

Minimal change: add an `llm_only_canonical_pipeline` runner alongside `hybrid_structured_events`. No deterministic `CandidateSet` is built or consumed; final_label is the model's directly rendered answer.

Data surface: `validation` split, `gan2026_split_v1`, 1 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only canonical-pipeline single-shot extract/select/normalize/project/render extractor
- Prompt/program version: `gan2026_llm_only_canonical_pipeline_v0.8`
- Temperature: `0.0`
- Max tokens: `100`
- Mode: `prompt-only`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none as pre/post processing; the deterministic/hybrid rule taxonomy is embedded as prompt instructions only, and deterministic code is limited to label repair, evidence text-containment checking, and scoring.
- Git commit: `6c6df72c`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `C:/Users/cbrow/Code/clinical_extraction/.status-pytest-temp-20260718/test_run_split_checkpoints_pro0/checkpoint.jsonl`

## Summary

- Decision records: 0 / 1
- Call failures: 0
- Parse/schema/label issues: 1
- Deterministic repair notes: 0
- Evidence text-containment (free-text evidence found verbatim in note, the comparator-appropriate metric in place of `CandidateSet` source-id validity rate): 0 / 1 (0.0000)
- Purist validation accuracy/micro F1 proxy: 0.0000 (0 / 1)
- Pragmatic validation accuracy/micro F1 proxy: 0.0000 (0 / 1)

## Applied Rule-Taxonomy Families (Self-Reported)

These counts reflect which embedded rule-taxonomy families the model itself reported as shaping its answer (`applied_rule_families`); they are a prompt-compliance signal, not a verified trace.

- (none reported)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 |  | 2 per month | no | not_run; evidence_not_text_contained |
