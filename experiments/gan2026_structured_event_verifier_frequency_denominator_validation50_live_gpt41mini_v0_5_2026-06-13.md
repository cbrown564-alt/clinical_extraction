# Gan 2026 Structured-Event Verifier

Date: 2026-06-13

This is a validation-development V4 verifier-first structured-event artifact.
The model chooses an explicit verifier action over saved LLM structured events.

## Experiment Unit

- Work class: V4 verifier-first structured-event correction.
- Rows: 50
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_structured_event_verifier_v0_5`
- Structured-event source: `experiments\gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`
- JSONL artifact: `experiments\gan2026_structured_event_verifier_frequency_denominator_validation50_live_gpt41mini_v0_5_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 50
- Model calls attempted: 50
- Call failures: 0
- Parse/schema/label failures: 0
- Action-render failures: 0
- Exact evidence substrings: 46
- V0 Purist: 7/50
- Raw model Purist: 9/50
- Format-only Purist: 9/50
- Final Purist: 8/50
- Net Purist gain vs V0: 1
- Changed-label precision vs V0: 1.0
- Verifier actions: `{'keep_original_structured_event_final': 48, 'replace_with_existing_event': 2}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V4 verifier scaffold; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Action | V0 | Raw | Format-only | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10237 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 13051 | `keep_original_structured_event_final` | `1 per 8 month` | `1 per 8 month` | `1 per 8 month` | `1 per 8 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 9250 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 2459 | `replace_with_existing_event` | `5 per 5 month` | `7 to 9 per 2 week` | `7 to 9 per 2 week` | `7 to 9 per 2 week` | `wrong_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 5763 | `keep_original_structured_event_final` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 15108 | `keep_original_structured_event_final` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 15470 | `keep_original_structured_event_final` | `multiple per day` | `multiple per day` | `multiple per day` | `multiple per day` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 16203 | `keep_original_structured_event_final` | `8 per 2 month` | `8 per 2 month` | `8 per 2 month` | `8 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 16714 | `keep_original_structured_event_final` | `5 per 6 month` | `5 per 6 month` | `5 per 6 month` | `5 per 6 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 16839 | `keep_original_structured_event_final` | `19 per 2 month` | `19 per 2 month` | `19 per 2 month` | `19 per 2 month` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 16867 | `keep_original_structured_event_final` | `6 per 4 month` | `6 per 4 month` | `6 per 4 month` | `6 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 16938 | `keep_original_structured_event_final` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 16947 | `keep_original_structured_event_final` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 16961 | `keep_original_structured_event_final` | `1 per 3 month` | `1 per 3 month` | `1 per 3 month` | `1 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 17135 | `keep_original_structured_event_final` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 17167 | `keep_original_structured_event_final` | `1 per 6 month` | `1 per 6 month` | `1 per 6 month` | `1 per 6 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 7615 | `keep_original_structured_event_final` | `2 per 10 month` | `2 per 10 month` | `2 per 10 month` | `2 per 10 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 9943 | `keep_original_structured_event_final` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 14635 | `keep_original_structured_event_final` | `1 per 5 month` | `1 per 5 month` | `1 per 5 month` | `1 per 5 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 17110 | `replace_with_existing_event` | `unknown` | `4 to 5 per week` | `4 to 5 per week` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 2932 | `keep_original_structured_event_final` | `13 per 2 month` | `13 per 2 month` | `13 per 2 month` | `13 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 5837 | `keep_original_structured_event_final` | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 6321 | `keep_original_structured_event_final` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 6368 | `keep_original_structured_event_final` | `3 per 6 week` | `3 per 6 week` | `3 per 6 week` | `3 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 7195 | `keep_original_structured_event_final` | `1 per month` | `1 per month` | `1 per month` | `1 per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 8400 | `keep_original_structured_event_final` | `multiple per month` | `multiple per month` | `multiple per month` | `multiple per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 10097 | `keep_original_structured_event_final` | `3 per month` | `3 per month` | `3 per month` | `3 per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 10434 | `keep_original_structured_event_final` | `multiple per week` | `multiple per week` | `multiple per week` | `multiple per week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 10673 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 12366 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 12383 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 12412 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 14025 | `keep_original_structured_event_final` | `2 per 6 week` | `2 per 6 week` | `2 per 6 week` | `2 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 4839 | `keep_original_structured_event_final` | `2025 per 4 month` | `seizure free` | `seizure free for multiple year` | `2025 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile; final_label_format_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 6358 | `keep_original_structured_event_final` | `2 per 2 month` | `2 per 2 month` | `2 per 2 month` | `2 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 7167 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 8160 | `keep_original_structured_event_final` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 13209 | `keep_original_structured_event_final` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 13267 | `keep_original_structured_event_final` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 13843 | `keep_original_structured_event_final` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 6244 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 6987 | `keep_original_structured_event_final` | `10 to 15 per 1 year` | `10 to 15 per 1 year` | `10 to 15 per year` | `10 to 15 per 1 year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile; final_label_format_repaired: '10 to 15 per 1 year' -> '10 to 15 per year' |
| 10245 | `keep_original_structured_event_final` | `2 per 6 month` | `2 per 6 month` | `2 per 6 month` | `2 per 6 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 10630 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 3371 | `keep_original_structured_event_final` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 9937 | `keep_original_structured_event_final` | `multiple per month` | `multiple per month` | `multiple per month` | `multiple per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 3534 | `keep_original_structured_event_final` | `seizure free for 7 month` | `seizure free for 7 month` | `seizure free for 7 month` | `seizure free for 7 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 10967 | `keep_original_structured_event_final` | `unknown` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 11389 | `keep_original_structured_event_final` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
| 6077 | `keep_original_structured_event_final` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:contradiction_profile |
