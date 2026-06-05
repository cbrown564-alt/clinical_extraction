# H10 Runtime Variance Audit

Decision: `h10_rejected_as_primary_gap_explanation`.

No live model calls were made. No locked-test row-level failures were inspected; locked-test evidence is limited to the saved aggregate surface map.

## Raw Output Identity

Matched source rows: 750.

| Field | Identical rows | Identity rate |
| --- | ---: | ---: |
| `raw_output` | 750 | 1.0000 |
| `llm_candidate_raw_output` | 750 | 1.0000 |
| `adjudicator_raw_output` | 750 | 1.0000 |

## Score-Layer Drift

| Score layer | Final-label changed | Purist changed | Live accuracy | Replay accuracy |
| --- | ---: | ---: | ---: | ---: |
| `adapter_only_sidecar_from_adjudicator_selection` | 114 | 58 | 0.8920 | 0.9293 |
| `deterministic_top_candidate` | 0 | 0 | 0.9293 | 0.9293 |
| `hybrid_adjudicator_raw` | 69 | 26 | 0.9107 | 0.9240 |
| `hybrid_adjudicator_with_adapters` | 114 | 58 | 0.8920 | 0.9293 |
| `llm_candidate_selector_raw` | 0 | 0 | 0.6646 | 0.6646 |
| `state_graph_projection` | 0 | 0 | 0.8733 | 0.8733 |

## Surface Gap Context

Paired candidates with saved validation/test gap: 3.
Maximum saved validation-minus-test gap: 0.1747.
Mean saved validation-minus-test gap: 0.1713.

## Interpretation

The paired validation live/replay surface has byte-identical saved raw outputs for every matched row, while saved validation/test surface-map gaps remain large. Runtime variance may affect downstream attribution when adapters or repair code change, but it is not the primary explanation for the observed generalisation gap.
