# Gan 2026 LLM Event Reasoner

Date: 2026-06-13

This is a validation-development Stage 1 structured-event reasoning artifact.
The model sees saved LLM structured events, not deterministic final-label candidates.

## Experiment Unit

- Work class: V1 single LLM event reasoner scaffold.
- Rows: 25
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_llm_event_reasoner_v1`
- Structured-event source: `experiments\gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`
- JSONL artifact: `experiments\gan2026_llm_event_reasoner_validation25_live_gpt41mini_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 0
- Model calls attempted: 25
- Call failures: 0
- Parse/schema/label failures: 25
- Exact evidence substrings: 0
- V0 Purist: 25/25
- Raw model Purist: 0/25
- Format-only Purist: 0/25
- Final Purist: 0/25
- Net Purist gain vs V0: 0
- Changed-label precision vs V0: None

## Gate

- Status: `prompt_only_no_prediction`
- Interpretation: Prompt-only scaffold generated without model calls; run live validation25 before applying contract promotion gates.

## Claim Boundary

validation-development Stage 1 scaffold; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | V0 | Raw | Format-only | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | `4 per day` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 40 | `4 per week` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 79 | `6 to 7 per year` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 103 | `2 to 4 per year` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 128 | `17 per month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 156 | `1 per 6 day` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 180 | `1 per 7 day` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 182 | `1 per 2 day` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 187 | `1 per 7 to 9 day` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 190 | `1 per 4 week` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 198 | `1 per 4 week` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'llm_selected_tool_rendered', 'llm_selected_format_repaired' or 'llm_original_structured_event_kept' |
| 212 | `2 to 3 per month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'llm_selected_tool_rendered', 'llm_selected_format_repaired' or 'llm_original_structured_event_kept' |
| 218 | `1 per 3 week` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 243 | `1 per 4 month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 278 | `multiple per week` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 280 | `multiple per day` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 338 | `multiple per month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 409 | `1 per month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 419 | `2 per year` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 446 | `15 per 3 month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 466 | `21 to 28 per month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'llm_selected_tool_rendered', 'llm_selected_format_repaired' or 'llm_original_structured_event_kept' |
| 467 | `9 per month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 531 | `12 to 30 per 3 month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 598 | `1 per 8 month` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 659 | `2 per 4 day` | `None` | `None` | `None` | `unscored` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; schema_validation_error: Input should be 'low', 'medium' or 'high' |
