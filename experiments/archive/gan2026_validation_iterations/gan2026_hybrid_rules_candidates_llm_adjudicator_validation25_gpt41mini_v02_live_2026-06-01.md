# Gan 2026 Hybrid Rules-Candidates LLM Adjudicator

Date: 2026-06-01

This is a validation development artifact unless the split is explicitly `test` and the candidate was frozen before evaluation. It is not a benchmark claim.

## Experiment Unit

Hypothesis: deterministic V1 can serve as a high-recall candidate generator, while an LLM adjudicator proposes semantic selection changes that pass named overreach gates.

Prediction-bearing component: conservative gated adjudicator final label. The raw LLM decision is retained, but deterministic V1 is the fallback when gate checks find unsupported candidate membership, label support, evidence, empty selection, or boundary-demotion overreach.

Data surface: `validation` split, `gan2026_split_v1`, 25 rows.
Escalation reason: not applicable for this run size.

## Model And Prompt Metadata

- Architecture: `hybrid_rules_candidates_llm_adjudicator`
- Claim type: `hybrid_llm_adjudicator`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: final-selection adjudicator
- Prompt/program version: `gan2026_final_selection_adjudicator_v0.5_conservative`
- Temperature: `0.0`
- Max tokens: `1100`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: frozen V1 candidate generator before LLM adjudication.
- Git commit: `fc19eb7`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_gpt41mini_v02_live_2026-06-01.jsonl`

## Summary

- Decision records: 25 / 25
- Call failures: 0
- Parse/schema/label issues: 0
- Candidate-set Purist recall proxy: 1.0000 (25 / 25)
- Deterministic top Purist: 1.0000 (25 / 25)
- Deterministic top Pragmatic: 1.0000 (25 / 25)
- Adjudicator Purist: 1.0000 (25 / 25)
- Adjudicator Pragmatic: 1.0000 (25 / 25)
- Changed final labels: 0
- Raw changed final labels before gates: 0
- Deterministic fallbacks after gates: 0
- Overreach gates: {}
- Deterministic-wrong to adjudicator-correct: 0
- Deterministic-correct to adjudicator-wrong: 0

## Rows

| Row | Candidate recall | Deterministic | Raw LLM | Gated final | Gold | Det Purist | Gated Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | yes | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | yes | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes |  |
| 103 | yes | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 128 | yes | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | yes | 1 per 6 day | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | yes | 1 per 7 day | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 187 | yes | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes |  |
| 190 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 198 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | yes | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | yes | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | yes | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 278 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | yes | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes | final_label_repaired: 'many seizures per month' -> 'no seizure frequency reference' |
| 409 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 419 | yes | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | yes | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | yes | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | yes | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | yes | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes |  |
| 598 | yes | 1 per 8 month | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes |  |
| 659 | yes | 2 per 4 day | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
