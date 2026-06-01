# Gan 2026 Hybrid Rules-Candidates LLM Adjudicator

Date: 2026-06-01

This is a validation development artifact unless the split is explicitly `test` and the candidate was frozen before evaluation. It is not a benchmark claim.

## Experiment Unit

Hypothesis: deterministic V1 can serve as a high-recall candidate generator, while an LLM adjudicator proposes semantic selection changes that pass named overreach gates.

Prediction-bearing component: conservative gated adjudicator final label. The raw LLM decision is retained, but deterministic V1 is the fallback when gate checks find unsupported candidate membership, label support, evidence, empty selection, or boundary-demotion overreach.

Data surface: `synthetic_hard_cases` split, `gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01`, 56 rows.
Escalation reason: component stress over approved synthetic hard-case panel

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
- Git commit: `0d4770d`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl`

## Summary

- Decision records: 51 / 56
- Call failures: 0
- Parse/schema/label issues: 5
- Candidate-set Purist recall proxy: 0.7500 (42 / 56)
- Deterministic top Purist: 0.6964 (39 / 56)
- Deterministic top Pragmatic: 0.7500 (42 / 56)
- Adjudicator Purist: 0.7500 (42 / 56)
- Adjudicator Pragmatic: 0.7500 (42 / 56)
- Changed final labels: 5
- Raw changed final labels before gates: 7
- Deterministic fallbacks after gates: 7
- Overreach gates: {'adjudicator_output_missing_or_invalid': 5, 'unsupported_boundary_demotion_overreach': 2}
- Deterministic-wrong to adjudicator-correct: 3
- Deterministic-correct to adjudicator-wrong: 0

## Rows

| Row | Candidate recall | Deterministic | Raw LLM | Gated final | Gold | Det Purist | Gated Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 900000 | yes | 2 per month | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 900001 | yes | 5 per week | 1 per 2 week | 1 per 2 week | 1 per 2 week | no | yes |  |
| 900002 | yes | 3 per week | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | no | yes |  |
| 900003 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 900004 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 900005 | yes | 20 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 900006 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 900007 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 900008 | no | 8 per week | 1 per 8 month | 1 per 8 month | 1 per week | no | no |  |
| 900009 | yes | 2 per month | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 900010 | yes | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 900011 | yes | 4 per month | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 900012 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 900013 | yes | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 900014 | no | no seizure frequency reference |  | no seizure frequency reference | 2 per 1 month | no | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical', 'unclear' or 'mixed'; adjudicator_output_missing_or_invalid |
| 900015 | yes | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | yes |  |
| 900016 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 900017 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 900018 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 900019 | yes | no seizure frequency reference |  | no seizure frequency reference | unknown | yes | yes | schema_validation_error: Input should be 'low', 'medium' or 'high'; adjudicator_output_missing_or_invalid |
| 900020 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 900021 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 900022 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 900023 | yes | no seizure frequency reference |  | no seizure frequency reference | no seizure frequency reference | yes | yes | schema_validation_error: Input should be 'low', 'medium' or 'high'; adjudicator_output_missing_or_invalid |
| 900024 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 cluster per 2 week, 3 per cluster | no | no |  |
| 900025 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 2 cluster per month, 5 per cluster | no | no |  |
| 900026 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 cluster per week, multiple per cluster | no | no |  |
| 900027 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 2 cluster per 6 week, 1 to 2 per cluster | no | no |  |
| 900028 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 900029 | yes | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 900030 | yes | 1 per multiple week | 1 per multiple week | 1 per multiple week | unknown | yes | yes |  |
| 900031 | no | unknown | unknown | unknown | 1 cluster per month, 6 to 7 per cluster | no | no |  |
| 900032 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 2 per month | no | no |  |
| 900033 | yes | 8 per 4 week | 8 per 4 week | 8 per 4 week | 8 per month | yes | yes |  |
| 900034 | yes | 12 per 6 month | 12 per 6 month | 12 per 6 month | 2 per month | yes | yes |  |
| 900035 | no | 1 per month |  | 1 per month | 3 per 2 week | no | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future', 'unclear' or 'mixed'; adjudicator_output_missing_or_invalid |
| 900036 | yes | 10 to 15 per year | 10 to 15 per year | 10 to 15 per year | 10 to 15 per 1 year | yes | yes |  |
| 900037 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | 3 per month | no | no |  |
| 900038 | yes | 5 per 10 day | 5 per 10 day | 5 per 10 day | 5 per 10 day | yes | yes |  |
| 900039 | yes | 30 per 30 day | 30 per 30 day | 30 per 30 day | 1 per day | yes | yes |  |
| 900040 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 900041 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 900042 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 7 to 9 day | no | no |  |
| 900043 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 900044 | no | 4 per day | 4 per day | 4 per day | unknown | no | no |  |
| 900045 | yes | 1 per day | 1 per 2 day | 1 per 2 day | 1 per 2 day | no | yes |  |
| 900046 | yes | 6 to 8 per year | 6 to 8 per year | 6 to 8 per year | 6 to 8 per 1 year | yes | yes |  |
| 900047 | yes | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | yes |  |
| 900048 | yes | no seizure frequency reference |  | no seizure frequency reference | no seizure frequency reference | yes | yes | schema_validation_error: Input should be 'low', 'medium' or 'high'; adjudicator_output_missing_or_invalid |
| 900049 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 900050 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 900051 | no | 2 per week | no seizure frequency reference | 2 per week | no seizure frequency reference | no | no | unsupported_boundary_demotion_overreach |
| 900052 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 900053 | no | 3 per week | no seizure frequency reference | 3 per week | no seizure frequency reference | no | no | unsupported_boundary_demotion_overreach |
| 900054 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 900055 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
