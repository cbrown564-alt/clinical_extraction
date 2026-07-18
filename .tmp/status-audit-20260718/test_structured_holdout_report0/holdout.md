# Gan 2026 LLM-Structured Holdout Aggregate

Date: 2026-07-15

This is an aggregate-only locked-holdout result on `gan2026_split_v1`. No row-level result is included in this report.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `test` split, `gan2026_split_v1`, 1 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.0.0`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.7`
- Temperature: `0.0`
- Max tokens: `10000`
- Mode: `live`
- DSPy cache enabled: `False`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: none
- Git commit: `abc123`
- Working tree note: `dirty`
- JSONL artifact: `C:/Users/cbrow/Code/clinical_extraction/.tmp/status-audit-20260718/test_structured_holdout_report0/sealed.jsonl`

## Summary

- Structured records: 1 / 1
- Call failures: 0
- Parse/schema/label issues: 0
- Initial parse/schema/label issues: 0
- Format retries applied: 0
- Format retries rejected: 0
- JSON dialect repairs: 0
- Deterministic repair notes: 0
- Exact selection evidence substrings: 1 / 1
- Purist holdout accuracy/micro F1 proxy: 1.0000 (1 / 1)
- Pragmatic holdout accuracy/micro F1 proxy: 1.0000 (1 / 1)
