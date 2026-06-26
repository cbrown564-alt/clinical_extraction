# Gan 2026 LLM Event Reasoner

Date: 2026-06-13

This is a validation-development Stage 1 structured-event reasoning artifact.
The model sees saved LLM structured events, not deterministic final-label candidates.

## Experiment Unit

- Work class: V1 single LLM event reasoner scaffold.
- Rows: 50
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_llm_event_reasoner_v1_2`
- Structured-event source: `experiments\gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`
- JSONL artifact: `experiments\gan2026_llm_event_reasoner_hard50_live_gpt41mini_v1_2_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 50
- Model calls attempted: 50
- Call failures: 0
- Parse/schema/label failures: 0
- Exact evidence substrings: 46
- V0 Purist: 39/50
- Raw model Purist: 34/50
- Format-only Purist: 34/50
- Final Purist: 34/50
- Net Purist gain vs V0: -5
- Changed-label precision vs V0: 0.0769

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development Stage 1 scaffold; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | V0 | Raw | Format-only | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 3356 | `no seizure frequency reference` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 3528 | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 4690 | `multiple per day` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 5534 | `1 per 2 week` | `1 per 2 week` | `1 per 2 week` | `1 per 2 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 5974 | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6077 | `no seizure frequency reference` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6094 | `4 per 2 month` | `4 per 2 month` | `4 per 2 month` | `4 per 2 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6131 | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6153 | `9 per 4 week` | `9 per 4 week` | `9 per 4 week` | `9 per 4 week` | `correct_to_correct` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6209 | `multiple per day` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6244 | `unknown` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6321 | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6368 | `3 per 6 week` | `3 per 6 week` | `3 per 6 week` | `3 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6501 | `unknown` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6571 | `1 per 4 month` | `seizure free` | `seizure free for multiple year` | `seizure free for multiple year` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; final_label_format_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 6987 | `10 to 15 per 1 year` | `unknown` | `unknown` | `unknown` | `wrong_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 7168 | `unknown` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 7615 | `2 per 10 month` | `2 per 10 month` | `2 per 10 month` | `2 per 10 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 9496 | `12 per 17 month` | `6 per 12 month` | `6 per 12 month` | `6 per 12 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 9888 | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 9937 | `multiple per month` | `multiple per month` | `multiple per month` | `multiple per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 9943 | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 9955 | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10266 | `unknown` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10618 | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10677 | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 per month` | `1 to 2 per month` | `1 to 2 per month` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12422 | `1 per day` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12438 | `1 per day` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12456 | `1 per day` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12460 | `1 per day` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12468 | `1 per day` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 13843 | `seizure free for multiple year` | `unknown` | `unknown` | `unknown` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 13858 | `seizure free for multiple year` | `unknown` | `unknown` | `unknown` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 13889 | `seizure free for multiple year` | `unknown` | `unknown` | `unknown` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 14025 | `2 per 6 week` | `2 per 6 week` | `2 per 6 week` | `2 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 14076 | `unknown` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 14810 | `1 per 1 month` | `seizure free` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; final_label_format_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14821 | `1 per 1 month` | `seizure free` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; final_label_format_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 15168 | `multiple per month` | `multiple per month` | `multiple per month` | `multiple per month` | `correct_to_correct` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 15193 | `no seizure frequency reference` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 15672 | `1 per day` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 15834 | `5 per week` | `5 per week` | `5 per week` | `5 per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 2748 | `7 per 10 month` | `7 per 10 month` | `7 per 10 month` | `7 per 10 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 4368 | `5 per 2 month` | `5 per 2 month` | `5 per 2 month` | `5 per 2 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 5921 | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6889 | `multiple per week` | `multiple per week` | `multiple per week` | `multiple per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10386 | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 11216 | `seizure free for 4 month` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
