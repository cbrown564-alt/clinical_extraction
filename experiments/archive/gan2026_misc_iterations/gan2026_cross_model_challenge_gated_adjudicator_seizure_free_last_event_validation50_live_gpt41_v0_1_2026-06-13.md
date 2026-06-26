# Gan 2026 Cross-Model Challenge Adjudicator

Date: 2026-06-13

This is a validation-development V11 open peer-challenge artifact.
The model chooses among saved GPT, Qwen, and DeepSeek structured-event finals.

## Experiment Unit

- Work class: V11 open cross-model peer challenge.
- Rows: 50
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1`
- Prompt version: `gan2026_cross_model_challenge_adjudicator_v0_1`
- Safety policy: `high_precision_peer_gate`
- JSONL artifact: `experiments\gan2026_cross_model_challenge_gated_adjudicator_seizure_free_last_event_validation50_live_gpt41_v0_1_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 50
- Model calls attempted: 50
- Call failures: 0
- Parse/schema/label failures: 0
- Action-render fallbacks: 0
- Exact evidence substrings: 49
- GPT V0 Purist: 15/50
- Raw declared Purist: 11/50
- Final Purist: 16/50
- Net Purist gain vs GPT V0: 1
- Changed-label precision vs GPT V0: 0.3333
- Selected agents: `{'deepseek': 11, 'gpt': 23, 'qwen': 16}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V11 open cross-model challenge adjudicator; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Selected | GPT | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 13051 | `deepseek` | `1 per 8 month` | `seizure free for multiple year` | `1 per 8 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9250 | `qwen` | `unknown` | `seizure free for 6 month` | `unknown` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 2932 | `qwen` | `13 per 2 month` | `13 per 2 month` | `13 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 2992 | `qwen` | `1 per 8 month` | `1 per 8 month` | `1 per 8 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 3015 | `gpt` | `1 per 13 month` | `1 per 13 month` | `1 per 13 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 4839 | `qwen` | `2025 per 4 month` | `1 per 5 month` | `2025 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6358 | `qwen` | `2 per 2 month` | `1 per 16 month` | `2 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 11216 | `gpt` | `seizure free for 4 month` | `seizure free for 4 month` | `seizure free for 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 11254 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 11272 | `qwen` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 11282 | `gpt` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 3534 | `gpt` | `seizure free for 7 month` | `seizure free for 7 month` | `seizure free for 7 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6571 | `deepseek` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14635 | `qwen` | `1 per 5 month` | `5 per 5 month` | `1 per 5 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 3371 | `deepseek` | `no seizure frequency reference` | `seizure free for multiple year` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6077 | `deepseek` | `no seizure frequency reference` | `seizure free for 8 month` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 8160 | `deepseek` | `seizure free for multiple year` | `no seizure frequency reference` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 8180 | `deepseek` | `1 per 6 month` | `no seizure frequency reference` | `1 per 6 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 8400 | `gpt` | `multiple per month` | `multiple per month` | `multiple per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 11389 | `qwen` | `no seizure frequency reference` | `1 per month` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13209 | `deepseek` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15470 | `gpt` | `multiple per day` | `multiple per day` | `multiple per day` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6368 | `qwen` | `3 per 6 week` | `1 per 1 to 2 week` | `3 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6987 | `deepseek` | `10 to 15 per 1 year` | `unknown` | `unknown` | `wrong_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10245 | `gpt` | `2 per 6 month` | `2 per 6 month` | `2 per 6 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13267 | `qwen` | `no seizure frequency reference` | `multiple per week` | `no seizure frequency reference` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15108 | `qwen` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9937 | `deepseek` | `multiple per month` | `unknown` | `multiple per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10434 | `gpt` | `multiple per week` | `multiple per week` | `multiple per week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14025 | `gpt` | `2 per 6 week` | `2 per 6 week` | `2 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 17135 | `gpt` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5763 | `qwen` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5837 | `qwen` | `1 per 3 week` | `multiple per week` | `1 per 3 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 7615 | `qwen` | `2 per 10 month` | `multiple per week` | `2 per 10 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9943 | `gpt` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13843 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 16938 | `gpt` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 17110 | `deepseek` | `unknown` | `4 to 5 per week` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 8924 | `deepseek` | `seizure free for multiple year` | `1 per 5 month` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14214 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14282 | `gpt` | `10 per 6 week` | `10 per 6 week` | `10 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 8144 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14250 | `qwen` | `2 per 1 month` | `2 per 1 month` | `2 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids; final_label_format_repaired: '2 per 1 month' -> '2 per month' |
| 16220 | `qwen` | `11 per 4 month` | `11 per 2 month` | `11 per 4 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5092 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5110 | `gpt` | `seizure free for 3 month` | `seizure free for 3 month` | `seizure free for 3 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10371 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13190 | `gpt` | `1 per 5 month` | `1 per 5 month` | `1 per 5 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 14284 | `gpt` | `2 to 3 per 1 month` | `2 to 3 per 1 month` | `2 to 3 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids; final_label_format_repaired: '2 to 3 per 1 month' -> '2 to 3 per month' |
| 14530 | `gpt` | `2 per 2 month` | `2 per 2 month` | `2 per 2 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
