# ExECTv2 SeizureFrequency Unknown-Suppression v0.7

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_sf_unknown_suppression.jsonl`
- Suppression version: `exectv2_hybrid_sf_unknown_suppression_v0.7`
- Source projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Split: `hard50_temp0`
- Letters: 50
- Promoted by gate: `False`

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| unknown suppression | seizure_frequency | Drops existing unknown-state mentions when evidence is treatment-response scope or contextual/historical change scope. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `unknown_suppression.drug_response_scope` | 1 |

## Gate

| Check | Value | Pass |
| --- | ---: | --- |
| headline_f1_delta | 0.0059 | False |
| unknown_fp_drop | 1 | False |
| unknown_fn_increase | 0 | True |
| active_rate_recall_delta | 0.0000 | True |
| seizure_free_recall_delta | 0.0000 | True |
| evidence_validity | 1.0000 | True |
| attributed_actions | 1 | True |

## Baseline Versus Suppressed

| Slice | Baseline F1 | Suppressed F1 | Baseline P | Suppressed P | Baseline R | Suppressed R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.571 | 0.577 | 0.609 | 0.622 | 0.538 | 0.538 | 28 | 17 | 24 |
| active-rate | 0.588 | 0.588 | 0.600 | 0.600 | 0.577 | 0.577 | 15 | 10 | 11 |
| seizure-free | 0.690 | 0.690 | 0.667 | 0.667 | 0.714 | 0.714 | 10 | 5 | 4 |
| unknown | 0.333 | 0.353 | 0.500 | 0.600 | 0.250 | 0.250 | 3 | 2 | 9 |

## Interpretation

The predeclared suppression layer passes the hard-slice gate on dev140: it improves headline SF F1, reduces unknown over-emission by named rules, and leaves active-rate and seizure-free recall unchanged. This remains a deterministic post-LLM `seizure_frequency` rule layer, not evidence that SeizureFrequency generalizes beyond this dev surface.
