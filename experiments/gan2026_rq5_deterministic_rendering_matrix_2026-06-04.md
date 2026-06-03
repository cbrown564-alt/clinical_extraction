# Gan 2026 RQ5 Fixed Selected-State Rendering Matrix

Validation-development artifact for deterministic compilation/rendering over fixed selected states and explicit ACD projection-policy decisions. No model calls or locked-holdout rows are used.

- JSONL artifact: `experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.jsonl`
- Matrix rows: 2295
- Source rows represented: 751

## Variant Summary

| Variant | Rows | Parse valid | Exact label | Purist correct | Pragmatic correct | Semantic drift | Evidence retained | Source ids retained |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| acd_aware | 9 | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 1.000 | 1.000 |
| acd_off_ablation | 9 | 1.000 | 0.333 | 0.556 | 0.556 | 6 | 1.000 | 1.000 |
| current_production | 759 | 1.000 | 0.649 | 0.875 | 0.887 | 0 | 1.000 | 1.000 |
| evidence_preserving | 759 | 1.000 | 0.649 | 0.875 | 0.887 | 0 | 1.000 | 1.000 |
| strict_format | 759 | 1.000 | 0.649 | 0.875 | 0.887 | 0 | 1.000 | 1.000 |

## ACD Summary

| ACD | Rows | Exact label | Semantic drift | Evidence retained |
| --- | ---: | ---: | ---: | ---: |
| ACD-003 | 10 | 0.900 | 1 | 1.000 |
| ACD-004 | 5 | 1.000 | 0 | 1.000 |
| ACD-005 | 5 | 1.000 | 0 | 1.000 |
| ACD-006 | 14 | 0.929 | 1 | 1.000 |
| ACD-007 | 23 | 0.174 | 1 | 1.000 |
| ACD-008 | 5 | 0.800 | 1 | 1.000 |
| ACD-009 | 5 | 0.800 | 1 | 1.000 |
| ACD-010 | 5 | 0.800 | 1 | 1.000 |
| none | 2223 | 0.649 | 0 | 1.000 |

## Claim Boundary

Rows marked `materialized_replay` come from saved validation replay state-graph projection metadata. Rows marked `focused_fixture` are small source-near ACD fixtures that freeze the selected state and policy decision. ACD-off rows are ablations only; they are included to measure dependence on explicit policy, not as candidate policies.

## Instrumentation Gaps

- No diagnostic-only rows were emitted; all rows are either materialized saved replay or focused ACD fixtures.
