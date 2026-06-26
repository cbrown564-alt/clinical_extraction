# Gan 2026 Event-Completion Reasoner

Date: 2026-06-13

This is a validation-development V7 event-completion artifact.
The model may create one completed event from exact raw-note evidence.

## Experiment Unit

- Work class: V7 event-completion reasoner over saved structured events.
- Rows: 25
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_event_completion_reasoner_v0_1`
- Structured-event source: `experiments\gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`
- JSONL artifact: `experiments\gan2026_event_completion_reasoner_validation25_live_gpt41mini_v0_1_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 2
- Model calls attempted: 25
- Call failures: 0
- Parse/schema/label failures: 23
- Completed-event actions: 0
- Exact evidence substrings: 2
- V0 Purist: 25/25
- Final Purist: 2/25
- Net Purist gain vs V0: 0
- Changed-label precision vs V0: None
- Completion profiles: `{}`

## Gate

- Status: `needs_contract_work`
- Interpretation: Do not promote; fix schema/evidence contract before hard-slice claims.

## Claim Boundary

validation-development V7 event-completion scaffold; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Action | Profiles | V0 | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | `None` | `None` | `4 per day` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 40 | `None` | `None` | `4 per week` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 79 | `None` | `None` | `6 to 7 per year` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 103 | `None` | `None` | `2 to 4 per year` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 128 | `None` | `None` | `17 per month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 156 | `keep_original_structured_event_final` | `[]` | `1 per 6 day` | `1 per 6 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 180 | `None` | `None` | `1 per 7 day` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 182 | `None` | `None` | `1 per 2 day` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 187 | `None` | `None` | `1 per 7 to 9 day` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 190 | `None` | `None` | `1 per 4 week` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 198 | `None` | `None` | `1 per 4 week` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 212 | `None` | `None` | `2 to 3 per month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 218 | `None` | `None` | `1 per 3 week` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 243 | `None` | `None` | `1 per 4 month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 278 | `None` | `None` | `multiple per week` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 280 | `None` | `None` | `multiple per day` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 338 | `None` | `None` | `multiple per month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 409 | `None` | `None` | `1 per month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 419 | `None` | `None` | `2 per year` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 446 | `None` | `None` | `15 per 3 month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 466 | `keep_original_structured_event_final` | `[]` | `21 to 28 per month` | `21 to 28 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 467 | `None` | `None` | `9 per month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 531 | `None` | `None` | `12 to 30 per 3 month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 598 | `None` | `None` | `1 per 8 month` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
| 659 | `None` | `None` | `2 per 4 day` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be a valid string |
