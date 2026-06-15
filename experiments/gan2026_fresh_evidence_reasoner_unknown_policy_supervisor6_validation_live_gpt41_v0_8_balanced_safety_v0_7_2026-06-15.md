# Gan 2026 Fresh-Evidence Reasoner

Date: 2026-06-15

This is a validation-development V12 fresh-evidence reasoning artifact.
The model may replace the GPT structured-event final only from exact raw-note evidence.

## Experiment Unit

- Work class: V12 fresh-evidence reasoner over saved structured events.
- Rows: 6
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1`
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_8_balanced_unknown_policy`
- JSONL artifact: `experiments\gan2026_fresh_evidence_reasoner_unknown_policy_supervisor6_validation_live_gpt41_v0_8_balanced_safety_v0_7_2026-06-15.jsonl`

## Summary

- Prediction-bearing rows: 6
- Model calls attempted: 6
- Call failures: 0
- Parse/schema/label failures: 0
- Fresh-evidence replace actions: 5
- Evidence-gate fallbacks: 3
- Exact evidence substrings: 6
- V0 Purist: 4/6
- V0 Pragmatic: 4/6
- Raw model Purist: 2/6
- Raw model Pragmatic: 2/6
- Format-only Purist: 2/6
- Format-only Pragmatic: 2/6
- Final Purist: 3/6
- Final Pragmatic: 3/6
- Net Purist gain vs V0: -1
- Changed-label precision vs V0: 0.0
- Actions: `{'keep_original_structured_event_final': 1, 'replace_with_fresh_evidence_final': 5}`
- Profiles: `{'cluster burden': 2, 'denominator/window': 1, 'do not upconvert short seizure-free intervals to longer durations': 1, "duration boundary: only ~3 months since last event, not 'multiple year'": 1, 'explicit count and time window': 1, 'explicit count and window': 1, 'explicit no seizures since': 1, 'frequency label supported by raw evidence': 1, 'highest active semiology': 1, 'highest current clinically active burden': 1, 'last-event-only boundary': 1, 'last_event_only': 1, 'recent last event only': 1, 'seizure_free boundary': 1, "seizure_free boundary: last seizure date plus explicit 'no seizures since' statement": 1, 'unknown-frequency boundary': 3}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V12 fresh-evidence reasoner; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Action | Profiles | V0 | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 11272 | `replace_with_fresh_evidence_final` | `["seizure_free boundary: last seizure date plus explicit 'no seizures since' statement", "duration boundary: only ~3 months since last event, not 'multiple year'", 'do not upconvert short seizure-free intervals to longer durations']` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:replace_with_fresh_evidence_final |
| 14454 | `keep_original_structured_event_final` | `['seizure_free boundary', 'recent last event only', 'explicit no seizures since']` | `2 per 2 month` | `2 per 2 month` | `2 per 2 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 14029 | `replace_with_fresh_evidence_final` | `['unknown-frequency boundary', 'cluster burden', 'denominator/window']` | `multiple per month` | `unknown` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_action_rendered:fallback_original_structured_event_final |
| 13267 | `replace_with_fresh_evidence_final` | `['unknown-frequency boundary', 'last-event-only boundary', 'cluster burden', 'highest active semiology']` | `no seizure frequency reference` | `unknown` | `no seizure frequency reference` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_action_rendered:fallback_original_structured_event_final |
| 14137 | `replace_with_fresh_evidence_final` | `['explicit count and time window', 'highest current clinically active burden', 'frequency label supported by raw evidence']` | `no seizure frequency reference` | `3 to 4 per month` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: open_ended_treatment_start_denominator; fresh_evidence_gate_fallback: open_ended_treatment_start_denominator; fresh_evidence_action_rendered:fallback_original_structured_event_final |
| 11337 | `replace_with_fresh_evidence_final` | `['last_event_only', 'explicit count and window', 'unknown-frequency boundary']` | `no seizure frequency reference` | `1 per 8 week` | `1 per 8 week` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:replace_with_fresh_evidence_final |
