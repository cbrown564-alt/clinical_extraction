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
- Prompt version: `gan2026_llm_event_reasoner_v1_1`
- Structured-event source: `experiments\gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`
- JSONL artifact: `experiments\gan2026_llm_event_reasoner_validation25_live_gpt41mini_v1_1_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 25
- Model calls attempted: 25
- Call failures: 0
- Parse/schema/label failures: 1
- Exact evidence substrings: 24
- V0 Purist: 25/25
- Raw model Purist: 24/25
- Format-only Purist: 24/25
- Final Purist: 24/25
- Net Purist gain vs V0: -1
- Changed-label precision vs V0: 0.0

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

validation-development Stage 1 scaffold; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | V0 | Raw | Format-only | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | `4 per day` | `4 per day` | `4 per day` | `4 per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 40 | `4 per week` | `4 per week` | `4 per week` | `4 per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 79 | `6 to 7 per year` | `6 to 7 per year` | `6 to 7 per year` | `6 to 7 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 103 | `2 to 4 per year` | `2 to 4 per year` | `2 to 4 per year` | `2 to 4 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 128 | `17 per month` | `17 per month` | `17 per month` | `17 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 156 | `1 per 6 day` | `1 per 6 day` | `1 per 6 day` | `1 per 6 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 180 | `1 per 7 day` | `1 per 7 day` | `1 per 7 day` | `1 per 7 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 182 | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 187 | `1 per 7 to 9 day` | `2 nocturnal generalised tonic–clonic seizures since last review` | `2 nocturnal generalised tonic–clonic since last review` | `2 nocturnal generalised tonic–clonic since last review` | `correct_to_wrong` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile; final_label_format_repaired: '2 nocturnal generalised tonic–clonic seizures since last review' -> '2 nocturnal generalised tonic–clonic since last review'; unscorable_final_label: Unparsable label (raw: '2 nocturnal generalised tonic–clonic since last review' / normalized: '2 nocturnal generalised tonic–clonic since last review') |
| 190 | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 198 | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 212 | `2 to 3 per month` | `2 to 3 per month` | `2 to 3 per month` | `2 to 3 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 218 | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 243 | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `correct_to_correct` | no | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 278 | `multiple per week` | `multiple per week` | `multiple per week` | `multiple per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 280 | `multiple per day` | `multiple per day` | `multiple per day` | `multiple per day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 338 | `multiple per month` | `multiple per month` | `multiple per month` | `multiple per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 409 | `1 per month` | `1 per month` | `1 per month` | `1 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 419 | `2 per year` | `2 per year` | `2 per year` | `2 per year` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 446 | `15 per 3 month` | `2 per week` | `2 per week` | `2 per week` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 466 | `21 to 28 per month` | `21 to 28 per month` | `21 to 28 per month` | `21 to 28 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 467 | `9 per month` | `9 per month` | `9 per month` | `9 per month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 531 | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 598 | `1 per 8 month` | `1 per 8 month` | `1 per 8 month` | `1 per 8 month` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
| 659 | `2 per 4 day` | `2 per 4 day` | `2 per 4 day` | `2 per 4 day` | `correct_to_correct` | yes | decision_field_shape_repaired:selected_event_ids; decision_field_shape_repaired:rejected_event_ids; decision_field_shape_repaired:evidence; decision_field_shape_repaired:boundary_profile |
