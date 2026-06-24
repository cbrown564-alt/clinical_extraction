# ExECTv2 Review-Routing Validation Audit

Date: 2026-06-24

Status: aggregate-only validation preflight and stop-rule readout. No promotion claim is made.

## Preflight

- Surface: rich-schema holistic assembly reliability scorecard
- Scorer: `headline_target family-cell correctness`
- Split: `full-200 aggregate-only validation requested`
- Code hash: `1a3e1cd+dirty`
- Row-inspection boundary: Aggregate metrics and artifact inventory only; no row identifiers, note text, gold labels, predictions, evidence spans, rationales, or selected failure examples are emitted.

## Frozen Candidate Operating Points

| Candidate | Dev status | Eligible cells | Reviewed | Burden | Error cells | Caught | Catch | False alarms | False alarms / caught error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High-recall predeclared trigger net | dev replay only; not a promoted policy | 1706 | 1605 | 0.9408 | 426 | 379 | 0.8897 | 1226 | 3.2348 |
| Balanced dev candidate | dev-tuned candidate; needs frozen validation | 1706 | 1291 | 0.7567 | 426 | 342 | 0.8028 | 949 | 2.7749 |

## Validation Artifact Inventory

| Artifact | Rows | Surface | Eligibility | Reason |
| --- | ---: | --- | --- | --- |
| `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl` | 200 | current-code v08-shape rich-schema holistic assembly | eligible | Accepted for a one-shot aggregate validation of the current-code v08-shaped rich-schema holistic assembly surface. This is not byte-identical archived dev140 prompt/module replay, so promotion claims remain limited to the current-code validation surface. |
| `experiments/exectv2_audit_hybrid_full200_gpt41mini_20260611.jsonl` | 200 | historical Phase 7 SF-only hybrid audit | ineligible | SF-only audit artifact; not the rich-schema holistic assembly headline_target surface used by the reliability scorecard. |
| `experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl` | 200 | historical all-entity LLM-only audit | ineligible | LLM-only all-entity surface; lacks the final-consolidation rich-schema assembly surface and provenance features that define the dev review-routing candidate. |
| `experiments/exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611.jsonl` | 200 | historical SF-only LLM-only per-entity audit | ineligible | SF-only audit artifact; not the all-family rich-schema holistic assembly reliability surface. |
| `experiments/exectv2_audit_rules_full200_modelindependent_20260611.jsonl` | 200 | historical SF-only deterministic-rules audit | ineligible | Rules-only SF audit artifact; not the rich-schema holistic assembly scorecard surface. |

## Aggregate Validation Readout

- Artifact: `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl`
- Rows: 200
- Eligible family cells: 619

| Operating point | Reviewed | Burden | Error cells | Caught | Catch | False alarms | False alarms / caught error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High-recall predeclared trigger net | 597 | 0.9645 | 218 | 196 | 0.8991 | 401 | 2.0459 |
| Balanced dev candidate | 598 | 0.9661 | 218 | 197 | 0.9037 | 401 | 2.0355 |

### Per-Family Validation Metrics

| Operating point | Family | Eligible | Errors | Reviewed | Caught | Missed | False alarms | Burden | Catch |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High-recall predeclared trigger net | Diagnosis | 189 | 83 | 187 | 81 | 2 | 106 | 0.9894 | 0.9759 |
| High-recall predeclared trigger net | Investigations | 110 | 21 | 108 | 19 | 2 | 89 | 0.9818 | 0.9048 |
| High-recall predeclared trigger net | Prescription | 167 | 44 | 155 | 32 | 12 | 123 | 0.9281 | 0.7273 |
| High-recall predeclared trigger net | SeizureFrequency | 153 | 70 | 147 | 64 | 6 | 83 | 0.9608 | 0.9143 |
| Balanced dev candidate | Diagnosis | 189 | 83 | 188 | 82 | 1 | 106 | 0.9947 | 0.9880 |
| Balanced dev candidate | Investigations | 110 | 21 | 108 | 19 | 2 | 89 | 0.9818 | 0.9048 |
| Balanced dev candidate | Prescription | 167 | 44 | 155 | 32 | 12 | 123 | 0.9281 | 0.7273 |
| Balanced dev candidate | SeizureFrequency | 153 | 70 | 147 | 64 | 6 | 83 | 0.9608 | 0.9143 |

## Stop-Rule Outcome

- Status: `completed_current_code_surface_validation`
- Validation run executed: `True`
- Promotion decision: `not_promoted`
- Reason: The current-code v08-shaped full-200 artifact was accepted as an aggregate-only validation surface, but the lower-burden dev candidate did not preserve a lower review burden on validation.

## Promotion Gates

| Gate | Outcome | Note |
| --- | --- | --- |
| Review burden at least 0.15 absolute below high-recall burden | fail | Validation burden delta is -0.0016. |
| Overall error catch at least 0.80 | pass | Validation catch is 0.9037. |
| Per-family eligible/error/caught/missed/false-alarm metrics | pass | Per-family aggregate metrics are reported without row-level details. |
| No family with at least ten error cells below 0.70 catch | pass | Balanced candidate family catch floor evaluated on aggregate counts. |
| False alarms per caught error lower than high-recall policy | pass | Validation high-recall cost 2.0459; balanced cost 2.0355. |

## Result

The current-code v08-shaped full-200 artifact was accepted for this aggregate-only validation readout, but the lower-burden review-routing candidate is not promoted. It preserved high catch, but review burden rose to the high-recall policy level instead of meeting the predeclared lower-burden gate.

Next action: Do not promote the lower-burden review-routing candidate. Move review-routing work back to dev140 risk-feature redesign or a fresh predeclared calibration/routing model before another validation attempt.
