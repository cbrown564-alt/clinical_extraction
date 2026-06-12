# Gan 2026 LLM-Only Canonical-Pipeline Validation Run

Date: 2026-06-09

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that collapses extract/select/normalize/project/render into one pass, with the now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing — can produce a directly scorable, fully rendered label without any deterministic normalization or projection stage downstream.

Minimal change: add an `llm_only_canonical_pipeline` runner alongside (not replacing) `llm_only_direct_labeler` and `hybrid_structured_events`. No deterministic `CandidateSet` is built or consumed; final_label is the model's directly rendered answer.

Data surface: `validation` split, `gan2026_split_v1`, 370 rows.
Rare full-validation reason: Phase3v05fixes
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only canonical-pipeline single-shot extract/select/normalize/project/render extractor
- Prompt/program version: `gan2026_llm_only_canonical_pipeline_v0.5`
- Temperature: `0.0`
- Max tokens: `1200`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none as pre/post processing; the deterministic/hybrid rule taxonomy is embedded as prompt instructions only, and deterministic code is limited to label repair, evidence text-containment checking, and scoring.
- Git commit: `a7c426f`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `C:/Users/cbrow/Code/clinical_extraction/experiments/gan2026_llm_only_canonical_pipeline_v05_validation750_gpt41mini_2026-06-09.resume-part.jsonl`

## Summary

- Decision records: 370 / 370
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 195
- Evidence text-containment (free-text evidence found verbatim in note, the comparator-appropriate metric in place of `CandidateSet` source-id validity rate): 325 / 370 (0.8784)
- Purist validation accuracy/micro F1 proxy: 0.6243 (231 / 370)
- Pragmatic validation accuracy/micro F1 proxy: 0.7000 (259 / 370)

## Applied Rule-Taxonomy Families (Self-Reported)

These counts reflect which embedded rule-taxonomy families the model itself reported as shaping its answer (`applied_rule_families`); they are a prompt-compliance signal, not a verified trace.

