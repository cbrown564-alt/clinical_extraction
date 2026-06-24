# ExECTv2 Review-Routing Validation Audit

Date: 2026-06-24

Status: aggregate-only validation preflight and stop-rule readout. No promotion claim is made.

## Preflight

- Surface: rich-schema holistic assembly reliability scorecard
- Scorer: `headline_target family-cell correctness`
- Split: `full-200 aggregate-only validation requested`
- Code hash: `deac4ae+dirty`
- Row-inspection boundary: Aggregate metrics and artifact inventory only; no row identifiers, note text, gold labels, predictions, evidence spans, rationales, or selected failure examples are emitted.

## Frozen Candidate Operating Points

| Candidate | Dev status | Eligible cells | Reviewed | Burden | Error cells | Caught | Catch | False alarms | False alarms / caught error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High-recall predeclared trigger net | dev replay only; not a promoted policy | 1706 | 1605 | 0.9408 | 426 | 379 | 0.8897 | 1226 | 3.2348 |
| Balanced dev candidate | dev-tuned candidate; needs frozen validation | 1706 | 1291 | 0.7567 | 426 | 342 | 0.8028 | 949 | 2.7749 |

## Validation Artifact Inventory

| Artifact | Rows | Surface | Eligibility | Reason |
| --- | ---: | --- | --- | --- |
| `experiments/exectv2_audit_hybrid_full200_gpt41mini_20260611.jsonl` | 200 | historical Phase 7 SF-only hybrid audit | ineligible | SF-only audit artifact; not the rich-schema holistic assembly headline_target surface used by the reliability scorecard. |
| `experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl` | 200 | historical all-entity LLM-only audit | ineligible | LLM-only all-entity surface; lacks the final-consolidation rich-schema assembly surface and provenance features that define the dev review-routing candidate. |
| `experiments/exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611.jsonl` | 200 | historical SF-only LLM-only per-entity audit | ineligible | SF-only audit artifact; not the all-family rich-schema holistic assembly reliability surface. |
| `experiments/exectv2_audit_rules_full200_modelindependent_20260611.jsonl` | 200 | historical SF-only deterministic-rules audit | ineligible | Rules-only SF audit artifact; not the rich-schema holistic assembly scorecard surface. |

## Stop-Rule Outcome

- Status: `blocked_no_same_surface_full200_artifact`
- Validation run executed: `False`
- Promotion decision: `not_promoted`
- Reason: No full-200 artifact matches the frozen rich-schema holistic assembly reliability surface, so applying the dev routing candidate would blend surfaces.

## Promotion Gates

| Gate | Outcome | Note |
| --- | --- | --- |
| Review burden at least 0.15 absolute below high-recall burden | not_evaluable | No same-surface full-200 aggregate artifact is available. |
| Overall error catch at least 0.80 | not_evaluable | No same-surface full-200 aggregate artifact is available. |
| Per-family eligible/error/caught/missed/false-alarm metrics | not_evaluable | No same-surface full-200 aggregate artifact is available. |
| No family with at least ten error cells below 0.70 catch | not_evaluable | No same-surface full-200 aggregate artifact is available. |
| False alarms per caught error lower than high-recall policy | not_evaluable | No same-surface full-200 aggregate artifact is available. |

## Result

The lower-burden review-routing candidate is not promoted. The dev140 candidate remains useful but unvalidated because the available full-200 artifacts do not match the frozen rich-schema holistic assembly surface.

Next action: Freeze and generate a same-surface full-200 rich-schema holistic assembly artifact, then run the validation once with this report template before reading metrics.
