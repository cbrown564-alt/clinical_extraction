# Gan 2026 RQ1 Candidate-Discovery Matrix

Replay-first component matrix for RQ1 candidate discovery. This is a validation-development artifact, not a benchmark or locked-holdout claim.

- JSONL artifact: `experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl`
- Matrix rows: 5442
- Source rows represented: 750

## Generator Summary

| Generator | Source rows | Candidates | Recalled source rows | Recall rate | False positives/note | Exact evidence | Exact rate | Median candidates/note | p90 candidates/note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deterministic_candidates_all | 750 | 1194 | 725 | 0.967 | 0.257 | 1072 | 0.898 | 1.0 | 3 |
| deterministic_top_candidate | 750 | 750 | 716 | 0.955 | 0.045 | 635 | 0.847 | 1.0 | 1 |
| llm_candidate_selector_raw | 739 | 2126 | 642 | 0.869 | 1.365 | 2095 | 0.985 | 3 | 4 |
| llm_selected_state_or_evidence | 250 | 250 | 222 | 0.888 | 0.112 | 239 | 0.956 | 1.0 | 1 |
| state_graph_nodes | 750 | 1122 | 725 | 0.967 | 0.244 | 1000 | 0.891 | 1.0 | 3 |

## Claim Boundary

This matrix measures candidate recall, exact evidence, candidate burden, and metadata availability from saved artifacts. It does not measure final Purist/Pragmatic F1 and does not authorize locked-holdout use.
