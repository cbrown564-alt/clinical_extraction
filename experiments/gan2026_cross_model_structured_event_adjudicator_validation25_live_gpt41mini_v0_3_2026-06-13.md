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
- Prompt version: `gan2026_cross_model_structured_event_adjudicator_v0_2`
- Safety gate version: `gan2026_cross_model_peer_selection_gate_v0_1`
- JSONL artifact: `experiments\gan2026_cross_model_structured_event_adjudicator_validation25_live_gpt41mini_v0_3_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 25
- Model calls attempted: 25
- Call failures: 0
- Parse/schema/label failures: 0
- Action-render fallbacks: 0
- Exact evidence substrings: 25
- GPT V0 Purist: 25/25
- Raw declared Purist: 25/25
- Format-only declared Purist: 25/25
- Final Purist: 25/25
- Net Purist gain vs GPT V0: 0
- Changed-label precision vs GPT V0: None
- Selected agents: `{'gpt': 24, 'qwen': 1}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V10 cross-model structured-event adjudicator; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Selected | GPT | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | `gpt` | `4 per day` | `4 per day` | `4 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 40 | `gpt` | `4 per week` | `4 per week` | `4 per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 79 | `gpt` | `6 to 7 per year` | `6 to 7 per year` | `6 to 7 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 103 | `gpt` | `2 to 4 per year` | `2 to 4 per year` | `2 to 4 per year` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 128 | `gpt` | `17 per month` | `17 per month` | `17 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 156 | `gpt` | `1 per 6 day` | `1 per 6 day` | `1 per 6 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 180 | `gpt` | `1 per 7 day` | `1 per 7 day` | `1 per 7 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 182 | `gpt` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 187 | `gpt` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 190 | `gpt` | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 198 | `gpt` | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 212 | `qwen` | `2 to 3 per month` | `1 to 2 per month` | `2 to 3 per month` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 218 | `gpt` | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 243 | `gpt` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 278 | `gpt` | `multiple per week` | `multiple per week` | `multiple per week` | `correct_to_correct` | yes | decision_field_defaulted:attribution; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 280 | `gpt` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 338 | `gpt` | `multiple per month` | `multiple per month` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 409 | `gpt` | `1 per month` | `1 per month` | `1 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 419 | `gpt` | `2 per year` | `2 per year` | `2 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 446 | `gpt` | `15 per 3 month` | `15 per 3 month` | `15 per 3 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 466 | `gpt` | `21 to 28 per month` | `21 to 28 per month` | `21 to 28 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 467 | `gpt` | `9 per month` | `9 per month` | `9 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 531 | `gpt` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 598 | `gpt` | `1 per 8 month` | `1 per 8 month` | `1 per 8 month` | `correct_to_correct` | yes | decision_enum_shape_repaired:action; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
| 659 | `gpt` | `2 per 4 day` | `2 per 4 day` | `2 per 4 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:comparison_profile; decision_field_shape_repaired:rejected_agent_ids |
