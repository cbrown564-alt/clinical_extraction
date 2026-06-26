# Gan 2026 Cross-Model Structured-Event Adjudicator

Date: 2026-06-13

This is a validation-development V10 coordinator over saved LLM agents.
The model may keep GPT or select Qwen/DeepSeek; deterministic code renders the selected agent final.

## Experiment Unit

- Work class: V10 cross-model structured-event adjudicator.
- Rows: 25
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_cross_model_structured_event_adjudicator_v0_1`
- JSONL artifact: `experiments\gan2026_cross_model_structured_event_adjudicator_validation25_live_gpt41mini_v0_1_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 25
- Model calls attempted: 25
- Call failures: 0
- Parse/schema/label failures: 0
- Action-render fallbacks: 23
- Exact evidence substrings: 24
- GPT V0 Purist: 25/25
- Raw declared Purist: 2/25
- Format-only declared Purist: 2/25
- Final Purist: 25/25
- Net Purist gain vs GPT V0: 0
- Changed-label precision vs GPT V0: None
- Selected agents: `{'gpt': 2}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V10 cross-model structured-event adjudicator; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Selected | GPT | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | `None` | `4 per day` | `None` | `4 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 40 | `None` | `4 per week` | `None` | `4 per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 79 | `None` | `6 to 7 per year` | `None` | `6 to 7 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Input should be 'gpt', 'qwen' or 'deepseek' |
| 103 | `None` | `2 to 4 per year` | `None` | `2 to 4 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 128 | `gpt` | `17 per month` | `17 per month` | `17 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile |
| 156 | `None` | `1 per 6 day` | `None` | `1 per 6 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 180 | `None` | `1 per 7 day` | `None` | `1 per 7 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 182 | `None` | `1 per 2 day` | `None` | `1 per 2 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 187 | `None` | `1 per 7 to 9 day` | `None` | `1 per 7 to 9 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 190 | `None` | `1 per 4 week` | `None` | `1 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 198 | `None` | `1 per 4 week` | `None` | `1 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 212 | `None` | `2 to 3 per month` | `None` | `2 to 3 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 218 | `None` | `1 per 3 week` | `None` | `1 per 3 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Input should be 'gpt', 'qwen' or 'deepseek' |
| 243 | `None` | `1 per 4 month` | `None` | `1 per 4 month` | `correct_to_correct` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 278 | `None` | `multiple per week` | `None` | `multiple per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 280 | `None` | `multiple per day` | `None` | `multiple per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 338 | `gpt` | `multiple per month` | `multiple per month` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile |
| 409 | `None` | `1 per month` | `None` | `1 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Input should be 'gpt', 'qwen' or 'deepseek' |
| 419 | `None` | `2 per year` | `None` | `2 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 446 | `None` | `15 per 3 month` | `None` | `15 per 3 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Input should be 'gpt', 'qwen' or 'deepseek' |
| 466 | `None` | `21 to 28 per month` | `None` | `21 to 28 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Input should be 'gpt', 'qwen' or 'deepseek' |
| 467 | `None` | `9 per month` | `None` | `9 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Input should be 'gpt', 'qwen' or 'deepseek' |
| 531 | `None` | `12 to 30 per 3 month` | `None` | `12 to 30 per 3 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 598 | `None` | `1 per 8 month` | `None` | `1 per 8 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
| 659 | `None` | `2 per 4 day` | `None` | `2 per 4 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_agent_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; action_render_error:schema_validation_error:Field required |
