# Gan 2026 Hybrid Rules-Candidates LLM Adjudicator

Date: 2026-06-01

This is a validation development artifact unless the split is explicitly `test` and the candidate was frozen before evaluation. It is not a benchmark claim.

## Experiment Unit

Hypothesis: deterministic V1 can serve as a high-recall candidate generator, while an LLM adjudicator proposes semantic selection changes that pass named overreach gates.

Prediction-bearing component: conservative gated adjudicator final label. The raw LLM decision is retained, but deterministic V1 is the fallback when gate checks find unsupported candidate membership, label support, evidence, empty selection, or boundary-demotion overreach.

Data surface: `test` split, `gan2026_split_v1`, 450 rows.
Escalation reason: frozen locked-test generalization audit for hybrid v0.2 cluster_diary_candidate_recall; no test-row failure inspection or tuning

## Model And Prompt Metadata

- Architecture: `hybrid_rules_candidates_llm_adjudicator`
- Claim type: `hybrid_llm_adjudicator`
- Candidate revision: `cluster_diary_candidate_recall`
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
- Git commit: `cf4233f`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`

## Summary

- Decision records: 448 / 450
- Call failures: 0
- Parse/schema/label issues: 2
- Candidate-set Purist recall proxy: 0.7978 (359 / 450)
- Deterministic top Purist: 0.7622 (343 / 450)
- Deterministic top Pragmatic: 0.7867 (354 / 450)
- Adjudicator Purist: 0.7622 (343 / 450)
- Adjudicator Pragmatic: 0.7844 (353 / 450)
- Changed final labels: 29
- Raw changed final labels before gates: 38
- Deterministic fallbacks after gates: 11
- Overreach gates: {'adjudicator_output_missing_or_invalid': 2, 'label_support_overreach': 3, 'unsupported_boundary_demotion_overreach': 5, 'unsupported_empty_selection_overreach': 1}
- Deterministic-wrong to adjudicator-correct: 9
- Deterministic-correct to adjudicator-wrong: 9

## Rows

| Row | Candidate recall | Deterministic | Raw LLM | Gated final | Gold | Det Purist | Gated Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 31 | yes | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 51 | yes | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 61 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 115 | yes | 7 to 8 per month | 7 to 8 per month | 7 to 8 per month | 7 to 8 per month | yes | yes |  |
| 136 | yes | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | yes | yes |  |
| 174 | yes | 1 per 1 to 3 day | 1 per 1 to 3 day | 1 per 1 to 3 day | 1 per 1 to 3 day | yes | yes |  |
| 176 | yes | 1 per 6 to 7 day | 1 per 6 to 7 day | 1 per 6 to 7 day | 1 per 6 to 7 day | yes | yes |  |
| 234 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 240 | yes | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | yes |  |
| 364 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 493 | yes | 11 per month | 11 per month | 11 per month | 11 per month | yes | yes |  |
| 503 | yes | 11 to 28 per 3 month | 11 to 28 per 3 month | 11 to 28 per 3 month | 11 to 28 per 3 month | yes | yes |  |
| 538 | yes | 1 per 4 day | 1 per 4 day | 1 per 4 day | 1 per 4 day | yes | yes |  |
| 610 | yes | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | yes |  |
| 632 | yes | 1 per 1 to 2 month | 1 per 1 to 2 month | 1 per 1 to 2 month | 1 per 1 to 2 month | yes | yes |  |
| 666 | yes | 2 per 2 to 3 month | 2 per 2 to 3 month | 2 per 2 to 3 month | 2 per 2 to 3 month | yes | yes |  |
| 685 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 714 | yes | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 722 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 735 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 739 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 748 | yes | 2 per 4 month | 2 per 4 month | 2 per 4 month | 1 per 2 month | yes | yes |  |
| 750 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 803 | yes | 1 per 8 day | 1 per month | 1 per month | 1 per month | no | yes |  |
| 804 | no | 2 cluster per month, 2 per cluster | 2 cluster per month, 2 per cluster | 2 cluster per month, 2 per cluster | 1 per month | no | no |  |
| 824 | no | no seizure frequency reference | 1 per month | no seizure frequency reference | 1 per month | no | no | final_label_repaired: 'approximately 1 per month' -> '1 per month'; label_support_overreach |
| 836 | yes | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 841 | yes | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 892 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 2 day | no | no |  |
| 934 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 2 week | no | no |  |
| 938 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 2 week | no | no |  |
| 1005 | no | 1 per 3 month | 1 per 3 month | 1 per 3 month | multiple per 3 month | no | no |  |
| 1017 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 1060 | yes | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | yes | yes |  |
| 1182 | yes | 6 to 14 per 3 month | 6 to 14 per 3 month | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | yes |  |
| 1184 | yes | 6 to 14 per 3 month | 6 to 14 per 3 month | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | yes |  |
| 1250 | yes | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 1289 | yes | 5 to 6 per year | 5 to 6 per year | 5 to 6 per year | 5 to 6 per year | yes | yes |  |
| 1290 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 8 to 9 per year | no | no |  |
| 1326 | yes | multiple per week | multiple per week | multiple per week | multiple per day | yes | yes |  |
| 1378 | yes | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1422 | yes | 9 per week | 9 per week | 9 per week | 9 per week | yes | yes |  |
| 1433 | yes | 4 per month | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 1460 | yes | 7 per month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 1497 | yes | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 1511 | yes | 7 per month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 1534 | yes | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 1624 | yes | 12 per week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1629 | yes | 12 per month | 12 per month | 12 per month | 12 per month | yes | yes |  |
| 1633 | yes | 12 per week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1656 | yes | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1683 | yes | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 1705 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 cluster per month, multiple per cluster | no | no |  |
| 1722 | yes | 3 per 2 month | 3 per 2 month | 3 per 2 month | 3 per 2 month | yes | yes |  |
| 1736 | yes | 4 per 6 month | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes |  |
| 1812 | yes | 12 per 3 month | 12 per 3 month | 12 per 3 month | 12 per 3 month | yes | yes |  |
| 1868 | yes | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1883 | yes | 4 per 3 month | 4 per 3 month | 4 per 3 month | 4 per 3 month | yes | yes |  |
| 1889 | yes | 4 per 6 month | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes |  |
| 1898 | yes | 4 per 6 month | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes |  |
| 1911 | yes | 7 per 2 month | 7 per 2 month | 7 per 2 month | 7 per 2 month | yes | yes |  |
| 1934 | yes | 7 per 2 month | 7 per 2 month | 7 per 2 month | 7 per 2 month | yes | yes |  |
| 1938 | yes | 5 per 4 month | 5 per 4 month | 5 per 4 month | 5 per 4 month | yes | yes |  |
| 2071 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 2112 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 2135 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 2220 | yes | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | yes |  |
| 2226 | yes | seizure free for 96 month | 3 to 10 per 2 week | 3 to 10 per 2 week | 3 to 10 per 2 week | no | yes |  |
| 2246 | yes | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | yes |  |
| 2262 | yes | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | yes |  |
| 2306 | yes | 8 to 9 per month | 8 to 9 per month | 8 to 9 per month | 8 to 9 per month | yes | yes |  |
| 2311 | no | 1 per multiple week | 1 per multiple week | 1 per multiple week | 5 to 7 per month | no | no |  |
| 2356 | yes | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | yes | yes |  |
| 2404 | yes | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | 6 to 7 per month | yes | yes |  |
| 2486 | yes | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | yes |  |
| 2543 | yes | 2 to 4 per 2 week | 2 to 4 per 2 week | 2 to 4 per 2 week | 2 to 4 per 2 week | yes | yes |  |
| 2564 | yes | 3 to 5 per 2 month | 3 to 5 per 2 month | 3 to 5 per 2 month | 3 to 5 per 2 month | yes | yes |  |
| 2596 | no | no seizure frequency reference | unknown | unknown | 2 per day | no | no |  |
| 2597 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | 2 per day | no | no |  |
| 2652 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per day | no | no |  |
| 2684 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2725 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 2749 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2781 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2795 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2854 | yes | 2 per month | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 2879 | yes | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 2978 | yes | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | yes | yes |  |
| 3054 | yes | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 3102 | yes | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 3214 | yes | 1 cluster per month, 5 to 7 per cluster | 1 cluster per month, 5 to 7 per cluster | 1 cluster per month, 5 to 7 per cluster | 1 cluster per month, 5 to 7 per cluster | yes | yes |  |
| 3225 | yes | 1 cluster per month, 3 to 10 per cluster | 1 cluster per month, 3 to 10 per cluster | 1 cluster per month, 3 to 10 per cluster | 1 cluster per month, 3 to 10 per cluster | yes | yes |  |
| 3237 | yes | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | yes | yes |  |
| 3246 | yes | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | yes |  |
| 3291 | yes | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3293 | yes | 8 per month | 8 per month | 8 per month | 8 per month | yes | yes |  |
| 3300 | yes | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3327 | yes | 5 to 6 per year | 5 to 6 per year | 5 to 6 per year | 5 to 6 per year | yes | yes |  |
| 3329 | yes | 2 to 3 per day | 2 to 3 per day | 2 to 3 per day | 2 to 3 per day | yes | yes |  |
| 3340 | yes | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | yes | yes |  |
| 3353 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3355 | no | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | 1 per 3 month | no | no |  |
| 3407 | yes | no seizure frequency reference | unknown | unknown | multiple per week | yes | yes |  |
| 3452 | yes | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | yes | yes |  |
| 3514 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3630 | yes | 7 per week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 3638 | yes | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 3675 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 3706 | yes | 6 per week | 6 per week | 6 per week | 6 per week | yes | yes |  |
| 3747 | yes | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 3831 | yes | 7 per month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 3864 | yes | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 3867 | yes | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 3888 | yes | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3906 | yes | 4 per year | 4 per year | 4 per year | 4 per year | yes | yes |  |
| 3918 | yes | 9 per week | 9 per week | 9 per week | 9 per week | yes | yes |  |
| 3934 | yes | 9 per week | 9 per week | 9 per week | 9 per week | yes | yes |  |
| 4003 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4004 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4073 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4076 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4197 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 2 day | no | no |  |
| 4217 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 2 day | no | no |  |
| 4239 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 4342 | yes | 5 per 3 month | 5 per 3 month | 5 per 3 month | 5 per 3 month | yes | yes |  |
| 4352 | no | 5 per 10 month | 5 per 10 month | 5 per 10 month | 5 per 3 month | no | no |  |
| 4424 | yes | 3 per 6 month | 3 per 6 month | 3 per 6 month | 3 per 6 month | yes | yes |  |
| 4679 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per day | yes | yes |  |
| 4707 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per day | yes | yes |  |
| 4809 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 4831 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 4892 | yes | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | yes | yes |  |
| 4903 | yes | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 4967 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 4996 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for 16 month | yes | yes |  |
| 5088 | yes | 1 per 2 month | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | no | yes |  |
| 5174 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 5213 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5385 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 1 year | no | no |  |
| 5395 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 6 month | no | no |  |
| 5505 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5527 | no | 2 per month | seizure free for multiple year | seizure free for multiple year | 1 per year | no | no |  |
| 5540 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 4 to 5 month | no | no |  |
| 5555 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5627 | yes | 1 per 5 day | 1 per 5 day | 1 per 5 day | 1 per 5 day | yes | yes |  |
| 5653 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 5684 | no | 2 per 2 week | 2 per 2 week | 2 per 2 week | unknown | no | no |  |
| 5708 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5764 | no | no seizure frequency reference | 3 per month | no seizure frequency reference | 3 per month | no | no | label_support_overreach |
| 5766 | yes | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | multiple per week | no | no |  |
| 5976 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6025 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 6028 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | 1 per 3 months | no | no |  |
| 6063 | no | 3 per 2 week | 3 per 2 week | 3 per 2 week | unknown | no | no |  |
| 6073 | yes | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 weeks | yes | yes |  |
| 6164 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 6216 | yes | 5 per 6 week | 5 per 6 week | 5 per 6 week | 4 per 6 week | yes | yes |  |
| 6252 | yes | 2 to 4 per month | 2 to 4 per month | 2 to 4 per month | 2 to 4 per month | yes | yes |  |
| 6288 | yes | 2 per 10 week | 2 per 10 week | 2 per 10 week | 2 per 10 week | yes | yes |  |
| 6296 | yes | 3 per 4 month | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 6303 | yes | multiple per multiple day | multiple per multiple day | multiple per multiple day | unknown | yes | yes |  |
| 6330 | no | 2 per 3 month | 2 per 3 month | 2 per 3 month | multiple per month | no | no |  |
| 6365 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown, 1 to 2 per cluster | yes | yes |  |
| 6380 | no | 2 per 3 month | 2 per 3 month | 2 per 3 month | unknown | no | no |  |
| 6387 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6408 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6592 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6661 | yes | 1 per day | 3 per 6 week | 3 per 6 week | 0.5 per week | no | yes |  |
| 6763 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 6775 | yes | 1 per 5 month | 1 per 5 month | 1 per 5 month | 1 per 5 month | yes | yes |  |
| 6787 | yes | 8 per 6 week | 8 per 6 week | 8 per 6 week | 8 per 6 week | yes | yes |  |
| 6909 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 weeks | yes | yes |  |
| 6929 | yes | 2 per 6 week | 2 per 6 week | 2 per 6 week | multiple per week | no | no |  |
| 6930 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6976 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6979 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6986 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 7005 | yes | 2 per 6 month | 2 per 6 month | 2 per 6 month | 2 per 6 month | yes | yes |  |
| 7047 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7061 | no | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 per 6 week | no | no |  |
| 7232 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 6 to 8 cluster per month, multiple per cluster | no | no | final_label_repaired: '6-8 days per month' -> 'no seizure frequency reference' |
| 7280 | no | 1 per 2 week | 1 per 2 week | 1 per 2 week | 5 per month | no | no |  |
| 7318 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 7327 | yes | 2 per 4 month | 2 per 4 month | 2 per 4 month | 2 per 4 months | yes | yes |  |
| 7328 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 7341 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7386 | yes | 5 per 8 week | 5 per 8 week | 5 per 8 week | 7 per 8 week | yes | yes |  |
| 7393 | yes | 2 per 3 month | 2 per 3 month | 2 per 3 month | unknown | no | no |  |
| 7405 | yes | 1 per multiple month | 1 per multiple month | 1 per multiple month | 1 per multiple months | yes | yes |  |
| 7431 | yes | 2 per 8 week | 2 per 8 week | 2 per 8 week | 1 per month | yes | yes |  |
| 7670 | no | 1 per day | 1 per day | 1 per day | multiple per week | no | no |  |
| 7688 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for 1 year | yes | yes |  |
| 7708 | no | 1 per 6 month |  | 1 per 6 month | seizure free for multiple month | no | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical', 'unclear' or 'mixed'; adjudicator_output_missing_or_invalid |
| 7712 | yes | 2 per 3 month | 2 per 3 month | 2 per 3 month | 2 per 3 month | yes | yes |  |
| 7719 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7783 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 7816 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7863 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 7884 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7892 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7935 | yes | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | seizure free for multiple month | yes | yes |  |
| 7958 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple year | no | no |  |
| 7987 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 7993 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown, 2 to 3 per cluster | yes | yes |  |
| 8109 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 8116 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 8127 | yes | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 8135 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 8169 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 8221 | yes | 1 per 3 to 4 week | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | no | yes |  |
| 8222 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 8244 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8286 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8342 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 9 month | no | no |  |
| 8346 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 8423 | no | 1 per month | no seizure frequency reference | 1 per month | seizure free for multiple month | no | no | unsupported_boundary_demotion_overreach |
| 8432 | yes | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | yes |  |
| 8488 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8540 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 8624 | yes | seizure free for 13 month | seizure free for 13 month | seizure free for 13 month | seizure free for 13 month | yes | yes |  |
| 8645 | yes | 5 per day | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | no | yes |  |
| 8723 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8790 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8791 | no | 1 per month | 0 per 6 week | 1 per month | seizure free for multiple month | no | no | final_label_repaired: '0 per 6 weeks' -> '0 per 6 week'; unsupported_empty_selection_overreach |
| 8799 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 8813 | no | 1 per multiple week | 1 per multiple week | 1 per multiple week | seizure free for multiple month | no | no |  |
| 8852 | yes | 1 per 2 to 3 week | seizure free for multiple year | seizure free for multiple year | seizure free for 8 month | no | yes |  |
| 8858 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8954 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 8 month | no | no |  |
| 8957 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for 8 month | yes | yes |  |
| 8979 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 9014 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for 11 month | yes | yes |  |
| 9065 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for 13 month | yes | yes |  |
| 9109 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 9114 | yes | 1 per 4 to 6 week | 1 per 4 to 6 week | 1 per 4 to 6 week | 1 per 4 to 6 week | yes | yes |  |
| 9147 | no | 3 per year | no seizure frequency reference | 3 per year | seizure free for multiple month | no | no | unsupported_boundary_demotion_overreach |
| 9179 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9189 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9202 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9212 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for 3 months | no | no |  |
| 9251 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for multiple month | yes | yes |  |
| 9279 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 to 2 per week | no | no |  |
| 9294 | yes | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 9377 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 9471 | yes | 6 per 8 month | 6 per 8 month | 6 per 8 month | 7 per 11 month | yes | yes |  |
| 9483 | yes | 8 per 6 month | 8 per 6 month | 8 per 6 month | 8 per 6 month | yes | yes |  |
| 9562 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 9566 | no | 1 to 2 per 8 week | 1 to 2 per 8 week | 1 to 2 per 8 week | unknown | no | no |  |
| 9601 | no | 3 per day | 3 per day | 3 per day | seizure free for multiple month | no | no |  |
| 9618 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 9654 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 9696 | no | 1 per day | unknown | 1 per day | unknown | no | no | unsupported_boundary_demotion_overreach |
| 9786 | no | 1 per day | unknown | 1 per day | unknown | no | no | unsupported_boundary_demotion_overreach |
| 9801 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 9891 | no | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | unknown | no | no |  |
| 9926 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 cluster per month, multiple per cluster | no | no |  |
| 9942 | no | 1 per month | 1 per month | 1 per month | 1 cluster per month, multiple per cluster | no | no |  |
| 9946 | no | 1 per month | 1 per month | 1 per month | 1 cluster per month, multiple per cluster | no | no |  |
| 9979 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 3 to 4 cluster per week, multiple per cluster | no | no |  |
| 10009 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 cluster per week, multiple per cluster | no | no |  |
| 10031 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 cluster per week, multiple per cluster | no | no |  |
| 10052 | yes | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | yes | yes |  |
| 10159 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10186 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | unknown, 3 to 5 per cluster | no | no |  |
| 10213 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown, 3 per cluster | yes | yes |  |
| 10292 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10298 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10316 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10330 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10398 | yes | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | yes | yes |  |
| 10408 | yes | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | yes | yes |  |
| 10441 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10445 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 9 cluster per month, 2 to 4 per cluster | no | no |  |
| 10447 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 10514 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 10538 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown, 6 per cluster | yes | yes |  |
| 10553 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown, 2 to 3 per cluster | yes | yes |  |
| 10621 | no | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | multiple cluster per week, 4 to 6 per cluster | no | no |  |
| 10737 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10751 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 10794 | yes | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | yes | yes |  |
| 10795 | yes | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | yes |  |
| 10863 | yes | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | yes |  |
| 10884 | yes | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | yes |  |
| 10908 | yes | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | 4 cluster per month, 4 per cluster | yes | yes |  |
| 10931 | yes | 6 cluster per month, multiple per cluster | 6 cluster per month, multiple per cluster | 6 cluster per month, multiple per cluster | 6 cluster per month, 4 per cluster | yes | yes |  |
| 10941 | no | 6 cluster per month, multiple per cluster | 6 cluster per month, multiple per cluster | 6 cluster per month, multiple per cluster | 6 cluster per month, 5 per cluster | no | no |  |
| 10954 | yes | 3 cluster per month, 5 to 6 per cluster | 3 cluster per month, 5 to 6 per cluster | 3 cluster per month, 5 to 6 per cluster | 3 cluster per month, 5 to 6 per cluster | yes | yes |  |
| 10977 | yes | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | yes | yes |  |
| 10994 | yes | 3 to 4 cluster per month, multiple per cluster | 3 to 4 cluster per month, multiple per cluster | 3 to 4 cluster per month, multiple per cluster | 3 to 4 cluster per month, 3 per cluster | yes | yes |  |
| 11076 | no | 1 per 8 week | 1 per 8 week | 1 per 8 week | 1 cluster per 2 months, 2 to 4 per cluster | no | no |  |
| 11196 | yes | 3 cluster per month, 5 per cluster | 3 cluster per month, 5 per cluster | 3 cluster per month, 5 per cluster | 3 cluster per month, 5 per cluster | yes | yes |  |
| 11207 | yes | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | yes |  |
| 11221 | yes | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | unknown | no | no |  |
| 11334 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per 2 month | no | no |  |
| 11401 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11431 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11472 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11492 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11499 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11576 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11590 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11733 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11748 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11787 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11825 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11842 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11844 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11864 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11867 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11889 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11918 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 5 per week | no | no |  |
| 11936 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 3 to 4 per week | no | no |  |
| 11983 | no | no seizure frequency reference | unknown | unknown | 2 to 3 per day | no | no |  |
| 12005 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 2 to 6 per day | no | no |  |
| 12060 | yes | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12080 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12090 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12169 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12173 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12258 | yes | 1 to 2 per day | 1 to 2 per day | 1 to 2 per day | 1 to 2 per day | yes | yes |  |
| 12300 | yes | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 12319 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 12326 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 12330 | yes | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 12335 | yes | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 12348 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 12392 | yes | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12504 | yes | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 12590 | yes | 1 per week | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per week | yes | no |  |
| 12643 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12645 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12674 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12778 | yes | 8 per 3 month | 8 per 3 month | 8 per 3 month | 8 per 3 month | yes | yes |  |
| 12791 | yes | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 12826 | yes | 1 per day | 10 per 4 month | 10 per 4 month | 10 per 4 month | no | yes |  |
| 12866 | yes | 10 per 5 month | 10 per 5 month | 10 per 5 month | 10 per 5 month | yes | yes |  |
| 12919 | no | 1 per 6 to 8 week | 5 per year | 5 per year | 5 per 5 month | no | no |  |
| 12948 | yes | 7 per 5 month | 7 per 5 month | 7 per 5 month | 7 per 5 month | yes | yes |  |
| 12985 | no | no seizure frequency reference | 3 per year | no seizure frequency reference | 3 per 5 month | no | no | label_support_overreach |
| 13043 | yes | 2 per 5 month | 2 per 5 month | 2 per 5 month | 2 per 5 month | yes | yes |  |
| 13064 | yes | 2 per 5 month | 2 per 5 month | 2 per 5 month | 2 per 5 month | yes | yes |  |
| 13069 | yes | 2 per 5 month | 2 per 5 month | 2 per 5 month | 2 per 5 month | yes | yes |  |
| 13077 | yes | 2 per 3 month | 2 per 3 month | 2 per 3 month | 2 per 3 month | yes | yes |  |
| 13079 | yes | 2 per 8 month | 2 per 8 month | 2 per 8 month | 2 per 8 month | yes | yes |  |
| 13109 | yes | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 13162 | yes | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 13167 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 13183 | yes | 1 per month | 1 per month | 1 per month | 1 per 8 month | no | no |  |
| 13210 | yes | 1 per 5 month | 1 per 5 month | 1 per 5 month | 1 per 5 month | yes | yes |  |
| 13266 | yes | 2 per 3 month | 2 per 3 month | 2 per 3 month | 2 per 3 month | yes | yes |  |
| 13376 | yes | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 13473 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for 5 year | yes | yes |  |
| 13590 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13591 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13600 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13611 | yes | 71 per 11 month | 71 per 11 month | 71 per 11 month | 57 per 11 month | yes | yes |  |
| 13645 | yes | 85 per 12 month | 85 per 12 month | 85 per 12 month | 85 per 12 month | yes | yes |  |
| 13753 | no | 47 per 9 month | 47 per 9 month | 47 per 9 month | 33 per 9 month | no | no |  |
| 13765 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 50 per 9 month | no | no |  |
| 13796 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 13822 | no | 1 per 28 to 32 day |  | 1 per 28 to 32 day | seizure free for multiple month | no | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical', 'unclear' or 'mixed'; adjudicator_output_missing_or_invalid |
| 13841 | no | 1 per day | unknown | 1 per day | seizure free for 6 months | no | no | unsupported_boundary_demotion_overreach |
| 13901 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 13912 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 13970 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 13990 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14009 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14031 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14036 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14081 | no | 1 per day | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 14145 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14236 | yes | 4 per month | seizure free for multiple year | seizure free for multiple year | 4 per month | yes | no |  |
| 14237 | yes | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 14243 | yes | 4 per month | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 14271 | yes | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | yes | yes |  |
| 14306 | yes | 4 per 2 month | 4 per 2 month | 4 per 2 month | 4 per 2 month | yes | yes |  |
| 14369 | yes | 2 per 3 month | 2 per 3 month | 2 per 3 month | 2 per 3 month | yes | yes |  |
| 14390 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 2 per 3 month | no | no |  |
| 14443 | yes | 4 per 2 month | 4 per 2 month | 4 per 2 month | 4 per 2 month | yes | yes |  |
| 14468 | yes | 2 per 6 month | 2 per 6 month | 2 per 6 month | 2 per 6 month | yes | yes |  |
| 14483 | yes | 4 per 2 month | 4 per 2 month | 4 per 2 month | 4 per 2 month | yes | yes |  |
| 14485 | yes | 2 per 3 month | seizure free for multiple year | seizure free for multiple year | 2 per 3 month | yes | no |  |
| 14551 | yes | 2 per 2 month | 2 per 2 month | 2 per 2 month | 2 per 2 month | yes | yes |  |
| 14590 | yes | 2 per 6 month | 2 per 6 month | 2 per 6 month | 2 per 6 month | yes | yes |  |
| 14598 | yes | 5 per 8 month | 5 per 8 month | 5 per 8 month | 5 per 8 month | yes | yes |  |
| 14655 | yes | 2 per 2 month | seizure free for multiple year | seizure free for multiple year | 2 per 2 month | yes | no |  |
| 14689 | yes | 3 per 2 month | seizure free for multiple year | seizure free for multiple year | 3 per 2 month | yes | no |  |
| 14792 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per month | no | no |  |
| 14823 | yes | 2 per month | 1 per month | 1 per month | 1 per month | no | yes |  |
| 14824 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | 1 per month | no | no |  |
| 14845 | no | 3 to 4 per week | seizure free for multiple year | seizure free for multiple year | 1 per month | no | no |  |
| 14877 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 14881 | yes | 1 per month | seizure free for multiple year | seizure free for multiple year | 1 per month | yes | no |  |
| 14888 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per month | no | no |  |
| 14930 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 14944 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 14954 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 15039 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per 12 month | yes | yes |  |
| 15113 | yes | 3 to 4 per 16 month | 3 to 4 per 16 month | 3 to 4 per 16 month | 3 to 4 per 16 month | yes | yes |  |
| 15148 | yes | 2 to 3 per 16 month | 2 to 3 per 16 month | 2 to 3 per 16 month | 2 to 3 per 16 month | yes | yes |  |
| 15203 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | multiple per 13 month | no | no |  |
| 15240 | no | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple cluster per 12 month, multiple per cluster | no | no |  |
| 15250 | yes | multiple cluster per 15 month, multiple per cluster | seizure free for multiple year | seizure free for multiple year | multiple cluster per 15 month, multiple per cluster | yes | no |  |
| 15255 | yes | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | yes |  |
| 15268 | yes | 3 per 15 month | 3 per 15 month | 3 per 15 month | 3 per 15 month | yes | yes |  |
| 15302 | yes | 1 to 2 per 14 month | 1 to 2 per 14 month | 1 to 2 per 14 month | 1 to 2 per 14 month | yes | yes |  |
| 15385 | yes | 1 cluster per 2 month, 3 per cluster | 1 cluster per 2 month, 3 per cluster | 1 cluster per 2 month, 3 per cluster | 1 cluster per 2 month, 3 per cluster | yes | yes |  |
| 15396 | yes | 1 cluster per 2 month, 4 per cluster | 1 cluster per 2 month, 4 per cluster | 1 cluster per 2 month, 4 per cluster | 1 cluster per 2 month, 4 per cluster | yes | yes |  |
| 15399 | yes | 1 cluster per 4 month, 2 to 4 per cluster | 1 cluster per 4 month, 2 to 4 per cluster | 1 cluster per 4 month, 2 to 4 per cluster | 1 cluster per 4 month, 2 to 4 per cluster | yes | yes |  |
| 15434 | yes | 1 cluster per 5 day, 2 per cluster | 1 cluster per 5 day, 2 per cluster | 1 cluster per 5 day, 2 per cluster | 1 cluster per 5 day, 2 per cluster | yes | yes |  |
| 15518 | yes | 1 cluster per 5 day, 5 per cluster | 1 cluster per 5 day, 5 per cluster | 1 cluster per 5 day, 5 per cluster | 1 cluster per 5 day, 5 per cluster | yes | yes |  |
| 15544 | yes | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | yes |  |
| 15609 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 15620 | yes | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 15685 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 15737 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 15847 | no | 1 per 2 week | 1 per 2 week | 1 per 2 week | 6 per week | no | no |  |
| 15900 | yes | 12 per 2 month | 12 per 2 month | 12 per 2 month | 12 per 2 month | yes | yes |  |
| 15927 | yes | 18 per 2 month | 18 per 2 month | 18 per 2 month | 18 per 2 month | yes | yes |  |
| 16050 | yes | 6 per 2 month | 6 per 2 month | 6 per 2 month | 6 per 2 month | yes | yes |  |
| 16128 | yes | 10 per 3 month | 10 per 3 month | 10 per 3 month | 10 per 3 month | yes | yes |  |
| 16158 | yes | 13 per 4 month | 13 per 4 month | 13 per 4 month | 13 per 4 month | yes | yes |  |
| 16253 | yes | 8 per 3 month | 8 per 3 month | 8 per 3 month | 8 per 3 month | yes | yes |  |
| 16257 | yes | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 16281 | yes | 21 per 4 month | 21 per 4 month | 21 per 4 month | 21 per 4 month | yes | yes |  |
| 16286 | yes | 13 per 3 month | 13 per 3 month | 13 per 3 month | 13 per 3 month | yes | yes |  |
| 16357 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 16368 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 16422 | yes | 1 per 2 to 3 day | 1 per 2 to 3 day | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | yes |  |
| 16436 | yes | 1 per day | 1 per day | 1 per day | 1 per 3 to 4 day | no | no |  |
| 16512 | yes | 1 per day | 1 per day | 1 per day | 1 per multiple day | no | no |  |
| 16718 | yes | 9 per 6 month | 9 per 6 month | 9 per 6 month | 9 per 6 month | yes | yes |  |
| 16727 | yes | 8 per 5 month | 8 per 5 month | 8 per 5 month | 8 per 5 month | yes | yes |  |
| 16807 | yes | 8 per 3 month | 8 per 3 month | 8 per 3 month | 8 per 3 month | yes | yes |  |
| 16820 | yes | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 16825 | yes | 10 per 6 month | 10 per 6 month | 10 per 6 month | 10 per 6 month | yes | yes |  |
| 16834 | yes | 7 per 5 month | 7 per 5 month | 7 per 5 month | 7 per 5 month | yes | yes |  |
| 16962 | yes | 2 per week | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 per week | yes | no |  |
| 16964 | yes | 2 per week | 4 to 5 per 2 month | 4 to 5 per 2 month | 2 per week | yes | no |  |
| 16977 | yes | 4 to 5 per month | 4 to 5 per month | 4 to 5 per month | 4 to 5 per month | yes | yes |  |
| 16991 | yes | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 17107 | yes | 5 cluster per week, multiple per cluster | 5 cluster per week, multiple per cluster | 5 cluster per week, multiple per cluster | 5 cluster per week, multiple per cluster | yes | yes |  |
| 17133 | yes | 2 cluster per week, multiple per cluster | 2 cluster per week, multiple per cluster | 2 cluster per week, multiple per cluster | 2 cluster per week, multiple per cluster | yes | yes |  |
| 17202 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 17207 | yes | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | yes | yes |  |
| 17229 | yes | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 17258 | yes | 1 per 4 day | 1 per 4 day | 1 per 4 day | 1 per 4 day | yes | yes |  |
| 17292 | yes | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 17297 | yes | 1 per multiple week | 1 per multiple week | 1 per multiple week | 1 per multiple week | yes | yes |  |
