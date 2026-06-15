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
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_5`
- JSONL artifact: `experiments\gan2026_fresh_evidence_reasoner_unknown_policy_supervisor6_validation_live_gpt41_v0_5_2026-06-15.jsonl`

## Summary

- Prediction-bearing rows: 6
- Model calls attempted: 6
- Call failures: 0
- Parse/schema/label failures: 0
- Fresh-evidence replace actions: 5
- Evidence-gate fallbacks: 2
- Exact evidence substrings: 6
- V0 Purist: 4/6
- V0 Pragmatic: 4/6
- Raw model Purist: 2/6
- Raw model Pragmatic: 2/6
- Format-only Purist: 2/6
- Format-only Pragmatic: 2/6
- Final Purist: 2/6
- Final Pragmatic: 2/6
- Net Purist gain vs V0: -2
- Changed-label precision vs V0: 0.0
- Actions: `{'keep_original_structured_event_final': 1, 'replace_with_fresh_evidence_final': 5}`
- Profiles: `{'do not turn one-off since-last-review counts into rates unless the interval length or recurring cadence is explicit': 1, 'do not use no_reference when usable frequency evidence exists': 1, 'duration boundary: interval from 20/Dec to 23 March 2017 is about 3 months': 1, 'explicit numerator and denominator': 1, 'explicit seizure count and time window': 1, 'explicit seizure-free interval less than 2-3 months': 1, 'highest active semiology': 1, 'highest current clinically active burden': 1, 'last-event-only boundary': 2, 'last-event-only evidence is unknown': 1, 'no conflicting current/recent frequency evidence': 1, 'no current recurring rate': 1, 'no explicit duration for seizure-free label': 1, 'open-ended since-medication/diet boundary': 1, 'seizure_free boundary: explicit no-events-since evidence with defined interval': 1, 'unknown-frequency boundary': 1, 'unknown-frequency boundary: when either the number of seizures or the relevant time period is unclear, prefer unknown over an inferred rate': 1}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V12 fresh-evidence reasoner; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Action | Profiles | V0 | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 11272 | `replace_with_fresh_evidence_final` | `['seizure_free boundary: explicit no-events-since evidence with defined interval', 'duration boundary: interval from 20/Dec to 23 March 2017 is about 3 months', 'no conflicting current/recent frequency evidence']` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:replace_with_fresh_evidence_final |
| 14454 | `keep_original_structured_event_final` | `['last-event-only boundary', 'explicit seizure-free interval less than 2-3 months', 'no current recurring rate', 'no explicit duration for seizure-free label']` | `2 per 2 month` | `2 per 2 month` | `2 per 2 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:keep_original_structured_event_final |
| 14029 | `replace_with_fresh_evidence_final` | `['unknown-frequency boundary', 'open-ended since-medication/diet boundary']` | `multiple per month` | `unknown` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_action_rendered:fallback_original_structured_event_final |
| 13267 | `replace_with_fresh_evidence_final` | `['last-event-only evidence is unknown', 'unknown-frequency boundary: when either the number of seizures or the relevant time period is unclear, prefer unknown over an inferred rate', 'do not turn one-off since-last-review counts into rates unless the interval length or recurring cadence is explicit']` | `no seizure frequency reference` | `unknown` | `no seizure frequency reference` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_gate_fallback: unknown_replacement_not_selective; fresh_evidence_action_rendered:fallback_original_structured_event_final |
| 14137 | `replace_with_fresh_evidence_final` | `['explicit seizure count and time window', 'highest current clinically active burden', 'do not use no_reference when usable frequency evidence exists']` | `no seizure frequency reference` | `3 to 4 per 3 months` | `3 to 4 per 3 month` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; final_label_format_repaired: '3 to 4 per 3 months' -> '3 to 4 per 3 month'; fresh_evidence_action_rendered:replace_with_fresh_evidence_final |
| 11337 | `replace_with_fresh_evidence_final` | `['last-event-only boundary', 'explicit numerator and denominator', 'highest active semiology']` | `no seizure frequency reference` | `1 per 8 week` | `1 per 8 week` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; fresh_evidence_action_rendered:replace_with_fresh_evidence_final |
