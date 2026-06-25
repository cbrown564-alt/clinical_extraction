# ExECTv2 Investigations Rule Ablation

- Generated: `2026-06-25`
- JSON: `experiments/exectv2_investigations_rule_ablation_20260625.json`
- Selective diagnostic JSONL: `experiments/exectv2_v08_full200_currentcode_investigations_selective_adjudicator_v02_empty_pending_no_diagnostic_20260625.jsonl`
- Row inspection policy: `aggregate_only_no_full200_failure_ledgers`
- Model calls during this build: `False`
- Surface: current-code v08-shape full-200 Investigations
- Maximum acceptable selective review burden: `0.20`
- Claim boundary: Aggregate-only component ablation over saved current-code full-200 Investigations artifacts. Reports rule-family deltas, call burden, and action counts without full-200 row identifiers, note text, evidence snippets, rationales, or failure examples.

## Aggregate Table

| Variant | Rule family | Calls / letter | Selective burden | Changed rows | Actions | F1 | P | R | TP | FP | FN | Evidence valid |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Structured direct + result lens | `result_lens` | 0.0000 | 0.0000 | 0 | 0 | 0.8563 | 0.9241 | 0.7978 | 146 | 12 | 37 | 1.0000 |
| Structured direct + pending-test suppression | `pending_test_suppression` | 0.0000 | 0.0000 | 2 | 4 | 0.8665 | 0.9481 | 0.7978 | 146 | 8 | 37 | 1.0000 |
| Verifier only | `llm_verifier` | 1.0000 | 0.0000 | 62 | 0 | 0.8770 | 0.8586 | 0.8962 | 164 | 27 | 19 | 0.9791 |
| Verifier + deterministic pending-test suppression | `llm_verifier_plus_pending_test_suppression` | 1.0000 | 0.0000 | 13 | 16 | 0.9213 | 0.9480 | 0.8962 | 164 | 9 | 19 | 1.0000 |
| Selective verifier v01 broad ambiguity + pending-test suppression | `selective_llm_verifier_plus_pending_test_suppression` | 0.7350 | 0.7350 | 24 | 10 | 0.8812 | 0.9383 | 0.8306 | 152 | 10 | 31 | 1.0000 |
| Selective verifier v02 empty/pending/not-performed + pending-test suppression | `selective_llm_verifier_v02_plus_pending_test_suppression` | 0.5100 | 0.5100 | 10 | 9 | 0.8812 | 0.9383 | 0.8306 | 152 | 10 | 31 | 1.0000 |
| Selective verifier v03 empty-output-only + pending-test suppression | `selective_llm_verifier_v03_empty_output_only` | 0.4800 | 0.4800 | 7 | 8 | 0.8661 | 0.9048 | 0.8306 | 152 | 16 | 31 | 1.0000 |
| Selective verifier v04 capped direct-risk top 20% + pending-test suppression | `selective_llm_verifier_v04_capped_direct_risk_top20` | 0.2000 | 0.2000 | 5 | 2 | 0.8655 | 0.9308 | 0.8087 | 148 | 11 | 35 | 1.0000 |

## Dev140 Policy Selection

| Policy | Routed burden | Burden gate | F1 | P | R | TP | FP | FN |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v01 broad ambiguity | 0.8357 | fail | 0.9042 | 0.9440 | 0.8676 | 118 | 7 | 18 |
| v02 empty/pending/not-performed | 0.5643 | fail | 0.9084 | 0.9444 | 0.8750 | 119 | 7 | 17 |
| v03 empty-output-only | 0.2929 | fail | 0.7580 | 0.6685 | 0.8750 | 119 | 59 | 17 |
| v04 capped direct-risk top 20% | 0.2000 | pass | 0.7987 | 0.7346 | 0.8750 | 119 | 43 | 17 |

## Selective Review Burden Gate

- Ceiling: `0.2000` routed letters per letter
- Gate status: `passes_design_ceiling`
- Selected low-burden dev policy: `v04_capped_direct_risk_top20`
- Blocked over-ceiling dev policies: `v01_broad_ambiguous, v02_empty_pending_or_explicit_not_performed, v03_empty_output_only`
- Live-call boundary: this is a no-call dev140 scaffold; a live selective-adjudicator experiment still needs a fresh predeclaration freezing the selected policy, scorer, surface, and stop rule.

## Decision

- Selected next architecture: `selective_investigations_adjudicator_low_burden_dev_scaffold`
- Deterministic replacement promoted: `False`
- Selective burden acceptable: `False`
- Rationale: Deterministic replacement is promoted only if direct structured plus deterministic suppression is within 0.0100 F1 of the verifier plus suppression control. Otherwise any selective Investigations policy must first satisfy the <= 0.20 dev140 routed-letter burden ceiling before a live selective-adjudicator experiment is predeclared.

## Interpretation

The deterministic pending-test suppression layer is useful as a precision cleanup over the verifier, but the saved direct structured surface does not close the gap to the verifier-backed lane. The v02 selective policy was chosen on dev140 because it removes the broad unknown-result and multi-modality triggers while keeping empty-output, planned-test, and explicit-not-performed cases routed. On the aggregate-only full-200 replay it reduces verifier burden versus v01 without improving F1, but `0.5100` is far above the maximum acceptable review burden of `0.2000`, so it remains diagnostic. The v01-v03 selective policies remain over the selective-review burden ceiling, so continued cost work should use the v04 capped direct-risk scaffold, or another dev-only policy that is <=0.20 by construction, before any live selective-adjudicator experiment is predeclared.
