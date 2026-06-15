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
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_6`
- JSONL artifact: `experiments\gan2026_fresh_evidence_reasoner_unknown_policy_supervisor6_validation_live_gpt41_v0_6_2026-06-15.jsonl`

## Summary

- Prediction-bearing rows: 6
- Model calls attempted: 6
- Call failures: 0
- Parse/schema/label failures: 0
- Fresh-evidence replace actions: 5
- Evidence-gate fallbacks: 4
- Exact evidence substrings: 6
- V0 Purist: 4/6
- V0 Pragmatic: 4/6
- Raw model Purist: 4/6
- Raw model Pragmatic: 4/6
- Format-only Purist: 4/6
- Format-only Pragmatic: 4/6
- Final Purist: 3/6
- Final Pragmatic: 3/6
- Net Purist gain vs V0: -1
- Changed-label precision vs V0: 0.0
- Actions: `{'keep_original_structured_event_final': 1, 'replace_with_fresh_evidence_final': 5}`
- Profiles: `{'Do not label seizure_free when the support is only a last seizure date plus no seizures since; choose unknown unless the note independently states a seizure-free/no-seizures duration as the current frequency state': 1, 'cluster burden': 1, 'explicit event count but unclear denominator': 1, 'explicit seizure count and time window': 1, 'frequency label supported by count and interval': 1, 'highest active semiology': 1, 'highest current clinically active burden': 1, 'last-event-only boundary': 2, 'last-event-only evidence': 1, 'last-event-only evidence is unknown: a most-recent seizure date does not prove one seizure in a defined period, and no-seizures-since-last-event does not by itself create a Gan frequency or seizure-free label': 1, 'no explicit denominator': 1, 'open-ended since-medication/diet start': 1, 'short seizure-free interval': 1, 'unknown-frequency boundary': 4}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V12 fresh-evidence reasoner; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Action | Profiles | V0 | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 11272 | `replace_with_fresh_evidence_final` | `['last-event-only evidence is unknown: a most-recent seizure date does not prove one seizure in a defined period, and no-seizures-since-last-event does not by itself create a Gan frequency or seizure-free label', 'Do not label seizure_free when the support is only a last seizure date plus no seizures since; choose unknown unless the note independently states a seizure-free/no-seizures duration as the current frequency state']` | `seizure free for multiple year` | `unknown` | `seizure free for multiple year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: original_seizure_free_to_unknown_or_no_reference; fresh_evidence_gate_fallback: original_seizure_free_to_unknown_or_no_reference; fresh_evidence_action_rendered:fallback_original_structured_event_final |
| 14454 | `keep_original_structured_event_final` | `['last-event-only boundary', 'unknown-frequency boundary', 'short seizure-free interval']` | `2 per 2 month` | `2 per 2 month` | `2 per 2 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 14029 | `replace_with_fresh_evidence_final` | `['unknown-frequency boundary', 'open-ended since-medication/diet start', 'no explicit denominator']` | `multiple per month` | `unknown` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_action_rendered:fallback_original_structured_event_final |
| 13267 | `replace_with_fresh_evidence_final` | `['last-event-only evidence', 'unknown-frequency boundary', 'cluster burden', 'highest active semiology']` | `no seizure frequency reference` | `unknown` | `no seizure frequency reference` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_action_rendered:fallback_original_structured_event_final |
| 14137 | `replace_with_fresh_evidence_final` | `['explicit seizure count and time window', 'highest current clinically active burden', 'frequency label supported by count and interval']` | `no seizure frequency reference` | `3 to 4 per 3 months` | `3 to 4 per 3 month` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; final_label_format_repaired: '3 to 4 per 3 months' -> '3 to 4 per 3 month'; fresh_evidence_action_rendered:replace_with_fresh_evidence_final |
| 11337 | `replace_with_fresh_evidence_final` | `['last-event-only boundary', 'unknown-frequency boundary', 'explicit event count but unclear denominator']` | `no seizure frequency reference` | `unknown` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_action_rendered:fallback_original_structured_event_final |
