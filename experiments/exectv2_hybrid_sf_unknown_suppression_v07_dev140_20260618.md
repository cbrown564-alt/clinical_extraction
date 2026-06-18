# ExECTv2 SeizureFrequency Unknown-Suppression v0.7

- JSONL: `experiments\exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`
- Suppression version: `exectv2_hybrid_sf_unknown_suppression_v0.7`
- Source projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Split: `dev`
- Letters: 140
- Promoted by gate: `True`

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| unknown suppression | seizure_frequency | Drops existing unknown-state mentions when evidence is treatment-response scope or contextual/historical change scope. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `unknown_suppression.contextual_or_historical_change` | 5 |
| `unknown_suppression.drug_response_scope` | 5 |

## Gate

| Check | Value | Pass |
| --- | ---: | --- |
| headline_f1_delta | 0.0198 | True |
| unknown_fp_drop | 10 | True |
| unknown_fn_increase | 0 | True |
| active_rate_recall_delta | 0.0000 | True |
| seizure_free_recall_delta | 0.0000 | True |
| evidence_validity | 1.0000 | True |
| attributed_actions | 10 | True |

## Baseline Versus Suppressed

| Slice | Baseline F1 | Suppressed F1 | Baseline P | Suppressed P | Baseline R | Suppressed R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.763 | 0.782 | 0.722 | 0.759 | 0.807 | 0.807 | 151 | 48 | 36 |
| active-rate | 0.800 | 0.800 | 0.791 | 0.791 | 0.809 | 0.809 | 72 | 19 | 17 |
| seizure-free | 0.794 | 0.794 | 0.761 | 0.761 | 0.831 | 0.831 | 54 | 17 | 11 |
| unknown | 0.625 | 0.714 | 0.532 | 0.676 | 0.758 | 0.758 | 25 | 12 | 8 |

## Interpretation

The predeclared suppression layer passes the hard-slice gate on dev140: it improves headline SF F1, reduces unknown over-emission by named rules, and leaves active-rate and seizure-free recall unchanged. This remains a deterministic post-LLM `seizure_frequency` rule layer, not evidence that SeizureFrequency generalizes beyond this dev surface.
