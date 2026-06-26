# Gan 2026 LLM-Only Typed Adapter Reasoner V0

- JSONL: `experiments/gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`
- Architecture: `llm_only_typed_adapter_reasoner`
- Claim language: typed-adapter LLM-only architecture.
- Prompt/program version: `gan2026_llm_only_typed_adapter_reasoner_v0`
- Typed output schema version: `typed_adapter_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- DSPy adapter: `JSONAdapter`
- Deterministic selected-evidence arithmetic, benchmark alignment, and full-stack repairs are side-car diagnostics.
- Typed-adapter outcome: `reject`

## Predeclared Smoke

- Surface: `validation25` under `gan2026_split_v1`.
- Primary question: can typed DSPy output plus scoped JSONAdapter reduce schema/parser/rendering failures while preserving LLM-owned clinical interpretation?
- Stop rule: do not escalate beyond this smoke from this artifact.

## Smoke Summary

- Structured records: 25/25
- Adapter parse failures: 0
- Parse/schema failures: 0
- Selected evidence valid: 19/25
- Rendering operands present: 25/25
- Arithmetic/rendering traces present: 17/25
- Event evidence valid: 31/38
- Selected-event trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 22, Purist 22/25 (0.8800), Pragmatic 22/25 (0.8800)
- `format_only`: scorable 24, Purist 24/25 (0.9600), Pragmatic 24/25 (0.9600)
- `selected_evidence_arithmetic`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `benchmark_aligned`: scorable 25, Purist 22/25 (0.8800), Pragmatic 22/25 (0.8800)
- `oracle_format_upper_bound`: scorable 24, Purist 24/25 (0.9600), Pragmatic 24/25 (0.9600)

## Adapter Gate

- Structured adapter outputs: 25/25
- Raw parser-compatible labels: 22/25
- Raw model-owned Purist: 22/25
- Deterministic selected-evidence arithmetic raw-wrong to correct: 3
- Deterministic selected-evidence arithmetic raw-correct to wrong: 0

## Row Review

- 10: side-car correction; gold `4 per day`; raw `up to 4 per day`; selected-evidence arithmetic `4 per day`; taxonomy `wrong selected fact`
- 190: side-car correction; gold `1 per 4 week`; raw `1 cluster per 4 weeks lasting 1 to 2 days`; selected-evidence arithmetic `1 per 4 week`; taxonomy `parser/schema issue`
- 446: side-car correction; gold `2 per week`; raw `up to 2 per week`; selected-evidence arithmetic `2 per week`; taxonomy `wrong selected fact`

## Failure Taxonomy

- `no raw failure`: 18
- `parser/schema issue`: 1
- `wrong selected fact`: 6

## Interpretation

This validation25 typed-adapter smoke fails at least one hard adapter or attribution gate. Do not escalate this artifact.
