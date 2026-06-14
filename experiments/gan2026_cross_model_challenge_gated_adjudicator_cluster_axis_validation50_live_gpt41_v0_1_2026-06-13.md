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
- JSONL artifact: `experiments\gan2026_cross_model_challenge_gated_adjudicator_cluster_axis_validation50_live_gpt41_v0_1_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 50
- Model calls attempted: 50
- Call failures: 0
- Parse/schema/label failures: 0
- Action-render fallbacks: 0
- Exact evidence substrings: 49
- GPT V0 Purist: 7/50
- Raw declared Purist: 12/50
- Final Purist: 8/50
- Net Purist gain vs GPT V0: 1
- Changed-label precision vs GPT V0: 1.0
- Selected agents: `{'deepseek': 15, 'gpt': 20, 'qwen': 15}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V11 open cross-model challenge adjudicator; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Selected | GPT | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10237 | `gpt` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9250 | `qwen` | `unknown` | `seizure free for 6 month` | `unknown` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13051 | `deepseek` | `1 per 8 month` | `seizure free for multiple year` | `1 per 8 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 17135 | `gpt` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5837 | `qwen` | `1 per 3 week` | `multiple per week` | `1 per 3 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 7167 | `deepseek` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10097 | `deepseek` | `3 per month` | `3 per month` | `3 per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10245 | `gpt` | `2 per 6 month` | `2 per 6 month` | `2 per 6 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10630 | `deepseek` | `unknown` | `no seizure frequency reference` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10967 | `gpt` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 17110 | `deepseek` | `unknown` | `4 to 5 per week` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 4839 | `qwen` | `2025 per 4 month` | `1 per 5 month` | `2025 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6571 | `deepseek` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6987 | `deepseek` | `10 to 15 per 1 year` | `unknown` | `unknown` | `wrong_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9943 | `gpt` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13209 | `deepseek` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 16714 | `qwen` | `5 per 6 month` | `5 per 4 month` | `5 per 6 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6077 | `deepseek` | `no seizure frequency reference` | `seizure free for 8 month` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 5763 | `qwen` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6368 | `qwen` | `3 per 6 week` | `1 per 1 to 2 week` | `3 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 7615 | `qwen` | `2 per 10 month` | `multiple per week` | `2 per 10 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13267 | `qwen` | `no seizure frequency reference` | `multiple per week` | `no seizure frequency reference` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15470 | `gpt` | `multiple per day` | `multiple per day` | `multiple per day` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 16839 | `deepseek` | `19 per 2 month` | `12 per 3 month` | `19 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 2459 | `gpt` | `5 per 5 month` | `5 per 5 month` | `5 per 5 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 2992 | `qwen` | `1 per 8 month` | `1 per 8 month` | `1 per 8 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 6321 | `gpt` | `2 per 3 month` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 9937 | `deepseek` | `multiple per month` | `unknown` | `multiple per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10434 | `gpt` | `multiple per week` | `multiple per week` | `multiple per week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10673 | `deepseek` | `unknown` | `multiple per month` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12366 | `deepseek` | `unknown` | `multiple per day` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12383 | `gpt` | `unknown` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12412 | `deepseek` | `unknown` | `multiple per day` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15108 | `qwen` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 16938 | `gpt` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 16947 | `gpt` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10829 | `qwen` | `unknown` | `2 cluster per month, multiple per cluster` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10965 | `qwen` | `unknown` | `2 cluster per month, 4 to 5 per cluster` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12502 | `gpt` | `4 per day` | `4 per day` | `4 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 7401 | `qwen` | `unknown` | `2 to 3 per month` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 15431 | `gpt` | `5 per 4 month` | `5 per 4 month` | `5 per 4 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 1880 | `qwen` | `7 per 2 month` | `multiple per week` | `7 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10183 | `deepseek` | `2 per 6 week` | `unknown` | `2 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10264 | `gpt` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10371 | `gpt` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 10542 | `gpt` | `unknown` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12236 | `gpt` | `multiple per day` | `multiple per day` | `multiple per day` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 12665 | `qwen` | `1 to 2 per month` | `1 per day` | `1 to 2 per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13058 | `gpt` | `1 per 7 month` | `1 per 7 month` | `1 per 7 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 13290 | `gpt` | `2 per 2 week` | `2 per 2 week` | `2 per 2 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