- `cluster_axis_ambiguity`: 61
- `cluster_cadence_as_event_rate`: 3
- `concrete_frequency_precedence`: 7
- `conditional_only_trigger`: 27
- `denominator_window_mismatch`: 96
- `dominant_vague_current_burden`: 79
- `same_window_additive_frequency`: 2
- `seizure_free_conflict`: 97
- `seizure_free_proxy_evidence_overreach`: 14
- `unknown_cadence_cluster_burden`: 23

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 9103 | 1 per 4 month | unknown | no | final_label_repaired: '1 per 4 months' -> '1 per 4 month'; evidence_not_text_contained |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9190 | seizure free for 7 month | seizure free for multiple month | yes |  |
| 9215 | seizure free for 3 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 9238 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9250 | seizure free for 9 month | seizure free for multiple month | yes |  |
| 9259 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '2 per month' -> '4 per 6 month' |
| 9462 | 7 per 11 month | 7 per 11 month | yes | final_label_repaired: '1 to 2 per month' -> '7 per 11 month' |
| 9496 | 6 per 12 month | 6 per 12 month | yes | final_label_repaired: '2 per month' -> '6 per 12 month' |
| 9547 | unknown | unknown | yes |  |
| 9588 | seizure free for 8 month | seizure free for multiple month | yes |  |
| 9704 | unknown | unknown | yes |  |
| 9815 | multiple per day | multiple per day | yes |  |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes |  |
| 9888 | unknown | unknown | yes |  |
| 9912 | unknown | unknown | yes |  |
| 9937 | unknown | 1 cluster per month, multiple per cluster | no |  |
| 9943 | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: 'unknown' -> '1 per 4 to 5 week' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '2 per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '3 per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10147 | unknown | unknown | yes | evidence_not_text_contained |
| 10183 | unknown | unknown | yes |  |
| 10189 | unknown | unknown, 3 to 4 per cluster | yes |  |
| 10200 | no seizure frequency reference | unknown, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster' -> 'no seizure frequency reference' |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no |  |
| 10245 | unknown | 3 cluster per month, multiple per cluster | no |  |
| 10260 | unknown | unknown | yes | evidence_not_text_contained |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | unknown | unknown | yes |  |
| 10371 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 5 per cluster' |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 2 to 3 per cluster' |
| 10434 | multiple per week | multiple cluster per week, 2 to 3 per cluster | no |  |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes | evidence_not_text_contained |
| 10517 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: 'multiple per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10542 | no seizure frequency reference | unknown, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster' -> 'no seizure frequency reference' |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes |  |
| 10583 | no seizure frequency reference | unknown, 2 to 3 per cluster | yes | final_label_repaired: '2 to 3 per cluster' -> 'no seizure frequency reference' |
| 10594 | unknown | unknown, 2 per cluster | yes |  |
| 10618 | unknown | unknown, 4 to 6 per cluster | yes |  |
| 10629 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 10630 | unknown | multiple cluster per 2 week, 5 per cluster | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10673 | unknown | 1 cluster per month, multiple per cluster | no |  |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | unknown | unknown | yes | evidence_not_text_contained |
| 10807 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | final_label_repaired: '2 cluster days per month' -> '2 cluster per month, multiple per cluster' |
| 10829 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | final_label_repaired: 'unknown' -> '2 cluster per month, multiple per cluster' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 3 per month' -> '2 to 3 cluster per month, 5 per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 10965 | unknown | 2 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '2 clusters per month' -> 'unknown' |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | final_label_repaired: '1 to 2 per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | final_label_repaired: '1 cluster 2 to 4 per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per 3 months' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 per month' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 cluster days per month' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '2 per month' -> '2 cluster per month, 3 to 4 per cluster' |
| 11197 | unknown | 1 cluster per month, 4 to 6 per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 11216 | seizure free for 4 month | unknown | no | evidence_not_text_contained |
| 11254 | seizure free for 3 month | unknown | no |  |
| 11259 | unknown | unknown | yes |  |
| 11262 | 4 per 2 month | unknown | no | final_label_repaired: 'unknown' -> '4 per 2 month' |
| 11272 | seizure free for 3 month | unknown | no |  |
| 11282 | seizure free for 3 month | unknown | no |  |
| 11337 | 1 per 2 month | unknown | no | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 11350 | multiple per day | unknown | yes | final_label_repaired: 'several per week' -> 'multiple per day' |
| 11380 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 11389 | 1 per 2 month | unknown | no | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 11400 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11409 | unknown | no seizure frequency reference | yes |  |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11658 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11737 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11824 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11841 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 12036 | multiple per day | multiple per day | yes |  |
| 12041 | multiple per day | multiple per day | yes |  |
| 12046 | multiple per day | multiple per day | yes |  |
| 12051 | multiple per day | multiple per day | yes |  |
| 12111 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12127 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12130 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12139 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12145 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12192 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12218 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12236 | multiple per day | 1 per day | no |  |
| 12246 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12314 | 3 per week | 3 per week | yes |  |
| 12366 | 4 per day | 4 per day | yes |  |
| 12378 | 4 per day | 4 per day | yes |  |
| 12383 | 4 per day | 4 per day | yes |  |
| 12403 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 12412 | 2 per day | 2 per day | yes |  |
| 12422 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12438 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12456 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12460 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12468 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12484 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12502 | 4 per day | 4 per day | yes |  |
| 12506 | 4 per day | 4 per day | yes |  |
| 12537 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12548 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12551 | 1 per day | 1 per day | yes | final_label_repaired: 'daily drop attacks' -> '1 per day' |
| 12556 | 1 per day | 1 per day | yes | final_label_repaired: 'daily drop attacks' -> '1 per day' |
| 12562 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12573 | 1 per day | 1 per day | yes | final_label_repaired: 'daily drop attacks' -> '1 per day' |
| 12584 | 1 per 3 month | 1 per week | no | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 12641 | 1 to 2 per week | 1 per day | no |  |
| 12665 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_text_contained |
| 12667 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12676 | 1 per day | 1 per day | yes | final_label_repaired: 'daily absences' -> '1 per day' |
| 12679 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12751 | 4 per day | 4 per day | yes |  |
| 12788 | 6 per year | 6 per 4 month | no | final_label_repaired: '6 so far this year' -> '6 per year' |
| 12810 | 5 per year | 5 per 2 month | no |  |
| 12823 | 1 per 3 to 4 week | 9 per month | no | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 12827 | 5 per year | 5 per 5 month | no | final_label_repaired: 'unknown' -> '5 per year' |
| 12835 | 4 per year | 4 per month | no |  |
| 12877 | 10 per year | 10 per 4 month | no | final_label_repaired: 'unknown' -> '10 per year' |
| 12882 | 7 per year | 7 per 4 month | no | final_label_repaired: '7 generalised tonic-clonic seizures this year to date; 1 to 2 focal impaired-awareness episodes per month' -> '7 per year' |
| 12901 | 8 per year | 8 per 5 month | no | final_label_repaired: 'unknown' -> '8 per year' |
| 12949 | 9 per year | 9 per 6 month | no | final_label_repaired: '9 so far this year' -> '9 per year' |
| 12950 | 7 per year | 7 per 3 month | no | final_label_repaired: '7 generalised tonic-clonic seizures this year to date; brief focal events approximately once every 2 to 3 weeks' -> '7 per year' |
| 12963 | unknown | unknown | yes |  |
| 12979 | 3 per year | 3 per 4 month | yes |  |
| 13008 | 4 per year | 4 per month | no | final_label_repaired: '4 tonic seizures in 2021 so far' -> '4 per year' |
| 13011 | 3 per year | 3 per 4 month | yes | final_label_repaired: '3 so far this year' -> '3 per year' |
| 13051 | unknown | 2 per 8 month | no | final_label_repaired: '1 generalised tonic-clonic seizure 3 weeks ago preceded by a cluster of absences, no further events since' -> 'unknown'; evidence_not_text_contained |
| 13058 | unknown | 2 per 7 month | no | final_label_repaired: '1 cluster per 3 weeks' -> 'unknown' |
| 13114 | multiple per day | 1 per year | no |  |
| 13122 | unknown | 3 per year | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 13149 | unknown | 3 per year | no |  |
| 13178 | 1 per 2 week | 1 per 6 month | no | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 13190 | 1 per month | 1 per 5 month | no |  |
| 13209 | 1 per month | 1 per 8 month | no |  |
| 13267 | 1 per month | 2 per 5 month | no |  |
| 13290 | 2 per month | 4 per 6 month | no | evidence_not_text_contained |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes |  |
| 13349 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13385 | seizure free for 1.5 year | seizure free for 1.5 year | yes |  |
| 13450 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over one year' -> 'seizure free for multiple year' |
| 13471 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13478 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over one year' -> 'seizure free for multiple year' |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13513 | seizure free for 1.5 year | seizure free for 1.5 year | yes |  |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13627 | 64 per 12 month | 64 per 12 month | yes | final_label_repaired: 'unknown' -> '64 per 12 month' |
| 13635 | 47 per 7 month | 47 per 7 month | yes | final_label_repaired: 'multiple per month' -> '47 per 7 month' |
| 13711 | 76 per 12 month | 76 per 12 month | yes | final_label_repaired: 'multiple per month' -> '76 per 12 month' |
| 13721 | 77 per 12 month | 77 per 12 month | yes | final_label_repaired: 'multiple per month' -> '77 per 12 month' |
| 13732 | 52 per 8 month | 52 per 8 month | yes | final_label_repaired: 'unknown' -> '52 per 8 month' |
| 13843 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13858 | no seizure frequency reference | seizure free for multiple month | no |  |
| 13889 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13893 | 2 per year | 2 per year | yes |  |
| 13922 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 seizures since medication increase' -> 'no seizure frequency reference' |
| 14002 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 14025 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 drop attacks since starting ketogenic diet 6 weeks ago' -> 'no seizure frequency reference' |
| 14029 | unknown | unknown | yes |  |
| 14040 | unknown | unknown | yes |  |
| 14076 | unknown | unknown | yes |  |
| 14092 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 myoclonic jerks since last clinic appointment' -> 'no seizure frequency reference' |
| 14096 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 events since last clinic appointment' -> 'no seizure frequency reference' |
| 14137 | 3 to 4 per 3 month | unknown | no | final_label_repaired: '3 to 4 per 3 months' -> '3 to 4 per 3 month' |
| 14146 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 seizures since starting Clobazam' -> 'no seizure frequency reference' |
| 14187 | unknown | 2 to 3 per month | no |  |
| 14214 | seizure free for 1 month | 2 to 4 per month | no |  |
| 14250 | 2 per week | 2 per month | no |  |
| 14282 | unknown | multiple per month | yes |  |
| 14284 | seizure free for multiple year | 2 to 3 per month | no | final_label_repaired: '2 to 3 in the week after 21-Feb, then seizure free' -> 'seizure free for multiple year' |
| 14317 | seizure free for 2 month | 4 per 2 month | no | evidence_not_text_contained |
| 14332 | seizure free for multiple year | 5 per 2 month | no | final_label_repaired: '5 seizures around early October then seizure free since' -> 'seizure free for multiple year' |
| 14335 | seizure free for multiple year | 3 to 4 per 2 month | no | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 14383 | seizure free for 3 month | 3 to 4 per 3 month | no |  |
| 14454 | seizure free for 2 month | 2 per 2 month | no |  |
| 14524 | unknown | 2 per 6 month | no |  |
| 14530 | no seizure frequency reference | 2 per 2 month | no | final_label_repaired: '2 events since May 2019' -> 'no seizure frequency reference'; evidence_not_text_contained |
| 14540 | seizure free for multiple year | 2 per 8 month | no | final_label_repaired: 'seizure free for 6 week' -> 'seizure free for multiple year' |
| 14562 | 2 to 3 per year | 3 per 6 month | yes | evidence_not_text_contained |
| 14567 | no seizure frequency reference | 3 per 3 month | no | final_label_repaired: '3 seizures over approximately 4 months' -> 'no seizure frequency reference'; evidence_not_text_contained |
| 14581 | seizure free for multiple year | 2 per 3 month | no | final_label_repaired: 'seizure free since late October 2014' -> 'seizure free for multiple year' |
| 14587 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 seizures in 3 months' -> '2 per 3 month' |
| 14592 | 3 per 6 month | 3 per 5 month | yes | final_label_repaired: '3 per 6 months' -> '3 per 6 month' |
| 14611 | no seizure frequency reference | 2 per 4 month | no |  |
| 14628 | unknown | 2 per 2 month | no | final_label_repaired: '2 events total, unknown recurrence rate' -> 'unknown' |
| 14635 | seizure free for multiple year | 5 per 4 month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year' |
| 14645 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 seizures in 6 months' -> '2 per 6 month'; evidence_not_text_contained |
| 14662 | 3 per 5 month | 3 per 4 month | yes | final_label_repaired: '3 seizures over 5 months' -> '3 per 5 month'; evidence_not_text_contained |
| 14672 | seizure free for 6 month | 3 per 8 month | no |  |
| 14706 | no seizure frequency reference | 2 per 5 month | no | final_label_repaired: '2 over 5 months' -> 'no seizure frequency reference' |
| 14765 | seizure free for 1 month | 1 per month | no |  |
| 14806 | seizure free for 1 month | 1 per 2 month | no |  |
| 14810 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year' |
| 14821 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 14872 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 14943 | seizure free for multiple year | 1 per 3 month | no | final_label_repaired: 'seizure free since 21 Feb' -> 'seizure free for multiple year' |
| 14949 | 1 per month | 1 per month | yes |  |
| 14965 | seizure free for multiple year | 1 per 3 month | no | final_label_repaired: 'seizure free since 20 May' -> 'seizure free for multiple year' |
| 14973 | seizure free for 1 month | 1 per month | no |  |
| 15004 | seizure free for 2 month | 1 per 3 month | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 15012 | seizure free for 2 month | 1 per 2 month | no |  |
| 15021 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 15029 | seizure free for 3 month | 1 per 3 month | no |  |
| 15094 | no seizure frequency reference | 4 per 13 month | no | final_label_repaired: '3 since Apr 2022' -> 'no seizure frequency reference' |
| 15108 | 2 to 3 per month | 3 to 4 per 15 month | no |  |
| 15127 | 4 per month | 5 per 13 month | no |  |
| 15129 | 4 per year | 4 per 15 month | yes | evidence_not_text_contained |
| 15141 | 3 to 4 per month | 4 to 5 per 15 month | no |  |
| 15168 | multiple per month | multiple per 15 month | yes | evidence_not_text_contained |
| 15193 | multiple per month | multiple per 13 month | yes | evidence_not_text_contained |
| 15242 | unknown | multiple cluster per 15 month, multiple per cluster | no | final_label_repaired: 'occasional clusters of myoclonic jerks' -> 'unknown' |
| 15262 | unknown | multiple cluster per 13 month, multiple per cluster | no |  |
| 15267 | no seizure frequency reference | 3 per 14 month | no |  |
| 15306 | 2 to 3 per month | 2 to 3 per 15 month | no |  |
| 15317 | 2 to 3 per month | 2 to 3 per 15 month | no |  |
| 15376 | 4 to 6 per day | 1 cluster per 2 week, 4 to 6 per cluster | no |  |
| 15404 | no seizure frequency reference | 1 cluster per 4 month, 3 to 4 per cluster | no | final_label_repaired: '3 to 4 per cluster' -> 'no seizure frequency reference'; evidence_not_text_contained |
| 15429 | unknown | 1 cluster per 2 month, 4 per cluster | no | final_label_repaired: '4 per day during clusters' -> 'unknown'; evidence_not_text_contained |
| 15431 | 5 per day | 1 cluster per 4 month, 5 per cluster | no | evidence_not_text_contained |
| 15442 | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | yes | final_label_repaired: 'multiple per day' -> '1 cluster per 4 day, 2 per cluster' |
| 15470 | multiple per day | 1 cluster per 5 day, multiple per cluster | no |  |
| 15479 | 1 cluster per 4 to 5 day, 2 per cluster | 1 cluster per 4 to 5 day, 2 per cluster | yes | final_label_repaired: 'multiple per cluster' -> '1 cluster per 4 to 5 day, 2 per cluster' |
| 15497 | unknown | 1 cluster per 4 to 5 day, 5 per cluster | no | final_label_repaired: '5 per day during clusters' -> 'unknown' |
| 15503 | unknown | 1 cluster per 5 day, 3 to 4 per cluster | no | final_label_repaired: '3 to 4 per 24 hours during clusters' -> 'unknown' |
| 15513 | unknown | 1 cluster per 4 to 5 day, 2 to 3 per cluster | no | final_label_repaired: '2 to 3 per day during clusters' -> 'unknown' |
| 15519 | unknown | 1 cluster per 4 day, 3 per cluster | no | final_label_repaired: '3 per day during clusters' -> 'unknown' |
| 15529 | unknown | 1 cluster per 3 day, 4 per cluster | no | final_label_repaired: '4 per day during clusters' -> 'unknown' |
| 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15614 | 3 per week | 3 per week | yes |  |
| 15628 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 15639 | 2 per week | 2 per week | yes |  |
| 15642 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 15650 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 15672 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 15697 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 15715 | multiple per month | 1 per day | no | final_label_repaired: 'multiple per day' -> 'multiple per month' |
| 15745 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15766 | 4 per week | 4 per week | yes | final_label_repaired: '4 days per week' -> '4 per week' |
| 15768 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15771 | 3 per week | 3 per week | yes |  |
| 15772 | 2 per week | 2 per week | yes | final_label_repaired: '2 days per week' -> '2 per week' |
| 15774 | 2 per week | 2 per week | yes | final_label_repaired: '2 days per week' -> '2 per week' |
| 15783 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15802 | 7 per week | 7 per week | yes |  |
| 15831 | 2 to 4 per day | 2 to 4 per day | yes |  |
| 15834 | 5 per week | 5 per week | yes |  |
| 15964 | 11 per 2 month | 11 per 3 month | no | final_label_repaired: '3 to 4 per month' -> '11 per 2 month' |
| 15965 | 13 per 2 month | 13 per 2 month | yes | final_label_repaired: '9 per month' -> '13 per 2 month' |
| 15966 | 5 per 2 month | 5 per 3 month | yes | final_label_repaired: '5 per 3 months' -> '5 per 2 month' |
| 15982 | 8 per month | 9 per 2 month | yes |  |
| 15986 | 11 per 2 month | 11 per 3 month | no | final_label_repaired: '6 per month' -> '11 per 2 month' |
| 15992 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '3 to 4 per month' -> '7 per 2 month' |
| 15997 | 10 per 2 month | 10 per 3 month | no | final_label_repaired: 'unknown' -> '10 per 2 month' |
| 16021 | 9 per 2 month | 9 per 3 month | no | final_label_repaired: '8 per 2 months' -> '9 per 2 month' |
| 16041 | 9 per 2 month | 9 per 3 month | no | final_label_repaired: '7 per month' -> '9 per 2 month' |
| 16084 | no seizure frequency reference | 8 per 4 month | no | final_label_repaired: 'no seizures this month' -> 'no seizure frequency reference'; evidence_not_text_contained |
| 16091 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '2 per month' -> '3 per 3 month' |
| 16097 | 1 per month | 17 per 4 month | no |  |
| 16107 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '4 per month' -> '8 per 3 month' |
| 16108 | 1 per month | 12 per 4 month | no |  |
| 16132 | 13 per 2 month | 15 per 3 month | yes | final_label_repaired: 'unknown' -> '13 per 2 month' |
| 16133 | 18 per 4 month | 18 per 4 month | yes | final_label_repaired: '6 per month' -> '18 per 4 month' |
| 16161 | 7 per month | 18 per 3 month | yes |  |
| 16162 | 6 per month | 11 per 3 month | no |  |
| 16181 | 15 per 4 month | 15 per 4 month | yes | final_label_repaired: '4 per month' -> '15 per 4 month' |
| 16195 | 6 per month | 16 per 4 month | no |  |
| 16203 | 8 per 2 month | 9 per 3 month | no | final_label_repaired: 'multiple per month' -> '8 per 2 month' |
| 16204 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: 'unknown' -> '5 per 3 month' |
| 16220 | no seizure frequency reference | 11 per 4 month | no | final_label_repaired: 'no seizures this month' -> 'no seizure frequency reference' |
| 16324 | 7 per 2 month | 10 per 3 month | yes | final_label_repaired: 'unknown' -> '7 per 2 month' |
| 16335 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: 'unknown' -> '7 per 3 month' |
| 16356 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 cluster every 4 days' -> '1 per 4 day' |
| 16394 | 1 per 2 to 4 day | 1 per 2 to 4 day | yes | final_label_repaired: '1 cluster every 2 to 4 days' -> '1 per 2 to 4 day' |
| 16408 | 1 per day | 1 per 3 day | no | final_label_repaired: '2 to 3 per week' -> '1 per day' |
| 16429 | 1 per day | 1 per 2 to 3 day | no | final_label_repaired: '2 to 3 per week' -> '1 per day' |
| 16432 | 1 per day | 1 per 2 day | no | final_label_repaired: 'multiple per week' -> '1 per day' |
| 16450 | multiple per day | 1 per multiple day | yes |  |
| 16529 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster every 5 days' -> '1 per 5 day' |
| 16557 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '1 cluster every 2 to 3 days' -> '1 per 2 to 3 day' |
| 16574 | unknown | 1 per 4 day | no | final_label_repaired: '1 cluster per 4 days' -> 'unknown' |
| 16590 | unknown | 1 per 4 to 5 day | no |  |
| 16618 | unknown | 1 per 5 day | no |  |
| 16645 | 4 per 2 month | 5 per 7 month | no | final_label_repaired: 'unknown' -> '4 per 2 month' |
| 16674 | unknown | 7 per 6 month | no |  |
| 16685 | 9 per 2 month | 10 per 3 month | no | final_label_repaired: 'unknown' -> '9 per 2 month' |
| 16697 | 3 per 6 month | 3 per 6 month | yes | final_label_repaired: '3 per 6 months' -> '3 per 6 month' |
| 16704 | unknown | 9 per 6 month | no |  |
| 16714 | unknown | 5 per 6 month | no |  |
| 16717 | 1 per month | 5 per 6 month | no |  |
| 16719 | 1 per week | 7 per 6 month | no |  |
| 16728 | 3 per year | 4 per 6 month | yes |  |
| 16750 | unknown | 6 per 7 month | no |  |
| 16757 | unknown | 13 per 6 month | no |  |
| 16758 | unknown | 9 per 5 month | no |  |
| 16772 | unknown | 9 per 5 month | no |  |
| 16774 | unknown | 19 per 7 month | no |  |
| 16780 | unknown | 3 per 7 month | no |  |
| 16824 | 10 per 2 month | 11 per 5 month | no | final_label_repaired: 'unknown' -> '10 per 2 month' |
| 16833 | unknown | 8 per 6 month | no |  |
| 16839 | unknown | 9 per 4 month | no |  |
| 16867 | 6 per 7 month | 6 per 7 month | yes | final_label_repaired: '6 per 7 months' -> '6 per 7 month' |
| 16907 | unknown | 9 per 6 month | no |  |
| 16938 | 1 per 2 month | 2 per week | no | final_label_repaired: '2 per 2 months' -> '1 per 2 month' |
| 16947 | 1 per 2 month | 2 per week | no | final_label_repaired: '4 per 2 months' -> '1 per 2 month' |
| 16961 | 1 per 3 month | 2 per week | no | final_label_repaired: '3 per 3 months' -> '1 per 3 month' |
| 16983 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 16990 | 4 to 5 per week | 4 to 5 per week | yes |  |
| 17001 | 5 per week | 5 per week | yes |  |
| 17003 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 17110 | 4 to 5 per week | 4 to 5 cluster per week, multiple per cluster | no |  |
| 17135 | 1 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | no | final_label_repaired: '5 per month' -> '1 cluster per month, multiple per cluster' |
| 17146 | multiple per week | 1 per day | no |  |
| 17167 | 1 per 6 month | 1 per week | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17189 | 1 per 6 month | 1 per month | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17200 | 1 per 6 month | 1 per month | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17201 | 4 per month | 4 per month | yes |  |
| 17273 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes |  |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 per 1 to 2 days' -> '1 per 1 to 2 day' |
