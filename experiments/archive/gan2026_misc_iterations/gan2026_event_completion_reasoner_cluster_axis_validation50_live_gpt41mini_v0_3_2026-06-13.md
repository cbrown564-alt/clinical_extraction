# Gan 2026 Event-Completion Reasoner

Date: 2026-06-13

This is a validation-development V7 event-completion artifact.
The model may create one completed event from exact raw-note evidence.

## Experiment Unit

- Work class: V7 event-completion reasoner over saved structured events.
- Rows: 50
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_event_completion_reasoner_v0_3`
- Structured-event source: `experiments\gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`
- JSONL artifact: `experiments\gan2026_event_completion_reasoner_cluster_axis_validation50_live_gpt41mini_v0_3_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 50
- Model calls attempted: 50
- Call failures: 0
- Parse/schema/label failures: 0
- Completed-event actions: 0
- Exact evidence substrings: 46
- V0 Purist: 7/50
- Final Purist: 7/50
- Net Purist gain vs V0: 0
- Changed-label precision vs V0: None
- Completion profiles: `{'event_completion:cluster_axis': 13, 'event_completion:seizure_free': 1}`

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development V7 event-completion scaffold; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Action | Profiles | V0 | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10237 | `keep_original_structured_event_final` | `[]` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 9250 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `unknown` | `unknown` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 13051 | `keep_original_structured_event_final` | `[]` | `1 per 8 month` | `1 per 8 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 17135 | `keep_original_structured_event_final` | `[]` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 5837 | `keep_original_structured_event_final` | `[]` | `1 per 3 week` | `1 per 3 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 7167 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10097 | `keep_original_structured_event_final` | `[]` | `3 per month` | `3 per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10245 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `2 per 6 month` | `2 per 6 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10630 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10967 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 17110 | `keep_original_structured_event_final` | `[]` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 4839 | `keep_original_structured_event_final` | `['event_completion:seizure_free']` | `2025 per 4 month` | `2025 per 4 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6571 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `1 per 4 month` | `1 per 4 month` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6987 | `keep_original_structured_event_final` | `[]` | `10 to 15 per 1 year` | `10 to 15 per 1 year` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; final_label_format_repaired: '10 to 15 per 1 year' -> '10 to 15 per year' |
| 9943 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 13209 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 16714 | `keep_original_structured_event_final` | `[]` | `5 per 6 month` | `5 per 6 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6077 | `keep_original_structured_event_final` | `[]` | `no seizure frequency reference` | `no seizure frequency reference` | `correct_to_correct` | yes | decision_field_shape_repaired:clinical_rationale_alias; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 5763 | `keep_original_structured_event_final` | `[]` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6368 | `keep_original_structured_event_final` | `[]` | `3 per 6 week` | `3 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 7615 | `keep_original_structured_event_final` | `[]` | `2 per 10 month` | `2 per 10 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 13267 | `keep_original_structured_event_final` | `[]` | `no seizure frequency reference` | `no seizure frequency reference` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 15470 | `keep_original_structured_event_final` | `[]` | `multiple per day` | `multiple per day` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 16839 | `keep_original_structured_event_final` | `[]` | `19 per 2 month` | `19 per 2 month` | `wrong_to_wrong` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 2459 | `keep_original_structured_event_final` | `[]` | `5 per 5 month` | `5 per 5 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 2992 | `keep_original_structured_event_final` | `[]` | `1 per 8 month` | `1 per 8 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 6321 | `keep_original_structured_event_final` | `[]` | `2 per 3 month` | `2 per 3 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 9937 | `keep_original_structured_event_final` | `[]` | `multiple per month` | `multiple per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10434 | `keep_original_structured_event_final` | `[]` | `multiple per week` | `multiple per week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10673 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12366 | `keep_original_structured_event_final` | `[]` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:clinical_rationale_alias; decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12383 | `keep_original_structured_event_final` | `[]` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12412 | `keep_original_structured_event_final` | `[]` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 15108 | `keep_original_structured_event_final` | `[]` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 16938 | `keep_original_structured_event_final` | `[]` | `1 per 2 month` | `1 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 16947 | `keep_original_structured_event_final` | `[]` | `1 per 2 month` | `1 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10829 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10965 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12502 | `keep_original_structured_event_final` | `[]` | `4 per day` | `4 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 7401 | `keep_original_structured_event_final` | `[]` | `unknown` | `unknown` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 15431 | `keep_original_structured_event_final` | `[]` | `5 per 4 month` | `5 per 4 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 1880 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `7 per 2 month` | `7 per 2 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10183 | `keep_original_structured_event_final` | `[]` | `2 per 6 week` | `2 per 6 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10264 | `keep_original_structured_event_final` | `[]` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10371 | `keep_original_structured_event_final` | `[]` | `seizure free for multiple year` | `seizure free for multiple year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 10542 | `keep_original_structured_event_final` | `[]` | `unknown` | `unknown` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12236 | `keep_original_structured_event_final` | `[]` | `multiple per day` | `multiple per day` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 12665 | `keep_original_structured_event_final` | `[]` | `1 to 2 per month` | `1 to 2 per month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 13058 | `keep_original_structured_event_final` | `['event_completion:cluster_axis']` | `1 per 7 month` | `1 per 7 month` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 13290 | `keep_original_structured_event_final` | `[]` | `2 per 2 week` | `2 per 2 week` | `wrong_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
