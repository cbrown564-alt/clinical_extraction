# Gan 2026 Cross-Model Challenge Adjudicator

Date: 2026-06-13

This is a validation-development V11 open peer-challenge artifact.
The model chooses among saved GPT, Qwen, and DeepSeek structured-event finals.

## Experiment Unit

- Work class: V11 open cross-model peer challenge.
- Rows: 50
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_cross_model_challenge_adjudicator_v0_1`
- Safety policy: `none_model_owned_agent_selection`
- JSONL artifact: `experiments\gan2026_cross_model_challenge_adjudicator_hard50_live_gpt41mini_v0_2_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 50
- Model calls attempted: 50
- Call failures: 0
- Parse/schema/label failures: 0
- Action-render fallbacks: 0
- Exact evidence substrings: 50
- GPT V0 Purist: 39/50
- Raw declared Purist: 38/50
- Final Purist: 38/50
- Net Purist gain vs GPT V0: -1
- Changed-label precision vs GPT V0: 0.0833
- Selected agents: `{'deepseek': 18, 'gpt': 19, 'qwen': 13}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V11 open cross-model challenge adjudicator; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Selected | GPT | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 3356 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 3528 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 4690 | `qwen` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5534 | `gpt` | `1 per 2 week` | `1 per 2 week` | `1 per 2 week` | `wrong_to_wrong` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5974 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6077 | `deepseek` | `no seizure frequency reference` | `seizure free for 8 month` | `seizure free for 8 month` | `correct_to_wrong` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6094 | `deepseek` | `4 per 2 month` | `4 per 2 month` | `4 per 2 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6131 | `deepseek` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6153 | `deepseek` | `9 per 4 week` | `9 per 4 week` | `9 per 4 week` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6209 | `qwen` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6244 | `deepseek` | `unknown` | `2 per week` | `2 per week` | `correct_to_wrong` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6321 | `deepseek` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6368 | `qwen` | `3 per 6 week` | `1 per 1 to 2 week` | `1 per 1 to 2 week` | `wrong_to_wrong` | yes | decision_enum_shape_repaired:selected_agent_id; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6501 | `deepseek` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6571 | `deepseek` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6987 | `gpt` | `10 to 15 per 1 year` | `10 to 15 per 1 year` | `10 to 15 per year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids; final_label_format_repaired: '10 to 15 per 1 year' -> '10 to 15 per year' |
| 7168 | `deepseek` | `unknown` | `multiple per week` | `multiple per week` | `correct_to_correct` | yes | json_dialect_repaired: escaped_list_item_quotes; decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 7615 | `qwen` | `2 per 10 month` | `multiple per week` | `multiple per week` | `wrong_to_wrong` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9496 | `deepseek` | `12 per 17 month` | `12 per 24 month` | `12 per 24 month` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9888 | `gpt` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9937 | `deepseek` | `multiple per month` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9943 | `gpt` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9955 | `gpt` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10266 | `gpt` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10618 | `qwen` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10677 | `gpt` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10996 | `deepseek` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12422 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | json_dialect_repaired: escaped_list_item_quotes; decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12438 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12456 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12460 | `gpt` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12468 | `qwen` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13843 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13858 | `qwen` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13889 | `qwen` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14025 | `deepseek` | `2 per 6 week` | `2 per 6 week` | `2 per 6 week` | `wrong_to_wrong` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14076 | `gpt` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14810 | `qwen` | `1 per 1 month` | `1 per 1 month` | `1 per month` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids; final_label_format_repaired: '1 per 1 month' -> '1 per month' |
| 14821 | `qwen` | `1 per 1 month` | `1 per 1 month` | `1 per month` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids; final_label_format_repaired: '1 per 1 month' -> '1 per month' |
| 15168 | `deepseek` | `multiple per month` | `multiple per month` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15193 | `qwen` | `no seizure frequency reference` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15593 | `deepseek` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15672 | `deepseek` | `1 per day` | `1 per day` | `1 per day` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15834 | `gpt` | `5 per week` | `5 per week` | `5 per week` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 2748 | `qwen` | `7 per 10 month` | `1 per month` | `1 per month` | `wrong_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 4368 | `qwen` | `5 per 2 month` | `5 per 2 month` | `5 per 2 month` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5921 | `deepseek` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6889 | `gpt` | `multiple per week` | `multiple per week` | `multiple per week` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10386 | `gpt` | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 11216 | `deepseek` | `seizure free for 4 month` | `seizure free for 4 month` | `seizure free for 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
