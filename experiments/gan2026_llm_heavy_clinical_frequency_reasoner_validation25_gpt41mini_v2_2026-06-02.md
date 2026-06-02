# Gan 2026 LLM-Heavy Clinical Frequency Reasoner V2

- JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.jsonl`
- Pipeline family: `llm_heavy_clinical_frequency_reasoner`
- Prompt version: `gan2026_llm_heavy_clinical_frequency_reasoner_v2`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy validation development result; deterministic selected-evidence arithmetic and benchmark-aligned layers are side-cars.
- Decision 0006 outcome: `reject`

## Smoke Summary

- Structured records: 22/25
- Parse/schema failures: 3
- Selected evidence valid: 22/25
- Rendering operands present: 22/25
- Arithmetic/rendering traces present: 22/25
- Event evidence valid: 51/53
- Selected-event trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 22, Purist 21/25 (0.8400), Pragmatic 22/25 (0.8800)
- `format_only`: scorable 22, Purist 21/25 (0.8400), Pragmatic 22/25 (0.8800)
- `selected_evidence_arithmetic`: scorable 22, Purist 21/25 (0.8400), Pragmatic 22/25 (0.8800)
- `benchmark_aligned`: scorable 22, Purist 21/25 (0.8400), Pragmatic 22/25 (0.8800)
- `oracle_format_upper_bound`: scorable 22, Purist 21/25 (0.8400), Pragmatic 22/25 (0.8800)

## Decision 0006 Stop Rules

- Raw parser-compatible labels: 22/25
- Raw model-owned Purist: 21/25
- Deterministic selected-evidence arithmetic raw-wrong to correct: 0
- Deterministic selected-evidence arithmetic raw-correct to wrong: 0

## Row Review

- 10: raw miss; gold `4 per day`; raw `None`; selected-evidence arithmetic `None`; taxonomy `parser/schema issue`
- 79: raw miss; gold `6 to 7 per year`; raw `None`; selected-evidence arithmetic `None`; taxonomy `parser/schema issue`
- 187: raw miss; gold `1 per 7 to 9 day`; raw `2 per 7 to 9 day`; selected-evidence arithmetic `2 per 7 to 9 day`; taxonomy `wrong selected fact`
- 659: raw miss; gold `2 per 4 day`; raw `None`; selected-evidence arithmetic `None`; taxonomy `parser/schema issue`

## Failure Taxonomy

- `no raw failure`: 21
- `parser/schema issue`: 3
- `wrong selected fact`: 1

## Interpretation

The decision-0006 validation25 smoke fails at least one hard stop rule. Do not escalate this v2 prompt to validation50; revise the prompt/schema or keep selected-evidence arithmetic as an explicit deterministic component.
