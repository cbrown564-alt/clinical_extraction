# Gan 2026 Fresh-Evidence Reasoner

Date: 2026-06-13

This is a validation-development V12 fresh-evidence reasoning artifact.
The model may replace the GPT structured-event final only from exact raw-note evidence.

## Experiment Unit

- Work class: V12 fresh-evidence reasoner over saved structured events.
- Rows: 25
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1`
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_2`
- JSONL artifact: `experiments\gan2026_fresh_evidence_reasoner_validation25_live_gpt41_v0_2_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 25
- Model calls attempted: 25
- Call failures: 0
- Parse/schema/label failures: 0
- Fresh-evidence replace actions: 2
- Evidence-gate fallbacks: 0
- Exact evidence substrings: 24
- V0 Purist: 25/25
- Raw model Purist: 25/25
- Final Purist: 25/25
- Net Purist gain vs V0: 0
- Changed-label precision vs V0: 0.0
- Actions: `{'keep_original_structured_event_final': 23, 'replace_with_fresh_evidence_final': 2}`
- Profiles: `{'cluster burden': 1, 'current frequency': 1, 'current frequency explicitly stated': 1, 'current/recent frequency': 22, 'denominator/window': 15, 'explicit current frequency': 1, 'explicit denominator/window': 1, 'highest active semiology': 7, 'no ambiguity in denominator/window': 1, 'no cluster cadence for current period': 1, 'no evidence for seizure-free': 1, 'no evidence for unknown or no_reference': 1, 'no seizure-free or unknown conflict': 1, 'no seizure-free statement': 1, 'window of five months specified': 1}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V12 fresh-evidence reasoner; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Action | Profiles | V0 | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | `keep_original_structured_event_final` | `['current/recent frequency', 'highest active semiology']` | `4 per day` | `4 per day` | `4 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 40 | `keep_original_structured_event_final` | `['current/recent frequency', 'highest active semiology']` | `4 per week` | `4 per week` | `4 per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 79 | `keep_original_structured_event_final` | `['current/recent frequency', 'highest active semiology']` | `6 to 7 per year` | `6 to 7 per year` | `6 to 7 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 103 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `2 to 4 per year` | `2 to 4 per year` | `2 to 4 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 128 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `17 per month` | `17 per month` | `17 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 156 | `keep_original_structured_event_final` | `['current frequency', 'explicit denominator/window', 'no seizure-free or unknown conflict']` | `1 per 6 day` | `1 per 6 day` | `1 per 6 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 180 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `1 per 7 day` | `1 per 7 day` | `1 per 7 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 182 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 187 | `keep_original_structured_event_final` | `['current/recent frequency', 'cluster burden', 'highest active semiology']` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 190 | `keep_original_structured_event_final` | `['current/recent frequency', 'highest active semiology']` | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 198 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 212 | `replace_with_fresh_evidence_final` | `['current/recent frequency', 'denominator/window']` | `2 to 3 per month` | `1 to 1.3 per month` | `1 to 1.3 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:replace_with_fresh_evidence_final |
| 218 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 243 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `correct_to_correct` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 278 | `keep_original_structured_event_final` | `['current/recent frequency', 'highest active semiology']` | `multiple per week` | `multiple per week` | `multiple per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 280 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 338 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `multiple per month` | `multiple per month` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 409 | `keep_original_structured_event_final` | `['current frequency explicitly stated', 'window of five months specified', 'no evidence for seizure-free', 'no cluster cadence for current period']` | `1 per month` | `1 per month` | `1 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 419 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `2 per year` | `2 per year` | `2 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 446 | `replace_with_fresh_evidence_final` | `['current/recent frequency', 'denominator/window']` | `15 per 3 month` | `2 per week` | `2 per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:replace_with_fresh_evidence_final |
| 466 | `keep_original_structured_event_final` | `['current/recent frequency', 'highest active semiology']` | `21 to 28 per month` | `21 to 28 per month` | `21 to 28 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 467 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `9 per month` | `9 per month` | `9 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 531 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 598 | `keep_original_structured_event_final` | `['current/recent frequency', 'denominator/window']` | `1 per 8 month` | `1 per 8 month` | `1 per 8 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 659 | `keep_original_structured_event_final` | `['explicit current frequency', 'no seizure-free statement', 'no ambiguity in denominator/window', 'no evidence for unknown or no_reference']` | `2 per 4 day` | `2 per 4 day` | `2 per 4 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
