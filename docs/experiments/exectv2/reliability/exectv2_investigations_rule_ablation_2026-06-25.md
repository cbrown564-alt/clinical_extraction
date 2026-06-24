# ExECTv2 Investigations Rule Ablation

- Generated: `2026-06-25`
- JSON: `experiments/exectv2_investigations_rule_ablation_20260625.json`
- Selective diagnostic JSONL: `experiments/exectv2_v08_full200_currentcode_investigations_selective_adjudicator_diagnostic_20260625.jsonl`
- Row inspection policy: `aggregate_only_no_full200_failure_ledgers`
- Model calls during this build: `False`
- Surface: current-code v08-shape full-200 Investigations
- Claim boundary: Aggregate-only component ablation over saved current-code full-200 Investigations artifacts. Reports rule-family deltas, call burden, and action counts without full-200 row identifiers, note text, evidence snippets, rationales, or failure examples.

## Aggregate Table

| Variant | Rule family | Calls / letter | Selective burden | Changed rows | Actions | F1 | P | R | TP | FP | FN | Evidence valid |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Structured direct + result lens | `result_lens` | 0.0000 | 0.0000 | 0 | 0 | 0.8563 | 0.9241 | 0.7978 | 146 | 12 | 37 | 1.0000 |
| Structured direct + pending-test suppression | `pending_test_suppression` | 0.0000 | 0.0000 | 2 | 4 | 0.8665 | 0.9481 | 0.7978 | 146 | 8 | 37 | 1.0000 |
| Verifier only | `llm_verifier` | 1.0000 | 0.0000 | 62 | 0 | 0.8770 | 0.8586 | 0.8962 | 164 | 27 | 19 | 0.9791 |
| Verifier + deterministic pending-test suppression | `llm_verifier_plus_pending_test_suppression` | 1.0000 | 0.0000 | 13 | 16 | 0.9213 | 0.9480 | 0.8962 | 164 | 9 | 19 | 1.0000 |
| Selective verifier for ambiguous direct rows + pending-test suppression | `selective_llm_verifier_plus_pending_test_suppression` | 0.7350 | 0.7350 | 24 | 10 | 0.8812 | 0.9383 | 0.8306 | 152 | 10 | 31 | 1.0000 |

## Decision

- Selected next architecture: `selective_investigations_adjudicator_diagnostic`
- Deterministic replacement promoted: `False`
- Rationale: Deterministic replacement is promoted only if direct structured plus deterministic suppression is within 0.0100 F1 of the verifier plus suppression control. Otherwise the next diagnostic is selective Investigations adjudication.

## Interpretation

The deterministic pending-test suppression layer is useful as a precision cleanup over the verifier, but the saved direct structured surface does not close the gap to the verifier-backed lane. The next architecture should therefore test selective Investigations adjudication rather than promote a deterministic-only replacement.
