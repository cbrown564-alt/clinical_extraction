# Gan 2026 LLM-Only Typed Adapter Reasoner V0

- JSONL: `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_gpt41mini_v0_diagnostic_2026-06-02.jsonl`
- Architecture: `llm_only_typed_adapter_reasoner`
- Claim language: typed-adapter LLM-only architecture.
- Prompt/program version: `gan2026_llm_only_typed_adapter_reasoner_v0`
- Typed output schema version: `typed_adapter_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live diagnostic validation50 after rejected validation25 gate`
- DSPy adapter: `JSONAdapter`
- Deterministic selected-evidence arithmetic, benchmark alignment, and full-stack repairs are side-car diagnostics.
- Typed-adapter outcome: `reject`

## Predeclared Smoke

- Surface: `validation25` under `gan2026_split_v1`.
- Current artifact rows: `50`. Runs above 25 rows are diagnostic only unless separately promoted.
- Primary question: can typed DSPy output plus scoped JSONAdapter reduce schema/parser/rendering failures while preserving LLM-owned clinical interpretation?
- Stop rule: do not escalate beyond this smoke from this artifact.

## Smoke Summary

- Structured records: 50/50
- Adapter parse failures: 0
- Parse/schema failures: 0
- Selected evidence valid: 45/50
- Rendering operands present: 49/50
- Arithmetic/rendering traces present: 38/50
- Event evidence valid: 79/85
- Selected-event trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 45, Purist 42/50 (0.8400), Pragmatic 42/50 (0.8400)
- `format_only`: scorable 48, Purist 45/50 (0.9000), Pragmatic 45/50 (0.9000)
- `selected_evidence_arithmetic`: scorable 50, Purist 49/50 (0.9800), Pragmatic 49/50 (0.9800)
- `benchmark_aligned`: scorable 50, Purist 43/50 (0.8600), Pragmatic 43/50 (0.8600)
- `oracle_format_upper_bound`: scorable 48, Purist 45/50 (0.9000), Pragmatic 45/50 (0.9000)

## Adapter Gate

- Structured adapter outputs: 50/50
- Raw parser-compatible labels: 45/50
- Raw model-owned Purist: 42/50
- Deterministic selected-evidence arithmetic raw-wrong to correct: 7
- Deterministic selected-evidence arithmetic raw-correct to wrong: 0

## Row Review

- 10: side-car correction; gold `4 per day`; raw `up to 4 per day`; selected-evidence arithmetic `4 per day`; taxonomy `parser/schema issue`
- 40: side-car correction; gold `4 per week`; raw `up to 4 per week`; selected-evidence arithmetic `4 per week`; taxonomy `wrong selected fact`
- 190: side-car correction; gold `1 per 4 week`; raw `1 cluster per 4 weeks lasting 1-2 days`; selected-evidence arithmetic `1 per 4 week`; taxonomy `parser/schema issue`
- 446: side-car correction; gold `2 per week`; raw `up to 2 per week`; selected-evidence arithmetic `2 per week`; taxonomy `wrong selected fact`
- 743: side-car correction; gold `multiple per week`; raw `frequent per shift`; selected-evidence arithmetic `no seizure frequency reference`; taxonomy `parser/schema issue`
- 960: side-car correction; gold `1 per 2 month`; raw `2 per 1 to 2 month`; selected-evidence arithmetic `1 per 2 month`; taxonomy `wrong arithmetic/rendering`
- 987: side-car correction; gold `1 per 2 month`; raw `2 per 1 month`; selected-evidence arithmetic `1 per 2 month`; taxonomy `wrong arithmetic/rendering`
- 1165: raw miss; gold `5 to 7 per 3 week`; raw `seizure free for 6 weeks`; selected-evidence arithmetic `seizure free for multiple year`; taxonomy `wrong selected fact`

## Failure Taxonomy

- `no raw failure`: 39
- `parser/schema issue`: 3
- `wrong arithmetic/rendering`: 2
- `wrong selected fact`: 6

## Interpretation

This validation25 typed-adapter smoke fails at least one hard adapter or attribution gate. Do not escalate this artifact.
