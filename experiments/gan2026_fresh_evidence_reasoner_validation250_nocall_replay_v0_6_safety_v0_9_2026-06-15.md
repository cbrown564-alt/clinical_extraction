# Gan 2026 Fresh-Evidence Reasoner v0.9 No-Call Replay

Date: 2026-06-15

Validation diagnostic no-call replay over saved v0.6/safety-v0.8 raw outputs.

## Experiment Unit

- Work class: semantic unknown/no-reference replay.
- Rows: 250
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `no-call-replay`.
- Model: `none; saved raw outputs from openai/gpt-4.1 v0.6/safety-v0.8`.
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_6`.
- Safety gate version: `gan2026_fresh_evidence_safety_gate_v0_9`.
- Replay source: `experiments/gan2026_fresh_evidence_reasoner_validation250_nocall_replay_v0_6_safety_v0_8_2026-06-15.jsonl`.
- JSONL artifact: `experiments/gan2026_fresh_evidence_reasoner_validation250_nocall_replay_v0_6_safety_v0_9_2026-06-15.jsonl`.

## Summary

- prediction_bearing_rows: 248
- model_calls_attempted: 250
- call_failures: 0
- parse_or_validation_failures: 0
- fresh_evidence_replace_actions: 54
- fresh_evidence_gate_fallbacks: 23
- semantic_no_reference_to_unknown_repairs: 5
- evidence_exact_substrings: 242
- v0_purist_correct: 236
- raw_model_purist_correct: 232
- format_only_purist_correct: 232
- final_purist_correct: 240
- v0_pragmatic_correct: 238
- final_pragmatic_correct: 241
- wrong_to_correct_vs_v0: 4
- correct_to_wrong_vs_v0: 0
- changed_label_precision_vs_v0: 0.1379

## Decision

Diagnostic/revise only; this replay changes unknown/no-reference semantics but does not create a holdout candidate.
