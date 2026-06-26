# Gan 2026 Architecture 2 Candidate Adjudicator

Date: 2026-06-01

This is a validation development artifact unless the split is explicitly `test` and the candidate was frozen before evaluation. It is not a benchmark claim.

## Experiment Unit

Hypothesis: deterministic V1 can serve as a high-recall candidate generator, while an LLM adjudicator makes the prediction-bearing semantic selection.

Prediction-bearing component: LLM final-selection adjudicator over unscored deterministic candidate evidence. Deterministic code generates candidate labels, validates output shape, applies existing label repair, and scores.

Data surface: `validation` split, `gan2026_split_v1`, 50 rows.

## Model And Prompt Metadata

- Architecture: `architecture_2_deterministic_candidates_llm_adjudicator`
- Claim type: `hybrid_llm_adjudicator`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: final-selection adjudicator
- Prompt/program version: `gan2026_final_selection_adjudicator_v0.4`
- Temperature: `0.0`
- Max tokens: `1100`
- Mode: `live`
- Reused raw model outputs: `25`
- Reuse source: `experiments/gan2026_arch2_validation25_gpt41mini_v01_2026-06-01.jsonl`
- Deterministic rule configuration: frozen V1 candidate generator before LLM adjudication.
- Git commit: `691903d`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_arch2_validation50_gpt41mini_v01_2026-06-01.jsonl`

## Summary

- Decision records: 47 / 50
- Call failures: 0
- Parse/schema/label issues: 3
- Candidate-set Purist recall proxy: 1.0000 (50 / 50)
- Deterministic top Purist: 1.0000 (50 / 50)
- Deterministic top Pragmatic: 1.0000 (50 / 50)
- Adjudicator Purist: 0.9200 (46 / 50)
- Adjudicator Pragmatic: 0.9200 (46 / 50)
- Changed final labels: 2
- Deterministic-wrong to adjudicator-correct: 0
- Deterministic-correct to adjudicator-wrong: 1

## Rows

| Row | Candidate recall | Deterministic | Adjudicator | Gold | Det Purist | Adj Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | yes | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | yes | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | yes | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes |  |
| 103 | yes | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 128 | yes | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | yes | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | yes | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 187 | yes | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes |  |
| 190 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 198 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | yes | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | yes | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | yes | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 278 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | yes | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | yes | no seizure frequency reference | unknown | multiple per month | yes | yes |  |
| 409 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 419 | yes | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | yes | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | yes | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | yes | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | yes | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes |  |
| 598 | yes | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes |  |
| 659 | yes | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
| 665 | yes | 2 per 2 week | 2 per 2 week | 2 per 2 week | yes | yes |  |
| 678 | yes | 2 per 4 month | 2 per 4 month | 2 per 4 month | yes | yes |  |
| 694 | yes | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 704 | yes | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 725 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 731 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 743 | yes | no seizure frequency reference |  | multiple per week | yes |  | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical', 'unclear' or 'mixed' |
| 744 | yes | multiple per week | 1 per 8 week | multiple per week | yes | no |  |
| 763 | yes | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 790 | yes | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | yes |  |
| 816 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 849 | yes | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 854 | yes | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | yes | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes |  |
| 891 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 899 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 959 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 960 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 978 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 987 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 1030 | yes | 1 to 3 per month |  | 1 to 3 per month | yes |  | schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 1046 | yes | 3 to 5 per month |  | 3 to 5 per month | yes |  | schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 1070 | yes | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | yes | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | yes | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes |  |
