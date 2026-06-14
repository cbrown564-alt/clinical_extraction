# Gan 2026 Cross-Model Structured-Event Adjudicator

Date: 2026-06-13

This is a validation-development V10 coordinator over saved LLM agents.
The model may keep GPT or select Qwen/DeepSeek; deterministic code renders the selected agent final.

## Experiment Unit

- Work class: V10 cross-model structured-event adjudicator.
- Rows: 50
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_cross_model_structured_event_adjudicator_v0_3`
- Safety gate version: `gan2026_cross_model_peer_selection_gate_v0_2`
- JSONL artifact: `experiments\gan2026_cross_model_structured_event_adjudicator_hard50_live_gpt41mini_v0_4_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 50
- Model calls attempted: 50
- Call failures: 0
- Parse/schema/label failures: 0
- Action-render fallbacks: 0
- Exact evidence substrings: 49
- GPT V0 Purist: 39/50
- Raw declared Purist: 38/50
- Format-only declared Purist: 38/50
- Final Purist: 40/50
- Net Purist gain vs GPT V0: 1
- Changed-label precision vs GPT V0: 0.25
- Selected agents: `{'deepseek': 2, 'gpt': 47, 'qwen': 1}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V10 cross-model structured-event adjudicator; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Selected | GPT | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 3356 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 3528 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 4690 | `gpt` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5534 | `gpt` | `1 per 2 week` | `1 per 2 week` | `1 per 2 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5974 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6077 | `deepseek` | `no seizure frequency reference` | `seizure free for 8 month` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6094 | `gpt` | `4 per 2 month` | `4 per 2 month` | `4 per 2 month` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6131 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6153 | `gpt` | `9 per 4 week` | `9 per 4 week` | `9 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6209 | `gpt` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6244 | `deepseek` | `unknown` | `2 per week` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6321 | `gpt` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6368 | `gpt` | `3 per 6 week` | `3 per 6 week` | `3 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6501 | `gpt` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6571 | `gpt` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6987 | `gpt` | `10 to 15 per 1 year` | `10 to 15 per 1 year` | `10 to 15 per year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids; final_label_format_repaired: '10 to 15 per 1 year' -> '10 to 15 per year' |
| 7168 | `gpt` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 7615 | `gpt` | `2 per 10 month` | `2 per 10 month` | `2 per 10 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9496 | `gpt` | `12 per 17 month` | `12 per 17 month` | `12 per 17 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9888 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9937 | `gpt` | `multiple per month` | `multiple per month` | `multiple per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9943 | `gpt` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9955 | `gpt` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10266 | `gpt` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10618 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10677 | `gpt` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10996 | `gpt` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12422 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12438 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12456 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12460 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12468 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13843 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13858 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13889 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14025 | `gpt` | `2 per 6 week` | `2 per 6 week` | `2 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14076 | `gpt` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14810 | `gpt` | `1 per 1 month` | `1 per 1 month` | `1 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids; final_label_format_repaired: '1 per 1 month' -> '1 per month' |
| 14821 | `gpt` | `1 per 1 month` | `1 per 1 month` | `1 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids; final_label_format_repaired: '1 per 1 month' -> '1 per month' |
| 15168 | `gpt` | `multiple per month` | `multiple per month` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15193 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15593 | `gpt` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15672 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15834 | `gpt` | `5 per week` | `5 per week` | `5 per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 2748 | `qwen` | `7 per 10 month` | `1 per month` | `1 per month` | `wrong_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 4368 | `gpt` | `5 per 2 month` | `5 per 2 month` | `5 per 2 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5921 | `gpt` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6889 | `gpt` | `multiple per week` | `multiple per week` | `multiple per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10386 | `gpt` | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | `correct_to_correct` | yes | decision_field_defaulted:attribution; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 11216 | `gpt` | `seizure free for 4 month` | `seizure free for 4 month` | `seizure free for 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
